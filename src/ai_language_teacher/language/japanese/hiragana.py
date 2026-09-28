from importlib.resources import files

from ai_language_teacher.language.loader import load_lesson

ROWS = ["vowels", "k", "s", "t", "n", "h", "m", "y", "r", "w"]

DATA_DIR = files("ai_language_teacher") / "data" / "japanese"
DATA_FILE = DATA_DIR / "hiragana_vowels.json"

HIRAGANA_LESSONS = [load_lesson(DATA_DIR / f"hiragana_{row}.json") for row in ROWS]
HIRAGANA_VOWELS_LESSON = HIRAGANA_LESSONS[0]
HIRAGANA = {item: answer for lesson in HIRAGANA_LESSONS for item, answer in lesson.items.items()}
