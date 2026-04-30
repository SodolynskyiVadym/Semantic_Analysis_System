PROMPT_NER_MAIN = """
Generate {batch_size} unique, realistic, and short military radio conversations in Russian between two soldiers. Use diverse scenarios: spotting enemy movements, reporting coordinates, or coordination. Ensure the entities are accurately labeled according to the provided schema. The output should be a JSON list of objects, where each object has:
- `text`: A string (2-4 sentences) representing a conversation snippet in Russian (including military slang, callsigns, and coordinates).
- `entities`: A list of dictionaries with `word` and `label`. Labels MUST BE chosen from this list ONLY: CALLSIGN, EQUIPMENT, LOCATION, QUANTITY, PERSONNEL.

Example:
[
  {
    "text": "Берёза, я Сокол-2. Наблюдаю движение противника: три пикапа и до взвода пехоты заходят в квадрат 45. Запрашиваю арту.",
    "entities": [
      {"word": "Берёза", "label": "CALLSIGN"},
      {"word": "Сокол-2", "label": "CALLSIGN"},
      {"word": "три", "label": "QUANTITY"},
      {"word": "пикапа", "label": "EQUIPMENT"},
      {"word": "взвода", "label": "QUANTITY"},
      {"word": "пехоты", "label": "PERSONNEL"},
      {"word": "квадрат 45", "label": "LOCATION"}
    ]
  },
  {
    "text": "Сокол-2, принял. Ждите, работает наша птичка. Движение снайперов подтверждаю.",
    "entities": [
      {"word": "Сокол-2", "label": "CALLSIGN"},
      {"word": "птичка", "label": "EQUIPMENT"},
      {"word": "снайперов", "label": "PERSONNEL"}
    ]
  }
]
"""


PROMPT_NER_EQUIPMENT = """
Generate {batch_size} short military radio conversations in Russian focused SPECIFICALLY on spotting and counting enemy vehicles/equipment. The conversations should involve reporting numbers, types of vehicles, and their positions. 
Labels to use: CALLSIGN, EQUIPMENT, LOCATION, QUANTITY.

Example:
[
  {
    "text": "Ворон, ответь базе. По дороге на юг прошли четыре коробочки, похожи на БМП. Зашли в лесопосадку за высотой 200.",
    "entities": [
      {"word": "Ворон", "label": "CALLSIGN"},
      {"word": "базе", "label": "CALLSIGN"},
      {"word": "четыре", "label": "QUANTITY"},
      {"word": "коробочки", "label": "EQUIPMENT"},
      {"word": "БМП", "label": "EQUIPMENT"},
      {"word": "лесопосадку", "label": "LOCATION"},
      {"word": "высотой 200", "label": "LOCATION"}
    ]
  }
]
"""


PROMPT_NER_INFANTRY = """
Generate {batch_size} short military radio conversations in Russian focused SPECIFICALLY on infantry movements, firefights, or casualties. The conversations should involve reporting enemy troops, snipers, or requesting medevac for wounded personnel.
Labels to use: CALLSIGN, PERSONNEL, LOCATION, QUANTITY.

Example:
[
  {
    "text": "Гранит, я Альфа. У нас контакт. Вижу группу пехоты, около десяти человек, лезут через траншею. У нас один трехсотый, нужна эвакуация.",
    "entities": [
      {"word": "Гранит", "label": "CALLSIGN"},
      {"word": "Альфа", "label": "CALLSIGN"},
      {"word": "группу", "label": "QUANTITY"},
      {"word": "пехоты", "label": "PERSONNEL"},
      {"word": "десяти", "label": "QUANTITY"},
      {"word": "человек", "label": "PERSONNEL"},
      {"word": "траншею", "label": "LOCATION"},
      {"word": "один", "label": "QUANTITY"},
      {"word": "трехсотый", "label": "PERSONNEL"}
    ]
  }
]
"""