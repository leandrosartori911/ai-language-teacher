from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from markupsafe import escape

from ai_language_teacher.core.review import Card
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES
from ai_language_teacher.storage import connect, list_students, load_student, save_student
from ai_language_teacher.web.app import create_app

TODAY = date(2026, 10, 5)
APP_URL = "http://127.0.0.1:8000"
HIRAGANA = COURSES["hiragana"]


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


def load(db_path, name="Ana"):
    conn = connect(db_path)
    student = load_student(conn, name)
    conn.close()
    return student


def html(text):
    # Jinja escapes quotes and ampersands in page text.
    return str(escape(text))


def master(student, skill):
    for lesson in COURSES[skill]:
        for item in lesson.items:
            student.knowledge[skill].update(item, 1.0)


@pytest.fixture
def ana(db_path):
    student = Student("Ana")
    save(db_path, student)
    return student


def test_dashboard_links_to_study_only_for_open_skills(client, ana):
    text = client.get("/students/Ana").text

    assert 'href="/study/hiragana/Ana"' in text
    assert "/study/katakana/" not in text
    assert "/study/kanji/" not in text


def test_new_item_shows_teaching_card_without_answer_form(client, ana):
    teaching = HIRAGANA[0].teaching["あ"]

    text = client.get("/study/hiragana/Ana").text

    assert html(teaching.explanation) in text
    assert html(teaching.mnemonic) in text
    assert html(teaching.example.word) in text
    assert html(teaching.example.meaning) in text
    assert html(teaching.culture_note) in text
    assert 'href="/study/hiragana/Ana?step=quiz"' in text
    assert 'name="answer"' not in text


def test_quiz_step_shows_question_and_answer_form(client, ana):
    text = client.get("/study/hiragana/Ana?step=quiz").text

    assert "What is the romaji for あ?" in text
    assert 'name="answer"' in text
    assert 'name="item" value="あ"' in text
    assert html(HIRAGANA[0].teaching["あ"].mnemonic) not in text


def test_due_review_is_quizzed_directly_before_new_items(client, db_path):
    student = Student("Ana")
    student.cards["hiragana"]["い"] = Card(1, TODAY)
    save(db_path, student)

    text = client.get("/study/hiragana/Ana").text

    assert "What is the romaji for い?" in text
    assert "Quiz me" not in text


def test_correct_answer_is_saved_and_moves_the_card_up(client, ana, db_path):
    response = client.post("/study/hiragana/Ana", data={"item": "あ", "answer": "a"})

    assert response.status_code == 200
    assert "Correct" in response.text
    student = load(db_path)
    assert student.knowledge["hiragana"].get_score("あ") == 1.0
    assert student.cards["hiragana"]["あ"] == Card(1, TODAY + timedelta(days=1))


def test_correct_review_uses_box_intervals(client, db_path):
    student = Student("Ana")
    student.cards["hiragana"]["あ"] = Card(2, TODAY)
    save(db_path, student)

    client.post("/study/hiragana/Ana", data={"item": "あ", "answer": "a"})

    assert load(db_path).cards["hiragana"]["あ"] == Card(3, TODAY + timedelta(days=4))


def test_wrong_answer_is_saved_and_shows_answer_and_teaching(client, ana, db_path):
    response = client.post("/study/hiragana/Ana", data={"item": "あ", "answer": "e"})

    assert response.status_code == 200
    assert "Not quite" in response.text
    assert "Your answer: e" in response.text
    assert "Expected: a" in response.text
    assert html(HIRAGANA[0].teaching["あ"].mnemonic) in response.text
    student = load(db_path)
    assert student.knowledge["hiragana"].get_score("あ") == 0.0
    assert student.cards["hiragana"]["あ"] == Card(1, TODAY)


@pytest.mark.parametrize("answer", ["SHI", "si", "  shi "])
def test_answers_are_checked_like_the_core_assessment(client, db_path, answer):
    student = Student("Ana")
    student.cards["hiragana"]["し"] = Card(1, TODAY)
    save(db_path, student)

    response = client.post("/study/hiragana/Ana", data={"item": "し", "answer": answer})

    assert "Correct" in response.text
    assert load(db_path).knowledge["hiragana"].get_score("し") == 1.0


