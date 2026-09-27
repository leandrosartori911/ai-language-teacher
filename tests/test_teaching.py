import copy
import json

import pytest

from ai_language_teacher.core.teaching import Example, Teaching
from ai_language_teacher.language.japanese.hiragana import HIRAGANA_VOWELS_LESSON
from ai_language_teacher.language.japanese.katakana import KATAKANA_VOWELS_LESSON
from ai_language_teacher.language.loader import load_lesson

VALID_ITEM = {
    "item": "あ",
    "answer": "a",
    "explanation": "Sounds like the 'a' in 'father'.",
    "mnemonic": "A memory hook.",
    "example": {"word": "あめ", "reading": "ame", "meaning": "rain"},
    "culture_note": "A true note.",
}


def write_lesson(tmp_path, items):
    path = tmp_path / "lesson.json"
    path.write_text(json.dumps({"title": "Test", "items": items}), encoding="utf-8")
    return path


def item_with(**changes):
    item = copy.deepcopy(VALID_ITEM)
    for key, value in changes.items():
        if value is None:
            del item[key]
        else:
            item[key] = value
    return item


@pytest.mark.parametrize("lesson", [HIRAGANA_VOWELS_LESSON, KATAKANA_VOWELS_LESSON])
def test_every_vowel_item_has_teaching_content(lesson):
    assert set(lesson.teaching) == set(lesson.items)

    for item, teaching in lesson.teaching.items():
        assert teaching.explanation.strip()
        assert teaching.mnemonic.strip()
        assert item in teaching.example.word


def test_teaching_content_uses_dataclasses():
    teaching = HIRAGANA_VOWELS_LESSON.teaching["あ"]

    assert isinstance(teaching, Teaching)
    assert isinstance(teaching.example, Example)


def test_item_without_culture_note_loads_with_none(tmp_path):
    lesson = load_lesson(write_lesson(tmp_path, [item_with(culture_note=None)]))

    assert lesson.teaching["あ"].culture_note is None


def test_valid_item_loads(tmp_path):
    lesson = load_lesson(write_lesson(tmp_path, [VALID_ITEM]))

    assert lesson.items == {"あ": "a"}
    assert lesson.teaching["あ"].example.meaning == "rain"
    assert lesson.teaching["あ"].culture_note == "A true note."


@pytest.mark.parametrize(
    "items",
    [
        pytest.param([item_with(explanation=None)], id="missing explanation"),
        pytest.param([item_with(mnemonic=None)], id="missing mnemonic"),
        pytest.param([item_with(example=None)], id="missing example"),
        pytest.param([item_with(item=None)], id="missing item"),
        pytest.param([item_with(explanation="  ")], id="blank explanation"),
        pytest.param([item_with(mnemonic="")], id="blank mnemonic"),
        pytest.param(
            [item_with(example={"word": "あめ", "reading": "", "meaning": "rain"})],
            id="blank example reading",
        ),
        pytest.param(
            [item_with(example={"word": "あめ", "reading": "ame"})],
            id="missing example meaning",
        ),
        pytest.param(
            [item_with(example={"word": "いぬ", "reading": "inu", "meaning": "dog"})],
            id="example word without item",
        ),
        pytest.param([VALID_ITEM, VALID_ITEM], id="duplicate item"),
        pytest.param([item_with(culture_note=" ")], id="blank culture note"),
    ],
)
def test_load_lesson_rejects_invalid_teaching_content(tmp_path, items):
    with pytest.raises(ValueError):
        load_lesson(write_lesson(tmp_path, items))
