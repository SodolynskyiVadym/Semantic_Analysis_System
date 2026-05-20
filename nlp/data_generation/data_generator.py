import os
import json
import time
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
from promts import *
from config import settings


TRAINING_DATA_PATH = settings.TRAINING_DATA_PATH


PROJECT_ID = settings.PROJECT_ID
LOCATION = settings.LOCATION
MODEL = settings.MODEL

if not PROJECT_ID or not LOCATION:
    raise ValueError("PROJECT_ID and LOCATION must be set in the .env file")


vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL)


generation_config = GenerationConfig(
    response_mime_type="application/json",
    temperature=0.9,
    top_p=1.0,
    top_k=32,
)


def generate_batch(batch_size: int = 50, promt: str = PROMPT_NER_MAIN) -> list:
    print(f"Generating batch of {batch_size} samples...")
    try:
        response = model.generate_content(
            promt.replace("{batch_size}", str(batch_size)),
            generation_config=generation_config,
            safety_settings=[],
        )
        json_response = json.loads(response.text)
        print(f"Successfully generated {len(json_response)} samples.")
        return json_response
    except Exception as e:
        print(f"Error generating data: {e}")
        return []


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
    # main(num_batches=70, samples_per_batch=15, promt=PROMPT_NER_MAIN, start_index=1)
    # main(num_batches=30, samples_per_batch=15, promt=PROMPT_NER_RECON, start_index=71)
    # main(num_batches=30, samples_per_batch=15, promt=PROMPT_NER_FRIENDLY_OPS, start_index=101)
    # main(num_batches=20, samples_per_batch=15, promt=PROMPT_NER_NOISE, start_index=131)
    # main(num_batches=30, samples_per_batch=15, promt=PROMPT_NER_AMBIGUOUS, start_index=151)
    # main(num_batches=10, samples_per_batch=15, promt=PROMT_SPECIAL_DATA, start_index=181) # REMOVE THIS PROMT
    # main(num_batches=20, samples_per_batch=15, promt=PROMT_MILITARY_POSITIONS, start_index=191)
    # main(num_batches=10, samples_per_batch=15, promt=PROMT_CIVILIANS, start_index=211)
    # main(num_batches=20, samples_per_batch=15, promt=PROMT_SWEAR_WORD, start_index=221)
    # main(num_batches=15, samples_per_batch=15, promt=PROMT_MILITARY_UNITS, start_index=241)
    main(num_batches=15, samples_per_batch=15, promt=PROMT_CONTEXTUAL_PERSONNEL, start_index=256)

