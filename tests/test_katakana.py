from ai_language_teacher.core.assessment import Assessment
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.katakana import KATAKANA, KATAKANA_VOWELS_LESSON


def test_katakana_contains_basic_vowels():
    assert KATAKANA == {"ア": "a", "イ": "i", "ウ": "u", "エ": "e", "オ": "o"}


def test_katakana_vowels_lesson_uses_katakana_content():
    assert KATAKANA_VOWELS_LESSON.title == "Katakana vowels"
    assert KATAKANA_VOWELS_LESSON.items == KATAKANA


def test_katakana_vowels_lesson_has_a_question_for_each_item():
    question_items = [q.item for q in KATAKANA_VOWELS_LESSON.questions]
    expected_answers = [q.expected_answer for q in KATAKANA_VOWELS_LESSON.questions]

    assert question_items == list(KATAKANA.keys())
    assert expected_answers == list(KATAKANA.values())


def test_correct_katakana_assessment_updates_katakana_skill():
    student = Student("Test Student")
    question = KATAKANA_VOWELS_LESSON.questions[0]

    assessment = Assessment.from_question("katakana", question)
    result = assessment.evaluate(question.expected_answer)
    student.apply_assessment(result)

    assert student.skills["katakana"] == 1.0
