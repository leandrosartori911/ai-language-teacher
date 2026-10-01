import pytest

from ai_language_teacher.core.assessment import Assessment
from ai_language_teacher.core.question import Question


def test_from_question_copies_expected_answer_and_item():
    question = Question(
        prompt="What is the romaji for あ?",
        expected_answer="a",
        item="あ",
    )

    assessment = Assessment.from_question("hiragana", question)

    assert assessment.skill == "hiragana"
    assert assessment.expected_answer == "a"
    assert assessment.item == "あ"


def test_from_question_evaluates_like_a_manually_built_assessment():
    question = Question(
        prompt="What is the romaji for あ?",
        expected_answer="a",
        item="あ",
    )

    manual = Assessment("hiragana", question.expected_answer, question.item)
    from_question = Assessment.from_question("hiragana", question)

    manual_result = manual.evaluate("a")
    from_question_result = from_question.evaluate("a")

    assert from_question_result.skill == manual_result.skill
    assert from_question_result.correct == manual_result.correct
    assert from_question_result.score == manual_result.score
    assert from_question_result.item == manual_result.item


def test_answer_is_case_insensitive():
    assessment = Assessment("hiragana", "a")

    assert assessment.evaluate("A").correct is True


def test_answer_ignores_surrounding_whitespace():
    assessment = Assessment("hiragana", "a")

    assert assessment.evaluate(" a ").correct is True


def test_wrong_answer_is_still_wrong():
    assessment = Assessment("hiragana", "a")

    assert assessment.evaluate("i").correct is False


def test_multiple_accepted_answers():
    assessment = Assessment("hiragana", ["shi", "si"])

    assert assessment.evaluate("si").correct is True


def test_multiple_accepted_answers_case_insensitive():
    assessment = Assessment("hiragana", ["shi", "si"])

    assert assessment.evaluate("SHI").correct is True


def test_multiple_accepted_answers_rejects_other_spellings():
    assessment = Assessment("hiragana", ["shi", "si"])

    assert assessment.evaluate("shu").correct is False


@pytest.mark.parametrize("answer", ["The moon", "a moon", "an moon", "  moon  "])
def test_answer_ignores_leading_article(answer):
    assert Assessment("kanji", "moon").evaluate(answer).correct


def test_answer_ignores_leading_to_on_both_sides():
    assert Assessment("vocabulary", "to eat").evaluate("eat").correct
    assert Assessment("vocabulary", "eat").evaluate("to eat").correct


def test_answer_collapses_repeated_spaces():
    assert Assessment("katakana", "long vowel").evaluate("long   vowel").correct


def test_words_starting_with_article_letters_are_kept():
    assert not Assessment("hiragana", "to").evaluate("o").correct
    assert not Assessment("kanji", "another").evaluate("other").correct
