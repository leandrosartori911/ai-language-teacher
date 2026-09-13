from app.language.japanese.hiragana import HIRAGANA
from app.language.japanese.hiragana import HIRAGANA_VOWELS_LESSON


def test_hiragana_contains_basic_vowels():
    assert HIRAGANA["あ"] == "a"
    assert HIRAGANA["い"] == "i"
    assert HIRAGANA["う"] == "u"
    assert HIRAGANA["え"] == "e"
    assert HIRAGANA["お"] == "o"

def test_hiragana_vowels_lesson_uses_hiragana_content():
    assert HIRAGANA_VOWELS_LESSON.title == "Hiragana vowels"
    assert HIRAGANA_VOWELS_LESSON.items == HIRAGANA

def test_hiragana_vowels_lesson_has_a_question_for_each_item():
    question_items = [question.item for question in HIRAGANA_VOWELS_LESSON.questions]
    expected_answers = [
        question.expected_answer
        for question in HIRAGANA_VOWELS_LESSON.questions
    ]

    assert question_items == list(HIRAGANA.keys())
    assert expected_answers == list(HIRAGANA.values())