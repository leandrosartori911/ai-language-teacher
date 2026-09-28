from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.student import Student

UNLOCK_THRESHOLD = 0.8


def lesson_mastery(student: Student, skill: str, lesson: Lesson) -> float:
    if not lesson.items:
        raise ValueError(f"Lesson {lesson.title!r} has no items")

    knowledge = student.knowledge[skill]
    scores = [knowledge.get_score(item) for item in lesson.items]
    return sum(scores) / len(scores)


def unlocked_lessons(student: Student, skill: str, lessons: list[Lesson]) -> list[Lesson]:
    unlocked = lessons[:1]
    for previous, lesson in zip(lessons, lessons[1:], strict=False):
        if lesson_mastery(student, skill, previous) < UNLOCK_THRESHOLD:
            break
        unlocked.append(lesson)
    return unlocked
