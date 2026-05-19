from faster_whisper import WhisperModel
from config import settings
from models import TranscribeSegment


print("Loading Whisper model...")



model = WhisperModel(
    settings.WHISPER_MODEL_SIZE, 
    device="cuda", 
    compute_type=settings.WHISPER_COMPUTE_TYPE,
    download_root=settings.MODEL_DIR
)


print("Model successfully loaded.\n")

def run_transcription(file_path):
    print(f"[*] Starting Whisper transcription for: {file_path}")
    
    segments, _ = model.transcribe(
        file_path, 
        beam_size=settings.WHISPER_BEAM_SIZE, 
        vad_filter=True,
        vad_parameters=dict(threshold=0.1, min_speech_duration_ms=250),
        language="ru",
        condition_on_previous_text=False
    )
  
    segments_list = []
    for segment in segments:
        text = segment.text.strip()
        print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {text}")
        
        obj = TranscribeSegment(
            start=round(segment.start, 2),
            end=round(segment.end, 2),
            text=text,
            confidence=round(1 - segment.no_speech_prob, 2)
        )
        segments_list.append(obj)
        
    return segments_list