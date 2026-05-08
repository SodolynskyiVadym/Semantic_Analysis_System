from dotenv import load_dotenv
from faster_whisper import WhisperModel
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(CURRENT_DIR, "config.env"))
load_dotenv(os.path.join(CURRENT_DIR, "secret.env"), override=True)

MODEL_DIR = os.path.join("/app", os.getenv("MODEL_PATH", "model"))
WHISPER_MODEL_SIZE = "large-v3"

print(f"Downloading Whisper '{WHISPER_MODEL_SIZE}' model to {MODEL_DIR}...")

WhisperModel(
    WHISPER_MODEL_SIZE,
    device="cpu",
    compute_type="int8",
    download_root=MODEL_DIR
)

print("Download complete!")