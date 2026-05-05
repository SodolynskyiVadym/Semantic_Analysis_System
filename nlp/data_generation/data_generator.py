import os
import json
import time
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
from dotenv import load_dotenv
from nlp.data_generation.promts import *


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)


# Load environment variables from .env file
load_dotenv(os.path.join(PROJECT_ROOT, "config.env"))
load_dotenv(os.path.join(PROJECT_ROOT, "secret.env"), override=True)

TRAINING_DATA_PATH = os.path.join(PROJECT_ROOT, os.getenv("TRAINING_DATA_PATH", "training_data"))

# --- Configuration from .env ---
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
MODEL = "gemini-2.5-pro"

if not PROJECT_ID or not LOCATION:
    raise ValueError("PROJECT_ID and LOCATION must be set in the .env file")

# --- Vertex AI Initialization ---
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL)

# --- Generation Configuration ---
generation_config = GenerationConfig(
    response_mime_type="application/json",
    temperature=0.9,
    top_p=1.0,
    top_k=32,
)


# --- Data Generation Function ---
def generate_batch(batch_size: int = 50, promt: str = PROMPT_NER_MAIN) -> list:
    print(f"Generating batch of {batch_size} samples...")
    try:
        response = model.generate_content(
            promt.replace("{batch_size}", str(batch_size)),
            generation_config=generation_config,
            safety_settings=[],
        )
        # Assuming the model returns valid JSON directly
        json_response = json.loads(response.text)
        print(f"Successfully generated {len(json_response)} samples.")
        return json_response
    except Exception as e:
        print(f"Error generating data: {e}")
        return []


# --- Main Execution ---
def main(num_batches, samples_per_batch, promt=PROMPT_NER_MAIN, start_index=1):
    if not os.path.exists(TRAINING_DATA_PATH):
        os.makedirs(TRAINING_DATA_PATH)

    for i in range(num_batches):
        print(f"Starting batch {i + 1}/{num_batches}")
        batch_data = generate_batch(samples_per_batch, promt=promt)
        
        # Save each batch to a separate JSON file
        output_file = os.path.join(TRAINING_DATA_PATH, f"synthetic_dataset_{start_index}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
        print(f"Batch {i+1} saved to {output_file}")
        start_index += 1
        time.sleep(3)

    print(f"Finished generating {num_batches} batches.")


if __name__ == "__main__":
    main(num_batches=50, samples_per_batch=15, promt=PROMPT_NER_MAIN, start_index=1)
    main(num_batches=25, samples_per_batch=15, promt=PROMPT_NER_RECON, start_index=26)
    main(num_batches=25, samples_per_batch=15, promt=PROMPT_NER_FRIENDLY_OPS, start_index=86)
    main(num_batches=15, samples_per_batch=15, promt=PROMPT_NER_NOISE, start_index=111)

