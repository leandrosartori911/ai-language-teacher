"""The flag design applied to the pages (spec 031)."""

import re
from datetime import date
from importlib.resources import files

import pytest
from fastapi.testclient import TestClient
from jinja2 import Environment, PackageLoader, select_autoescape
from markupsafe import escape

from ai_language_teacher.core.review import Card
from ai_language_teacher.core.student import Student
from ai_language_teacher.core.teaching import Example, Teaching
from ai_language_teacher.language.japanese.course import COURSES
from ai_language_teacher.storage import connect, save_student
from ai_language_teacher.web.app import create_app

ANA = {"profile": "Ana"}
TODAY = date(2026, 10, 17)
APP_URL = "http://127.0.0.1:8000"
CSS = (files("ai_language_teacher.web") / "static" / "style.css").read_text(encoding="utf-8")
PLAIN_CSS = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)  # without comments
TEMPLATES = Environment(
    loader=PackageLoader("ai_language_teacher.web", "templates"), autoescape=select_autoescape()
)
KA = COURSES["hiragana"][1].teaching["か"]


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


def teaching_card(item, teaching):
    return TEMPLATES.get_template("_teaching.html").render(
        item=item, teaching=teaching, skill="vocabulary"
    )


def ruby(word, reading):
    return f'<ruby><span lang="ja">{escape(word)}</span><rt>{escape(reading)}</rt></ruby>'


def rule(selector_pattern):
    # The bodies of every CSS rule whose selector matches the pattern.
    return [
        body
        for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", PLAIN_CSS)
        if re.search(selector_pattern, selector)
    ]


# Favicon


@pytest.mark.parametrize("url", ["/", "/dashboard", "/study/hiragana", "/practice/hiragana"])
def test_every_page_links_the_favicon(client, db_path, url):
    save(db_path, Student("Ana"))

    text = client.get(url).text

    assert '<link rel="icon" href="/static/favicon.svg" type="image/svg+xml">' in text


def test_favicon_is_served_as_svg(client):
    response = client.get("/static/favicon.svg")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")
    assert "<svg" in response.text


# The item in the sun disc


def test_teaching_card_shows_the_item_in_the_disc(client, db_path):
    save(db_path, Student("Ana"))

    text = client.get("/study/hiragana").text

    assert '<p class="item" lang="ja">あ</p>' in text


def test_study_quiz_shows_the_item_in_the_disc(client, db_path):
    save(db_path, Student("Ana"))

    text = client.get("/study/hiragana?step=quiz").text

    assert '<p class="item" lang="ja">あ</p>' in text


def test_practice_quiz_shows_the_item_in_the_disc(client, db_path):
    student = Student("Ana")
    student.cards["hiragana"]["あ"] = Card(1, TODAY)
    save(db_path, student)

    text = client.get("/practice/hiragana?lesson=1&n=0").text

    assert '<p class="item" lang="ja">あ</p>' in text


def test_long_word_gets_the_long_disc():
    teaching = Teaching("Hello.", "Say it.", Example("こんにちは。", "こんにちは。", "Hello."))

    assert '<p class="item long" lang="ja">こんにちは</p>' in teaching_card("こんにちは", teaching)


# Readings with <ruby>


def test_kana_example_puts_romaji_over_the_word():
    text = teaching_card("か", KA)

    assert ruby(KA.example.word, KA.example.reading) in text


def test_kanji_word_gets_its_reading_as_ruby():
    teaching = Teaching(
        "Teacher.", "Sen-sei.", Example("先生です。", "せんせいです。", "I am a teacher."),
        reading="せんせい",
    )

    text = teaching_card("先生", teaching)

    assert ruby("先生", "せんせい") in text
    assert ruby("先生です。", "せんせいです。") in text
    assert "Reading:" not in text


def test_kana_only_word_gets_no_ruby_and_no_reading_line():
    teaching = Teaching(
        "Hello.", "Say it.", Example("こんにちは。", "こんにちは。", "Hello."),
        reading="こんにちは",
    )

    text = teaching_card("こんにちは", teaching)

    assert '<p class="item long" lang="ja">こんにちは</p>' in text
    assert "Reading:" not in text


# "Did you know?"


def test_culture_note_is_in_a_did_you_know_box():
    text = teaching_card("か", KA)

    assert re.search(
        r'<aside class="culture">\s*<strong>Did you know\?</strong>\s*'
        + re.escape(str(escape(KA.culture_note))),
        text,
    )


# CSS rules


def test_feedback_animation_is_off_with_reduced_motion():
    reduced = re.search(
        r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{(.*?)\}\s*\}", CSS, re.S
    )
    assert reduced
    assert re.search(r"\.result[^{]*\{[^}]*animation:\s*none", reduced.group(1))
    assert any("animation:" in body for body in rule(r"\.result\.correct\b"))
    assert any("animation:" in body for body in rule(r"\.result\.wrong\b"))


def test_phone_navigation_is_one_row_that_scrolls():
    narrow = re.findall(r"@media\s*\(max-width:[^)]*\)\s*\{(.*?)\}\s*\}", CSS, re.S)
    navs = [nav for block in narrow for nav in re.findall(r"(?:^|\s)nav\s*\{([^}]*)\}", block)]
    assert any("overflow-x: auto" in nav and "flex-wrap: nowrap" in nav for nav in navs)


def test_inputs_and_buttons_use_the_tokens():
    assert any("var(--" in body for body in rule(r"(^|[\s,])input\b"))
    assert any("var(--" in body for body in rule(r"^\s*\.button\s*$"))


def test_every_token_used_is_defined():
    defined = set(re.findall(r"--([\w-]+):", CSS))
    used = set(re.findall(r"var\(--([\w-]+)", CSS))

    assert used <= defined, used - defined
