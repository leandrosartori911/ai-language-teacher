import pytest
from fastapi.testclient import TestClient

from ai_language_teacher import main as main_module
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES
from ai_language_teacher.storage import connect, list_students, load_student, save_student
from ai_language_teacher.web.app import create_app

# The cookie that choosing "Ana" on the home page sets (spec 026).
ANA = {"profile": "Ana"}


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "data.db"


@pytest.fixture
def client(db_path):
    # The app only accepts 127.0.0.1 and localhost as hosts (spec 021).
    return TestClient(create_app(db_path), base_url="http://127.0.0.1:8000", cookies=ANA)


def save(db_path, student):
    conn = connect(db_path)
    save_student(conn, student)
    conn.close()


def load(db_path, name):
    conn = connect(db_path)
    student = load_student(conn, name)
    conn.close()
    return student


def test_home_with_empty_database_shows_only_the_form(client):
    response = client.get("/")

    assert response.status_code == 200
    assert '<form method="post" action="/students"' in response.text
    assert 'name="name" value=' not in response.text


def test_home_lists_saved_profiles_in_order(client, db_path):
    save(db_path, Student("Bia"))
    save(db_path, Student("Ana"))

    text = client.get("/").text

    ana = text.index('name="name" value="Ana"')
    assert ana < text.index('name="name" value="Bia"')


def test_creating_a_new_profile_saves_it_and_redirects(client, db_path):
    response = client.post("/students", data={"name": "  Ana  "}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"
    assert load(db_path, "Ana") == Student("Ana")


def test_creating_an_existing_profile_keeps_its_progress(client, db_path):
    student = Student("Ana")
    student.knowledge["hiragana"].update("あ", 1.0)
    save(db_path, student)

    response = client.post("/students", data={"name": "Ana"}, follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"
    assert load(db_path, "Ana") == student


@pytest.mark.parametrize("name", ["", "   "])
def test_blank_name_is_rejected_and_nothing_is_saved(client, db_path, name):
    response = client.post("/students", data={"name": name})

    assert response.status_code == 400
    assert "Please enter a name" in response.text
    conn = connect(db_path)
    assert list_students(conn) == []
    conn.close()


def card(text, skill):
    # The dashboard card of one course (spec 029).
    return text.split(f'id="course-{skill}"', 1)[1].split("</li>", 1)[0]


def test_new_student_dashboard_opens_only_hiragana(client, db_path):
    save(db_path, Student("Ana"))

    text = client.get("/dashboard").text

    assert '<progress max="100" value="0">' in card(text, "hiragana")
    assert f"1 / {len(COURSES['hiragana'])} lessons unlocked" in card(text, "hiragana")
    assert "Master hiragana to open: 0%" in card(text, "katakana")
    assert "Master katakana to open: 0%" in card(text, "kanji")
    assert "Master katakana to open: 0%" in card(text, "vocabulary")
    assert "grammar" not in text


def test_mastering_hiragana_opens_katakana(client, db_path):
    student = Student("Ana")
    for lesson in COURSES["hiragana"]:
        for item in lesson.items:
            student.knowledge["hiragana"].update(item, 1.0)
    save(db_path, student)

    text = client.get("/dashboard").text

    hiragana_total = len(COURSES["hiragana"])
    assert "100% mastered" in card(text, "hiragana")
    assert f"{hiragana_total} / {hiragana_total} lessons" in card(text, "hiragana")
    assert f"1 / {len(COURSES['katakana'])} lessons" in card(text, "katakana")
    assert "Master katakana to open: 0%" in card(text, "kanji")


def test_mastery_counts_every_item_of_the_course(client, db_path):
    student = Student("Ana")
    student.knowledge["hiragana"].update("あ", 1.0)
    save(db_path, student)

    text = client.get("/dashboard").text

    assert "1% mastered" in card(text, "hiragana")


def test_dashboard_does_not_save(client, db_path):
    student = Student("Ana")
    for lesson in COURSES["hiragana"]:
        for item in lesson.items:
            student.knowledge["hiragana"].update(item, 1.0)
    save(db_path, student)

    client.get("/dashboard")

    assert load(db_path, "Ana") == student


def test_stylesheet_is_served_with_css_variables(client):
    response = client.get("/static/style.css")

    assert response.status_code == 200
    assert ":root" in response.text
    assert "var(--" in response.text


def test_main_runs_uvicorn_on_localhost_only(monkeypatch):
    calls = []
    monkeypatch.setattr(main_module.uvicorn, "run", lambda app, **kwargs: calls.append(kwargs))

    main_module.main()

    assert calls == [{"host": "127.0.0.1", "port": 8000}]
