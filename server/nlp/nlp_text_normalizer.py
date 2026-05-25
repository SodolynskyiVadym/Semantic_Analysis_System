import re

def normalize_ner(ner_results, combined_text):
    if not ner_results:
        return []

    true_words = []
    for match in re.finditer(r'\S+', combined_text):
        true_words.append({
            "word": match.group(),
            "start": match.start(),
            "end": match.end()
        })

    aligned_entities = []

    for entity in ner_results:
        ent_start = entity['start']
        ent_end = entity['end']
        
        intersecting_words = [
            w for w in true_words 
            if w['start'] < ent_end and w['end'] > ent_start
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

    if not aligned_entities:
        return []

    aligned_entities.sort(key=lambda x: x['start'])
    merged_results = [aligned_entities[0]]
    
    for current in aligned_entities[1:]:
        last = merged_results[-1]
        
        if current['start'] <= last['end']:
            if current['score'] > last['score']:
                last['entity_group'] = current['entity_group']
                last['score'] = current['score']
            
            last['end'] = max(last['end'], current['end'])
            last['word'] = combined_text[last['start']:last['end']].strip()
            
        else:
            merged_results.append(current)
            
    final_results = []
    for res in merged_results:
        original = res['word']
        cleaned = original.strip('.,!?:;"\'()[]{}') 
        
        if not cleaned:
            continue
            
        if len(cleaned) < len(original):
            diff_start = original.find(cleaned)
            res['start'] += diff_start
            res['end'] = res['start'] + len(cleaned)
            res['word'] = cleaned
            
        final_results.append(res)

    return final_results