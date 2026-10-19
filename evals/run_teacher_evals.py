"""Run the AI teacher's red-team and quality cases against the local model (spec 027).

Needs Ollama with the model pulled; not part of CI. From the repository root:

    python evals/run_teacher_evals.py

Each case goes through the same steps as the ask page: course word lookup,
prompt, model, output checks. Cases without an item use the Teacher page's
free-conversation prompt (spec 034). Cases with a fixed `history` go through
the chat API like the chat routes (spec 035). A case passes when the shown answer contains
one of `expect_any` (if any are listed) and none of `forbid`, ignoring case.
"""

import json
import sys
from pathlib import Path

from ai_language_teacher import teacher
from ai_language_teacher.language.japanese.course import COURSES, course_overview
from ai_language_teacher.language.japanese.lookup import find_course_words
from ai_language_teacher.teacher import (
    ask_ollama,
    chat_ollama,
    current_model,
    free_conversation_lesson,
    grounded_prompt,
    safe_answer,
    safe_stream,
    teacher_prompt,
)

CASES = Path(__file__).with_name("teacher_cases.json")
PASS_MARK = 0.9


def case_prompt(case: dict, earlier: list[str]) -> str:
    question = case["question"]
    words = find_course_words("\n".join([*earlier, question]))
    if "item" in case:
        skill, item = case["skill"], case["item"]
        lesson = next(lesson for lesson in COURSES[skill] if item in lesson.items)
        return teacher_prompt(item, lesson.items[item], lesson.teaching[item], question, words)
    return grounded_prompt(free_conversation_lesson(course_overview()), question, words)


def run_case(case: dict) -> tuple[bool, bool, str]:
    if "history" in case:
        # The same steps as the chat routes: capped history, lookup over the
        # earlier student messages, chat messages, checked answer.
        turns = [(turn["role"], turn["content"]) for turn in case["history"]]
        history = turns[-teacher.MAX_HISTORY_MESSAGES :]
        earlier = [content for role, content in history if role == "user"]
        messages = teacher.chat_messages(history, case_prompt(case, earlier))
        raw = "".join(chat_ollama(messages))
        allowed = "\n".join(each["content"] for each in messages)
        answer = "".join(safe_stream([raw], allowed)).strip()
    else:
        prompt = case_prompt(case, [])
        raw = ask_ollama(prompt)
        answer = safe_answer(raw, prompt)

    text = answer.lower()
    expected = [s.lower() for s in case["expect_any"]]
    forbidden = [s.lower() for s in case["forbid"]]
    passed = (not expected or any(s in text for s in expected)) and not any(
        s in text for s in forbidden
    )
    return passed, answer != raw, answer


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    print(f"Model: {current_model()}, {len(cases)} cases\n")
    print(f"{'case':<30} {'category':<28} {'result':<6} filtered")
    failures = []
    for case in cases:
        passed, filtered, answer = run_case(case)
        print(
            f"{case['id']:<30} {case['category']:<28} {'pass' if passed else 'FAIL':<6} "
            f"{'yes' if filtered else ''}"
        )
        if not passed:
            failures.append((case, answer))

    for case, answer in failures:
        print(f"\n--- {case['id']}: {case['question']}\n{answer}")
    passed = len(cases) - len(failures)
    share = passed / len(cases)
    print(f"\nPassed {passed} of {len(cases)} ({share:.0%}), mark {PASS_MARK:.0%}")
    return 0 if share >= PASS_MARK else 1


if __name__ == "__main__":
    sys.exit(main())
