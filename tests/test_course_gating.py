import pytest

from ai_language_teacher.core.assessment import AssessmentResult
from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.progression import course_mastered, open_skills
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES, PREREQUISITES

ALL_SKILLS = ["hiragana", "katakana", "kanji", "vocabulary"]


def answer_lesson(student, skill, lesson, correct=True):
    for item in lesson.items:
        student.apply_assessment(AssessmentResult(skill, correct, float(correct), item))


def master(student, skill):
    for lesson in COURSES[skill]:
        answer_lesson(student, skill, lesson)


def is_open(student):
    return open_skills(student, COURSES, PREREQUISITES)


def test_course_not_mastered_for_new_student():
    assert not course_mastered(Student("Test"), "hiragana", COURSES["hiragana"])


def test_course_mastered_once_every_lesson_reaches_threshold():
    student = Student("Test")
    master(student, "hiragana")

    assert course_mastered(student, "hiragana", COURSES["hiragana"])


def test_one_lesson_below_threshold_means_not_mastered():
    student = Student("Test")
    master(student, "hiragana")
    answer_lesson(student, "hiragana", COURSES["hiragana"][-1], correct=False)

    assert not course_mastered(student, "hiragana", COURSES["hiragana"])


def test_empty_course_raises():
    with pytest.raises(ValueError):
        course_mastered(Student("Test"), "hiragana", [])


def test_new_student_has_only_hiragana_open():
    assert is_open(Student("Test")) == ["hiragana"]


def test_mastering_hiragana_opens_katakana_only():
    student = Student("Test")
    master(student, "hiragana")

    assert is_open(student) == ["hiragana", "katakana"]


def test_mastering_katakana_too_opens_kanji_and_vocabulary():
    student = Student("Test")
    master(student, "hiragana")
    master(student, "katakana")

    assert is_open(student) == ALL_SKILLS


def test_cannot_skip_hiragana():
    student = Student("Test")
    master(student, "katakana")

    assert is_open(student) == ["hiragana"]


def test_open_skills_stay_open_after_mastery_drops():
    student = Student("Test")
    master(student, "hiragana")
    master(student, "katakana")
    assert is_open(student) == ALL_SKILLS

    answer_lesson(student, "hiragana", COURSES["hiragana"][0], correct=False)
    answer_lesson(student, "katakana", COURSES["katakana"][0], correct=False)

    assert is_open(student) == ALL_SKILLS
    assert student.opened_skills == set(ALL_SKILLS)


def test_opened_skills_are_per_student():
    student, other = Student("Test"), Student("Other")
    master(student, "hiragana")
    is_open(student)

    assert is_open(other) == ["hiragana"]


def test_open_skills_works_for_any_course_data():
    lesson = Lesson("One", {"x": "x"})
    courses = {"grammar": [lesson], "listening": [lesson]}
    prerequisites = {"grammar": None, "listening": "grammar"}

    assert open_skills(Student("Test"), courses, prerequisites) == ["grammar"]


def test_courses_and_prerequisites_cover_the_same_skills():
    assert list(COURSES) == ALL_SKILLS
    assert set(PREREQUISITES) == set(COURSES)
    assert all(p is None or p in COURSES for p in PREREQUISITES.values())
