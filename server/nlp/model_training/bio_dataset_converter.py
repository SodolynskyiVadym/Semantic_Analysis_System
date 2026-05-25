from datasets import Dataset, ClassLabel

def read_conll_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        tokens = []
        ner_tags = []
        for line in f:
            line = line.strip()
            if not line: 
                if tokens:
                    yield {"tokens": tokens, "ner_tags": ner_tags}
                    tokens = []
                    ner_tags = []
            else:
                splits = line.split("\t")
                if len(splits) == 2:
                    tokens.append(splits[0])
                    ner_tags.append(splits[1])
        if tokens:
            yield {"tokens": tokens, "ner_tags": ner_tags}


def prepare_dataset(file_path):
    print(f"Reading data from {file_path}...")
    parsed_data = list(read_conll_file(file_path))

    unique_tags = set(tag for doc in parsed_data for tag in doc["ner_tags"])
    unique_tags = ["O"] + sorted(list(unique_tags - {"O"}))
    
    tags_class = ClassLabel(names=unique_tags)

    dataset = Dataset.from_list(parsed_data)

    def align_labels_to_ints(example):
        example["ner_tags"] = [tags_class.str2int(tag) for tag in example["ner_tags"]]
        return example

    dataset = dataset.map(align_labels_to_ints)
    dataset = dataset.train_test_split(test_size=0.2, seed=42)
    return dataset, tags_class


