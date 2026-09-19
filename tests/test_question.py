from ai_language_teacher.core.question import Question


def test_question_has_a_prompt_expected_answer_and_item():
    question = Question(
        prompt="What is the romaji for あ?",
        expected_answer="a",
        item="あ",
    )

    assert question.prompt == "What is the romaji for あ?"
    assert question.expected_answer == "a"
    assert question.item == "あ"