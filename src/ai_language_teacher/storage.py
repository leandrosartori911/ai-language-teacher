import sqlite3
from datetime import date
from pathlib import Path

from ai_language_teacher.core.review import Card
from ai_language_teacher.core.student import Student

DEFAULT_DB_PATH = Path.home() / ".ai-language-teacher" / "data.db"
SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE CHECK (trim(name) <> ''),
    level TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS skills (
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    score REAL NOT NULL CHECK (score BETWEEN 0 AND 1),
    unlocked_count INTEGER NOT NULL CHECK (unlocked_count >= 0),
    opened INTEGER NOT NULL CHECK (opened IN (0, 1)),
    PRIMARY KEY (student_id, skill)
);
CREATE TABLE IF NOT EXISTS knowledge (
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    item TEXT NOT NULL,
    score REAL NOT NULL CHECK (score BETWEEN 0 AND 1),
    PRIMARY KEY (student_id, skill, item)
);
CREATE TABLE IF NOT EXISTS cards (
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    item TEXT NOT NULL,
    box INTEGER NOT NULL CHECK (box BETWEEN 1 AND 5),
    due TEXT NOT NULL,
    PRIMARY KEY (student_id, skill, item)
);
"""


def connect(path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON")

    version = conn.execute("PRAGMA user_version").fetchone()[0]
    if version > SCHEMA_VERSION:
        conn.close()
        raise ValueError(f"{path}: schema version {version} is newer than {SCHEMA_VERSION}")

    conn.executescript(SCHEMA)
    # PRAGMA cannot take "?" parameters; SCHEMA_VERSION is a constant int.
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    return conn


def save_student(conn: sqlite3.Connection, student: Student) -> None:
    if not student.name.strip():
        raise ValueError("Student name is blank")

    # ponytail: rewrites every row of the student on each save; fine for a few
    # hundred items, switch to per-row upserts if saves get slow.
    with conn:
        conn.execute("DELETE FROM students WHERE name = ?", (student.name,))
        cursor = conn.execute(
            "INSERT INTO students (name, level) VALUES (?, ?)", (student.name, student.level)
        )
        student_id = cursor.lastrowid
        conn.executemany(
            "INSERT INTO skills VALUES (?, ?, ?, ?, ?)",
            [
                (
                    student_id,
                    skill,
                    score,
                    student.unlocked_count.get(skill, 0),
                    skill in student.opened_skills,
                )
                for skill, score in student.skills.items()
            ],
        )
        conn.executemany(
            "INSERT INTO knowledge VALUES (?, ?, ?, ?)",
            [
                (student_id, skill, item, score)
                for skill, knowledge in student.knowledge.items()
                for item, score in knowledge.items.items()
            ],
        )
        conn.executemany(
            "INSERT INTO cards VALUES (?, ?, ?, ?, ?)",
            [
                (student_id, skill, item, card.box, card.due.isoformat())
                for skill, cards in student.cards.items()
                for item, card in cards.items()
            ],
        )


def load_student(conn: sqlite3.Connection, name: str) -> Student | None:
    row = conn.execute("SELECT id, level FROM students WHERE name = ?", (name,)).fetchone()
    if row is None:
        return None

    student_id, level = row
    student = Student(name, level)

    for skill, score, unlocked_count, opened in conn.execute(
        "SELECT skill, score, unlocked_count, opened FROM skills WHERE student_id = ?",
        (student_id,),
    ):
        student.skills[skill] = score
        student.unlocked_count[skill] = unlocked_count
        if opened:
            student.opened_skills.add(skill)

    for skill, item, score in conn.execute(
        "SELECT skill, item, score FROM knowledge WHERE student_id = ?", (student_id,)
    ):
        student.knowledge[skill].update(item, score)

    for skill, item, box, due in conn.execute(
        "SELECT skill, item, box, due FROM cards WHERE student_id = ?", (student_id,)
    ):
        student.cards[skill][item] = Card(box, date.fromisoformat(due))

    return student


def list_students(conn: sqlite3.Connection) -> list[str]:
    return [name for (name,) in conn.execute("SELECT name FROM students ORDER BY name")]
