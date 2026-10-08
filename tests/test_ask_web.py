from datetime import date

import pytest
from fastapi.testclient import TestClient
from markupsafe import escape

from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES
from ai_language_teacher.storage import connect, load_student, save_student
from ai_language_teacher.teacher import TeacherUnavailable
from ai_language_teacher.web.app import create_app

APP_URL = "http://127.0.0.1:8000"
A = COURSES["hiragana"][0].teaching["あ"]


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "data.db"


@pytest.fixture
def asked():
    return []


@pytest.fixture
def client(db_path, asked):
    def fake_teacher(prompt):
        asked.append(prompt)
        return "Think of the stick figure falling in!"

    app = create_app(db_path, today=lambda: date(2026, 10, 8), ask=fake_teacher)
    return TestClient(app, base_url=APP_URL)


@pytest.fixture
def ana(db_path):
    student = Student("Ana")
    conn = connect(db_path)
    save_student(conn, student)
    conn.close()
    return student


def load(db_path):
    conn = connect(db_path)
    student = load_student(conn, "Ana")
    conn.close()
    return student


def ask(client, item="あ", question="Why is it shaped like that?", skill="hiragana", **kwargs):
    return client.post(f"/ask/{skill}/Ana", data={"item": item, "question": question}, **kwargs)


def test_teaching_card_has_the_ask_form(client, ana):
    text = client.get("/study/hiragana/Ana").text

    assert '<form method="post" action="/ask/hiragana/Ana"' in text
    assert '<input type="hidden" name="item" value="あ">' in text
    assert 'name="question"' in text


def test_asking_shows_question_answer_and_card_and_saves_nothing(client, ana, db_path, asked):
    response = ask(client)

    assert response.status_code == 200
    assert str(escape("Why is it shaped like that?")) in response.text
    assert str(escape("Think of the stick figure falling in!")) in response.text
    assert str(escape(A.explanation)) in response.text
    assert 'href="/study/hiragana/Ana"' in response.text
    assert "Why is it shaped like that?" in asked[0]
    assert A.mnemonic in asked[0]
    assert load(db_path) == ana


def test_unavailable_teacher_still_shows_the_card(db_path, ana, monkeypatch):
    def offline(prompt):
        raise TeacherUnavailable("connection refused")

    monkeypatch.setenv("AI_TEACHER_MODEL", "gemma3:4b")
    app = create_app(db_path, ask=offline)
    response = ask(TestClient(app, base_url=APP_URL))

    assert response.status_code == 200
    assert "ollama pull gemma3:4b" in response.text
    assert str(escape(A.explanation)) in response.text


@pytest.mark.parametrize("question", ["", "   ", "x" * 501])
def test_blank_or_long_question_returns_400(client, ana, asked, question):
    response = ask(client, question=question)

    assert response.status_code == 400
    assert asked == []


def test_question_of_500_characters_is_accepted(client, ana):
    assert ask(client, question="x" * 500).status_code == 200


def test_item_outside_unlocked_lessons_returns_404(client, ana, asked):
    assert ask(client, item="か").status_code == 404
    assert ask(client, item="nope").status_code == 404
    assert asked == []


def test_unknown_skill_or_student_404_and_closed_skill_403(client, ana):
    assert ask(client, skill="grammar").status_code == 404
    unknown = client.post("/ask/hiragana/Bia", data={"item": "あ", "question": "Hi"})
    assert unknown.status_code == 404
    assert ask(client, item="ア", skill="katakana").status_code == 403


def test_foreign_origin_is_blocked(client, ana, asked):
    response = ask(client, headers={"Origin": "http://evil.example"})

    assert response.status_code == 403
    assert asked == []
