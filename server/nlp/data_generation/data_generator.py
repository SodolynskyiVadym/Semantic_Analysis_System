import os
import json
import re
import time
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from promts import *
from config import settings


TRAINING_DATA_PATH = settings.TRAINING_DATA_PATH
PROJECT_ID = settings.PROJECT_ID
LOCATION = settings.LOCATION
MODEL = settings.GENERATION_DATA_MODEL

DATASET_PREFIX = "synthetic_dataset_"
DATASET_EXT = ".json"


vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL)


generation_config = GenerationConfig(
    response_mime_type="application/json",
    temperature=0.9,
    top_p=1.0,
    top_k=32,
)


def get_next_dataset_index():
    if not os.path.exists(TRAINING_DATA_PATH):
        os.makedirs(TRAINING_DATA_PATH)
        return 1

    max_index = 0
    pattern_str = rf"{re.escape(DATASET_PREFIX)}(\d+){re.escape(DATASET_EXT)}"
    pattern = re.compile(pattern_str)

    for filename in os.listdir(TRAINING_DATA_PATH):
        match = pattern.match(filename)
        if match:
            current_index = int(match.group(1))
            if current_index > max_index:
                max_index = current_index

    return max_index + 1


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


def main(num_batches, samples_per_batch, promt=PROMPT_NER_MAIN):
    if not os.path.exists(TRAINING_DATA_PATH):
        os.makedirs(TRAINING_DATA_PATH)

    current_index = get_next_dataset_index(TRAINING_DATA_PATH)

    for i in range(num_batches):
        print(f"Starting batch {i + 1}/{num_batches}")
        
        batch_data = generate_batch(samples_per_batch, promt=promt)
        
        file_name = f"{DATASET_PREFIX}{current_index}{DATASET_EXT}"
        output_file = os.path.join(TRAINING_DATA_PATH, file_name)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
            
        print(f"Batch {i+1} saved to {output_file}")
        current_index += 1
        time.sleep(3)

    print(f"Finished generating {num_batches} batches.")


if __name__ == "__main__":
    # main(num_batches=70, samples_per_batch=15, promt=PROMPT_NER_MAIN)
    # main(num_batches=30, samples_per_batch=15, promt=PROMPT_NER_RECON)
    # main(num_batches=30, samples_per_batch=15, promt=PROMPT_NER_FRIENDLY_OPS)
    # main(num_batches=20, samples_per_batch=15, promt=PROMPT_NER_NOISE)
    # main(num_batches=30, samples_per_batch=15, promt=PROMPT_NER_AMBIGUOUS)
    # main(num_batches=20, samples_per_batch=15, promt=PROMT_MILITARY_POSITIONS)
    # main(num_batches=10, samples_per_batch=15, promt=PROMT_CIVILIANS)
    # main(num_batches=20, samples_per_batch=15, promt=PROMT_SWEAR_WORD)
    # main(num_batches=15, samples_per_batch=15, promt=PROMT_MILITARY_UNITS)
    main(num_batches=15, samples_per_batch=15, promt=PROMT_CONTEXTUAL_PERSONNEL)

