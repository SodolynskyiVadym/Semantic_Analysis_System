import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # SHARED CONFIG
    # TODO: add ENV variable(maybe)
    CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))

    MONGO_CONNECTION_STRING: str = "mongodb://admin:password@localhost:27017/"
    MONGO_DB_NAME: str = "analysis_db"

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "password"
    RABBITMQ_QUEUE: str = "nlp_queue"


    # NLP CONFIG
    NLP_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nlp")

    NLP_MODEL_PATH: str = os.path.join(NLP_DIR, "models", "military_ner_model_v9")
    BIO_FILE_PATH: str = os.path.join(NLP_DIR, "dataset_bio.txt")
    TRAINING_DATA_PATH: str = os.path.join(NLP_DIR, "training_data")
    NLP_LOG_FILE: str = os.path.join(NLP_DIR, "nlp.log")

    PROJECT_ID: str
    LOCATION: str
    GENERATION_DATA_MODEL: str = "gemini-2.5-pro"

    MODEL_CHECKPOINT: str = "xlm-roberta-base"


    # STT CONFIG
    STT_DIR: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stt")

    AUDIO_DIR: str = os.path.join(CURRENT_DIR, "uploads")
    STT_MODEL_DIR: str = os.path.join(STT_DIR, "model")
    STT_LOG_FILE: str = os.path.join(STT_DIR, "stt.log")

    WHISPER_MODEL_SIZE: str = "large-v3"
    WHISPER_COMPUTE_TYPE: str = "int8"
    WHISPER_BEAM_SIZE: int = 8


    model_config = SettingsConfigDict(
        env_file="secret.env",
        env_file_encoding="utf-8"
    )


settings = Settings()
