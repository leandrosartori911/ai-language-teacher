from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from markupsafe import escape

from ai_language_teacher.core.review import Card
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES
from ai_language_teacher.storage import connect, load_student, save_student
from ai_language_teacher.web.app import create_app

TODAY = date(2026, 10, 5)
APP_URL = "http://127.0.0.1:8000"
HIRAGANA = COURSES["hiragana"]
LATER = Card(3, TODAY + timedelta(days=4))
PRACTICE = "/practice/hiragana/Ana"


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "data.db"


@pytest.fixture
def client(db_path):
    return TestClient(create_app(db_path, today=lambda: TODAY), base_url=APP_URL)


def save(db_path, student):
    conn = connect(db_path)
    save_student(conn, student)
    conn.close()


def load(db_path):
    conn = connect(db_path)
    student = load_student(conn, "Ana")
    conn.close()
    return student


@pytest.fixture
def ana(db_path):
    # Learned あ and い from the first hiragana lesson; reviews not due yet.
    student = Student("Ana")
    student.cards["hiragana"]["あ"] = LATER
    student.cards["hiragana"]["い"] = LATER
    save(db_path, student)
    return student


def practise(client, item, answer, n=0, lesson="1", **kwargs):
    data = {"lesson": lesson, "n": n, "item": item, "answer": answer}
    return client.post(PRACTICE, data=data, **kwargs)


def test_dashboard_links_to_practice_only_for_open_skills(client, ana):
    text = client.get("/students/Ana").text

    assert f'href="{PRACTICE}"' in text
    assert "/practice/katakana/" not in text


def test_lesson_list_shows_unlocked_lessons_with_learned_counts(client, ana):
    text = client.get(PRACTICE).text

    assert HIRAGANA[0].title in text
    assert f"2 of {len(HIRAGANA[0].items)} learned" in text
    assert f'href="{PRACTICE}?lesson=1"' in text
    assert HIRAGANA[1].title not in text


def test_lesson_without_learned_items_is_listed_but_not_linked(client, db_path):
    save(db_path, Student("Ana"))

    text = client.get(PRACTICE).text

    assert f"0 of {len(HIRAGANA[0].items)} learned" in text
    assert "?lesson=1" not in text


def test_practice_quizzes_learned_items_in_lesson_order(client, ana):
    first = client.get(f"{PRACTICE}?lesson=1").text
    second = client.get(f"{PRACTICE}?lesson=1&n=1").text

    assert "What is the romaji for あ?" in first
    assert "item 1 / 2" in first
    assert 'name="item" value="あ"' in first
    assert str(escape(HIRAGANA[0].teaching["あ"].mnemonic)) not in first
    assert "What is the romaji for い?" in second
    assert "item 2 / 2" in second


def test_correct_practice_answer_is_saved_without_moving_the_card(client, ana, db_path):
    response = practise(client, "あ", "a")

    assert response.status_code == 200
    assert "Correct" in response.text
    assert f'href="{PRACTICE}?lesson=1&n=1"' in response.text
    student = load(db_path)
    assert student.knowledge["hiragana"].get_score("あ") == 1.0
    assert student.cards["hiragana"]["あ"] == LATER


def test_wrong_practice_answer_demotes_and_shows_teaching(client, ana, db_path):
    response = practise(client, "あ", "o")

    assert "Not quite" in response.text
    assert "Expected: a" in response.text
    assert str(escape(HIRAGANA[0].teaching["あ"].mnemonic)) in response.text
    assert load(db_path).cards["hiragana"]["あ"] == Card(1, TODAY)


def test_past_the_last_item_practice_is_complete(client, ana):
    text = client.get(f"{PRACTICE}?lesson=1&n=2").text

    assert "Practice complete" in text
    assert f'href="{PRACTICE}"' in text
    assert 'href="/study/hiragana/Ana"' in text


def test_lesson_with_nothing_learned_says_so(client, db_path):
    save(db_path, Student("Ana"))

    text = client.get(f"{PRACTICE}?lesson=1").text

    assert "Nothing learned in this lesson yet" in text
    assert 'href="/study/hiragana/Ana"' in text


@pytest.mark.parametrize("item", ["う", "か", ""])
def test_item_not_learned_in_the_lesson_records_nothing(client, ana, db_path, item):
    response = practise(client, item, "u", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == f"{PRACTICE}?lesson=1"
    assert load(db_path) == ana


@pytest.mark.parametrize("answer", ["", "  "])
def test_blank_practice_answer_returns_400(client, ana, db_path, answer):
    response = practise(client, "あ", answer)

    assert response.status_code == 400
    assert "What is the romaji for あ?" in response.text
    assert load(db_path) == ana


def test_locked_lesson_returns_403(client, ana):
    assert client.get(f"{PRACTICE}?lesson=2").status_code == 403
    assert practise(client, "か", "ka", lesson="2").status_code == 403


@pytest.mark.parametrize("lesson", ["0", "99", "abc", "-1"])
def test_bad_lesson_number_returns_404(client, ana, lesson):
    assert client.get(f"{PRACTICE}?lesson={lesson}").status_code == 404
    assert practise(client, "あ", "a", lesson=lesson).status_code == 404


def test_negative_position_returns_404(client, ana):
    assert client.get(f"{PRACTICE}?lesson=1&n=-1").status_code == 404


def test_locked_skill_and_unknowns(client, ana):
    assert client.get("/practice/katakana/Ana").status_code == 403
    assert client.get("/practice/grammar/Ana").status_code == 404
    assert client.get("/practice/hiragana/Nobody").status_code == 404


def test_foreign_origin_cannot_practise(client, ana, db_path):
    response = practise(client, "あ", "a", headers={"Origin": "http://evil.example"})

    assert response.status_code == 403
    assert load(db_path) == ana
