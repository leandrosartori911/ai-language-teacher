# 006: Typed dataclass core models

## Problem
The core models (`Student`, `Knowledge`, `Question`, `Assessment`,
`AssessmentResult`, `Lesson`) are plain classes with hand-written
`__init__` methods and no type hints. That means:

- Every field is assigned by hand, so there is boilerplate to keep in sync.
- Nothing documents what type a field holds (e.g. `expected_answer` can be
  a `str` or a `list[str]` since spec 003, but only the spec says so).
- Two objects with the same data are not equal (`Question(...) ==
  Question(...)` is `False`) and print as `<... object at 0x...>`, which
  makes test failures and debugging harder.
- No tool checks types, so mistakes like passing a `Question` where a
  `str` is expected are only found at runtime, if at all.

The upcoming work (per-skill knowledge, SQLite persistence, web UI, LLM)
all passes these objects around, so they should have clear, checked types
before that code is written.

## Behavior
- Each core model becomes a `@dataclass` with type hints on every field.
  Constructor arguments, their order and their defaults stay the same, so
  every existing caller keeps working:
  - `Question(prompt: str, expected_answer: str | list[str], item: str)`
  - `AssessmentResult(skill: str, correct: bool, score: float, item: str | None = None)`
  - `Assessment(skill: str, expected_answer: str | list[str], item: str | None = None)`
  - `Lesson(title: str, items: dict[str, str], questions: list[Question] = [])`
    (implemented with `field(default_factory=list)`, so lessons never
    share one list)
  - `Knowledge()` with `items: dict[str, float]` defaulting to a new empty
    dict
  - `Student(name: str)` with `level`, `skills` and `knowledge` defaulting
    to the same values as today (`"beginner"`, all seven skills at `0.0`,
    empty `Knowledge`)
- Methods keep their current behavior and gain type hints
  (`evaluate(self, student_answer: str) -> AssessmentResult`, etc.).
  `load_lesson(path: str | Path) -> Lesson` also gains type hints.
- Because they are dataclasses, models now compare by value and have a
  readable `repr`. This is the only visible behavior change.
- `mypy` is added as a dev dependency and runs in CI next to `ruff` and
  `pytest`. `src/` must pass `mypy` in strict mode (`strict = true` in
  `pyproject.toml`) with no errors.

## Acceptance Criteria
- [x] All 34 existing tests pass without being modified.
- [x] `dataclasses.is_dataclass()` is true for `Student`, `Knowledge`,
      `Question`, `Assessment`, `AssessmentResult` and `Lesson`.
- [x] Two `Question`s built with the same arguments are equal.
- [x] Two `Lesson`s created without `questions` do not share the same
      list (appending to one leaves the other empty).
- [x] Two `Student`s do not share `skills` or `knowledge` (updating one
      leaves the other at its defaults).
- [x] `mypy src` reports no errors, and CI runs it.

## Out of Scope
- Any change to how assessments are scored or how mastery is computed.
- Per-skill `Knowledge` separation (spec 008).
- Moving `data/` into the package (spec 007).
- Freezing models (`frozen=True`) or adding runtime validation of field
  types; `mypy` checks types statically, which is enough for now.
- Type-checking `tests/` with `mypy`.
