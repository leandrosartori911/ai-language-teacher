import json
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any

from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.question import Question
from ai_language_teacher.core.teaching import Example, Teaching


def _text(entry: dict[str, Any], key: str, where: str) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{where}: {key!r} is missing or blank")
    return value


def _teaching(entry: dict[str, Any], where: str) -> Teaching:
    example = entry.get("example")
    if not isinstance(example, dict):
        raise ValueError(f"{where}: 'example' is missing")

    culture_note = entry.get("culture_note")
    if culture_note is not None:
        culture_note = _text(entry, "culture_note", where)

    return Teaching(
        explanation=_text(entry, "explanation", where),
        mnemonic=_text(entry, "mnemonic", where),
        example=Example(
            word=_text(example, "word", f"{where} example"),
            reading=_text(example, "reading", f"{where} example"),
            meaning=_text(example, "meaning", f"{where} example"),
        ),
        culture_note=culture_note,
    )


def load_lesson(path: str | Path | Traversable) -> Lesson:
    if isinstance(path, str):
        path = Path(path)

    data = json.loads(path.read_text(encoding="utf-8"))

    if not data["items"]:
        raise ValueError(f"{path}: lesson has no items")

    items: dict[str, str] = {}
    teaching: dict[str, Teaching] = {}

    for entry in data["items"]:
        item = _text(entry, "item", f"{path}")
        where = f"{path}: item {item!r}"

        if item in items:
            raise ValueError(f"{where} appears more than once")

        items[item] = _text(entry, "answer", where)
        teaching[item] = _teaching(entry, where)

        if item not in teaching[item].example.word:
            raise ValueError(f"{where}: example word does not contain the item")

    questions = [
        Question(f"What is the romaji for {item}?", answer, item)
        for item, answer in items.items()
    ]

    return Lesson(data["title"], items, questions, teaching)
