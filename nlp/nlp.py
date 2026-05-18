import os
import json
import numpy as np
from transformers import pipeline
from database import audio_tasks_collection
from dotenv import load_dotenv
from nlp_text_normalizer import normalize_ner
import re

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(CURRENT_DIR, "config.env"))
load_dotenv(os.path.join(CURRENT_DIR, "secret.env"), override=True)

NLP_MODEL_PATH = os.path.join(CURRENT_DIR, os.getenv("MODEL_PATH", "models"), "military_ner_model_v9")

try:
    print(f"Loading NER model from {NLP_MODEL_PATH}...")
    ner_pipeline = pipeline("ner", model=NLP_MODEL_PATH, aggregation_strategy="simple")
    print("NER model loaded successfully.")
except Exception as e:
    print(f"Error loading NER model: {e}")
    exit()


def process_transcription_for_ner():
    annotated_segments_result = [] 
    
    try:
        document = audio_tasks_collection.find_one(
            {"_id": "f9d4ced6-72fb-4b08-8751-a37ead0a0029", "status": "COMPLETED", "transcription": {"$exists": True, "$type": "array", "$ne": []}}
        )

        if not document:
            print("No document found with status 'COMPLETED' and a non-empty 'transcription' array.")
            return

        print(f"Processing document with _id: {document['_id']}")

        transcription = document.get("transcription", [])

        combined_text = ""
        char_offset = 0
        segment_mapping = []

        # Merge segments into a single text and calculate global character offsets
        for segment in transcription:
            text = segment.get("text", "").strip()
            start_time = segment.get("start")
            whisper_score = segment.get("confidence", segment.get("score"))

            if text and start_time is not None:
                start_char = char_offset
                end_char = char_offset + len(text)
                
                segment_mapping.append({
                    "start_char": start_char,
                    "end_char": end_char,
                    "start_time": start_time,
                    "whisper_score": whisper_score,
                    "original_text": text,
                    "entities": []
                })
                
                combined_text += text + " "
                char_offset += len(text) + 1 

        combined_text = combined_text.strip()

        if combined_text:
            ner_results = ner_pipeline(combined_text)
            ner_results = normalize_ner(ner_results, combined_text)
            
            # Map global NER entities into their corresponding transcription segments
            for entity in ner_results:
                if entity['entity_group'] != 'O':
                    cleaned_word = entity['word'].strip()
                    score = round(float(entity['score']), 3) if isinstance(entity['score'], np.float32) else round(entity['score'], 3)
                    
                    entity_start_char = entity['start']
                    entity_end_char = entity['end']
                    
                    # Align spanning or broken words using the end boundary index
                    matched_segment = next(
                        (seg for seg in segment_mapping if seg["start_char"] < entity_end_char <= seg["end_char"]), 
                        None
                    )
                    
                    if matched_segment:
                        local_start = max(0, entity_start_char - matched_segment["start_char"])
                        local_end = entity_end_char - matched_segment["start_char"]
                        
                        matched_segment["entities"].append({
                            "word": cleaned_word,
                            "entity_type": entity['entity_group'],
                            "score": score,
                            "local_start": local_start,
                            "local_end": local_end
                        })

            # Format the final text embedding [Entity Score] tags into each word
            for seg in segment_mapping:
                annotated_text = seg["original_text"]
                
                # Sort in reverse order to prevent character index shifting during injection
                sorted_entities = sorted(seg["entities"], key=lambda x: x["local_end"], reverse=True)
                
                for ent in sorted_entities:
                    local_start = ent["local_start"]
                    local_end = ent["local_end"]
                    tag = f"{ent['entity_type']} {ent['score']}"
                    
                    original_substring = annotated_text[local_start:local_end]
                    tagged_substring = re.sub(r'(\S+)', rf'\1 [{tag}]', original_substring)
                    
                    annotated_text = annotated_text[:local_start] + tagged_substring + annotated_text[local_end:]
                
                annotated_segments_result.append({
                    "start_time": seg["start_time"],
                    "whisper_score": seg["whisper_score"],
                    "annotated_text": annotated_text
                })

            unique_entity_types = list({
                ent['entity_group'] 
                for ent in ner_results 
                if ent['entity_group'] != 'O'
            })

            for original_seg in transcription:
                matched_annotated = next(
                    (ann for ann in annotated_segments_result if ann["start_time"] == original_seg.get("start")), 
                    None
                )
                if matched_annotated:
                    original_seg["annotated_text"] = matched_annotated["annotated_text"]

            print("Saving results to database...")
            update_result = audio_tasks_collection.update_one(
                {"_id": document["_id"]},
                {
                    "$set": {
                        "analysis": annotated_segments_result,
                        "entities": unique_entity_types
                    }
                }
            )

            if update_result.modified_count > 0:
                print(f"Document {document['_id']} successfully updated in database!")
            else:
                print(f"Document {document['_id']} matched, but no new data was modified.")

    except Exception as e:
        print(f"An error occurred during NER processing: {e}")
        
    print("\n--- Annotated Text Segments ---")
    print(json.dumps(annotated_segments_result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    process_transcription_for_ner()