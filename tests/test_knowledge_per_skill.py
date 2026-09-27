import pytest

from ai_language_teacher.core.assessment import Assessment, AssessmentResult
from ai_language_teacher.core.student import SKILLS, Student
from ai_language_teacher.language.japanese.hiragana import HIRAGANA_VOWELS_LESSON
from ai_language_teacher.language.japanese.katakana import KATAKANA_VOWELS_LESSON


def test_new_student_has_empty_knowledge_for_each_skill():
    student = Student("Test Student")

    assert set(student.knowledge) == set(SKILLS)
    assert all(knowledge.items == {} for knowledge in student.knowledge.values())


def test_other_skill_items_do_not_change_a_skill_mean():
    student = Student("Test Student")

    for question in HIRAGANA_VOWELS_LESSON.questions:
        assessment = Assessment.from_question("hiragana", question)
        student.apply_assessment(assessment.evaluate(question.expected_answer))

    katakana_question = KATAKANA_VOWELS_LESSON.questions[0]
    assessment = Assessment.from_question("katakana", katakana_question)
    student.apply_assessment(assessment.evaluate("wrong"))

    assert student.skills["hiragana"] == 1.0
    assert student.skills["katakana"] == 0.0


def test_same_item_key_is_tracked_separately_per_skill():
    student = Student("Test Student")

    student.apply_assessment(AssessmentResult("kanji", True, 1.0, "日"))
    student.apply_assessment(AssessmentResult("vocabulary", False, 0.0, "日"))

    assert student.knowledge["kanji"].get_score("日") == 1.0
    assert student.knowledge["vocabulary"].get_score("日") == 0.0
    assert student.skills["kanji"] == 1.0


def test_item_assessment_for_unknown_skill_raises_and_changes_nothing():
    student = Student("Test Student")

    with pytest.raises(ValueError):
        student.apply_assessment(AssessmentResult("unknown", True, 1.0, "あ"))

    assert all(knowledge.items == {} for knowledge in student.knowledge.values())