@pytest.mark.parametrize("item", ["し", "zzz", ""])
def test_item_not_in_queue_records_nothing(client, ana, db_path, item):
    response = client.post(
        "/study/hiragana/Ana", data={"item": item, "answer": "shi"}, follow_redirects=False
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/study/hiragana/Ana"
    assert load(db_path) == ana


def test_answering_twice_records_once(client, ana, db_path):
    client.post("/study/hiragana/Ana", data={"item": "あ", "answer": "a"})
    once = load(db_path)

    response = client.post(
        "/study/hiragana/Ana", data={"item": "あ", "answer": "a"}, follow_redirects=False
    )

    assert response.status_code == 303
    assert load(db_path) == once


@pytest.mark.parametrize("answer", ["", "   "])
def test_blank_answer_returns_400_and_records_nothing(client, ana, db_path, answer):
    response = client.post("/study/hiragana/Ana", data={"item": "あ", "answer": answer})

    assert response.status_code == 400
    assert "What is the romaji for あ?" in response.text
    assert load(db_path) == ana


def test_mastering_first_lesson_offers_the_second(client, ana):
    for item, answer in HIRAGANA[0].items.items():
        client.post("/study/hiragana/Ana", data={"item": item, "answer": answer})

    text = client.get("/study/hiragana/Ana").text

    first_of_second = next(iter(HIRAGANA[1].items))
    assert html(HIRAGANA[1].teaching[first_of_second].explanation) in text


def test_empty_queue_says_so_and_shows_next_review(client, db_path):
    student = Student("Ana")
    for item in HIRAGANA[0].items:
        student.cards["hiragana"][item] = Card(2, TODAY + timedelta(days=3))
    student.cards["hiragana"]["あ"] = Card(1, TODAY + timedelta(days=2))
    save(db_path, student)

    text = client.get("/study/hiragana/Ana").text

    assert "Nothing to study right now" in text
    assert "2026-10-07" in text
    assert 'href="/students/Ana"' in text


def test_kanji_card_shows_kun_and_on_readings(client, db_path):
    student = Student("Ana")
    master(student, "hiragana")
    master(student, "katakana")
    save(db_path, student)

    text = client.get("/study/kanji/Ana").text

    assert "Kun: ひと, ひと.つ" in text
    assert "On: イチ, イツ" in text


def test_vocabulary_card_shows_word_reading(client, db_path):
    student = Student("Ana")
    master(student, "hiragana")
    master(student, "katakana")
    save(db_path, student)

    text = client.get("/study/vocabulary/Ana").text

    assert "Reading: おはようございます" in text


def test_locked_skill_returns_403(client, ana):
    assert client.get("/study/katakana/Ana").status_code == 403
    response = client.post("/study/katakana/Ana", data={"item": "ア", "answer": "a"})
    assert response.status_code == 403


def test_unknown_skill_or_student_returns_404(client, ana):
    assert client.get("/study/grammar/Ana").status_code == 404
    assert client.get("/study/hiragana/Nobody").status_code == 404


@pytest.mark.parametrize("base_url", ["http://evil.example", "http://192.168.0.10:8000"])
def test_unknown_host_is_rejected(db_path, base_url):
    client = TestClient(create_app(db_path), base_url=base_url)

    assert client.get("/").status_code == 400


def test_localhost_host_is_accepted(db_path):
    client = TestClient(create_app(db_path), base_url="http://localhost:8000")

    assert client.get("/").status_code == 200


def test_foreign_origin_cannot_create_a_profile(client, db_path):
    response = client.post(
        "/students", data={"name": "Eve"}, headers={"Origin": "http://evil.example"}
    )

    assert response.status_code == 403
    conn = connect(db_path)
    assert list_students(conn) == []
    conn.close()


def test_foreign_origin_cannot_answer(client, ana, db_path):
    response = client.post(
        "/study/hiragana/Ana",
        data={"item": "あ", "answer": "a"},
        headers={"Origin": "http://evil.example"},
    )

    assert response.status_code == 403
    assert load(db_path) == ana


def test_own_origin_can_post(client, ana, db_path):
    response = client.post(
        "/study/hiragana/Ana", data={"item": "あ", "answer": "a"}, headers={"Origin": APP_URL}
    )

    assert response.status_code == 200
    assert load(db_path).knowledge["hiragana"].get_score("あ") == 1.0
