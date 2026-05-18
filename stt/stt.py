import os
from faster_whisper import WhisperModel
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, "config.env"))
load_dotenv(os.path.join(CURRENT_DIR, "secret.env"), override=True)

MODEL_DIR = os.path.join(CURRENT_DIR, os.getenv("MODEL_PATH", "model"))
WHISPER_MODEL_SIZE = "large-v3"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_BEAM_SIZE = 8

print("Loading Whisper model...")
model = WhisperModel(
    WHISPER_MODEL_SIZE, 
    device="cuda", 
    compute_type=WHISPER_COMPUTE_TYPE,
    download_root=MODEL_DIR
)
print("Model successfully loaded.\n")

def run_transcription(file_path):
    print(f"[*] Starting Whisper transcription for: {file_path}")
    
    segments, _ = model.transcribe(
        file_path, 
        beam_size=WHISPER_BEAM_SIZE, 
        vad_filter=True,
        vad_parameters=dict(threshold=0.1, min_speech_duration_ms=250),
        language="ru",
        condition_on_previous_text=False
    )
  
    transcript_data = []
    for segment in segments:
        text = segment.text.strip()
        print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {text}")
        
        transcript_data.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": text,
            "confidence": round(1 - segment.no_speech_prob, 2),
            "speaker_tag": "UNKNOWN"
        })
        
    return transcript_data