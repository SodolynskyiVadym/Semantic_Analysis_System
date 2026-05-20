from transformers import pipeline
from config import settings
from nlp.models import AnalysisSegment, TranscribeSegment
from nlp.nlp_text_normalizer import normalize_ner

print(f"[*] Loading NER model")
try:
    ner_pipeline = pipeline("ner", model=settings.MODEL_PATH, aggregation_strategy="simple")
    print("[v] NER model loaded successfully.")
except Exception as e:
    print(f"[!] Error loading NER model: {e}")
    exit(1)


def run_ner(transcription: list[TranscribeSegment]):
    try:
        combined_text = " ".join(
            segment.text.strip() 
            for segment in transcription
            if segment.text.strip()
        )

        if not combined_text:
            print("[!] Combined text is empty. Skipping NER.")
            return [], []

        raw_ner_results = ner_pipeline(combined_text)
        normalized_results = normalize_ner(raw_ner_results, combined_text)
        
        segments = [AnalysisSegment(**item) for item in normalized_results]

        unique_entity_types = list({
            segment.entity_group for segment in segments if segment.entity_group != "O"
        })
        
        print(f"[*] Unique entity types found: {unique_entity_types}")
        
        return segments, unique_entity_types

    except Exception as e:
        print(f"[!] An error occurred during NER processing: {e}")
        raise e