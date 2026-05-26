import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT: str = os.path.dirname(CURRENT_DIR)
    AUDIO_DIR: str = os.path.join(PROJECT_ROOT, "uploads")


    MONGO_CONNECTION_STRING: str = "mongodb://admin:password@localhost:27017/"
    MONGO_DB_NAME: str = "analysis_db"

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
