import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # TODO: add ENV variable(maybe)

    NLP_DIR: str = os.path.dirname(os.path.abspath(__file__))

    MODEL_PATH: str = os.path.join(NLP_DIR, "models", "military_ner_model_v9")
    BIO_FILE_PATH: str = os.path.join(NLP_DIR, "dataset_bio.txt")
    TRAINING_DATA_PATH: str = os.path.join(NLP_DIR, "training_data")

    PROJECT_ID: str
    LOCATION: str
    MODEL: str = "gemini-2.5-pro"

    MODEL_CHECKPOINT: str = "xlm-roberta-base"

    MONGO_CONNECTION_STRING: str = "mongodb://admin:password@localhost:27017/"
    MONGO_DB_NAME: str = "analysis_db"

    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "user"
    RABBITMQ_PASSWORD: str = "password"
    RABBITMQ_QUEUE: str = "nlp_queue"

    model_config = SettingsConfigDict(
        env_file="secret.env",
        env_file_encoding="utf-8"
    )


settings = Settings()
