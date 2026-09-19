class Knowledge:
    def __init__(self):
        self.items = {}

    def update(self, item, score):
        self.items[item] = score

    def get_score(self, item):
        return self.items.get(item, 0.0)