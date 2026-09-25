from ai_language_teacher.core.knowledge import Knowledge


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
        if result.item is None:
            self.update_skill(result.skill, result.score)
            return

        self.knowledge.update(result.item, result.score)
        # ponytail: Knowledge is one flat map for all skills, so this mean
        # mixes items across skills once a second skill (e.g. katakana)
        # starts sharing it. Fine while only hiragana has items; split
        # Knowledge per skill if that changes.
        scores = self.knowledge.items.values()
        self.update_skill(result.skill, sum(scores) / len(scores))