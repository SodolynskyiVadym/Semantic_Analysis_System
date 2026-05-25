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



# ==========================================
# ДВОЗНАЧНІ СЛОВА (Тест на розуміння контексту)
# Використовувати для ~10-15% датасету
# ==========================================
PROMPT_NER_AMBIGUOUS = """
Generate {batch_size} short military radio conversations in Russian specifically designed to test CONTEXTUAL DISAMBIGUATION.
You must use words that have a double meaning: a literal/civilian meaning and a military slang meaning. 
Mix scenarios where these words are used in their MILITARY slang sense (must be labeled) and their LITERAL civilian sense (must NOT be labeled, or labeled differently).

AMBIGUOUS VOCABULARY TO USE:
- "Птичка" (Bird / Enemy Drone) -> Drone is EQUIPMENT-ENEMY. Actual bird is NOT LABELED.
- "Таблетка" (Pill / UAZ-452 ambulance) -> Van is EQUIPMENT-FRIENDLY. Medicine is NOT LABELED.
- "Коробочка" (Small box / Armored vehicle) -> Vehicle is EQUIPMENT. Literal box is NOT LABELED.
- "Зеленка" (Antiseptic dye / Forest area) -> Forest is LOCATION. Medicine is NOT LABELED.
- "Огурцы" (Cucumbers / Artillery shells) -> Shells are EQUIPMENT-FRIENDLY. Food is NOT LABELED.
- "Карандаши" (Pencils / Rockets or recruits) -> Rockets/recruits are EQUIPMENT/PERSONNEL. Pencils are NOT LABELED.
- "Улитка" (Snail / Drum magazine for RPK) -> Magazine is EQUIPMENT-FRIENDLY. Insect is NOT LABELED.

STT FORMATTING RULES:
- Simulate raw Speech-to-Text (STT) output. No punctuation.
- Include hesitations ("ээ", "ну"), filler words, and Russian profanity naturally.

PERSPECTIVE & LABELING RULES:
- The speaker is a Russian soldier. 
- CRITICAL: Only label the MILITARY slang meaning. If the word is used in its literal civilian sense (e.g., eating cucumbers, treating a wound with zelenka, taking a pill), DO NOT include it in the entities list.

Example:
[
  {
    "text": "береза я сокол ээ тут птичка поет прям над блиндажом а погоди блядь это не птичка это дрон хохлов в укрытие бегом",
    "entities": [
      {"word": "береза", "label": "CALLSIGN"},
      {"word": "сокол", "label": "CALLSIGN"},
      {"word": "блиндажом", "label": "LOCATION"},
      {"word": "дрон", "label": "EQUIPMENT-ENEMY"},
      {"word": "хохлов", "label": "PERSONNEL-ENEMY"}
    ]
  },
  {
    "text": "рубин ответь тут у малого температура есть таблетки какие-то а то наша таблетка сгорела вчера на перекрестке медиков не на чем везти",
    "entities": [
      {"word": "рубин", "label": "CALLSIGN"},
      {"word": "таблетка", "label": "EQUIPMENT-FRIENDLY"},
      {"word": "перекрестке", "label": "LOCATION"},
      {"word": "медиков", "label": "PERSONNEL-FRIENDLY"}
    ]
  },
  {
    "text": "база я гном мы зашли в зеленку тут тихо ээ скиньте нам огурцов и тушенки а то жрать нечего",
    "entities": [
      {"word": "база", "label": "CALLSIGN"},
      {"word": "гном", "label": "CALLSIGN"},
      {"word": "зеленку", "label": "LOCATION"}
    ]
  },
  {
    "text": "алмаз я кедр дайте координаты ээ нам нужны огурцы срочно по квадрату сорок работайте",
    "entities": [
      {"word": "алмаз", "label": "CALLSIGN"},
      {"word": "кедр", "label": "CALLSIGN"},
      {"word": "огурцы", "label": "EQUIPMENT-FRIENDLY"},
      {"word": "квадрату сорок", "label": "LOCATION"}
    ]
  }
]
"""



