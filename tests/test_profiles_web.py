from datetime import date
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from ai_language_teacher.core.review import Card
from ai_language_teacher.core.student import Student
from ai_language_teacher.storage import (
    connect,
    delete_student,
    list_students,
    load_student,
    save_student,
)
from ai_language_teacher.web.app import create_app

APP_URL = "http://127.0.0.1:8000"


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "data.db"


@pytest.fixture
def client(db_path):
    return TestClient(create_app(db_path), base_url=APP_URL)


def save(db_path, student):
    conn = connect(db_path)
    save_student(conn, student)
    conn.close()


def names(db_path):
    conn = connect(db_path)
    result = list_students(conn)
    conn.close()
    return result


def open_profile(client, name):
    return client.post("/students", data={"name": name}, follow_redirects=False)


def progressed(name):
    student = Student(name)
    student.knowledge["hiragana"].update("あ", 1.0)
    student.cards["hiragana"]["あ"] = Card(1, date(2026, 10, 14))
    return student


def test_choosing_a_profile_sets_the_cookie_and_opens_the_dashboard(client, db_path):
    save(db_path, Student("Ana"))

    response = open_profile(client, "Ana")

    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"
    cookie = response.headers["set-cookie"]
    assert cookie.startswith("profile=Ana;")
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie
    assert "<h1>Ana</h1>" in client.get("/dashboard").text


def test_creating_a_profile_sets_the_cookie_and_opens_the_dashboard(client, db_path):
    response = open_profile(client, "  Bia  ")

    assert response.headers["location"] == "/dashboard"
    assert names(db_path) == ["Bia"]
    assert "<h1>Bia</h1>" in client.get("/dashboard").text


def test_home_lists_each_profile_as_a_button_that_opens_it(client, db_path):
    save(db_path, Student("Ana"))

    text = client.get("/").text

    assert '<input type="hidden" name="name" value="Ana">' in text
    assert "/students/Ana" not in text


@pytest.mark.parametrize("name", ["Ana Maria", "さくら", "a/b", "x;y=z"])
def test_any_name_round_trips_through_the_cookie(client, db_path, name):
    response = open_profile(client, name)

    assert response.headers["set-cookie"].startswith(f"profile={quote(name, safe='')};")
    page = client.get("/dashboard")
    assert page.status_code == 200
    assert name in page.text


@pytest.mark.parametrize(
    "path", ["/dashboard", "/study/hiragana", "/practice/hiragana", "/practice/hiragana?lesson=1"]
)
def test_profile_pages_without_a_profile_redirect_home(client, path):
    response = client.get(path, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"


@pytest.mark.parametrize(
    ("path", "data"),
    [
        ("/study/hiragana", {"item": "あ", "answer": "a"}),
        ("/practice/hiragana", {"lesson": "1", "n": "0", "item": "あ", "answer": "a"}),
        ("/ask/hiragana", {"item": "あ", "question": "Why?"}),
    ],
)
def test_posts_without_a_profile_redirect_home(client, path, data):
    response = client.post(path, data=data, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_cookie_for_a_missing_profile_counts_as_no_profile(client):
    client.cookies.set("profile", "Ghost")

    response = client.get("/dashboard", follow_redirects=False)

    assert response.headers["location"] == "/"


@pytest.mark.parametrize("path", ["/dashboard", "/study/hiragana", "/practice/hiragana"])
def test_profile_pages_show_the_name_and_logout_in_the_header(client, path):
    open_profile(client, "Ana")

    text = client.get(path).text

    header = text[text.index("<header") : text.index("</header>")]
    assert "Ana" in header
    assert '<form method="post" action="/logout"' in header


def test_home_without_a_profile_has_no_logout(client):
    assert 'action="/logout"' not in client.get("/").text


def test_logout_clears_the_cookie_and_goes_home(client):
    open_profile(client, "Ana")

    response = client.post("/logout", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert response.headers["set-cookie"].startswith('profile="";')
    assert client.get("/dashboard", follow_redirects=False).headers["location"] == "/"


def test_foreign_origin_cannot_log_out(client):
    open_profile(client, "Ana")

    response = client.post("/logout", headers={"Origin": "http://evil.example"})

    assert response.status_code == 403
    assert client.get("/dashboard").status_code == 200


@pytest.mark.parametrize("path", ["/students/Ana", "/study/hiragana/Ana", "/practice/hiragana/Ana"])
def test_old_urls_with_the_name_are_gone(client, path):
    open_profile(client, "Ana")

    assert client.get(path).status_code == 404


def test_home_has_a_trash_button_per_profile(client, db_path):
    save(db_path, Student("Ana"))
    save(db_path, Student("a/b"))

    text = client.get("/").text

    assert 'href="/delete?name=Ana"' in text
    assert 'href="/delete?name=a%2Fb"' in text
    assert 'aria-label="Delete profile Ana"' in text


def test_confirmation_page_asks_and_deletes_nothing(client, db_path):
    save(db_path, Student("Ana"))

    response = client.get("/delete?name=Ana")

    assert response.status_code == 200
    assert "You are about to delete the profile Ana" in response.text
    assert "Are you sure?" in response.text
    assert '<form method="post" action="/delete"' in response.text
    assert '<input type="hidden" name="name" value="Ana">' in response.text
    assert "Yes, delete" in response.text
    assert '<a class="button" href="/">No</a>' in response.text
    assert names(db_path) == ["Ana"]


def test_confirmation_for_unknown_profile_is_404(client):
    assert client.get("/delete?name=Nobody").status_code == 404


def test_yes_deletes_the_profile_and_its_progress_only(client, db_path):
    save(db_path, progressed("Ana"))
    save(db_path, progressed("Bia"))

    response = client.post("/delete", data={"name": "Ana"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/"
    assert names(db_path) == ["Bia"]
    conn = connect(db_path)
    rows = [
        conn.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
        for table in ("skills", "knowledge", "cards")
    ]
    assert load_student(conn, "Bia") == progressed("Bia")
    conn.close()
    assert rows == [len(Student("Bia").skills), 1, 1]


def test_deleting_unknown_profile_is_404(client):
    assert client.post("/delete", data={"name": "Nobody"}).status_code == 404


def test_deleting_the_open_profile_logs_out(client):
    open_profile(client, "Ana")

    response = client.post("/delete", data={"name": "Ana"}, follow_redirects=False)

    assert response.headers["set-cookie"].startswith('profile="";')
    assert client.get("/dashboard", follow_redirects=False).headers["location"] == "/"


def test_deleting_another_profile_keeps_the_open_one(client, db_path):
    save(db_path, Student("Bia"))
    open_profile(client, "Ana")

    response = client.post("/delete", data={"name": "Bia"}, follow_redirects=False)

    assert "set-cookie" not in response.headers
    assert client.get("/dashboard").status_code == 200


def test_foreign_origin_cannot_delete(client, db_path):
    save(db_path, Student("Ana"))

    response = client.post(
        "/delete", data={"name": "Ana"}, headers={"Origin": "http://evil.example"}
    )

    assert response.status_code == 403
    assert names(db_path) == ["Ana"]


def test_delete_student_reports_whether_it_existed(db_path):
    save(db_path, Student("Ana"))
    conn = connect(db_path)

    assert delete_student(conn, "Ana") is True
    assert delete_student(conn, "Ana") is False
    assert list_students(conn) == []
    conn.close()
