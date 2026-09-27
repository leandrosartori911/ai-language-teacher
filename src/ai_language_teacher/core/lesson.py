from dataclasses import dataclass, field

from ai_language_teacher.core.question import Question


@dataclass
class Lesson:
    title: str
    items: dict[str, str]
    questions: list[Question] = field(default_factory=list)