PROMT_SPECIAL_DATA = """
You are a Data Scientist specializing in generating high-quality synthetic datasets for training a Named Entity Recognition (NER) model based on XLM-RoBERTa or DeBERTa.

PROJECT CONTEXT:
This model is a core component of a semantic analysis system for intercepted military radio communications. The input text is the raw output from a Speech-to-Text (STT) system (like OpenAI Whisper), which means it contains transcription errors, lacks proper punctuation, and is filled with military slang, surzhyk, and informal language.

OBJECTIVE:
Generate {BATCH_SIZE} unique radio intercept snippets in Russian for targeted Data Augmentation.
The output must be a valid JSON list of objects, where each object contains:
- "text": The raw transcription string.
- "entities": A list of objects with "word" and "label".

TEXT GENERATION RULES (STT REALISM):
1. Simulate raw Whisper output: minimal to no punctuation (avoid periods and commas where possible).
2. Use filler words and hesitations: "ээ", "ну", "короче", "бля", "типа".
3. Naturally include Russian profanity (mat) and surzhyk (e.g., "шо", "поняв").
4. Maintain the chaotic nature of battlefield communication.

LABELING RULES (BIO/ENTITY STANDARDS):
1. Extract only the root noun: Do NOT include pronouns ("наш", "их") or adjectives in the "word" field.
2. Perspective: The speaker is a Russian soldier. 
   - Ukrainian/ZSU forces = ENEMY.
   - Russian/Allied forces = FRIENDLY.
3. Allowed Labels: CALLSIGN, EQUIPMENT-ENEMY, EQUIPMENT-FRIENDLY, PERSONNEL-ENEMY, PERSONNEL-FRIENDLY, LOCATION, QUANTITY.

--------------------------------------------------
🎯 ПОТОЧНЕ ЦІЛЬОВЕ ЗАВДАННЯ (TARGET AUGMENTATION):

Приклад використання:
- Обов'язково використовуй слово "Бурятия" у різних відмінках (из Бурятии, в Бурятию, буряты).
- Суворо розмічай географічну "Бурятию" як LOCATION.
- Якщо використовуєш слово "бурят" як національність солдатів - розмічай як PERSONNEL-FRIENDLY.
- Обов'язково використовуй слово "Хантамансийский" у зв'язці зі словом "округ" і розмічай це цілком як LOCATION. Не розмічай частину "Хан" як CALLSIGN!
--------------------------------------------------

Provide only the clean JSON output, no conversational filler."""


PROMT_MILITARY_POSITIONS = """
You are a Data Scientist specializing in generating high-quality synthetic datasets for training a Named Entity Recognition (NER) model based on XLM-RoBERTa or DeBERTa.

PROJECT CONTEXT:
This model is a core component of a semantic analysis system for intercepted military radio communications. The input text is the raw output from a Speech-to-Text (STT) system (like OpenAI Whisper), which means it contains transcription errors, lacks proper punctuation, and is filled with military slang, surzhyk, and informal language.

OBJECTIVE:
Generate {BATCH_SIZE} unique radio intercept snippets in Russian for targeted Data Augmentation.
The output must be a valid JSON list of objects, where each object contains:
- "text": The raw transcription string.
- "entities": A list of objects with "word" and "label".

TEXT GENERATION RULES (STT REALISM):
1. Simulate raw Whisper output: minimal to no punctuation (avoid periods and commas where possible).
2. Use filler words and hesitations: "ээ", "ну", "короче", "бля", "типа".
3. Naturally include Russian profanity (mat) and surzhyk (e.g., "шо", "поняв").
4. Maintain the chaotic nature of battlefield communication.

LABELING RULES (BIO/ENTITY STANDARDS):
1. Extract only the root noun: Do NOT include pronouns ("наш", "их") or adjectives in the "word" field.
2. Perspective: The speaker is a Russian soldier. 
   - Ukrainian/ZSU forces = ENEMY.
   - Russian/Allied forces = FRIENDLY.
3. Allowed Labels: CALLSIGN, EQUIPMENT-ENEMY, EQUIPMENT-FRIENDLY, PERSONNEL-ENEMY, PERSONNEL-FRIENDLY, LOCATION, QUANTITY.

--------------------------------------------------
🎯 ПОТОЧНЕ ЦІЛЬОВЕ ЗАВДАННЯ (TARGET AUGMENTATION):
- Використовуй у текстах наступні посади та звання: комбат, комбриг, ротный, взводный, замполит, старшина, полкан, кэп, командир батальона, командир роты.
- Дотримуйся пропорції стилів:
  * 20% реплік — офіційний стиль (доповіді, накази, статутне звернення).
  * 80% реплік — розмовний стиль (матірний, неформальний, панічний).
- Суворо розмічай ці посади як PERSONNEL-FRIENDLY або PERSONNEL-ENEMY залежно від контексту.
- КРИТИЧНО: Не розмічай назви посад як CALLSIGN. Посада — це завжди PERSONNEL.
--------------------------------------------------

Provide only the clean JSON output, no conversational filler."""



