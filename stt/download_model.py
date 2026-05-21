from faster_whisper import WhisperModel
from config import settings


WHISPER_MODEL_SIZE = settings.WHISPER_MODEL_SIZE

print(f"Downloading Whisper '{WHISPER_MODEL_SIZE}' model to {settings.STT_MODEL_DIR}...")

WhisperModel(
    WHISPER_MODEL_SIZE,
    compute_type="int8",
    download_root=settings.STT_MODEL_DIR
)

print("Download complete!")