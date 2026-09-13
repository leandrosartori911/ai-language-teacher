from app.core.knowledge import Knowledge


class Student:
    def __init__(self, name):
        self.name = name
        self.level = "beginner"

        self.skills = {
            "hiragana": 0.0,
            "katakana": 0.0,
            "kanji": 0.0,
            "vocabulary": 0.0,
            "grammar": 0.0,
            "listening": 0.0,
            "speaking": 0.0,
        }

        self.knowledge = Knowledge()

    def update_skill(self, skill, score):
        if skill not in self.skills:
            raise ValueError(f"Unknown skill: {skill}")

        self.skills[skill] = score

    def apply_assessment(self, result):
        self.update_skill(result.skill, result.score)

        if result.item is not None:
            self.knowledge.update(result.item, result.score)