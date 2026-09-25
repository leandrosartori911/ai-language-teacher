import json

import pytest

from ai_language_teacher.language.japanese.hiragana import HIRAGANA, HIRAGANA_VOWELS_LESSON
from ai_language_teacher.language.loader import load_lesson


def test_load_lesson_matches_hardcoded_hiragana_lesson():
    lesson = load_lesson("data/japanese/hiragana_vowels.json")

    assert lesson.title == HIRAGANA_VOWELS_LESSON.title
    assert lesson.items == HIRAGANA

    question_items = [q.item for q in lesson.questions]
    question_answers = [q.expected_answer for q in lesson.questions]
    question_prompts = [q.prompt for q in lesson.questions]

    expected_items = [q.item for q in HIRAGANA_VOWELS_LESSON.questions]
    expected_answers = [q.expected_answer for q in HIRAGANA_VOWELS_LESSON.questions]
    expected_prompts = [q.prompt for q in HIRAGANA_VOWELS_LESSON.questions]

    assert question_items == expected_items
    assert question_answers == expected_answers
    assert question_prompts == expected_prompts


def test_load_lesson_rejects_empty_items(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text(json.dumps({"title": "Empty", "items": {}}), encoding="utf-8")

    with pytest.raises(ValueError):
        load_lesson(str(path))


def test_load_lesson_rejects_blank_answer(tmp_path):
    path = tmp_path / "blank.json"
    path.write_text(
        json.dumps({"title": "Bad", "items": {"あ": ""}}), encoding="utf-8"
    )

    with pytest.raises(ValueError):
        load_lesson(str(path))
