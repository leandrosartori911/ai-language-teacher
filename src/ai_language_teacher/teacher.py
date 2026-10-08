"""The optional AI teacher: a local LLM via Ollama (ADR 0002, ADR 0004)."""

import json
import os
from urllib.request import Request, urlopen

from ai_language_teacher.core.teaching import Teaching

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_MODEL = "qwen2.5:7b"
TIMEOUT_SECONDS = 120

SYSTEM_PROMPT = (
    "You are a friendly Japanese teacher for absolute beginners. Answer in "
    "English, in at most 5 short sentences. Use ONLY the lesson content "
    "given in the message for facts about Japanese language, history or "
    "culture. If the lesson content does not answer the question, say so "
    "plainly instead of guessing. Never write new Japanese sentences: only "
    "use Japanese that appears in the lesson content."
)


class TeacherUnavailable(Exception):
    """Ollama is not running, the model is missing, or it took too long."""


def current_model() -> str:
    return os.environ.get("AI_TEACHER_MODEL", DEFAULT_MODEL)


def teacher_prompt(item: str, answer: str, teaching: Teaching, question: str) -> str:
    example = teaching.example
    lines = [
        f"Lesson content for {item}:",
        f"- answer: {answer}",
        f"- explanation: {teaching.explanation}",
        f"- mnemonic: {teaching.mnemonic}",
        f"- example: {example.word} ({example.reading}) = {example.meaning}",
    ]
    if teaching.reading:
        lines.append(f"- reading: {teaching.reading}")
    if teaching.kun_readings:
        lines.append(f"- kun readings: {', '.join(teaching.kun_readings)}")
    if teaching.on_readings:
        lines.append(f"- on readings: {', '.join(teaching.on_readings)}")
    if teaching.culture_note:
        lines.append(f"- culture note: {teaching.culture_note}")
    return "\n".join(lines) + f"\n\nStudent asks: {question}"


def ask_ollama(prompt: str) -> str:
    body = {
        "model": current_model(),
        "system": SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0},
    }
    request = Request(
        OLLAMA_URL, json.dumps(body).encode(), {"Content-Type": "application/json"}
    )
    # ponytail: no streaming, the page waits for the whole answer (slow on a
    # CPU); stream it if students find the wait too long.
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            answer: str = json.load(response)["response"]
    except OSError as error:  # URLError, HTTPError and timeouts are OSErrors
        raise TeacherUnavailable(str(error)) from error
    return answer.strip()
