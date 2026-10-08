import io
import json
from urllib.error import HTTPError, URLError

import pytest

from ai_language_teacher import teacher
from ai_language_teacher.core.teaching import Example, Teaching
from ai_language_teacher.teacher import (
    DEFAULT_MODEL,
    SYSTEM_PROMPT,
    TeacherUnavailable,
    ask_ollama,
    teacher_prompt,
)

NU = Teaching(
    explanation="ぬ is 'nu', like 'noo' but short.",
    mnemonic="A tangle of noodles with a chopstick through it.",
    example=Example("いぬ", "inu", "dog"),
)
TSUKI = Teaching(
    explanation="月 means moon and month.",
    mnemonic="A crescent moon drawn as a tall box.",
    example=Example("月曜日", "げつようび", "Monday"),
    culture_note="The months are simply numbered.",
    kun_readings=["つき"],
    on_readings=["ゲツ", "ガツ"],
)


def test_prompt_has_the_lesson_content_and_the_question():
    prompt = teacher_prompt("ぬ", "nu", NU, "How do I tell it from め?")

    for text in ["ぬ", "nu", NU.explanation, NU.mnemonic, "いぬ", "inu", "dog"]:
        assert text in prompt
    assert prompt.rstrip().endswith("How do I tell it from め?")
    assert "culture" not in prompt.lower()
    assert "kun" not in prompt.lower()


def test_prompt_includes_culture_note_and_readings_when_present():
    prompt = teacher_prompt("月", "moon", TSUKI, "Why two readings?")

    assert TSUKI.culture_note in prompt
    assert "つき" in prompt
    assert "ゲツ, ガツ" in prompt


def test_vocabulary_reading_is_included():
    water = Teaching("Water.", "Mizu.", Example("水を飲む。", "みずを のむ。", "I drink water."))
    water.reading = "みず"

    assert "みず" in teacher_prompt("水", "water", water, "Hot water?")


def test_system_prompt_forbids_outside_facts_and_new_japanese():
    text = SYSTEM_PROMPT.lower()

    assert "only" in text and "lesson content" in text
    assert "new japanese sentences" in text


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


@pytest.fixture
def sent(monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        return FakeResponse(json.dumps({"response": "  Nu is nu.  "}).encode())

    monkeypatch.setattr(teacher, "urlopen", fake_urlopen)
    return calls


def test_ask_ollama_sends_prompt_and_returns_the_answer(sent, monkeypatch):
    monkeypatch.delenv("AI_TEACHER_MODEL", raising=False)

    assert ask_ollama("What is ぬ?") == "Nu is nu."

    request, timeout = sent[0]
    body = json.loads(request.data)
    assert request.full_url == "http://127.0.0.1:11434/api/generate"
    assert body["model"] == DEFAULT_MODEL == "qwen2.5:7b"
    assert body["prompt"] == "What is ぬ?"
    assert body["system"] == SYSTEM_PROMPT
    assert body["stream"] is False
    assert body["options"]["temperature"] == 0
    assert timeout == 120


def test_model_comes_from_the_environment(sent, monkeypatch):
    monkeypatch.setenv("AI_TEACHER_MODEL", "llama3.1:8b")

    ask_ollama("Hi")

    assert json.loads(sent[0][0].data)["model"] == "llama3.1:8b"


@pytest.mark.parametrize(
    "error",
    [
        URLError(ConnectionRefusedError()),
        HTTPError("http://127.0.0.1:11434/api/generate", 404, "model not found", {}, None),
        TimeoutError(),
    ],
)
def test_ask_ollama_raises_teacher_unavailable(monkeypatch, error):
    def failing_urlopen(request, timeout):
        raise error

    monkeypatch.setattr(teacher, "urlopen", failing_urlopen)

    with pytest.raises(TeacherUnavailable):
        ask_ollama("Hi")
