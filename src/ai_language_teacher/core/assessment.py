from dataclasses import dataclass

from ai_language_teacher.core.question import Question

LEADING_WORDS = ("to ", "a ", "an ", "the ")


def normalize(answer: str) -> str:
    answer = " ".join(answer.lower().split())
    for word in LEADING_WORDS:
        if answer.startswith(word):
            return answer.removeprefix(word)
    return answer


@dataclass
class AssessmentResult:
    skill: str
    correct: bool
    score: float
    item: str | None = None


@dataclass
class Assessment:
    skill: str
    expected_answer: str | list[str]
    item: str | None = None

    @classmethod
    def from_question(cls, skill: str, question: Question) -> "Assessment":
        return cls(skill, question.expected_answer, question.item)

    def evaluate(self, student_answer: str) -> AssessmentResult:
        accepted = self.expected_answer
        if isinstance(accepted, str):
            accepted = [accepted]

        normalized_answer = normalize(student_answer)
        correct = any(normalized_answer == normalize(a) for a in accepted)

        if correct:
            score = 1.0
        else:
            score = 0.0

        return AssessmentResult(
            self.skill,
            correct,
            score,
            self.item,
        )
