from importlib.resources import files

from ai_language_teacher.language.loader import load_lesson

LESSONS = [
    "vowels", "k", "s", "t", "n", "h", "m", "y", "r", "w", "long_vowel", "g", "z", "d", "b", "p",
    "combinations", "voiced_combinations", "small_tsu",
]

DATA_DIR = files("ai_language_teacher") / "data" / "japanese"
DATA_FILE = DATA_DIR / "katakana_vowels.json"

KATAKANA_LESSONS = [load_lesson(DATA_DIR / f"katakana_{name}.json") for name in LESSONS]
KATAKANA_VOWELS_LESSON = KATAKANA_LESSONS[0]
KATAKANA = {item: answer for lesson in KATAKANA_LESSONS for item, answer in lesson.items.items()}
