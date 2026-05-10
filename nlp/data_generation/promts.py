# ==========================================
# ЗАГАЛЬНИЙ БІЙ (Мікс своїх та чужих)
# Використовувати для ~50% датасету
# ==========================================
PROMPT_NER_MAIN = """
Generate {batch_size} unique, realistic, and short military radio conversations in Russian between two soldiers. Use diverse scenarios: combat engagements, spotting enemy movements, or coordination. The output should be a JSON list of objects, where each object has:
- `text`: A string (2-4 sentences) representing a conversation snippet.
- `entities`: A list of dictionaries with `word` and `label`. Labels MUST BE chosen from this list ONLY: CALLSIGN, EQUIPMENT-ENEMY, EQUIPMENT-FRIENDLY, LOCATION, QUANTITY, PERSONNEL-ENEMY, PERSONNEL-FRIENDLY.

STT FORMATTING RULES:
- The generated text MUST simulate raw Speech-to-Text (STT) output. 
- Remove most punctuation (commas, periods, question marks). Keep it as a continuous stream of words. Use lowercase mostly.
- Insert realistic hesitations ("ээ", "ну", "короче"), stuttering ("б-база"), and Russian profanity naturally.
- Spell out numbers as words (e.g., "двадцать второй" instead of "22").
- Mix Russian with Surzhyk (e.g., "шо", "поняв", "тю").

PERSPECTIVE & VOCABULARY RULES:
- The speaker is a Russian soldier. 
- `EQUIPMENT-FRIENDLY` / `PERSONNEL-FRIENDLY`: Russian/Allied forces (e.g., "наши", "мобики", "коробочка", "мотолыга", "арта", "двухсотый", "трехсотый").
- `EQUIPMENT-ENEMY` / `PERSONNEL-ENEMY`: Ukrainian forces (e.g., "хохлы", "укропы", "зсу", "птичка", "брэдли").
- `QUANTITY`: Use ONLY for counting equipment or personnel (e.g., "два", "взвод"). Ignore time and distance.
- BOUNDARY RULE: Extract ONLY the core noun. DO NOT extract generic pronouns like "мы" or "у нас" as personnel.

Example:
[
  {
    "text": "береза я сокол два блядь ну коробочка повреждена ээ наблюдаю движение противника короче три пикапа и до взвода их пехоты заходят в сорок пятый квадрат запрашиваю арту давай бегом",
    "entities": [
      {"word": "береза", "label": "CALLSIGN"},
      {"word": "сокол два", "label": "CALLSIGN"},
      {"word": "коробочка", "label": "EQUIPMENT-FRIENDLY"},
      {"word": "противника", "label": "PERSONNEL-ENEMY"},
      {"word": "три", "label": "QUANTITY"},
      {"word": "пикапа", "label": "EQUIPMENT-ENEMY"},
      {"word": "взвода", "label": "QUANTITY"},
      {"word": "пехоты", "label": "PERSONNEL-ENEMY"},
      {"word": "сорок пятый квадрат", "label": "LOCATION"}
    ]
  }
]
"""

