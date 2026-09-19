class Lesson:
    def __init__(self, title, items, questions=None):
        self.title = title
        self.items = items
        self.questions = questions if questions is not None else []