from datetime import date, timedelta

import pytest

from ai_language_teacher.core.assessment import AssessmentResult
from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.review import (
    BOX_INTERVALS,
    Card,
    due_items,
    record_answer,
    study_queue,
)
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.hiragana import HIRAGANA_LESSONS

TODAY = date(2026, 1, 1)

LESSON_1 = Lesson("One", {"a1": "x", "a2": "x"})
LESSON_2 = Lesson("Two", {"b1": "x", "b2": "x"})
LESSON_3 = Lesson("Three", {"c1": "x"})
COURSE = [LESSON_1, LESSON_2, LESSON_3]


def result(item, correct, skill="hiragana"):
    return AssessmentResult(skill, correct, 1.0 if correct else 0.0, item)


def days(n):
    return TODAY + timedelta(days=n)


def test_box_intervals():
    assert BOX_INTERVALS == (1, 2, 4, 8, 16)


def test_new_student_has_no_cards():
    student = Student("Test")

    assert all(cards == {} for cards in student.cards.values())
    assert set(student.cards) == set(student.skills)


def test_first_correct_answer_goes_to_box_1_due_tomorrow():
    student = Student("Test")
    record_answer(student, result("あ", True), TODAY)

    assert student.cards["hiragana"]["あ"] == Card(1, days(1))


def test_each_correct_answer_moves_up_one_box_until_box_5():
    student = Student("Test")
    expected = [Card(1, days(1)), Card(2, days(2)), Card(3, days(4)), Card(4, days(8))]
    expected += [Card(5, days(16)), Card(5, days(16))]

    for card in expected:
        record_answer(student, result("あ", True), TODAY)
        assert student.cards["hiragana"]["あ"] == card


@pytest.mark.parametrize("correct_answers", [0, 1, 3, 5])
def test_wrong_answer_goes_back_to_box_1_due_today(correct_answers):
    student = Student("Test")
    for _ in range(correct_answers):
        record_answer(student, result("あ", True), TODAY)

    record_answer(student, result("あ", False), days(30))

    assert student.cards["hiragana"]["あ"] == Card(1, days(30))


def test_record_answer_updates_knowledge_and_mastery_like_apply_assessment():
    recorded, applied = Student("Recorded"), Student("Applied")
    for res in [result("あ", True), result("い", False), result("う", True)]:
        record_answer(recorded, res, TODAY)
        applied.apply_assessment(res)

    assert recorded.knowledge == applied.knowledge
    assert recorded.skills == applied.skills


def test_record_answer_rejects_result_without_item():
    student = Student("Test")

    with pytest.raises(ValueError):
        record_answer(student, AssessmentResult("hiragana", True, 1.0), TODAY)

    assert student.skills["hiragana"] == 0.0


def test_record_answer_rejects_unknown_skill():
    with pytest.raises(ValueError):
        record_answer(Student("Test"), result("あ", True, skill="klingon"), TODAY)


def test_cards_are_kept_per_skill():
    student = Student("Test")
    record_answer(student, result("a", True, skill="hiragana"), TODAY)
    record_answer(student, result("a", False, skill="katakana"), TODAY)

    assert student.cards["hiragana"]["a"] == Card(1, days(1))
    assert student.cards["katakana"]["a"] == Card(1, TODAY)


def test_students_do_not_share_cards():
    first, second = Student("First"), Student("Second")
    record_answer(first, result("あ", True), TODAY)

    assert second.cards["hiragana"] == {}


def test_due_items_returns_only_due_items():
    student = Student("Test")
    student.cards["hiragana"] = {
        "past": Card(2, days(-1)),
        "today": Card(1, TODAY),
        "future": Card(1, days(1)),
    }

    assert set(due_items(student, "hiragana", TODAY)) == {"past", "today"}


def test_due_items_most_overdue_first_then_lowest_box():
    student = Student("Test")
    student.cards["hiragana"] = {
        "late_box3": Card(3, days(-2)),
        "later_box4": Card(4, days(-5)),
        "late_box1": Card(1, days(-2)),
        "today_box1": Card(1, TODAY),
    }

    assert due_items(student, "hiragana", TODAY) == [
        "later_box4",
        "late_box1",
        "late_box3",
        "today_box1",
    ]


def test_study_queue_for_new_student_is_the_five_vowels():
    queue = study_queue(Student("Test"), "hiragana", HIRAGANA_LESSONS, TODAY)

    assert queue == ["あ", "い", "う", "え", "お"]


def test_study_queue_puts_due_items_before_new_ones_and_skips_not_due():
    student = Student("Test")
    record_answer(student, result("a1", True), TODAY)
    record_answer(student, result("a2", False), TODAY)

    assert study_queue(student, "hiragana", COURSE, TODAY) == ["a2"]
    assert study_queue(student, "hiragana", COURSE, days(1)) == ["a2", "a1"]


def test_study_queue_adds_new_items_from_unlocked_lessons_in_course_order():
    student = Student("Test")
    record_answer(student, result("a1", True), TODAY)
    record_answer(student, result("a2", True), TODAY)

    assert study_queue(student, "hiragana", COURSE, TODAY) == ["b1", "b2"]


def test_study_queue_never_includes_items_from_locked_lessons():
    student = Student("Test")
    record_answer(student, result("a1", True), TODAY)

    queue = study_queue(student, "hiragana", COURSE, days(1))

    assert queue == ["a1", "a2"]
