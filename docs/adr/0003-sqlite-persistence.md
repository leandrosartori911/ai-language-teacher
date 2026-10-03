# 0003: Student progress is stored in SQLite with normal tables

- Status: accepted
- Date: 2026-10-03

## Context
Student progress (mastery, per-item knowledge, spaced-repetition cards,
unlocked lessons and opened skills) must survive restarts for the web UI.
It has to stay local and free, and the project is also a way to learn
software engineering.

## Decision
Use SQLite through the standard library `sqlite3` module, with one table
per kind of data (`students`, `skills`, `knowledge`, `cards`), foreign
keys, primary keys and `CHECK` constraints. The database lives in the
user's home folder (`~/.ai-language-teacher/data.db`), not in the repo.
Several profiles are supported, identified by name, without login. The
schema version is kept in `PRAGMA user_version`; a database newer than
the code is refused.

## Consequences
- No new dependency, no server, one file to back up.
- The database itself rejects invalid data (a card in box 6, a duplicate
  item, a score above 1), and each save is one transaction, so a failed
  save keeps the previous one.
- Queries such as "cards due today" can be written in SQL later.
- Every change to the `Student` model needs a matching schema change and,
  once real data exists, a migration.

## Alternatives considered
- One JSON blob per student in SQLite (or a JSON file): less code and no
  migrations, but no integrity checks and every query loads everything.
- An ORM such as SQLAlchemy: a large dependency for four small tables.
