import copy
import json

import pytest

from ai_language_teacher.core.assessment import Assessment
from ai_language_teacher.language.japanese.hiragana import HIRAGANA
from ai_language_teacher.language.japanese.katakana import KATAKANA, KATAKANA_LESSONS
from ai_language_teacher.language.loader import load_lesson

ROW_STARTS = ["ア", "カ", "サ", "タ", "ナ", "ハ", "マ", "ヤ", "ラ", "ワ", "ー"]

BASIC_KATAKANA = (
    "アイウエオ カキクケコ サシスセソ タチツテト ナニヌネノ "
    "ハヒフヘホ マミムメモ ヤユヨ ラリルレロ ワヲン"
).replace(" ", "")

ALTERNATIVE_SPELLINGS = {
    "シ": ["shi", "si"],
    "チ": ["chi", "ti"],
    "ツ": ["tsu", "tu"],
    "フ": ["fu", "hu"],
    "ヲ": ["o", "wo"],
    "ン": ["n", "nn"],
}

DEFAULT_PROMPT = "What is the romaji for {}?"


def all_questions():
    return [question for lesson in KATAKANA_LESSONS for question in lesson.questions]


def question_for(item):
    return next(question for question in all_questions() if question.item == item)


def test_katakana_course_starts_with_ten_rows_plus_long_vowel_mark():
    basic = KATAKANA_LESSONS[:11]

    assert [next(iter(lesson.items)) for lesson in basic] == ROW_STARTS


def test_lessons_cover_46_basic_katakana_and_long_vowel_mark_once():
    all_items = [item for lesson in KATAKANA_LESSONS[:11] for item in lesson.items]

    assert len(all_items) == 47
    assert sorted(all_items) == sorted(BASIC_KATAKANA + "ー")


def test_katakana_dict_is_the_union_of_all_lessons():
    union = {}
    for lesson in KATAKANA_LESSONS:
        union.update(lesson.items)

    assert KATAKANA == union


@pytest.mark.parametrize("lesson", KATAKANA_LESSONS, ids=lambda lesson: lesson.title)
def test_every_katakana_item_has_teaching_content(lesson):
    assert set(lesson.teaching) == set(lesson.items)

    for item, teaching in lesson.teaching.items():
        assert teaching.explanation.strip()
        assert teaching.mnemonic.strip()
        assert item in teaching.example.word


@pytest.mark.parametrize("katakana", list(BASIC_KATAKANA))
def test_katakana_romaji_matches_hiragana(katakana):
    hiragana = chr(ord(katakana) - 0x60)

    assert KATAKANA[katakana] == HIRAGANA[hiragana]


@pytest.mark.parametrize(
    ("item", "spelling"),
    [
        (item, spelling)
        for item, spellings in ALTERNATIVE_SPELLINGS.items()
        for spelling in spellings
    ],
)
def test_alternative_spellings_are_accepted(item, spelling):
    result = Assessment.from_question("katakana", question_for(item)).evaluate(spelling)

    assert result.correct is True


def test_long_vowel_mark_uses_custom_prompt_and_others_keep_default():
    for question in all_questions():
        if question.item == "ー":
            assert question.prompt == "What does ー mean in katakana words?"
        elif question.item != "ッ":  # small tsu prompt is checked in test_combinations.py
            assert question.prompt == DEFAULT_PROMPT.format(question.item)


def test_load_lesson_rejects_blank_prompt(tmp_path):
    item = {
        "item": "ー",
        "answer": "long vowel",
        "prompt": " ",
        "explanation": "Makes the vowel before it long.",
        "mnemonic": "A long line for a long sound.",
        "example": {"word": "コーヒー", "reading": "kōhī", "meaning": "coffee"},
    }
    path = tmp_path / "lesson.json"
    path.write_text(json.dumps({"title": "Test", "items": [copy.deepcopy(item)]}), encoding="utf-8")

    with pytest.raises(ValueError):
        load_lesson(path)
