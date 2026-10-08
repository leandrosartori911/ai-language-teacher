# 024: Ask the AI teacher about an item

## Problem
The teaching card is fixed text. A student who does not understand it,
or wants to know more (why 月 has two on readings, how to tell ぬ from
め), has nobody to ask. ADR 0002 plans a local LLM for this, and ADR 0004
picks the default model and the rule that it only explains curated
content.

## Behavior
- New module `ai_language_teacher/teacher.py` (stdlib only, no new
  dependency):
  - `teacher_prompt(item, answer, teaching, question) -> str`: the item's lesson
    content (answer, readings, explanation, mnemonic, example, culture
    note) followed by the student's question.
  - A system prompt telling the model: beginner teacher, English, at most
    5 short sentences, facts about language, history and culture only
    from the lesson content, say so plainly when the content does not
    answer, never write new Japanese sentences (only Japanese that
    appears in the content).
  - `ask_ollama(prompt) -> str`: calls the local Ollama API
    (`http://127.0.0.1:11434/api/generate`, not streamed, temperature 0)
    with the model from the environment variable `AI_TEACHER_MODEL`,
    default `qwen2.5:7b`. Raises `TeacherUnavailable` when Ollama cannot
    be reached, answers with an error (for example the model is not
    pulled), or times out (120 s).
- Web:
  - The teaching card (new item in Study, and after a wrong answer in
    Study or Practice) gets a form "Ask the teacher about <item>": one
    text box and a button, posting `item` and `question` to
    `/ask/<skill>/<name>`.
  - `POST /ask/<skill>/<name>`: shows the teaching card again, the
    student's question and the teacher's answer, with a link back to
    Study. Nothing is saved; progress never changes.
  - When the teacher is unavailable, the page still returns 200 with the
    teaching card and a message naming the model and how to start it
    (`ollama pull <model>`), so the student can keep studying.
  - Checks: unknown skill or student 404, closed skill 403 (as in
    Study); an item that is not in an unlocked lesson of the skill 404;
    a blank question or one longer than 500 characters 400, without
    calling the model.
  - `create_app` takes the ask function as a parameter (like `today`),
    so tests use a fake teacher and never need Ollama.
- README: an "AI teacher (optional)" section: install Ollama,
  `ollama pull qwen2.5:7b`, how to pick another model with
  `AI_TEACHER_MODEL`, and the tested-models table from ADR 0004.

## Acceptance Criteria
- [x] `teacher_prompt` includes the item, its explanation, mnemonic,
      example and the question; it includes the culture note and the
      readings only when the item has them.
- [x] The system prompt forbids facts outside the content and new
      Japanese sentences.
- [x] `ask_ollama` sends the prompt, system prompt, `stream: false` and
      the model from `AI_TEACHER_MODEL` (default `qwen2.5:7b`) and
      returns the response text (tested with a fake HTTP call).
- [x] `ask_ollama` raises `TeacherUnavailable` on connection error, on
      an HTTP error from Ollama and on timeout.
- [x] The teaching card on the Study page has the ask form for its item.
- [x] Posting a question shows the question, the teacher's answer and
      the teaching card, and saves nothing.
- [x] When the teacher raises `TeacherUnavailable`, the page returns 200
      with the teaching card and a message naming the model.
- [x] A blank question or one over 500 characters returns 400 and the
      teacher is not called.
- [x] An item outside the skill's unlocked lessons returns 404; unknown
      skill or student 404; closed skill 403.
- [x] An ask post with a foreign `Origin` returns 403 (spec 021
      middleware).

## Out of Scope
- Multi-turn conversation or chat history.
- Streaming the answer while it is generated (the page waits; on a CPU
  it can take tens of seconds).
- Choosing the model in the web interface.
- Generating new Japanese sentences or conversation practice (ADR 0004).
- The LLM grading answers or explaining wrong answers automatically.
- A remote Ollama host (`OLLAMA_HOST`).
