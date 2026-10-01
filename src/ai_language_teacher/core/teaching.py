from dataclasses import dataclass, field


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
    kun_readings: list[str] = field(default_factory=list)
    on_readings: list[str] = field(default_factory=list)
