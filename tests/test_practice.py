from datetime import date, timedelta

import pytest

from ai_language_teacher.core.assessment import AssessmentResult
from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.review import Card, learned_items, record_practice
from ai_language_teacher.core.student import Student

TODAY = date(2026, 1, 1)
LESSON = Lesson("One", {"a1": "x", "a2": "x", "a3": "x"})


def result(item, correct, skill="hiragana"):
    return AssessmentResult(skill, correct, 1.0 if correct else 0.0, item)


def test_learned_items_are_the_lesson_items_with_a_card_in_lesson_order():
    student = Student("Ana")
    student.cards["hiragana"]["a3"] = Card(1, TODAY)
    student.cards["hiragana"]["a1"] = Card(2, TODAY)
    student.cards["hiragana"]["other"] = Card(1, TODAY)

    assert learned_items(student, "hiragana", LESSON) == ["a1", "a3"]


def test_learned_items_is_empty_when_nothing_was_studied():
    assert learned_items(Student("Ana"), "hiragana", LESSON) == []


def test_wrong_practice_answer_demotes_the_card_and_counts_for_mastery():
    student = Student("Ana")
    student.knowledge["hiragana"].update("a1", 1.0)
    student.cards["hiragana"]["a1"] = Card(5, TODAY + timedelta(days=16))

    record_practice(student, result("a1", False), TODAY)

    assert student.knowledge["hiragana"].get_score("a1") == 0.0
    assert student.skills["hiragana"] == 0.0
    assert student.cards["hiragana"]["a1"] == Card(1, TODAY)


def test_correct_practice_answer_counts_for_mastery_but_never_moves_the_card():
    student = Student("Ana")
    student.cards["hiragana"]["a1"] = Card(1, TODAY)

    record_practice(student, result("a1", True), TODAY)

    assert student.knowledge["hiragana"].get_score("a1") == 1.0
    assert student.skills["hiragana"] == 1.0
    assert student.cards["hiragana"]["a1"] == Card(1, TODAY)


def test_practising_an_item_without_a_card_raises_and_changes_nothing():
    student = Student("Ana")

    with pytest.raises(ValueError, match="a1"):
        record_practice(student, result("a1", True), TODAY)

    assert student == Student("Ana")


def test_practising_a_result_without_an_item_raises():
    with pytest.raises(ValueError):
        record_practice(Student("Ana"), result(None, True), TODAY)
