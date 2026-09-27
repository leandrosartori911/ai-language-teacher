from dataclasses import dataclass, field

from ai_language_teacher.core.question import Question
from ai_language_teacher.core.teaching import Teaching


@dataclass
class Lesson:
    title: str
    items: dict[str, str]
    questions: list[Question] = field(default_factory=list)
    teaching: dict[str, Teaching] = field(default_factory=dict)
