import importlib
import sqlite3
from datetime import date
from pathlib import Path

import pytest

from ai_language_teacher import storage
from ai_language_teacher.core.assessment import AssessmentResult
from ai_language_teacher.core.progression import open_skills, unlocked_lessons
from ai_language_teacher.core.review import Card, record_answer
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES, PREREQUISITES
from ai_language_teacher.storage import connect, list_students, load_student, save_student

TODAY = date(2026, 10, 3)


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "nested" / "folder" / "data.db"


@pytest.fixture
def conn(db_path):
    connection = connect(db_path)
    yield connection
    connection.close()


def student_with_progress(name="Ana"):
    student = Student(name)
    for item in ["あ", "い", "う", "え", "お"]:
        record_answer(student, AssessmentResult("hiragana", True, 1.0, item), TODAY)
    record_answer(student, AssessmentResult("hiragana", False, 0.0, "か"), TODAY)
    record_answer(student, AssessmentResult("katakana", True, 1.0, "ア"), TODAY)
    unlocked_lessons(student, "hiragana", COURSES["hiragana"])
    open_skills(student, COURSES, PREREQUISITES)
    return student


def test_connect_creates_file_and_folders_with_foreign_keys(db_path, conn):
    assert db_path.exists()
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_reopening_keeps_data(db_path, conn):
    save_student(conn, Student("Ana"))
    conn.close()

    reopened = connect(db_path)
    try:
        assert list_students(reopened) == ["Ana"]
    finally:
        reopened.close()


def test_new_student_round_trips(conn):
    save_student(conn, Student("Ana"))

    assert load_student(conn, "Ana") == Student("Ana")


def test_student_with_progress_round_trips(conn):
    student = student_with_progress()
    assert student.unlocked_count["hiragana"] == 2
    assert student.opened_skills == {"hiragana"}

    save_student(conn, student)

    assert load_student(conn, "Ana") == student


def test_saving_again_updates_without_duplicates(conn):
    student = student_with_progress()
    save_student(conn, student)

    record_answer(student, AssessmentResult("hiragana", True, 1.0, "か"), TODAY)
    save_student(conn, student)

    assert load_student(conn, "Ana") == student
    assert conn.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0] == 7


def test_students_are_stored_separately(conn):
    ana, bruno = student_with_progress("Ana"), Student("Bruno")
    save_student(conn, bruno)
    save_student(conn, ana)

    assert list_students(conn) == ["Ana", "Bruno"]
    assert load_student(conn, "Ana") == ana
    assert load_student(conn, "Bruno") == bruno


def test_loading_unknown_name_returns_none(conn):
    assert load_student(conn, "Nobody") is None


@pytest.mark.parametrize("name", ["", "   "])
def test_blank_name_is_rejected(conn, name):
    with pytest.raises(ValueError):
        save_student(conn, Student(name))


def test_invalid_data_is_rejected_and_previous_save_kept(conn):
    student = student_with_progress()
    save_student(conn, student)
    saved = load_student(conn, "Ana")

    student.cards["hiragana"]["あ"] = Card(6, TODAY)
    with pytest.raises(sqlite3.IntegrityError):
        save_student(conn, student)

    assert load_student(conn, "Ana") == saved


def test_newer_schema_version_is_refused(db_path, conn):
    conn.execute("PRAGMA user_version = 2")
    conn.close()

    with pytest.raises(ValueError):
        connect(db_path)


def test_default_path_is_in_home_and_import_creates_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    try:
        module = importlib.reload(storage)
        assert module.DEFAULT_DB_PATH == Path(tmp_path) / ".ai-language-teacher" / "data.db"
        assert not (tmp_path / ".ai-language-teacher").exists()
    finally:
        monkeypatch.undo()
        importlib.reload(storage)
