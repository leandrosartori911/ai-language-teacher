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