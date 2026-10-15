from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from ai_language_teacher.core.review import Card
from ai_language_teacher.core.student import Student
from ai_language_teacher.storage import connect, save_student
from ai_language_teacher.web.app import create_app

# The cookie that choosing "Ana" on the home page sets (spec 026).
ANA = {"profile": "Ana"}

TODAY = date(2026, 10, 8)


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "data.db"


@pytest.fixture
def client(db_path):
    return TestClient(
        create_app(db_path, today=lambda: TODAY), base_url="http://127.0.0.1:8000", cookies=ANA
    )


def save(db_path, student):
    conn = connect(db_path)
    save_student(conn, student)
    conn.close()


def dashboard(client):
    return client.get("/dashboard").text


def card(text, skill):
    # The dashboard card of one course (spec 029).
    return text.split(f'id="course-{skill}"', 1)[1].split("</li>", 1)[0]


def test_student_without_cards_sees_zero_due(client, db_path):
    student = Student("Ana")
    student.opened_skills.add("katakana")
    save(db_path, student)

    text = dashboard(client)

    assert "lessons unlocked · 0 due" in card(text, "hiragana")
    assert "lessons unlocked · 0 due" in card(text, "katakana")


def test_only_cards_due_today_or_earlier_are_counted(client, db_path):
    student = Student("Ana")
    student.cards["hiragana"] = {
        "あ": Card(1, TODAY - timedelta(days=3)),
        "い": Card(2, TODAY),
        "う": Card(3, TODAY + timedelta(days=1)),
    }
    save(db_path, student)

    assert "lessons unlocked · 2 due" in dashboard(client)


def test_counts_are_per_skill(client, db_path):
    student = Student("Ana")
    student.opened_skills.add("katakana")
    student.cards["hiragana"] = {"あ": Card(1, TODAY)}
    save(db_path, student)

    text = dashboard(client)

    assert "lessons unlocked · 1 due" in card(text, "hiragana")
    assert "lessons unlocked · 0 due" in card(text, "katakana")


def test_locked_skills_show_no_due_count(client, db_path):
    save(db_path, Student("Ana"))

    text = dashboard(client)

    assert "due" not in card(text, "katakana")
    assert "Master hiragana to open" in card(text, "katakana")


def test_count_uses_the_app_today(db_path):
    student = Student("Ana")
    student.cards["hiragana"] = {"あ": Card(2, TODAY + timedelta(days=2))}
    save(db_path, student)

    def count_on(day):
        app = create_app(db_path, today=lambda: day)
        return TestClient(app, base_url="http://127.0.0.1:8000", cookies=ANA).get("/dashboard").text

    assert "lessons unlocked · 0 due" in count_on(TODAY)
    assert "lessons unlocked · 1 due" in count_on(TODAY + timedelta(days=2))
