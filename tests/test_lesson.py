from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.question import Question


def test_lesson_has_a_title_and_items():
    items = {
        "あ": "a",
        "い": "i",
    }

    lesson = Lesson("Hiragana vowels", items)

    assert lesson.title == "Hiragana vowels"
    assert lesson.items == items

def test_lesson_can_have_questions():
    question = Question(
        prompt="What is the romaji for あ?",
        expected_answer="a",
        item="あ",
    )

    lesson = Lesson(
        "Hiragana vowels",
        {"あ": "a"},
        [question],
    )

    assert lesson.questions == [question]