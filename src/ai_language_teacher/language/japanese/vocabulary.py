from importlib.resources import files

from ai_language_teacher.language.loader import load_lesson

THEMES = [
    "greetings", "people", "questions", "food", "places",
    "things", "time", "verbs_1", "verbs_2", "adjectives",
]

DATA_DIR = files("ai_language_teacher") / "data" / "japanese"

VOCABULARY_LESSONS = [load_lesson(DATA_DIR / f"vocabulary_{theme}.json") for theme in THEMES]
VOCABULARY = {
    item: answer for lesson in VOCABULARY_LESSONS for item, answer in lesson.items.items()
}
