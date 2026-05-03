import os
from dotenv import load_dotenv

from bio_dataset_converter import prepare_dataset
from tokenization import tokenize_dataset
from training_model import train_ner_model

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

load_dotenv(os.path.join(PROJECT_ROOT, "config.env"))
load_dotenv(os.path.join(PROJECT_ROOT, "secret.env"), override=True)

BIO_FILE_PATH = os.path.join(PROJECT_ROOT, os.getenv("BIO_FILE_PATH", "data/dataset_bio.txt"))
NLP_MODEL_SAVE_PATH = os.path.join(PROJECT_ROOT, os.getenv("MODEL_PATH", "models"), "military_ner_model_local")
MODEL_CHECKPOINT = os.getenv("MODEL_CHECKPOINT", "xlm-roberta-base")

def main():
    print("\n--- Step 1: Preparing dataset ---")
    dataset, tags_class = prepare_dataset(BIO_FILE_PATH)
    print("Dataset prepared successfully.")
    print(dataset)
    print("Your entity classes:", tags_class.names)

    print("\n--- Step 2: Tokenizing dataset ---")
    tokenized_datasets, tokenizer, data_collator = tokenize_dataset(dataset, MODEL_CHECKPOINT)
    print("Dataset tokenized successfully.")

    print("\n--- Step 3: Training NER model ---")
    train_ner_model(tokenized_datasets, data_collator, tokenizer, tags_class, MODEL_CHECKPOINT, NLP_MODEL_SAVE_PATH)
    print("Model training completed and saved!")

if __name__ == "__main__":
    print(PROJECT_ROOT)
    print(CURRENT_DIR)
    print(BIO_FILE_PATH)
    main()
