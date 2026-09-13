from app.core.assessment import Assessment
from app.core.question import Question
from app.core.student import Student


def test_student_knowledge_is_updated_from_an_assessed_question():
    student = Student("Ana")

    question = Question(
        prompt="What is the romaji for あ?",
        expected_answer="a",
        item="あ",
    )

    assessment = Assessment(
        skill="hiragana",
        expected_answer=question.expected_answer,
        item=question.item,
    )

    result = assessment.evaluate("a")
    student.apply_assessment(result)

    assert student.skills["hiragana"] == 1.0
    assert student.knowledge.get_score("あ") == 1.0