from importlib.resources import files

from ai_language_teacher.language.loader import load_lesson

THEMES = ["numbers", "big_numbers", "days", "people", "position", "time"]

DATA_DIR = files("ai_language_teacher") / "data" / "japanese"

KANJI_LESSONS = [load_lesson(DATA_DIR / f"kanji_{theme}.json") for theme in THEMES]
KANJI = {item: answer for lesson in KANJI_LESSONS for item, answer in lesson.items.items()}