# ==========================================
# РОЗВІДКА (Фокус на ворогах - ENEMY)
# Використовувати для ~20% датасету
# ==========================================
PROMPT_NER_RECON = """
Generate {batch_size} short military radio conversations in Russian focused SPECIFICALLY on reconnaissance: spotting and counting enemy vehicles, equipment, and troops. 
Labels to use ONLY: CALLSIGN, EQUIPMENT-ENEMY, PERSONNEL-ENEMY, LOCATION, QUANTITY.

STT FORMATTING RULES:
- Simulate raw Speech-to-Text (STT) output. Remove punctuation. 
- Insert hesitations ("ээ", "типа"), filler words, and Russian profanity.
- Spell out numbers as words.

PERSPECTIVE & VOCABULARY RULES:
- The speaker is a Russian soldier observing Ukrainian forces.
- Use slang for enemy forces: "птичка" (drone), "укропы", "хохлы", "бэха", "пикапы".
- `QUANTITY`: Use ONLY for counting equipment or personnel.
- BOUNDARY RULE: Extract ONLY the core noun. DO NOT include adjectives like "вражеские" in the 'word' field.

Example:
[
  {
    "text": "ворон ответь базе шо там по дороге на юг прошли блядь четыре коробочки похожи на бмп их пехота зашла в зеленку за высотой двести",
    "entities": [
      {"word": "ворон", "label": "CALLSIGN"},
      {"word": "базе", "label": "CALLSIGN"},
      {"word": "четыре", "label": "QUANTITY"},
      {"word": "коробочки", "label": "EQUIPMENT-ENEMY"},
      {"word": "бмп", "label": "EQUIPMENT-ENEMY"},
      {"word": "пехота", "label": "PERSONNEL-ENEMY"},
      {"word": "зеленку", "label": "LOCATION"},
      {"word": "высотой двести", "label": "LOCATION"}
    ]
  }
]
"""

# ==========================================
# ЛОГІСТИКА ТА МЕДИЦИНА (Фокус на своїх - FRIENDLY)
# Використовувати для ~20% датасету
# ==========================================
PROMPT_NER_FRIENDLY_OPS = """
Generate {batch_size} short military radio conversations in Russian focused SPECIFICALLY on friendly operations: requesting medevac, reporting casualties, ammo resupply, or allied troop movements.
Labels to use ONLY: CALLSIGN, EQUIPMENT-FRIENDLY, PERSONNEL-FRIENDLY, LOCATION, QUANTITY.

STT FORMATTING RULES:
- Simulate raw Speech-to-Text (STT) output without punctuation.
- Include background panic, stuttering, and heavy Russian profanity.
- Spell out numbers as words.

PERSPECTIVE & VOCABULARY RULES:
- The speaker is a Russian soldier talking about their own forces.
- Use slang for casualties and equipment: "двухсотый", "трехсотый", "бк", "броня", "мотолыга", "медики".
- `QUANTITY`: Use ONLY for counting equipment or casualties.
- BOUNDARY RULE: Extract ONLY the core noun (e.g., "броню", "трехсотый").

Example:
[
  {
    "text": "гранит я альфа пиздец у нас один тяжелый трехсотый ээ нужна срочная эвакуация блядь заканчивается бк к пулемету ждем броню на точке сбора быстрее",
    "entities": [
      {"word": "гранит", "label": "CALLSIGN"},
      {"word": "альфа", "label": "CALLSIGN"},
      {"word": "один", "label": "QUANTITY"},
      {"word": "трехсотый", "label": "PERSONNEL-FRIENDLY"},
      {"word": "бк", "label": "EQUIPMENT-FRIENDLY"},
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
PROMPT_NER_NOISE = """
Generate {batch_size} short military radio conversations in Russian representing BACKGROUND CHATTER. Topics: checking radio signal, complaining about weather/mud, food, or general fatigue.
CRITICAL RULE: DO NOT include ANY mentions of weapons, vehicles, enemy troops, friendly troops, or casualties. 
Labels to use ONLY: CALLSIGN, LOCATION.

STT FORMATTING RULES:
- Simulate raw Speech-to-Text (STT) output. No punctuation.
- Include Surzhyk, sighing sounds ("уф", "ага"), and everyday profanity.

Example:
[
  {
    "text": "сокол я дерево ээ как слышишь меня прием блядь дождь заливает окопы связи нихуя почти нет",
    "entities": [
      {"word": "сокол", "label": "CALLSIGN"},
      {"word": "дерево", "label": "CALLSIGN"},
      {"word": "окопы", "label": "LOCATION"}
    ]
  },
  {
    "text": "дерево слышу тебя на троечку короче захватите сигарет когда будете идти на базу шото вообще курить нечего",
    "entities": [
      {"word": "дерево", "label": "CALLSIGN"},
      {"word": "базу", "label": "LOCATION"}
    ]
  }
]
"""