from importlib.resources import files

from ai_language_teacher.language.loader import load_lesson

DATA_FILE = files("ai_language_teacher") / "data" / "japanese" / "katakana_vowels.json"

KATAKANA_VOWELS_LESSON = load_lesson(DATA_FILE)
KATAKANA = KATAKANA_VOWELS_LESSON.items
