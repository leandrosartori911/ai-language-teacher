# 019: SQLite persistence for student progress

## Problem
Everything the tutor knows about a student (mastery, per-item knowledge,
review cards, unlocked lessons and skills) lives in memory and is lost
when the program exits. The web UI (spec 020+) needs progress that
survives restarts, kept locally at zero cost.

## Behavior
- New module `ai_language_teacher/storage.py`, standard library
  `sqlite3` only. Several student profiles, told apart by name; no login.
- `DEFAULT_DB_PATH = ~/.ai-language-teacher/data.db`: outside the repo,
  so progress never ends up in git. Importing the module creates nothing.
- `connect(path=DEFAULT_DB_PATH) -> sqlite3.Connection`: creates the
  parent folder and the schema if missing, turns on foreign keys, and
  marks the schema version with `PRAGMA user_version = 1`. Opening a
  database with a newer version raises `ValueError` instead of guessing.
- Schema (four tables; the database enforces the rules):
  - `students(id, name UNIQUE NOT NULL, level)`; a blank name is rejected.
  - `skills(student_id, skill, score, unlocked_count, opened)`: one row
    per skill, holding mastery, how many lessons are unlocked, and whether
    the skill is open. Score between 0 and 1, `unlocked_count` >= 0.
  - `knowledge(student_id, skill, item, score)`: score between 0 and 1.
  - `cards(student_id, skill, item, box, due)`: box between 1 and 5, due
    stored as an ISO date (`2026-10-03`).
  - Child rows reference `students(id)` and are deleted with it; primary
    keys stop duplicates (one card per student, skill and item).
- `save_student(conn, student)`: writes the whole student in one
  transaction, replacing any earlier save under the same name. If any
  row is rejected, nothing is written and the previous save is kept.
- `load_student(conn, name) -> Student | None`: rebuilds the `Student`
  exactly as saved, or `None` if no profile has that name.
- `list_students(conn) -> list[str]`: profile names, sorted.
- All queries with values use parameters (`?`), never string formatting.
  The one exception is `PRAGMA user_version`, which cannot take
  parameters and is set from a constant.
- ADR `docs/adr/0003-sqlite-persistence.md` records SQLite with normal
  tables over a JSON blob per student.

## Acceptance Criteria
- [x] `connect` creates the database file and missing folders; reopening
      an existing database keeps its data; foreign keys are on.
- [x] A new student and a student with progress (mastery, knowledge,
      cards, unlocked lessons, opened skills) load back equal to what was
      saved.
- [x] Saving the same student again updates the stored progress without
      duplicating rows.
- [x] Two students are stored separately; `list_students` returns their
      names sorted; loading an unknown name returns `None`.
- [x] Saving a student with a blank name raises `ValueError`.
- [x] Saving invalid data (e.g. a card in box 6) raises
      `sqlite3.IntegrityError` and leaves the previous save untouched.
- [x] A database with a newer schema version raises `ValueError`.
- [x] `DEFAULT_DB_PATH` is `~/.ai-language-teacher/data.db`, and importing
      the module does not create it.

## Out of Scope
- Renaming or deleting profiles, backups, export/import.
- Schema migrations beyond the version check (added when the schema first
  changes).
- Saving lesson content: lessons stay in the package JSON files.
- Concurrent access from several processes, encryption, authentication.
- Wiring persistence into a UI (spec 020+).
