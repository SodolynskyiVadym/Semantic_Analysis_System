# ==========================================
# ЗАГАЛЬНИЙ БІЙ (Мікс своїх та чужих)
# Використовувати для ~50% датасету
# ==========================================
PROMPT_NER_MAIN_CLEAN = """
Generate {batch_size} unique, realistic, and short military radio conversations in Russian between two soldiers. Use diverse scenarios: combat engagements, spotting enemy movements, or coordination. Ensure the entities are accurately labeled according to the provided schema. The output should be a JSON list of objects, where each object has:
- `text`: A string (2-4 sentences) representing a conversation snippet in Russian. Use context clues (e.g., "наш", "вражеский", "противник") to show affiliation, but DO NOT overuse them. Sound like a natural, fast-paced radio exchange.
- `entities`: A list of dictionaries with `word` and `label`. Labels MUST BE chosen from this list ONLY: CALLSIGN, EQUIPMENT-ENEMY, EQUIPMENT-FRIENDLY, LOCATION, QUANTITY, PERSONNEL-ENEMY, PERSONNEL-FRIENDLY.

IMPORTANT RULES FOR LABELS:
- `EQUIPMENT-ENEMY` / `PERSONNEL-ENEMY`: Enemy vehicles, weapons, and troops.
- `EQUIPMENT-FRIENDLY` / `PERSONNEL-FRIENDLY`: Allied/own vehicles, weapons, and troops.
- `QUANTITY`: Use ONLY for counting equipment or personnel (e.g., "два", "взвод"). Ignore time and distance.
- BOUNDARY RULE: Extract ONLY the core noun or specific military term (e.g., "БМП", "пулеметчик", "танк"). DO NOT include pronouns or descriptive adjectives in the 'word' field (e.g., extract "БМП", NOT "наш БМП" or "вражеский БМП"). DO NOT extract generic pronouns like "мы" or "у нас" as personnel.

Example:
[
  {
    "text": "Берёза, я Сокол-2. Коробочка повреждена. Наблюдаю движение противника: три пикапа и до взвода пехоты заходят в квадрат 45. Запрашиваю арту.",
    "entities": [
      {"word": "Берёза", "label": "CALLSIGN"},
      {"word": "Сокол-2", "label": "CALLSIGN"},
      {"word": "Коробочка", "label": "EQUIPMENT-FRIENDLY"},
      {"word": "противника", "label": "PERSONNEL-ENEMY"},
      {"word": "три", "label": "QUANTITY"},
      {"word": "пикапа", "label": "EQUIPMENT-ENEMY"},
      {"word": "взвода", "label": "QUANTITY"},
      {"word": "пехоты", "label": "PERSONNEL-ENEMY"},
      {"word": "квадрат 45", "label": "LOCATION"}
    ]
  }
]
"""

# ==========================================
# РОЗВІДКА (Фокус на ворогах - ENEMY)
# Використовувати для ~20% датасету
# ==========================================
PROMPT_NER_RECON_CLEAN = """
Generate {batch_size} short military radio conversations in Russian focused SPECIFICALLY on reconnaissance: spotting and counting enemy vehicles, equipment, and troops. 
Labels to use ONLY: CALLSIGN, EQUIPMENT-ENEMY, PERSONNEL-ENEMY, LOCATION, QUANTITY.

IMPORTANT RULES FOR LABELS:
- Focus on describing enemy forces, but keep it natural. DO NOT overuse words like "вражеский".
- `QUANTITY`: Use ONLY for counting equipment or personnel. DO NOT use for time or distance.
- BOUNDARY RULE: Extract ONLY the core noun or specific military term (e.g., "БМП", "пехота"). DO NOT include pronouns or descriptive adjectives in the 'word' field (e.g., extract "коробочки", NOT "вражеские коробочки").

Example:
[
  {
    "text": "Ворон, ответь базе. По дороге на юг прошли четыре коробочки, похожи на БМП. Их пехота зашла в лесопосадку за высотой 200.",
    "entities": [
      {"word": "Ворон", "label": "CALLSIGN"},
      {"word": "базе", "label": "CALLSIGN"},
      {"word": "четыре", "label": "QUANTITY"},
      {"word": "коробочки", "label": "EQUIPMENT-ENEMY"},
      {"word": "БМП", "label": "EQUIPMENT-ENEMY"},
      {"word": "пехота", "label": "PERSONNEL-ENEMY"},
      {"word": "лесопосадку", "label": "LOCATION"},
      {"word": "высотой 200", "label": "LOCATION"}
    ]
  }
]
"""

# ==========================================
# ЛОГІСТИКА ТА МЕДИЦИНА (Фокус на своїх - FRIENDLY)
# Використовувати для ~20% датасету
# ==========================================
PROMPT_NER_FRIENDLY_OPS_CLEAN = """
Generate {batch_size} short military radio conversations in Russian focused SPECIFICALLY on friendly operations: requesting medevac, reporting friendly casualties, ammo resupply, or allied troop movements.
Labels to use ONLY: CALLSIGN, EQUIPMENT-FRIENDLY, PERSONNEL-FRIENDLY, LOCATION, QUANTITY.

IMPORTANT RULES FOR LABELS:
- Focus on friendly terminology, but keep it natural. DO NOT overuse "наш".
- `QUANTITY`: Use ONLY for counting equipment or personnel. DO NOT use for time or distance.
- BOUNDARY RULE: Extract ONLY the core noun or specific military term (e.g., "пулемет", "броня", "трехсотый"). DO NOT include pronouns or descriptive adjectives in the 'word' field (e.g., extract "пулемету", NOT "нашему пулемету"). DO NOT extract generic pronouns like "мы" or "у нас" as personnel.

Example:
[
  {
    "text": "Гранит, я Альфа. У нас один тяжелый трехсотый, нужна срочная эвакуация. Заканчивается БК к пулемету. Ждем броню на точке сбора.",
    "entities": [
      {"word": "Гранит", "label": "CALLSIGN"},
      {"word": "Альфа", "label": "CALLSIGN"},
      {"word": "один", "label": "QUANTITY"},
      {"word": "трехсотый", "label": "PERSONNEL-FRIENDLY"},
      {"word": "пулемету", "label": "EQUIPMENT-FRIENDLY"},
      {"word": "броню", "label": "EQUIPMENT-FRIENDLY"},
      {"word": "точке сбора", "label": "LOCATION"}
    ]
  }
]
"""

# ==========================================
# ФОНОВИЙ ШУМ (Без техніки та піхоти)
# Використовувати для ~10% датасету
# ==========================================
PROMPT_NER_NOISE_CLEAN = """
Generate {batch_size} short military radio conversations in Russian representing BACKGROUND CHATTER. Topics should be mundane: checking radio signal, complaining about weather/mud, food, or asking for someone to come to a specific location. 
CRITICAL RULE: DO NOT include any mentions of weapons, vehicles, enemy troops, or casualties. 
Labels to use ONLY: CALLSIGN, LOCATION. Do not use any other labels.

Example:
[
  {
    "text": "Сокол, я Дерево. Как слышишь меня? Прием. Дождь заливает окопы, связи почти нет.",
    "entities": [
      {"word": "Сокол", "label": "CALLSIGN"},
      {"word": "Дерево", "label": "CALLSIGN"},
      {"word": "окопы", "label": "LOCATION"}
    ]
  },
  {
    "text": "Дерево, слышу тебя на троечку. Захватите сигарет, когда будете идти на базу.",
    "entities": [
      {"word": "Дерево", "label": "CALLSIGN"},
      {"word": "базу", "label": "LOCATION"}
    ]
  }
]
"""