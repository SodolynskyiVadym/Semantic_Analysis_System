from transformers import pipeline
import os
from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

load_dotenv(os.path.join(PROJECT_ROOT, "config.env"))
load_dotenv(os.path.join(PROJECT_ROOT, "secret.env"), override=True)

MODELS_DIR = os.path.join(PROJECT_ROOT, os.getenv("MODEL_PATH", "models"))
NLP_MODEL_PATH = os.path.join(PROJECT_ROOT, os.getenv("MODEL_PATH", "models"), os.getenv("NLP_MODEL_PATH", "military_ner_model_v1"))

print("Loading model from local disk...")
ner_pipeline = pipeline("ner", model=NLP_MODEL_PATH, aggregation_strategy="simple")

test_text = "База, я Ворон. Вижу два вражеских танка на перекрестке и до взвода их пехоты. У нас один трехсотый, нужна эвакуация."

print("🔍 Analyzing text...\n")
results = ner_pipeline(test_text)

print(f"Text: {test_text}\n")
print("Found entities:")

if not results:
    print("No entities found.")
else:
    for entity in results:
        print(f"  - [{entity['entity_group']}]: {entity['word']} (Confidence: {entity['score']:.2f})")
