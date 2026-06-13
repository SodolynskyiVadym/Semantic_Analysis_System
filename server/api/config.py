import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT: str = os.path.dirname(CURRENT_DIR)
    AUDIO_DIR: str = os.path.join(PROJECT_ROOT, "uploads")

    MAX_FILE_SIZE_MB: int = 25 
    MAX_FILE_SIZE_BYTES: int = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_EXTENSIONS: set[str] = {".mp3", ".mp4", ".wav", ".ogg", ".flac", ".m4a"}

    MONGO_CONNECTION_STRING: str = "mongodb://admin:password@localhost:27017/"
    MONGO_DB_NAME: str = "analysis_db"
    MONGO_AUDIO_TASK_COLLECTION: str = "audio_tasks"

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "password"
    RABBITMQ_STT_QUEUE: str = "stt_queue"
    RABBITMQ_NLP_QUEUE: str = "nlp_queue"


    model_config = SettingsConfigDict(
        env_file="config.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()