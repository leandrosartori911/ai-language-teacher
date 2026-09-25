class AssessmentResult:
    def __init__(self, skill, correct, score, item=None):
        self.skill = skill
        self.correct = correct
        self.score = score
        self.item = item


class Assessment:
    def __init__(self, skill, expected_answer, item=None):
        self.skill = skill
        self.expected_answer = expected_answer
        self.item = item

    @classmethod
    def from_question(cls, skill, question):
        return cls(skill, question.expected_answer, question.item)

    def evaluate(self, student_answer):
        correct = student_answer == self.expected_answer

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