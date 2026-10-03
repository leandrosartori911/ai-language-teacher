import pytest

from ai_language_teacher.core.assessment import AssessmentResult
from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.progression import (
    UNLOCK_THRESHOLD,
    lesson_mastery,
    unlocked_lessons,
)
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.hiragana import HIRAGANA_LESSONS

LESSON_1 = Lesson("One", {"a1": "x", "a2": "x", "a3": "x", "a4": "x", "a5": "x"})
LESSON_2 = Lesson("Two", {"b1": "x", "b2": "x", "b3": "x", "b4": "x", "b5": "x"})
LESSON_3 = Lesson("Three", {"c1": "x", "c2": "x"})
LESSON_4 = Lesson("Four", {"d1": "x", "d2": "x"})
COURSE = [LESSON_1, LESSON_2, LESSON_3, LESSON_4]


def answer(student, skill, item, correct):
    student.apply_assessment(AssessmentResult(skill, correct, 1.0 if correct else 0.0, item))


def answer_all(student, skill, lesson, correct=True):
    for item in lesson.items:
        answer(student, skill, item, correct)


def test_threshold_is_point_eight():
    assert UNLOCK_THRESHOLD == 0.8


def test_mastery_is_zero_for_new_student_and_one_when_all_correct():
    student = Student("Test")

    assert lesson_mastery(student, "hiragana", LESSON_1) == 0.0

    answer_all(student, "hiragana", LESSON_1)

    assert lesson_mastery(student, "hiragana", LESSON_1) == 1.0


def test_unanswered_items_count_as_zero():
    student = Student("Test")
    for item in ["a1", "a2", "a3", "a4"]:
        answer(student, "hiragana", item, True)

    assert lesson_mastery(student, "hiragana", LESSON_1) == pytest.approx(0.8)


def test_mastery_only_reads_the_given_skill():
    student = Student("Test")
    answer_all(student, "katakana", LESSON_1)

    assert lesson_mastery(student, "hiragana", LESSON_1) == 0.0


def test_mastery_of_empty_lesson_raises():
    with pytest.raises(ValueError):
        lesson_mastery(Student("Test"), "hiragana", Lesson("Empty", {}))


def test_mastery_of_unknown_skill_raises_value_error():
    with pytest.raises(ValueError):
        lesson_mastery(Student("Test"), "klingon", LESSON_1)


def test_new_student_has_only_first_lesson_unlocked():
    assert unlocked_lessons(Student("Test"), "hiragana", COURSE) == [LESSON_1]


def test_exactly_threshold_unlocks_next_lesson():
    student = Student("Test")
    for item in ["a1", "a2", "a3", "a4"]:
        answer(student, "hiragana", item, True)
    answer(student, "hiragana", "a5", False)

    assert unlocked_lessons(student, "hiragana", COURSE) == [LESSON_1, LESSON_2]


def test_below_threshold_keeps_next_lesson_locked():
    student = Student("Test")
    for item in ["a1", "a2", "a3"]:
        answer(student, "hiragana", item, True)
    for item in ["a4", "a5"]:
        answer(student, "hiragana", item, False)

    assert unlocked_lessons(student, "hiragana", COURSE) == [LESSON_1]


def test_cannot_skip_ahead_past_a_locked_lesson():
    student = Student("Test")
    answer_all(student, "hiragana", LESSON_1)
    answer_all(student, "hiragana", LESSON_2)
    answer(student, "hiragana", "c1", True)
    answer(student, "hiragana", "c2", False)
    answer_all(student, "hiragana", LESSON_4)

    assert unlocked_lessons(student, "hiragana", COURSE) == [LESSON_1, LESSON_2, LESSON_3]


def test_unlocked_lesson_stays_unlocked_after_mastery_drops():
    student = Student("Test")
    answer_all(student, "hiragana", LESSON_1)
    assert unlocked_lessons(student, "hiragana", COURSE) == [LESSON_1, LESSON_2]

    answer(student, "hiragana", "a1", False)
    answer(student, "hiragana", "a2", False)

    assert unlocked_lessons(student, "hiragana", COURSE) == [LESSON_1, LESSON_2]


def test_unlocks_are_kept_per_skill_and_per_student():
    student, other = Student("Test"), Student("Other")
    answer_all(student, "hiragana", LESSON_1)
    unlocked_lessons(student, "hiragana", COURSE)
    answer_all(student, "hiragana", LESSON_1, correct=False)

    assert unlocked_lessons(student, "katakana", COURSE) == [LESSON_1]
    assert unlocked_lessons(other, "hiragana", COURSE) == [LESSON_1]
    assert student.unlocked_count["hiragana"] == 2


def test_mastering_hiragana_vowels_unlocks_the_k_row():
    student = Student("Test")
    vowels, k_row = HIRAGANA_LESSONS[0], HIRAGANA_LESSONS[1]

    assert unlocked_lessons(student, "hiragana", HIRAGANA_LESSONS) == [vowels]

    answer_all(student, "hiragana", vowels)

    assert unlocked_lessons(student, "hiragana", HIRAGANA_LESSONS) == [vowels, k_row]


def test_unlocked_lessons_of_unknown_skill_raises_value_error():
    with pytest.raises(ValueError):
        unlocked_lessons(Student("Test"), "klingon", COURSE)
