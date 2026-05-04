import json
import os
from faster_whisper import WhisperModel
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

load_dotenv(os.path.join(PROJECT_ROOT, "config.env"))
load_dotenv(os.path.join(PROJECT_ROOT, "secret.env"), override=True)

MODEL_DIR = os.path.join(PROJECT_ROOT, os.getenv("MODEL_PATH", "models"))

DATA_PATH = os.path.join(PROJECT_ROOT, "data/audio_data")
TRANSCRIPTION_PATH = os.path.join(PROJECT_ROOT, "data/transcription_data")

WHISPER_MODEL_SIZE = "medium"
WHISPER_COMPUTE_TYPE = "int8"
WHISPER_BEAM_SIZE = 8

print("Loading Whisper model into VRAM...")

model = WhisperModel(
    WHISPER_MODEL_SIZE, 
    device="cuda", 
    compute_type=WHISPER_COMPUTE_TYPE,
    download_root=MODEL_DIR
)

print("Model successfully loaded and ready for use.\n")

def transcribe_and_save(audio_file, output_json_path):
    full_input_path = os.path.join(DATA_PATH, audio_file)
    
    if not os.path.exists(full_input_path):
        print(f"Error: File '{audio_file}' not found!")
        return

    print(f"Starting transcription for file: {audio_file}")
    
    segments, _ = model.transcribe(
        full_input_path, 
        beam_size=WHISPER_BEAM_SIZE, 
        vad_filter=True,
        language="ru"
    )
    
    transcript_data = []
    
    for segment in segments:
        text = segment.text.strip()
        print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {text}")
        
        transcript_data.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": text,
            "confidence": round(1 - segment.no_speech_prob, 2)
        })
        
    full_output_path = os.path.join(TRANSCRIPTION_PATH, output_json_path)
    
    os.makedirs(TRANSCRIPTION_PATH, exist_ok=True)
    
    with open(full_output_path, "w", encoding="utf-8") as f:
        json.dump(transcript_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    INPUT_AUDIO_FILE = "audio1.mp4" 
    OUTPUT_RESULT_FILE = "audio1.json"
    
    transcribe_and_save(INPUT_AUDIO_FILE, OUTPUT_RESULT_FILE)