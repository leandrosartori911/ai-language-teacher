from dataclasses import dataclass


@dataclass
class Example:
    word: str
    reading: str
    meaning: str


@dataclass
class Teaching:
    explanation: str
    mnemonic: str
    example: Example
    culture_note: str | None = None
