from transformers import pipeline
from config import settings
from nlp.models import AnalysisSegment, TranscribeSegment
from nlp.nlp_text_normalizer import normalize_ner

class NLPProcessor:
    def __init__(self):
        self.ner_pipeline = pipeline(
            "ner", 
            model=settings.NLP_AI_MODEL_PATH, 
            aggregation_strategy="simple"
        )

    def process(self, transcription: list[TranscribeSegment]) -> tuple[list[AnalysisSegment], list[str]]:
        combined_text = " ".join(
            segment.text.strip() 
            for segment in transcription
            if segment.text.strip()
        )

        if not combined_text:
            return [], []

        raw_ner_results = self.ner_pipeline(combined_text)
        normalized_results = normalize_ner(raw_ner_results, combined_text)
        
        segments = [AnalysisSegment(**item) for item in normalized_results]

        unique_entity_types = list({
            segment.entity_group for segment in segments if segment.entity_group != "O"
        })
        
        return segments, unique_entity_types