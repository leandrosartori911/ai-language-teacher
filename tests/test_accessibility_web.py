"""Keyboard, focus and offline checks before the release (spec 032)."""

import re
from datetime import date
from importlib.resources import files

import pytest
from fastapi.testclient import TestClient

from ai_language_teacher.core.student import Student
from ai_language_teacher.storage import connect, save_student
from ai_language_teacher.web.app import create_app
from test_design_tokens import contrast, theme

ANA = {"profile": "Ana"}
TODAY = date(2026, 10, 17)
APP_URL = "http://127.0.0.1:8000"
WEB = files("ai_language_teacher.web")
CSS = (WEB / "static" / "style.css").read_text(encoding="utf-8")
PLAIN_CSS = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)

# URLs that are not requests to another host.
ALLOWED_URLS = ("http://127.0.0.1", "http://localhost", "http://www.w3.org/2000/svg")

# Where the focus ring is drawn: (ring color, background).
FOCUS_PAIRS = [
    ("text", "bg"), ("text", "surface"), ("text", "accent-soft"),
    ("on-brand", "brand"),
]


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "data.db"


@pytest.fixture
def client(db_path):
    conn = connect(db_path)
    save_student(conn, Student("Ana"))
    conn.close()
    app = create_app(db_path, today=lambda: TODAY, ask=lambda prompt: "Hi")
    return TestClient(app, base_url=APP_URL, cookies=ANA)


def web_files():
    for folder in ("templates", "static"):
        for path in (WEB / folder).iterdir():
            if path.name.endswith((".html", ".css", ".js", ".svg")):
                yield path


# Offline


def test_web_files_exist():
    names = {path.name for path in web_files()}
    assert {"base.html", "style.css", "chat.js", "favicon.svg"} <= names


@pytest.mark.parametrize("path", list(web_files()), ids=lambda path: path.name)
def test_no_external_url(path):
    urls = re.findall(r"https?://[^\s\"'<>)]+", path.read_text(encoding="utf-8"))

    assert [url for url in urls if not url.startswith(ALLOWED_URLS)] == []


# Focus


def test_focus_ring_is_visible_on_pages_and_in_the_header():
    rules = dict(re.findall(r"([^{}]+)\{([^{}]*)\}", PLAIN_CSS))
    page = [body for selector, body in rules.items() if selector.strip() == ":focus-visible"]
    header = [b for selector, b in rules.items() if selector.strip() == "header :focus-visible"]

    assert page and "outline: 3px solid var(--text)" in page[0]
    assert "outline-offset: 2px" in page[0]
    assert header and "var(--on-brand)" in header[0]


@pytest.mark.parametrize("name", ["light", "dark"])
@pytest.mark.parametrize(("ring", "bg"), FOCUS_PAIRS)
def test_focus_ring_reaches_three_to_one(name, ring, bg):
    colors = theme(name)
    assert contrast(colors[ring], colors[bg]) >= 3


# Skip link


@pytest.mark.parametrize("url", ["/", "/dashboard", "/study/hiragana", "/practice/hiragana"])
def test_every_page_starts_with_a_skip_link(client, url):
    text = client.get(url).text
    body = text.split("<body>", 1)[1]

    assert body.lstrip().startswith('<a class="skip" href="#main">Skip to content</a>')
    assert '<main id="main">' in text


def test_skip_link_is_hidden_until_focused():
    rules = dict(re.findall(r"([^{}]+)\{([^{}]*)\}", PLAIN_CSS))

    assert any(s.strip() == ".skip" and "translateY(-" in b for s, b in rules.items())
    assert any(s.strip() == ".skip:focus" and "transform: none" in b for s, b in rules.items())


# Teaching card order


def test_quiz_me_comes_before_the_ask_form(client):
    text = client.get("/study/hiragana").text

    assert text.index(">Quiz me</a>") < text.index('class="ask"')
    assert text.count(">Quiz me</a>") == 1
