from datetime import date

import pytest
from fastapi.testclient import TestClient

from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES
from ai_language_teacher.storage import connect, save_student
from ai_language_teacher.web.app import create_app

# The cookie that choosing "Ana" on the home page sets (spec 026).
ANA = {"profile": "Ana"}

APP_URL = "http://127.0.0.1:8000"


@pytest.fixture
def chatted():
    return []


@pytest.fixture
def client(tmp_path, chatted):
    conn = connect(tmp_path / "data.db")
    save_student(conn, Student("Ana"))
    conn.close()

    def fake_chat(messages):
        chatted.append(messages)
        return iter(["Hi."])

    app = create_app(tmp_path / "data.db", today=lambda: date(2026, 10, 19), chat=fake_chat)
    return TestClient(app, base_url=APP_URL, cookies=ANA)


def history(count):
    return [
        {"role": "user" if n % 2 == 0 else "assistant", "content": f"turn {n}"}
        for n in range(count)
    ]


@pytest.mark.parametrize("url", ["/study/hiragana", "/teacher"])
def test_both_chats_have_a_new_conversation_button_shown_by_the_script(client, url):
    text = client.get(url).text

    chat = text.split('<section id="chat"', 1)[1].split("</section>", 1)[0]
    assert '<button type="button" class="button chat-new" hidden>New conversation</button>' in chat


@pytest.mark.parametrize("url", ["/study/hiragana", "/teacher"])
def test_browser_keeps_the_4_exchanges_the_server_reads(client, url):
    assert 'data-history="8"' in client.get(url).text


def test_teacher_page_sends_only_the_last_4_student_messages(client, chatted):
    client.post("/teacher", json={"message": "Hi", "history": history(12)})

    earlier = chatted[0][1:-1]
    assert earlier == [
        {"role": "user", "content": f"<student_message>\nturn {n}\n</student_message>"}
        for n in (4, 6, 8, 10)
    ]


def test_teacher_page_prompt_lists_every_course_and_the_dashboard(client, chatted):
    client.post("/teacher", json={"message": "What words are we learning?", "history": []})

    prompt = chatted[0][-1]["content"]
    lesson = prompt[: prompt.index("</lesson>")]
    for skill, lessons in COURSES.items():
        items = sum(len(lesson.items) for lesson in lessons)
        assert f"- {skill}: {len(lessons)} lessons, {items} items" in lesson
    assert "Dashboard" in lesson
    assert "hiragana: 18 lessons, 105 items" in lesson  # today's content


def test_item_chat_prompt_has_no_course_overview(client, chatted):
    body = {"item": "あ", "message": "Hi", "history": []}
    client.post("/chat/hiragana", json=body)

    assert "lessons, 105 items" not in chatted[0][-1]["content"]
