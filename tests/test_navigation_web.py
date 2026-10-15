import re
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from ai_language_teacher.core.review import Card
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES
from ai_language_teacher.storage import connect, save_student
from ai_language_teacher.web.app import create_app

# The cookie that choosing "Ana" on the home page sets (spec 026).
ANA = {"profile": "Ana"}

TODAY = date(2026, 10, 15)
APP_URL = "http://127.0.0.1:8000"
HIRAGANA = COURSES["hiragana"]
FIRST = HIRAGANA[0]
LATER = Card(2, TODAY + timedelta(days=3))


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "data.db"


@pytest.fixture
def client(db_path):
    app = create_app(db_path, today=lambda: TODAY, ask=lambda prompt: "Hi")
    return TestClient(app, base_url=APP_URL, cookies=ANA)


def save(db_path, student):
    conn = connect(db_path)
    save_student(conn, student)
    conn.close()


def master(student, skill):
    for lesson in COURSES[skill]:
        for item in lesson.items:
            student.knowledge[skill].update(item, 1.0)


def card(text, skill):
    # The dashboard card of one course.
    return text.split(f'id="course-{skill}"', 1)[1].split("</li>", 1)[0]


def done_with_first_lesson(student):
    # Every item of the first lesson learned, none due today, lesson not mastered.
    for item in FIRST.items:
        student.cards["hiragana"][item] = LATER
    return student


# Header navigation


@pytest.mark.parametrize(
    ("url", "current"),
    [
        ("/dashboard", "/dashboard"),
        ("/study/hiragana", "/study/hiragana"),
        ("/practice/hiragana", "/study/hiragana"),
    ],
)
def test_header_navigation_marks_the_current_page(client, db_path, url, current):
    save(db_path, Student("Ana"))

    text = client.get(url).text

    nav = text.split("<nav", 1)[1].split("</nav>", 1)[0]
    assert 'href="/dashboard"' in nav
    assert 'href="/study/hiragana"' in nav
    assert "/study/katakana" not in nav
    assert nav.count('aria-current="page"') == 1
    assert f'href="{current}" aria-current="page"' in nav


def test_header_navigation_lists_every_open_course(client, db_path):
    student = Student("Ana")
    master(student, "hiragana")
    master(student, "katakana")
    save(db_path, student)

    nav = client.get("/dashboard").text.split("<nav", 1)[1].split("</nav>", 1)[0]

    for skill in COURSES:
        assert f'href="/study/{skill}"' in nav


def test_ask_page_has_the_header_navigation(client, db_path):
    save(db_path, Student("Ana"))

    text = client.post("/ask/hiragana", data={"item": "あ", "question": "Why?"}).text

    assert 'href="/study/hiragana" aria-current="page"' in text


# Continue


def test_continue_offers_new_items_of_the_first_course(client, db_path):
    save(db_path, Student("Ana"))

    text = client.get("/dashboard").text

    assert re.search(r'<a class="button[^"]*" href="/study/hiragana">Continue', text)


def test_continue_prefers_due_reviews_in_course_order(client, db_path):
    student = Student("Ana")
    master(student, "hiragana")
    student.opened_skills.add("katakana")
    student.cards["katakana"]["ア"] = Card(1, TODAY)
    save(db_path, student)

    text = client.get("/dashboard").text

    assert re.search(r'href="/study/katakana">Continue', text)


def test_continue_says_all_done_with_the_next_review(client, db_path):
    student = done_with_first_lesson(Student("Ana"))
    save(db_path, student)

    text = client.get("/dashboard").text

    assert "All done for today" in text
    assert LATER.due.isoformat() in text
    assert "Continue" not in text


# Course cards


def test_open_course_card_shows_name_progress_lessons_and_due(client, db_path):
    student = Student("Ana")
    student.knowledge["hiragana"].update("あ", 1.0)
    student.cards["hiragana"]["あ"] = Card(1, TODAY)
    save(db_path, student)

    hiragana = card(client.get("/dashboard").text, "hiragana")

    assert "ひらがな" in hiragana
    assert "あ" in hiragana
    assert '<progress max="100" value="1">' in hiragana
    assert f"1 / {len(HIRAGANA)} lessons unlocked" in hiragana
    assert "1 due" in hiragana
    assert 'href="/study/hiragana"' in hiragana
    assert 'href="/practice/hiragana"' in hiragana


def test_locked_course_card_says_what_opens_it(client, db_path):
    student = Student("Ana")
    student.knowledge["hiragana"].update("あ", 1.0)
    save(db_path, student)

    text = client.get("/dashboard").text

    katakana = card(text, "katakana")
    assert "カタカナ" in katakana
    assert "Master hiragana to open: 1%" in katakana
    assert "/study/katakana" not in katakana
    assert "Master katakana to open: 0%" in card(text, "kanji")
    assert "語彙" in card(text, "vocabulary")


# Study progress


def test_teaching_card_shows_what_is_left(client, db_path):
    save(db_path, Student("Ana"))

    text = client.get("/study/hiragana").text

    assert f"0 reviews, {len(FIRST.items)} new left" in text


