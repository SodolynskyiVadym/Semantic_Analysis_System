import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # TODO: add ENV variable(maybe)

    CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT: str = os.path.dirname(CURRENT_DIR)
    AUDIO_DIR: str = os.path.join(PROJECT_ROOT, "uploads")
    MODEL_DIR: str = os.path.join(CURRENT_DIR, "model")

    WHISPER_MODEL_SIZE: str = "large-v3"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_BEAM_SIZE: int = 8

    MONGO_CONNECTION_STRING: str = "mongodb://admin:password@localhost:27017/"
    MONGO_DB_NAME: str = "analysis_db"

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "password"
    RABBITMQ_STT_QUEUE: str = "stt_queue"
    RABBITMQ_NLP_QUEUE: str = "nlp_queue"

    model_config = SettingsConfigDict(
        env_file=("config.env", "secret.env"),
        env_file_encoding="utf-8"
    )


settings = Settings()
