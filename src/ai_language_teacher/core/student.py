from dataclasses import dataclass, field

from ai_language_teacher.core.assessment import AssessmentResult
from ai_language_teacher.core.knowledge import Knowledge

SKILLS = (
    "hiragana",
    "katakana",
    "kanji",
    "vocabulary",
    "grammar",
    "listening",
    "speaking",
)


@dataclass
class Student:
    name: str
    level: str = "beginner"
    skills: dict[str, float] = field(default_factory=lambda: dict.fromkeys(SKILLS, 0.0))
    knowledge: dict[str, Knowledge] = field(
        default_factory=lambda: {skill: Knowledge() for skill in SKILLS}
    )

    def update_skill(self, skill: str, score: float) -> None:
        if skill not in self.skills:
            raise ValueError(f"Unknown skill: {skill}")

        self.skills[skill] = score

    def apply_assessment(self, result: AssessmentResult) -> None:
        if result.item is None:
            self.update_skill(result.skill, result.score)
            return

        if result.skill not in self.knowledge:
            raise ValueError(f"Unknown skill: {result.skill}")

        knowledge = self.knowledge[result.skill]
        knowledge.update(result.item, result.score)
        scores = knowledge.items.values()
        self.update_skill(result.skill, sum(scores) / len(scores))
