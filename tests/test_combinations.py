import pytest

from ai_language_teacher.core.assessment import Assessment
from ai_language_teacher.language.japanese.hiragana import HIRAGANA, HIRAGANA_LESSONS
from ai_language_teacher.language.japanese.katakana import KATAKANA, KATAKANA_LESSONS

PLAIN = "きしちにひみり"
VOICED = "ぎじびぴ"
SMALL = "ゃゅょ"

HIRAGANA_COMBINATIONS = [base + small for base in PLAIN for small in SMALL]
HIRAGANA_VOICED_COMBINATIONS = [base + small for base in VOICED for small in SMALL]


def to_katakana(text):
    return "".join(chr(ord(ch) + 0x60) for ch in text)


ALTERNATIVE_SPELLINGS = {
    "しゃ": ["sha", "sya"], "しゅ": ["shu", "syu"], "しょ": ["sho", "syo"],
    "ちゃ": ["cha", "tya"], "ちゅ": ["chu", "tyu"], "ちょ": ["cho", "tyo"],
    "じゃ": ["ja", "zya", "jya"], "じゅ": ["ju", "zyu", "jyu"], "じょ": ["jo", "zyo", "jyo"],
}
SMALL_TSU_ANSWERS = ["double consonant", "doubles the next consonant", "pause"]


def question_for(item):
    lessons = HIRAGANA_LESSONS + KATAKANA_LESSONS
    return next(q for lesson in lessons for q in lesson.questions if q.item == item)


@pytest.mark.parametrize(
    ("lessons", "convert"),
    [(HIRAGANA_LESSONS, str), (KATAKANA_LESSONS, to_katakana)],
    ids=["hiragana", "katakana"],
)
def test_course_ends_with_combinations_then_small_tsu(lessons, convert):
    combinations, voiced, small_tsu = lessons[-3:]

    assert list(combinations.items) == [convert(i) for i in HIRAGANA_COMBINATIONS]
    assert list(voiced.items) == [convert(i) for i in HIRAGANA_VOICED_COMBINATIONS]
    assert list(small_tsu.items) == [convert("っ")]


def test_course_lengths_and_totals():
    assert len(HIRAGANA_LESSONS) == 18
    assert len(KATAKANA_LESSONS) == 19
    assert len(HIRAGANA) == 105
    assert len(KATAKANA) == 106


@pytest.mark.parametrize(
    "lesson", HIRAGANA_LESSONS[-3:] + KATAKANA_LESSONS[-3:], ids=lambda lesson: lesson.title
)
def test_every_new_item_has_teaching_content(lesson):
    assert set(lesson.teaching) == set(lesson.items)

    for item, teaching in lesson.teaching.items():
        assert teaching.explanation.strip()
        assert teaching.mnemonic.strip()
        assert item in teaching.example.word


@pytest.mark.parametrize("item", HIRAGANA_COMBINATIONS + HIRAGANA_VOICED_COMBINATIONS)
def test_katakana_combination_romaji_matches_hiragana(item):
    assert KATAKANA[to_katakana(item)] == HIRAGANA[item]


@pytest.mark.parametrize(
    ("item", "spelling"),
    [
        (script(item), spelling)
        for item, spellings in ALTERNATIVE_SPELLINGS.items()
        for spelling in spellings
        for script in (str, to_katakana)
    ],
)
def test_alternative_spellings_are_accepted(item, spelling):
    result = Assessment.from_question("hiragana", question_for(item)).evaluate(spelling)

    assert result.correct is True


@pytest.mark.parametrize("item", ["っ", "ッ"])
def test_small_tsu_uses_custom_prompt_and_accepts_listed_answers(item):
    question = question_for(item)

    assert question.prompt == f"What does a small {item} do?"
    for answer in SMALL_TSU_ANSWERS:
        assert Assessment.from_question("hiragana", question).evaluate(answer).correct is True
