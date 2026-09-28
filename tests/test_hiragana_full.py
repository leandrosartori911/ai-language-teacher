import copy
import json

import pytest

from ai_language_teacher.core.assessment import Assessment
from ai_language_teacher.language.japanese.hiragana import HIRAGANA, HIRAGANA_LESSONS
from ai_language_teacher.language.loader import load_lesson

ROW_STARTS = ["あ", "か", "さ", "た", "な", "は", "ま", "や", "ら", "わ"]

BASIC_HIRAGANA = (
    "あいうえお かきくけこ さしすせそ たちつてと なにぬねの "
    "はひふへほ まみむめも やゆよ らりるれろ わをん"
).replace(" ", "")

ALTERNATIVE_SPELLINGS = {
    "し": ["shi", "si"],
    "ち": ["chi", "ti"],
    "つ": ["tsu", "tu"],
    "ふ": ["fu", "hu"],
    "を": ["o", "wo"],
    "ん": ["n", "nn"],
}

VALID_ITEM = {
    "item": "し",
    "answer": "shi",
    "explanation": "Sounds like 'she'.",
    "mnemonic": "A fishing hook.",
    "example": {"word": "しお", "reading": "shio", "meaning": "salt"},
}


def question_for(item):
    for lesson in HIRAGANA_LESSONS:
        for question in lesson.questions:
            if question.item == item:
                return question
    raise AssertionError(f"no question for {item}")


def test_hiragana_is_taught_in_ten_row_lessons():
    assert len(HIRAGANA_LESSONS) == 10
    assert [next(iter(lesson.items)) for lesson in HIRAGANA_LESSONS] == ROW_STARTS


def test_lessons_cover_the_46_basic_hiragana_once():
    all_items = [item for lesson in HIRAGANA_LESSONS for item in lesson.items]

    assert len(all_items) == 46
    assert sorted(all_items) == sorted(BASIC_HIRAGANA)


def test_hiragana_dict_is_the_union_of_all_lessons():
    union = {}
    for lesson in HIRAGANA_LESSONS:
        union.update(lesson.items)

    assert HIRAGANA == union
    assert len(HIRAGANA) == 46


@pytest.mark.parametrize("lesson", HIRAGANA_LESSONS, ids=lambda lesson: lesson.title)
def test_every_hiragana_item_has_teaching_content(lesson):
    assert set(lesson.teaching) == set(lesson.items)

    for item, teaching in lesson.teaching.items():
        assert teaching.explanation.strip()
        assert teaching.mnemonic.strip()
        assert item in teaching.example.word


@pytest.mark.parametrize(
    ("item", "spelling"),
    [
        (item, spelling)
        for item, spellings in ALTERNATIVE_SPELLINGS.items()
        for spelling in spellings
    ],
)
def test_alternative_spellings_are_accepted(item, spelling):
    question = question_for(item)
    result = Assessment.from_question("hiragana", question).evaluate(spelling)

    assert result.correct is True


def test_item_without_alternatives_accepts_only_main_answer():
    question = question_for("か")

    assert question.expected_answer == "ka"


def test_lesson_items_keep_the_main_answer():
    assert HIRAGANA["し"] == "shi"
    assert HIRAGANA["を"] == "o"


@pytest.mark.parametrize("also_accepted", [[""], ["  "], ["shi"]])
def test_load_lesson_rejects_bad_alternative_spelling(tmp_path, also_accepted):
    item = copy.deepcopy(VALID_ITEM)
    item["also_accepted"] = also_accepted
    path = tmp_path / "lesson.json"
    path.write_text(json.dumps({"title": "Test", "items": [item]}), encoding="utf-8")

    with pytest.raises(ValueError):
        load_lesson(path)
