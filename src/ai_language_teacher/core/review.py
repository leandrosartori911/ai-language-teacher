from dataclasses import dataclass
from datetime import date, timedelta

from ai_language_teacher.core.assessment import AssessmentResult
from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.progression import unlocked_lessons
from ai_language_teacher.core.student import Student

BOX_INTERVALS = (1, 2, 4, 8, 16)


@dataclass
class Card:
    box: int
    due: date


def record_answer(student: Student, result: AssessmentResult, today: date) -> None:
    if result.item is None:
        raise ValueError("Only results with an item can be scheduled")

    student.apply_assessment(result)

    cards = student.cards[result.skill]
    if not result.correct:
        cards[result.item] = Card(1, today)
        return

    previous = cards.get(result.item)
    box = min((previous.box if previous else 0) + 1, len(BOX_INTERVALS))
    cards[result.item] = Card(box, today + timedelta(days=BOX_INTERVALS[box - 1]))


def learned_items(student: Student, skill: str, lesson: Lesson) -> list[str]:
    cards = student.cards[skill]
    return [item for item in lesson.items if item in cards]


def record_practice(student: Student, result: AssessmentResult, today: date) -> None:
    # Free practice: a wrong answer demotes the card, a correct one never
    # moves it, so practice cannot push a review further away.
    if result.item is None:
        raise ValueError("Only results with an item can be practised")
    if result.item not in student.cards[result.skill]:
        raise ValueError(f"{result.item!r} has not been studied yet")

    student.apply_assessment(result)
    if not result.correct:
        student.cards[result.skill][result.item] = Card(1, today)


def due_items(student: Student, skill: str, today: date) -> list[str]:
    due = [(card.due, card.box, item) for item, card in student.cards[skill].items()]
    return [item for due_date, _, item in sorted(due) if due_date <= today]


def study_queue(student: Student, skill: str, lessons: list[Lesson], today: date) -> list[str]:
    cards = student.cards[skill]
    new = [
        item
        for lesson in unlocked_lessons(student, skill, lessons)
        for item in lesson.items
        if item not in cards
    ]
    return due_items(student, skill, today) + new
