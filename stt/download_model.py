from faster_whisper import WhisperModel
import os

# Вказуємо папку, куди збережемо модель (в Docker це буде /app/models)
MODEL_DIR = os.getenv("MODEL_PATH", "/app/models")
WHISPER_MODEL_SIZE = "medium"

print(f"Downloading Whisper '{WHISPER_MODEL_SIZE}' model to {MODEL_DIR}...")

# Ініціалізація завантажить файли, якщо їх там ще немає
WhisperModel(
    WHISPER_MODEL_SIZE,
    device="cpu", # Для завантаження пристрій не має значення
    compute_type="int8",
    download_root=MODEL_DIR
)

print("Download complete!")