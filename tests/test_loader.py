import json
from importlib.resources import files
from pathlib import Path

import pytest

import ai_language_teacher
from ai_language_teacher.language.japanese import hiragana, katakana
from ai_language_teacher.language.japanese.hiragana import HIRAGANA, HIRAGANA_VOWELS_LESSON
from ai_language_teacher.language.loader import load_lesson

HIRAGANA_RESOURCE = files("ai_language_teacher") / "data" / "japanese" / "hiragana_vowels.json"


def test_load_lesson_matches_hardcoded_hiragana_lesson():
    lesson = load_lesson(HIRAGANA_RESOURCE)

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


@pytest.mark.parametrize("module", [hiragana, katakana])
def test_lesson_files_are_read_from_inside_the_package(module):
    package_dir = Path(ai_language_teacher.__file__).resolve().parent

    assert Path(str(module.DATA_FILE)).resolve().is_relative_to(package_dir)


def test_load_lesson_accepts_str_path_and_resource():
    path = Path(str(HIRAGANA_RESOURCE))

    for source in (str(path), path, HIRAGANA_RESOURCE):
        assert load_lesson(source).items == HIRAGANA