PROMT_CIVILIANS = """
You are a Data Scientist specializing in generating high-quality synthetic datasets for training a Named Entity Recognition (NER) model based on XLM-RoBERTa or DeBERTa.

PROJECT CONTEXT:
This model is a core component of a semantic analysis system for intercepted military radio communications. The input text is the raw output from a Speech-to-Text (STT) system (like OpenAI Whisper), which means it contains transcription errors, lacks proper punctuation, and is filled with military slang, surzhyk, and informal language.

OBJECTIVE:
Generate {BATCH_SIZE} unique radio intercept snippets in Russian for targeted Data Augmentation.
The output must be a valid JSON list of objects, where each object contains:
- "text": The raw transcription string.
- "entities": A list of objects with "word" and "label".

TEXT GENERATION RULES (STT REALISM):
1. Simulate raw Whisper output: minimal to no punctuation (avoid periods and commas where possible).
2. Use filler words and hesitations: "ээ", "ну", "короче", "бля", "типа".
3. Naturally include Russian profanity (mat) and surzhyk (e.g., "шо", "поняв").
4. Maintain the chaotic nature of battlefield communication.

LABELING RULES (BIO/ENTITY STANDARDS):
1. Extract only the root noun: Do NOT include pronouns ("наш", "их") or adjectives in the "word" field.
2. Perspective: The speaker is a Russian soldier. 
   - Ukrainian/ZSU forces = ENEMY.
   - Russian/Allied forces = FRIENDLY.
3. Allowed Labels: CALLSIGN, EQUIPMENT-ENEMY, EQUIPMENT-FRIENDLY, PERSONNEL-ENEMY, PERSONNEL-FRIENDLY, LOCATION, QUANTITY.
4. ONLY MILITARY ENTITIES: Strictly ignore civilian population and family members in the labeling process.

--------------------------------------------------
🎯 ПОТОЧНЕ ЦІЛЬОВЕ ЗАВДАННЯ (TARGET AUGMENTATION):
- Сфокусуйся на розмовах, де солдати згадують цивільне населення, місцевих жителів або своїх родичів.
- Використовуй слова: жители, местные, гражданские, люди, бабка, дед, отец, сын, брат, жена, семья.
- КРИТИЧНЕ ПРАВИЛО: НІЯК НЕ РОЗМІЧАЙ ці слова! Вони взагалі не повинні потрапляти у список "entities". Модель має навчитися ігнорувати їх, оскільки це не військова жива сила.
- ДЛЯ КОНТРАСТУ: В цих же репліках обов'язково згадуй справжніх військових (наприклад, "пехота", "мобики", "укропы", "штурмовики"), яких ПОТРІБНО розмічати як PERSONNEL-FRIENDLY або PERSONNEL-ENEMY.
- Приклади сценаріїв:
  1. Доповідь про зачистку: солдат доповідає, що в селі залишилися тільки "местные" та "дед" (ігноруємо), а ворожа "пехота" (PERSONNEL-ENEMY) відійшла.
  2. Особиста розмова: солдат каже, що йому дзвонив "отец" або "жена" (ігноруємо), і скаржиться, що їхнього "комбата" (PERSONNEL-FRIENDLY) поранило.
--------------------------------------------------

Provide only the clean JSON output, no conversational filler."""



