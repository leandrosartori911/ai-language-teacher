import html
import re
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from ai_language_teacher.core.review import Card
from ai_language_teacher.core.student import Student
from ai_language_teacher.storage import connect, load_student, save_student
from ai_language_teacher.web.app import create_app

TODAY = date(2026, 10, 8)
APP_URL = "http://127.0.0.1:8000"
EXPLAIN_FORM = re.compile(
    r'<form method="post" action="/ask/hiragana/Ana" target="_blank" class="explain">'
    r'.*?name="item" value="(?P<item>[^"]*)"'
    r'.*?name="question" value="(?P<question>[^"]*)"',
    re.DOTALL,
)


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
        return "ぬ has a loop at the end; め does not."

    app = create_app(db_path, today=lambda: TODAY, ask=fake_teacher)
    return TestClient(app, base_url=APP_URL)


@pytest.fixture
def ana(db_path):
    # あ already learned (for Practice), not due yet; い is new (for Study).
    student = Student("Ana")
    student.cards["hiragana"]["あ"] = Card(3, TODAY + timedelta(days=4))
    conn = connect(db_path)
    save_student(conn, student)
    conn.close()
    return student


def load(db_path):
    conn = connect(db_path)
    student = load_student(conn, "Ana")
    conn.close()
    return student


def explain_form(text):
    match = EXPLAIN_FORM.search(text)
    assert match, "no explain form"
    return html.unescape(match["item"]), html.unescape(match["question"])


def study(client, item, answer):
    return client.post("/study/hiragana/Ana", data={"item": item, "answer": answer})


def practise(client, item, answer):
    data = {"lesson": "1", "n": 0, "item": item, "answer": answer}
    return client.post("/practice/hiragana/Ana", data=data)


def test_wrong_study_answer_offers_explain_my_mistake(client, ana):
    text = study(client, "い", "ri").text

    item, question = explain_form(text)
    assert "Explain my mistake (opens in a new tab)" in text
    assert item == "い"
    assert question == (
        'I answered "ri", but the right answer is "i". '
        "Why is my answer wrong, and how can I remember the right one?"
    )


def test_wrong_practice_answer_offers_explain_my_mistake(client, ana):
    item, question = explain_form(practise(client, "あ", "o").text)

    assert item == "あ"
    assert 'I answered "o", but the right answer is "a".' in question


def test_correct_answer_has_no_explain_form(client, ana):
    assert "Explain my mistake" not in study(client, "い", "i").text
    assert "Explain my mistake" not in practise(client, "あ", "a").text


def test_long_answer_is_cut_and_still_accepted(client, ana):
    _, question = explain_form(study(client, "い", "x" * 300).text)

    assert f'"{"x" * 100}"' in question
    assert "x" * 101 not in question
    response = client.post("/ask/hiragana/Ana", data={"item": "い", "question": question})
    assert response.status_code == 200


def test_explain_question_reaches_the_teacher_and_saves_nothing(client, ana, db_path, asked):
    item, question = explain_form(practise(client, "あ", "o").text)
    before = load(db_path)

    response = client.post("/ask/hiragana/Ana", data={"item": item, "question": question})

    assert response.status_code == 200
    assert 'I answered "o", but the right answer is "a".' in asked[0]
    assert "Lesson content for あ:" in asked[0]
    assert load(db_path) == before


def test_feedback_forms_open_in_a_new_tab_but_teaching_card_does_not(client, ana):
    teach = client.get("/study/hiragana/Ana").text
    feedback = study(client, "い", "ri").text

    assert 'action="/ask/hiragana/Ana" target="_blank" class="ask"' in feedback
    assert 'action="/ask/hiragana/Ana" class="ask"' in teach
    assert 'target="_blank"' not in teach
