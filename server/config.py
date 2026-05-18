import os
from pydantic_settings import BaseSettings, SettingsConfigDict


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

class Settings(BaseSettings):
    # TODO: add ENV variable(maybe)
    AUDIO_DIR: str = os.path.join(PROJECT_ROOT, "uploads")

    MONGO_CONNECTION_STRING: str = "mongodb://admin:password@localhost:27017/"
    MONGO_DB_NAME: str = "analysis_db"

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "password"
    RABBITMQ_QUEUE: str = "stt_tasks"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
