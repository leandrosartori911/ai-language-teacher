import pytest

from ai_language_teacher.core.assessment import Assessment
from ai_language_teacher.core.knowledge import Knowledge
from ai_language_teacher.core.student import Student


def test_student_creation():
    student = Student("Test Student")

    assert student.name == "Test Student"
    assert student.level == "beginner"


def test_student_skills_start_at_zero():
    student = Student("Test Student")

    for skill in student.skills.values():
        assert skill == 0.0


def test_assessment_correct_answer():
    assessment = Assessment("hiragana", "a")

    result = assessment.evaluate("a")

    assert result.correct is True
    assert result.score == 1.0
    assert result.skill == "hiragana"


def test_assessment_wrong_answer():
    assessment = Assessment("hiragana", "a")

    result = assessment.evaluate("i")

    assert result.correct is False
    assert result.score == 0.0
    assert result.skill == "hiragana"

def test_student_can_update_skill():
    student = Student("Test Student")

    student.update_skill("hiragana", 0.8)

    assert student.skills["hiragana"] == 0.8

def test_student_rejects_unknown_skill():
    student = Student("Test Student")

    with pytest.raises(ValueError):
        student.update_skill("unknown", 0.8)

def test_student_applies_assessment():
    student = Student("Test Student")
    assessment = Assessment("hiragana", "a")

    result = assessment.evaluate("a")
    student.apply_assessment(result)

    assert student.skills["hiragana"] == 1.0

def test_knowledge_starts_empty():
    knowledge = Knowledge()

    assert knowledge.get_score("あ") == 0.0


def test_knowledge_can_update_item():
    knowledge = Knowledge()

    knowledge.update("あ", 0.8)

    assert knowledge.get_score("あ") == 0.8

def test_student_has_knowledge():
    student = Student("Test Student")

    student.knowledge.update("あ", 0.8)

    assert student.knowledge.get_score("あ") == 0.8