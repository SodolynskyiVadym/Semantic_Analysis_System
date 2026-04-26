import os
import json
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig, Part
from dotenv import load_dotenv


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)


# Load environment variables from .env file
load_dotenv(os.path.join(PROJECT_ROOT, "config.env"))
load_dotenv(os.path.join(PROJECT_ROOT, "secret.env"), override=True)

# --- Configuration from .env ---
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")

if not PROJECT_ID or not LOCATION:
    raise ValueError("PROJECT_ID and LOCATION must be set in the .env file")

# --- Vertex AI Initialization ---
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.5-flash")

# --- Generation Configuration ---
generation_config = GenerationConfig(
    response_mime_type="application/json",
    temperature=0.9,
    top_p=1.0,
    top_k=32,
)

# --- Prompt for Gemini ---
PROMPT = """
Generate 50 unique, realistic, and short military radio conversations in Russian between two soldiers. Use diverse scenarios: spotting equipment, reporting coordinates, or coordination between units. Ensure the entities are accurately labeled according to the provided schema. The output should be a JSON list of objects, where each object has:
- `text`: A string (2-4 sentences) representing a conversation snippet in Russian (including military slang, callsigns, and coordinates).
- `entities`: A list of dictionaries with `word` and `label`.

Example:
[
  {
    "text": "Альфа-7, прием! Вижу танк противника на высоте 105. Запрашиваю разрешение на огонь.",
    "entities": [
      {"word": "Альфа-7", "label": "CALLSIGN"},
      {"word": "танк", "label": "EQUIPMENT"},
      {"word": "высоте 105", "label": "LOCATION"}
    ]
  },
  {
    "text": "Ваня, на связи! Принято. Жди подтверждения, работают наши дроны. Конец связи.",
    "entities": [
      {"word": "Ваня", "label": "CALLSIGN"},
      {"word": "дроны", "label": "EQUIPMENT"}
    ]
  }
]
"""

# --- Data Generation Function ---
def generate_batch(batch_size: int = 50) -> list:
    print(f"Generating batch of {batch_size} samples...")
    try:
        response = model.generate_content(
            PROMPT.replace("50", str(batch_size)),
            generation_config=generation_config,
            safety_settings=[], # Disable safety settings for this task
        )
        # Assuming the model returns valid JSON directly
        json_response = json.loads(response.text)
        print(f"Successfully generated {len(json_response)} samples.")
        return json_response
    except Exception as e:
        print(f"Error generating data: {e}")
        return []

# --- Main Execution ---
def main(num_batches: int = 10, samples_per_batch: int = 50, output_dir: str = "data_generation"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i in range(num_batches):
        print(f"Starting batch {i + 1}/{num_batches}")
        batch_data = generate_batch(samples_per_batch)
        
        # Save each batch to a separate JSON file
        output_file = os.path.join(output_dir, f"synthetic_ner_dataset_batch_{i+1}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)
        print(f"Batch {i+1} saved to {output_file}")

    print(f"Finished generating {num_batches} batches.")

if __name__ == "__main__":
    # You can change these parameters as needed
    main(num_batches=20, samples_per_batch=25)
