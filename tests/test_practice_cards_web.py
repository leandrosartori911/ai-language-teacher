"""The Practice page as lesson cards (spec 033)."""

import re
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from ai_language_teacher.core.review import Card
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES
from ai_language_teacher.storage import connect, save_student
from ai_language_teacher.web.app import create_app

ANA = {"profile": "Ana"}
TODAY = date(2026, 10, 17)
APP_URL = "http://127.0.0.1:8000"
HIRAGANA = COURSES["hiragana"]
LATER = Card(3, TODAY + timedelta(days=4))
PRACTICE = "/practice/hiragana"


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "data.db"


@pytest.fixture
def client(db_path):
    return TestClient(create_app(db_path, today=lambda: TODAY), base_url=APP_URL, cookies=ANA)


@pytest.fixture
def text(client, db_path):
    # Lesson 1 fully learned and mastered, so lesson 2 is unlocked with
    # nothing learned yet.
    student = Student("Ana")
    for item in HIRAGANA[0].items:
        student.cards["hiragana"][item] = LATER
        student.knowledge["hiragana"].update(item, 1.0)
    conn = connect(db_path)
    save_student(conn, student)
    conn.close()
    return client.get(PRACTICE).text


def lesson_card(text, number):
    cards = re.findall(r'<li class="lesson[^"]*">(.*?)</li>', text, re.S)
    return cards[number - 1]


def test_page_explains_practice_and_study(text):
    assert "Practice reviews what you already studied. New items come from Study." in text


def test_each_unlocked_lesson_is_a_card_with_progress(text):
    total = len(HIRAGANA[0].items)
    first, second = lesson_card(text, 1), lesson_card(text, 2)

    assert HIRAGANA[0].title in first
    assert f'<progress max="{total}" value="{total}">' in first
    assert f"{total} / {total} learned" in first
    assert HIRAGANA[1].title in second
    assert f"0 / {len(HIRAGANA[1].items)} learned" in second
    assert len(re.findall(r'<li class="lesson', text)) == 2


def test_learned_lesson_has_a_practice_button(text):
    assert re.search(
        rf'<a class="button primary" href="{PRACTICE}\?lesson=1">Practice</a>', lesson_card(text, 1)
    )


def test_unstudied_lesson_points_to_study(text):
    second = lesson_card(text, 2)

    assert "Not studied yet." in second
    assert '<a class="button" href="/study/hiragana">Study</a>' in second
    assert "?lesson=2" not in text


def test_fully_learned_lesson_says_so(text):
    assert "All learned" in lesson_card(text, 1)
    assert "All learned" not in lesson_card(text, 2)
