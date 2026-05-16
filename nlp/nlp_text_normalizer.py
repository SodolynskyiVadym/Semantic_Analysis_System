import re


def normalize_ner(ner_results, combined_text):
    if not ner_results:
        return []

    # 1. Tokenize combined_text into individual words with their exact character bounds
    true_words = []
    for match in re.finditer(r'\S+', combined_text):
        true_words.append({
            "word": match.group(),
            "start": match.start(),
            "end": match.end()
        })

    aligned_entities = []

    # 2. Map subword model predictions onto actual full-word boundaries
    for entity in ner_results:
        ent_start = entity['start']
        ent_end = entity['end']
        
        intersecting_words = [
            w for w in true_words 
            if w['start'] <= ent_end and w['end'] >= ent_start
        ]
        
        if intersecting_words:
            new_start = intersecting_words[0]['start']
            new_end = intersecting_words[-1]['end']
            
            aligned_entities.append({
                "entity_group": entity['entity_group'],
                "score": entity['score'],
                "word": combined_text[new_start:new_end],
                "start": new_start,
                "end": new_end
            })
        else:
            aligned_entities.append(entity.copy())

    # 3. Merge duplicate subword chunks and adjacent entities based on confidence score
    aligned_entities.sort(key=lambda x: x['start'])
    
    merged_results = [aligned_entities[0]]
    
    for current in aligned_entities[1:]:
        last = merged_results[-1]
        
        # Scenario A: Handle multi-chunk splits of the exact same word (duplicate bounds)
        if current['start'] == last['start'] and current['end'] == last['end']:
            if current['score'] > last['score']:
                last['entity_group'] = current['entity_group']
                last['score'] = current['score']
                
        # Scenario B: Merge adjacent words or multi-word phrases
        elif current['start'] <= last['end']:
            if current['score'] > last['score']:
                last['entity_group'] = current['entity_group']
                last['score'] = current['score']
            
            last['end'] = max(last['end'], current['end'])
            last['word'] = combined_text[last['start']:last['end']].strip()
            
        # Scenario C: Independent standalone entity
        else:
            merged_results.append(current)
            
    # 4. Strip trailing punctuation from word tokens and recalculate character indices
    for res in merged_results:
        original = res['word']
        cleaned = original.strip('.,!?:;"\'')
        
        if len(cleaned) < len(original):
            diff_start = original.find(cleaned)
            res['start'] += diff_start
            res['end'] = res['start'] + len(cleaned)
            res['word'] = cleaned

    return merged_results