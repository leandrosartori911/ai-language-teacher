from importlib.resources import files

from ai_language_teacher.language.loader import load_lesson

DATA_FILE = files("ai_language_teacher") / "data" / "japanese" / "hiragana_vowels.json"

HIRAGANA_VOWELS_LESSON = load_lesson(DATA_FILE)
HIRAGANA = HIRAGANA_VOWELS_LESSON.items