def test_quiz_counts_due_reviews_and_new_items(client, db_path):
    student = Student("Ana")
    student.cards["hiragana"]["あ"] = Card(1, TODAY)
    save(db_path, student)

    text = client.get("/study/hiragana").text

    assert f"1 review, {len(FIRST.items) - 1} new left" in text


def test_feedback_shows_what_is_left_after_the_answer(client, db_path):
    save(db_path, Student("Ana"))

    text = client.post("/study/hiragana", data={"item": "あ", "answer": "a"}).text

    assert f"0 reviews, {len(FIRST.items) - 1} new left" in text


# Unlock messages


def test_answer_that_unlocks_a_lesson_says_so(client, db_path):
    # Three of five right (0.6); the last answer reaches the 0.8 threshold.
    student = done_with_first_lesson(Student("Ana"))
    items = list(FIRST.items)
    del student.cards["hiragana"][items[-1]]
    for item in items[:3]:
        student.knowledge["hiragana"].update(item, 1.0)
    save(db_path, student)

    last = items[-1]
    text = client.post("/study/hiragana", data={"item": last, "answer": FIRST.items[last]}).text

    assert f"Lesson 2 unlocked: {HIRAGANA[1].title}" in text


def test_other_answers_show_no_unlock_message(client, db_path):
    save(db_path, Student("Ana"))

    text = client.post("/study/hiragana", data={"item": "あ", "answer": "a"}).text

    assert "unlocked:" not in text
    assert "now open" not in text


def test_answer_that_opens_a_course_says_so(client, db_path):
    student = Student("Ana")
    master(student, "hiragana")
    student.unlocked_count["hiragana"] = len(HIRAGANA)
    student.knowledge["hiragana"].update("あ", 0.0)
    student.knowledge["hiragana"].update("い", 0.0)
    student.cards["hiragana"]["あ"] = Card(1, TODAY)
    save(db_path, student)

    text = client.post("/study/hiragana", data={"item": "あ", "answer": "a"}).text

    assert "Katakana is now open!" in text
    assert "unlocked:" not in text


def test_practice_answer_that_unlocks_a_lesson_says_so(client, db_path):
    student = Student("Ana")
    for item in FIRST.items:
        student.knowledge["hiragana"].update(item, 1.0)
        student.cards["hiragana"][item] = LATER
    student.knowledge["hiragana"].update("あ", 0.0)
    student.knowledge["hiragana"].update("い", 0.0)
    save(db_path, student)

    data = {"lesson": "1", "n": 0, "item": "あ", "answer": "a"}
    text = client.post("/practice/hiragana", data=data).text

    assert f"Lesson 2 unlocked: {HIRAGANA[1].title}" in text


# End screen


def test_end_screen_shows_next_review_tomorrow_and_links(client, db_path):
    student = done_with_first_lesson(Student("Ana"))
    student.cards["hiragana"]["あ"] = Card(1, TODAY + timedelta(days=1))
    student.cards["hiragana"]["い"] = Card(1, TODAY + timedelta(days=1))
    save(db_path, student)

    text = client.get("/study/hiragana").text

    assert "Nothing to study right now" in text
    assert (TODAY + timedelta(days=1)).isoformat() in text
    assert "2 reviews due tomorrow" in text
    main = text.split("<main>", 1)[1]
    assert re.search(r'<a class="button[^"]*" href="/practice/hiragana">', main)
    assert re.search(r'<a class="button[^"]*" href="/dashboard">', main)


# Feedback, wording and buttons


@pytest.mark.parametrize(("answer", "result"), [("a", "correct"), ("e", "wrong")])
def test_feedback_shows_the_result_in_one_block(client, db_path, answer, result):
    save(db_path, Student("Ana"))

    text = client.post("/study/hiragana", data={"item": "あ", "answer": answer}).text

    block = text.split(f'class="result {result}"', 1)[1].split("</section>", 1)[0]
    assert f"Your answer: <strong>{answer}</strong>" in block
    assert "Expected: <strong>a</strong>" in block


def test_practise_spelling_is_gone(client, db_path):
    student = Student("Ana")
    student.cards["hiragana"]["あ"] = LATER
    save(db_path, student)

    pages = [
        client.get("/practice/hiragana").text,
        client.get("/practice/hiragana?lesson=1&n=1").text,
    ]

    for text in pages:
        assert "Practise" not in text


def test_every_button_uses_the_button_class(client, db_path):
    save(db_path, Student("Ana"))

    pages = [
        client.get("/").text,
        client.get("/delete?name=Ana").text,
        client.get("/dashboard").text,
        client.get("/study/hiragana").text,
        client.get("/study/hiragana?step=quiz").text,
        client.post("/study/hiragana", data={"item": "あ", "answer": "e"}).text,
        client.get("/practice/hiragana").text,
        client.post("/ask/hiragana", data={"item": "あ", "question": "Why?"}).text,
    ]

    for text in pages:
        for tag in re.findall(r"<button[^>]*>", text):
            # The chat's close icon (×) is the only control that is not an action button.
            assert 'class="button' in tag or "chat-close" in tag, tag
