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