PROMT_SWEAR_WORD = """
You are a Data Scientist specializing in generating high-quality synthetic datasets for training a Named Entity Recognition (NER) model based on XLM-RoBERTa or DeBERTa.

PROJECT CONTEXT:
This model is a core component of a semantic analysis system for intercepted military radio communications. The input text is the raw output from a Speech-to-Text (STT) system (like OpenAI Whisper), which means it contains transcription errors, lacks proper punctuation, and is filled with military slang, surzhyk, and informal language.

OBJECTIVE:
Generate {BATCH_SIZE} unique radio intercept snippets in Russian for targeted Data Augmentation.
The output must be a valid JSON list of objects, where each object contains:
- "text": The raw transcription string.
- "entities": A list of objects with "word" and "label".

TEXT GENERATION RULES (STT REALISM):
1. Simulate raw Whisper output: minimal to no punctuation (avoid periods and commas where possible).
2. Use filler words and hesitations: "ээ", "ну", "короче", "бля", "типа".
3. Naturally include Russian profanity (mat) and surzhyk (e.g., "шо", "поняв").
4. Maintain the chaotic nature of battlefield communication.

LABELING RULES (BIO/ENTITY STANDARDS):
1. Extract only the root noun: Do NOT include pronouns ("наш", "их") or adjectives in the "word" field.
2. Perspective: The speaker is a Russian soldier. 
   - Ukrainian/ZSU forces = ENEMY.
   - Russian/Allied forces = FRIENDLY.
3. Allowed Labels: CALLSIGN, EQUIPMENT-ENEMY, EQUIPMENT-FRIENDLY, PERSONNEL-ENEMY, PERSONNEL-FRIENDLY, LOCATION, QUANTITY.

--------------------------------------------------
🎯 ПОТОЧНЕ ЦІЛЬОВЕ ЗАВДАННЯ (TARGET AUGMENTATION):
- Сфокусуйся на інтенсивному використанні грубої лайки та образ (мудак, долбоеб, уебок, пидорас, гандон, черт, хуила).
- СУВОРЕ ПРАВИЛО 1 (Positive Sampling): Якщо образа використовується як іменник, що позначає конкретну людину чи групу людей — розмічай це як PERSONNEL. 
  * Якщо солдат сварить свого командира чи товариша по службі (наприклад: "этот мудак проебал рацию", "забрал у долбоеба", "уебки из соседней роты") — розмічай як PERSONNEL-FRIENDLY.
  * Якщо солдат називає так ворога (наприклад: "пидорасы наступают", "ебнули того черта") — розмічай як PERSONNEL-ENEMY.
- СУВОРЕ ПРАВИЛО 2 (Negative Sampling): Якщо мат або образа використовується як абстрактне явище, вигук, або прикметник — НІЯК НЕ РОЗМІЧАЙ ці слова (ігноруй їх).
  * Вигуки: "блядь", "нахуй", "пиздец", "ебать" (ІГНОРУВАТИ).
  * Прикметники до техніки/локацій: "ебаная машина", "мудацкая погода", "хуевая рация" (ІГНОРУВАТИ прикметники, розмічати тільки іменник-сутність).
  * Абстрактні ситуації: "какая-то хуйня", "тут полный пиздец" (ІГНОРУВАТИ).
- Обов'язково створи кілька прикладів із прийменниками "у", "к", "от", "за" перед образою (наприклад: "пошел к мудаку", "спрятался за долбоебом", "взял у пидораса"), щоб модель зрозуміла, що це не локації.
--------------------------------------------------

Provide only the clean JSON output, no conversational filler."""


PROMT_MILITARY_UNITS = """
You are a Data Scientist specializing in generating high-quality synthetic datasets for training a Named Entity Recognition (NER) model based on XLM-RoBERTa or DeBERTa.

PROJECT CONTEXT:
This model is a core component of a semantic analysis system for intercepted military radio communications. The input text is the raw output from a Speech-to-Text (STT) system (like OpenAI Whisper), which means it contains transcription errors, lacks proper punctuation, and is filled with military slang, surzhyk, and informal language.

OBJECTIVE:
Generate {BATCH_SIZE} unique radio intercept snippets in Russian for targeted Data Augmentation.
The output must be a valid JSON list of objects, where each object contains:
- "text": The raw transcription string.
- "entities": A list of objects with "word" and "label".

TEXT GENERATION RULES (STT REALISM):
1. Simulate raw Whisper output: minimal to no punctuation (avoid periods and commas where possible).
2. Use filler words and hesitations: "ээ", "ну", "короче", "бля", "типа".
3. Naturally include Russian profanity (mat) and surzhyk (e.g., "шо", "поняв").
4. Maintain the chaotic nature of battlefield communication.

LABELING RULES (BIO/ENTITY STANDARDS):
1. Extract only the root noun/core phrase: Do NOT include pronouns ("наш", "их"). If a unit has a number (e.g., "36-й полк"), include the number in the entity word.
2. Perspective: The speaker is a Russian soldier. 
   - Ukrainian/ZSU forces = ENEMY.
   - Russian/Allied forces = FRIENDLY.
3. Allowed Labels: CALLSIGN, EQUIPMENT-ENEMY, EQUIPMENT-FRIENDLY, PERSONNEL-ENEMY, PERSONNEL-FRIENDLY, LOCATION, QUANTITY.

--------------------------------------------------
🎯 ПОТОЧНЕ ЦІЛЬОВЕ ЗАВДАННЯ (TARGET AUGMENTATION):
- Сфокусуйся на згадках військових формувань та підрозділів: полк, бригада, батальон, рота, взвод, дивизия, отряд, группировка (обов'язково додавай до них номери, наприклад: "36-й полк", "15-я бригада", "третья рота").
- СУВОРЕ ПРАВИЛО (Військова частина = Люди): Ніколи не розмічай військові підрозділи як LOCATION! Оскільки підрозділ складається з живої сили, завжди розмічай назви підрозділів ("36-й полк", "наша бригада", "батальон") як PERSONNEL-FRIENDLY або PERSONNEL-ENEMY.
- ДЛЯ КОНТРАСТУ (Positive Location): В одному і тому ж реченні використовуй справжні географічні локації (населені пункти, позиції, лісопосадки).
- Приклад логіки: "наших пацанов перевели в 36-й полк [PERSONNEL-FRIENDLY] и кинули под Авдеевку [LOCATION] а там 47-я бригада укропов [PERSONNEL-ENEMY] сидит в посадке [LOCATION]".
- Використовуй різні прийменники перед назвами підрозділів ("в полк", "из бригады", "к батальону"), щоб модель звикла не асоціювати прийменник "в/из" виключно з локаціями.
--------------------------------------------------

Provide only the clean JSON output, no conversational filler."""




