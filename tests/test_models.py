from dataclasses import is_dataclass

import pytest

from ai_language_teacher.core.assessment import Assessment, AssessmentResult
from ai_language_teacher.core.knowledge import Knowledge
from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.question import Question
from ai_language_teacher.core.student import Student


@pytest.mark.parametrize(
    "model", [Student, Knowledge, Question, Assessment, AssessmentResult, Lesson]
)
def test_core_models_are_dataclasses(model):
    assert is_dataclass(model)


def test_questions_with_same_data_are_equal():
    assert Question("?", "a", "あ") == Question("?", "a", "あ")


def test_lessons_do_not_share_default_questions_list():
    first = Lesson("First", {"あ": "a"})
    second = Lesson("Second", {"い": "i"})

    first.questions.append(Question("?", "a", "あ"))

    assert second.questions == []


def test_students_do_not_share_skills_or_knowledge():
    first = Student("First")
    second = Student("Second")

    first.update_skill("hiragana", 1.0)
    first.knowledge["hiragana"].update("あ", 1.0)

    assert second.skills["hiragana"] == 0.0
    assert second.knowledge["hiragana"].items == {}
