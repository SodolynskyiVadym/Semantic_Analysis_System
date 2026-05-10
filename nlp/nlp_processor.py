import os
import json
import numpy as np
from transformers import pipeline
from database import audio_tasks_collection
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(CURRENT_DIR, "config.env"))
load_dotenv(os.path.join(CURRENT_DIR, "secret.env"), override=True)

NLP_MODEL_PATH = os.path.join(CURRENT_DIR, os.getenv("MODEL_PATH", "models"), "military_ner_model_cpu")

try:
    print(f"Loading NER model from {NLP_MODEL_PATH}...")
    ner_pipeline = pipeline("ner", model=NLP_MODEL_PATH, aggregation_strategy="simple")
    print("NER model loaded successfully.")
except Exception as e:
    print(f"Error loading NER model: {e}")
    exit() # Exit if model can't be loaded

def process_transcription_for_ner():
    found_entities = []
    try:
        # 3. Знайти один документ
        # find one document where status is "COMPLETED" and has a "transcription" array
        document = audio_tasks_collection.find_one(
            {"status": "COMPLETED", "transcription": {"$exists": True, "$type": "array", "$ne": []}}
        )

        if not document:
            print("No document found with status 'COMPLETED' and a non-empty 'transcription' array.")
            return

        print(f"Processing document with _id: {document['_id']}")

        # 4. Пройтися циклом по масиву transcription
        transcription = document.get("transcription", [])

        combined_text = ""
        char_offset = 0
        segment_mapping = []

        # 1. Збираємо весь текст і запам'ятовуємо, на яких символах починається кожен аудіосегмент
        for segment in transcription:
            text = segment.get("text", "").strip()
            start_time = segment.get("start")

            if text and start_time is not None:
                start_char = char_offset
                end_char = char_offset + len(text)
                
                # Зберігаємо "координати" сегмента
                segment_mapping.append({
                    "start_char": start_char,
                    "end_char": end_char,
                    "start_time": start_time,
                    "text": text
                })
                
                combined_text += text + " "
                char_offset += len(text) + 1  # +1 для пробілу, який ми додали

        combined_text = combined_text.strip()

        if combined_text:
            # 2. Викликаємо пайплайн ОДИН раз для всього об'єднаного тексту
            ner_results = ner_pipeline(combined_text)

            for entity in ner_results:
                if entity['entity_group'] != 'O':
                    cleaned_word = entity['word'].strip()
                    score = round(float(entity['score']), 3) if isinstance(entity['score'], np.float32) else round(entity['score'], 3)
                    
                    # 3. Розумний пошук: визначаємо, в якому саме сегменті було знайдено це слово
                    entity_start_char = entity['start']
                    matched_segment = next(
                        (seg for seg in segment_mapping if seg["start_char"] <= entity_start_char <= seg["end_char"]), 
                        None
                    )
                    
                    found_entities.append({
                        "entity": cleaned_word,
                        "entity_type": entity['entity_group'],
                        "score": score,
                        "start_char": entity['start'],
                        "end_char": entity['end'],
                        "text_segment": matched_segment["text"] if matched_segment else "UNKNOWN",
                        "start_time": matched_segment["start_time"] if matched_segment else None
                    })

    except Exception as e:
        print(f"An error occurred during NER processing: {e}")
    
    # 7. Красиво вивести фінальний масив знайдених сутностей
    print("\n--- Detected Entities ---")
    print(json.dumps(found_entities, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    process_transcription_for_ner()