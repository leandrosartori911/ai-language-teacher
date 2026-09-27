from dataclasses import dataclass, field


@dataclass
class Knowledge:
    items: dict[str, float] = field(default_factory=dict)

    def update(self, item: str, score: float) -> None:
        self.items[item] = score

    def get_score(self, item: str) -> float:
        return self.items.get(item, 0.0)
