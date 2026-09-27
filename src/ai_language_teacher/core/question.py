from dataclasses import dataclass


@dataclass
class Question:
    prompt: str
    expected_answer: str | list[str]
    item: str
