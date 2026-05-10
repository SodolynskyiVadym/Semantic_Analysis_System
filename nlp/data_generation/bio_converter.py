import os
import json
import re
from dotenv import load_dotenv


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
NLP_ROOT = os.path.dirname(CURRENT_DIR)


load_dotenv(os.path.join(NLP_ROOT, "config.env"))
load_dotenv(os.path.join(NLP_ROOT, "secret.env"), override=True)

TRAINING_DATA_PATH = os.path.join(NLP_ROOT, os.getenv("TRAINING_DATA_PATH", "training_data"))
OUTPUT_FILE = os.path.join(NLP_ROOT, os.getenv("BIO_FILE", "dataset_bio.txt"))

def tokenize_text(text):
    return re.findall(r"[\w'-]+|[.,!?;]", text)

def convert_json_to_bio(json_data):
    bio_dataset = []
    
    for item in json_data:
        text = item.get('text', '')
        entities = item.get('entities', [])
        
        tokens = tokenize_text(text)
        
        labels = ['O'] * len(tokens)
        
        for ent in entities:
            ent_word = ent.get('word', '')
            ent_label = ent.get('label', '')
            
            if not ent_word or not ent_label:
                continue
    
            ent_tokens = tokenize_text(ent_word)
            ent_len = len(ent_tokens)
            
            for i in range(len(tokens) - ent_len + 1):
                if tokens[i:i+ent_len] == ent_tokens:
                    labels[i] = f"B-{ent_label}"
                    for j in range(1, ent_len):
                        labels[i+j] = f"I-{ent_label}"
                        
        sentence_bio = list(zip(tokens, labels))
        bio_dataset.append(sentence_bio)
        
    return bio_dataset

def main():
    if not os.path.exists(TRAINING_DATA_PATH):
        print(f"Error: Directory {TRAINING_DATA_PATH} not found.")
        return

    all_bio_data = []
    
    print(f"Reading files from {TRAINING_DATA_PATH}...")
    for filename in os.listdir(TRAINING_DATA_PATH):
        if filename.endswith(".json"):
            filepath = os.path.join(TRAINING_DATA_PATH, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    all_bio_data.extend(convert_json_to_bio(json_data))
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    print(f"Saving converted data to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for sentence in all_bio_data:
            for word, label in sentence:
                f.write(f"{word}\t{label}\n")
            f.write("\n") 

    print(f"Done. Successfully converted {len(all_bio_data)} conversations.")

if __name__ == "__main__":
    main()