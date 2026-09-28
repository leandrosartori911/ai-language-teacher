import pytest

from ai_language_teacher.core.assessment import Assessment
from ai_language_teacher.language.japanese.hiragana import HIRAGANA, HIRAGANA_LESSONS
from ai_language_teacher.language.japanese.katakana import KATAKANA, KATAKANA_LESSONS

DAKUTEN_HIRAGANA = "がぎぐげご ざじずぜぞ だぢづでど ばびぶべぼ ぱぴぷぺぽ".split()
DAKUTEN_KATAKANA = "ガギグゲゴ ザジズゼゾ ダヂヅデド バビブベボ パピプペポ".split()

ALTERNATIVE_SPELLINGS = {
    "じ": ["ji", "zi"],
    "ぢ": ["ji", "di"],
    "づ": ["zu", "du"],
    "ジ": ["ji", "zi"],
    "ヂ": ["ji", "di"],
    "ヅ": ["zu", "du"],
}


def items_of(lessons):
    return [item for lesson in lessons for item in lesson.items]


def test_hiragana_dakuten_rows_follow_the_basic_rows():
    assert ["".join(lesson.items) for lesson in HIRAGANA_LESSONS[10:15]] == DAKUTEN_HIRAGANA


def test_katakana_dakuten_rows_follow_the_basic_rows():
    assert ["".join(lesson.items) for lesson in KATAKANA_LESSONS[11:16]] == DAKUTEN_KATAKANA


def test_full_courses_have_no_repeated_items():
    assert len(items_of(HIRAGANA_LESSONS)) == len(HIRAGANA)
    assert len(items_of(KATAKANA_LESSONS)) == len(KATAKANA)


@pytest.mark.parametrize(
    "lesson", HIRAGANA_LESSONS[10:15] + KATAKANA_LESSONS[11:16], ids=lambda lesson: lesson.title
)
def test_every_dakuten_item_has_teaching_content(lesson):
    assert set(lesson.teaching) == set(lesson.items)

    for item, teaching in lesson.teaching.items():
        assert teaching.explanation.strip()
        assert teaching.mnemonic.strip()
        assert item in teaching.example.word


@pytest.mark.parametrize("katakana", list("".join(DAKUTEN_KATAKANA)))
def test_dakuten_katakana_romaji_matches_hiragana(katakana):
    assert KATAKANA[katakana] == HIRAGANA[chr(ord(katakana) - 0x60)]


@pytest.mark.parametrize(
    ("item", "spelling"),
    [
        (item, spelling)
        for item, spellings in ALTERNATIVE_SPELLINGS.items()
        for spelling in spellings
    ],
)
def test_alternative_spellings_are_accepted(item, spelling):
    lessons = HIRAGANA_LESSONS + KATAKANA_LESSONS
    question = next(q for lesson in lessons for q in lesson.questions if q.item == item)

    assert Assessment.from_question("hiragana", question).evaluate(spelling).correct is True
