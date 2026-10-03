from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.student import Student

UNLOCK_THRESHOLD = 0.8


def lesson_mastery(student: Student, skill: str, lesson: Lesson) -> float:
    if not lesson.items:
        raise ValueError(f"Lesson {lesson.title!r} has no items")

    if skill not in student.knowledge:
        raise ValueError(f"Unknown skill: {skill}")

    knowledge = student.knowledge[skill]
    scores = [knowledge.get_score(item) for item in lesson.items]
    return sum(scores) / len(scores)


def unlocked_lessons(student: Student, skill: str, lessons: list[Lesson]) -> list[Lesson]:
    if skill not in student.unlocked_count:
        raise ValueError(f"Unknown skill: {skill}")

    unlocked = lessons[:1]
    for previous, lesson in zip(lessons, lessons[1:], strict=False):
        if lesson_mastery(student, skill, previous) < UNLOCK_THRESHOLD:
            break
        unlocked.append(lesson)

    # Unlocks are permanent: never return fewer lessons than already unlocked.
    count = max(len(unlocked), student.unlocked_count[skill])
    student.unlocked_count[skill] = count
    return lessons[:count]


def course_mastered(student: Student, skill: str, lessons: list[Lesson]) -> bool:
    if not lessons:
        raise ValueError(f"Course {skill!r} has no lessons")

    return all(lesson_mastery(student, skill, lesson) >= UNLOCK_THRESHOLD for lesson in lessons)


def open_skills(
    student: Student,
    courses: dict[str, list[Lesson]],
    prerequisites: dict[str, str | None],
) -> list[str]:
    # A prerequisite must come before the skills that need it in `courses`.
    opened = student.opened_skills
    for skill in courses:
        prerequisite = prerequisites[skill]
        if (
            skill in opened
            or prerequisite is None
            or (
                prerequisite in opened
                and course_mastered(student, prerequisite, courses[prerequisite])
            )
        ):
            opened.add(skill)
    return [skill for skill in courses if skill in opened]
