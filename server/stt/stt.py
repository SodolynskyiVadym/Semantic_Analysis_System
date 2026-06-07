import numpy as np
from faster_whisper import WhisperModel
from config import settings
from stt.models import TranscribeSegment

class WhisperProcessor:
    def __init__(self):
        self.model = WhisperModel(
            settings.WHISPER_MODEL_SIZE, 
            device="cuda", 
            compute_type=settings.WHISPER_COMPUTE_TYPE,
            download_root=settings.STT_AI_MODEL_DIR
        )

    def process(self, audio_data: np.ndarray) -> list:
        segments, _ = self.model.transcribe(
            audio_data, 
            beam_size=settings.WHISPER_BEAM_SIZE, 
            vad_filter=True,
            vad_parameters=dict(threshold=0.1, min_speech_duration_ms=250),
            language="ru",
            condition_on_previous_text=False
        )
        
        segments_list = []
        for segment in segments:
            text = segment.text.strip()
            confidence = round(1 - segment.no_speech_prob, 2)
            segments_list.append(TranscribeSegment(
                start=round(segment.start, 2),
                end=round(segment.end, 2),
                text=text,
                confidence=confidence
            ))
            print(f"[*] Text: {text} | Confidence: {confidence}")
            
        return segments_list