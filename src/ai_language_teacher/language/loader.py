import json

from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.question import Question


def load_lesson(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    items = data["items"]

    if not items:
        raise ValueError(f"{path}: lesson has no items")

    for item, answer in items.items():
        if not answer:
            raise ValueError(f"{path}: item {item!r} has a blank answer")

    questions = [
        Question(f"What is the romaji for {item}?", answer, item)
        for item, answer in items.items()
    ]

    return Lesson(data["title"], items, questions)
