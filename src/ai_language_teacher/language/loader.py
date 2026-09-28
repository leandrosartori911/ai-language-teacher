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
    questions: list[Question] = []

    for entry in data["items"]:
        item = _text(entry, "item", f"{path}")
        where = f"{path}: item {item!r}"

        if item in items:
            raise ValueError(f"{where} appears more than once")

        answer = _text(entry, "answer", where)
        items[item] = answer
        teaching[item] = _teaching(entry, where)

        if item not in teaching[item].example.word:
            raise ValueError(f"{where}: example word does not contain the item")

        also_accepted = entry.get("also_accepted", [])
        if not isinstance(also_accepted, list):
            raise ValueError(f"{where}: 'also_accepted' must be a list")
        for spelling in also_accepted:
            if not isinstance(spelling, str) or not spelling.strip() or spelling == answer:
                raise ValueError(f"{where}: bad 'also_accepted' spelling {spelling!r}")

        expected: str | list[str] = [answer, *also_accepted] if also_accepted else answer
        prompt = f"What is the romaji for {item}?"
        if "prompt" in entry:
            prompt = _text(entry, "prompt", where)
        questions.append(Question(prompt, expected, item))

    return Lesson(data["title"], items, questions, teaching)