PROMT_CONTEXTUAL_PERSONNEL = """
You are a Data Scientist specializing in generating high-quality synthetic datasets for training a Named Entity Recognition (NER) model based on XLM-RoBERTa or DeBERTa.

PROJECT CONTEXT:
This model is a core component of a semantic analysis system for intercepted military radio communications. The input text is the raw output from a Speech-to-Text (STT) system (like OpenAI Whisper), which means it contains transcription errors, lacks proper punctuation, and is filled with military slang, surzhyk, and informal language.

OBJECTIVE:
Generate {BATCH_SIZE} unique radio intercept snippets in Russian for targeted Data Augmentation.
The output must be a valid JSON list of objects, where each object contains:
- "text": The raw transcription string.
- "entities": A list of objects with "word" and "label".

TEXT GENERATION RULES (STT REALISM):
1. Simulate raw Whisper output: minimal to no punctuation (avoid periods and commas where possible).
2. Use filler words and hesitations: "ээ", "ну", "короче", "бля", "типа".
3. Naturally include Russian profanity (mat) and surzhyk (e.g., "шо", "поняв").
4. Maintain the chaotic nature of battlefield communication.

LABELING RULES (BIO/ENTITY STANDARDS):
1. Extract only the root noun: Do NOT include pronouns ("наш", "их", "те") or adjectives in the "word" field.
2. Perspective: The speaker is a Russian soldier. 
   - Ukrainian/ZSU forces = ENEMY.
   - Russian/Allied forces = FRIENDLY.
3. Allowed Labels: CALLSIGN, EQUIPMENT-ENEMY, EQUIPMENT-FRIENDLY, PERSONNEL-ENEMY, PERSONNEL-FRIENDLY, LOCATION, QUANTITY.

--------------------------------------------------
🎯 ПОТОЧНЕ ЦІЛЬОВЕ ЗАВДАННЯ (TARGET AUGMENTATION):
- Сфокусуйся на використанні нейтральних слів, що позначають особовий склад: "мобилизованные", "мобики", "пацаны", "ребята", "люди".
- ЗАВДАННЯ (Боротьба з дисбалансом класів): Модель повинна навчитися розрізняти, про кого йде мова, спираючись на контекст (займенники "их/наши", розташування "в тех окопах/у нас", напрямок стрільби тощо).
- КРИТИЧНЕ ПРАВИЛО СПІВВІДНОШЕННЯ (85/15):
  * У 15% згенерованих реплік ці слова мають належати до українських сил і розмічатися як PERSONNEL-ENEMY. Створюй контекст, де російський солдат говорить про ворога (наприклад: "их пацаны огрызаются", "те мобики пошли на штурм", "положили их ребят").
  * У 85% згенерованих реплік ці слова мають належати до російських сил і розмічатися як PERSONNEL-FRIENDLY (наприклад: "наших пацанов накрыло", "мои мобики отошли").
- СУВОРЕ ПРАВИЛО (Без займенників): Під час розмітки (поля "word") КАТЕГОРИЧНО ЗАБОРОНЕНО включати займенники у сутність! 
  * ПРАВИЛЬНО: text: "их пацаны", entity: "пацаны" (label: PERSONNEL-ENEMY).
  * НЕПРАВИЛЬНО: text: "их пацаны", entity: "их пацаны".
--------------------------------------------------

Provide only the clean JSON output, no conversational filler."""