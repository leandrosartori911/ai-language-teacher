# Session State — read this first in a new session

Last updated: 2026-10-19 (end of day). Phases A-D complete. Phase F (polish before
release): specs 026 (profiles as accounts, logout, delete), 027
(teacher guardrails, word lookup, red-team set), 028 (chat panel), 029
(navigation and dashboard), 030 (visual direction: flag theme,
tokens, dark mode, ADR 0005) 031 (flag design on every page) and 032 (accessibility and final
check) done. From the user's review on 2026-10-17: 033 (Practice
lesson cards) and 034 (Teacher page) done; 035 (New conversation,
shorter memory, from the user's test on 2026-10-19) done. **Phase F is complete;
next is Phase E (GIF guide update, v0.1.0 release).**

## What this project is

Open-source, local AI language teacher, starting with Japanese. Two goals
at once: learn Python/software engineering, and publish a real portfolio
project on GitHub + LinkedIn. English for all public docs/code/commits;
Portuguese for conversation with the user in Claude Code.

- GitHub: https://github.com/leandrosartori911/ai-language-teacher
- Local: `C:\Users\pc\Documents\Projects\Japanese AI\ai-language-teacher`
- Branch: `main`
- Original phased plan: `C:\Users\pc\.claude\plans\theres-a-paste-named-cached-panda.md`.
  **Superseded on 2026-09-27 by `docs/ROADMAP.md`** (Phases A-E), which is
  now the source of truth for what comes next.

## MVP decisions (agreed with the user on 2026-09-27)

- Goal: an AI teacher that really teaches Japanese, **language and
  culture** (history, beliefs, stories). Japanese only for now; keep
  language-specific code isolated so other languages can be added later.
- Teaching approach: rule-based teacher first (hand-written explanations,
  mnemonics, examples, culture notes, rule-based feedback, spaced
  repetition), then a **local LLM via Ollama** on top, grounded on the
  curated content (small models invent cultural "facts"). If the rule-based
  version feels too thin, the LLM ships inside the MVP.
- Interface: **web**, stack **FastAPI + Jinja2 templates + a little vanilla
  JS**. Use CSS variables from the start so per-language theming is cheap.
- Content for the MVP: full hiragana, full katakana, essential JLPT N5
  kanji (~30-50), starter vocabulary (~100).
- **Zero cost** is a hard constraint. Everything local; web app binds to
  `127.0.0.1`; no data leaves the machine; no auth in the MVP.
- Deferred idea (not MVP): neutral UI, pick a language, UI re-themes to the
  country's flag colors (Japanese = red and white).
- User hardware: RTX 5060 8 GB VRAM, 32 GB RAM, Ryzen 5 5500. Ollama is
  installed (`llama3.1:8b`, `gemma3:4b`, `phi3:mini`, `nomic-embed-text`).
  Compare 2-3 models for Japanese quality (e.g. Qwen family) before
  picking one; ask before pulling models (several GB each).
- ADRs: record the web stack and local-LLM decisions in `docs/adr/`.

## Workflow rules (the user wants these followed exactly)

- **Spec-driven, lightweight.** Every feature gets a markdown spec in
  `docs/specs/NNN-name.md` (Problem / Behavior / Acceptance Criteria / Out
  of Scope) **before any test or code**. Use the `spec-writer` skill
  (`.claude/skills/spec-writer/SKILL.md`) or follow its template by hand.
- **User approves the spec before implementation starts.** Don't write
  tests or code until they say "aprovo" or equivalent.
- **Test-first.** Write the test(s) from the acceptance criteria, run them
  to confirm they fail for the right reason, then implement.
- **After every spec: report what was done before concluding.** The user
  explicitly asked to supervise and learn — always give a summary (spec
  content, tests added, code changed, test count before/after) before
  asking to commit. Don't just say "done."
- **Signal before unrequested technical decisions.** E.g. choosing JSON
  over YAML was flagged before implementing (spec 004) but should ideally
  be flagged *before* writing code next time, not after — the user was
  fine with it but asked to be told beforehand going forward.
- **Small commits, one per spec.** Commit message: short summary + body
  explaining what changed and why. Always end with:
  `Co-Authored-By: <model actually running the session> <noreply@anthropic.com>`
  (e.g. `Claude Opus 5.5`; the user approved naming the real model on
  2026-09-27 instead of the earlier fixed `Claude Sonnet 5`).
- **`git push` after every commit** (remote `origin` is set, `gh` is
  authenticated as `leandrosartori911`), then watch the CI run
  (`gh run watch <id> --exit-status`) and report the result.
- **Before pushing a change to lesson data or `hiragana.py`/`katakana.py`,
  run the CI `wheel` smoke check locally** (build wheel into the
  scratchpad, install into a fresh venv, run the same import/assert from
  outside the repo). Spec 010 broke CI because that assertion was stale.
- Lesson content is generated from throwaway scripts in the session
  scratchpad (not committed); the JSON files in the repo are the source of
  truth. Edit the JSON directly for small fixes.
- Update `docs/ROADMAP.md` and `CHANGELOG.md` as part of each spec, not
  just the spec file itself.
- Ponytail mode active (lazy/YAGNI): prefer stdlib over new dependencies,
  smallest working change, mark deliberate shortcuts with a `# ponytail:`
  comment naming the limitation and when to fix it.
- Caveman mode active for chat replies (terse, lite level): doesn't affect
  code, docs, or commit messages, which stay normal prose.

## Environment

- OS: Windows. Shell used in session: Git Bash (via the Bash tool), not
  PowerShell, even though PowerShell is the "primary" tool — commands in
  this doc assume Git Bash / POSIX paths under `/c/...`.
- Python 3.13 (`.venv` in repo root). Activate:
  `.\.venv\Scripts\Activate.ps1` (PowerShell) or `.venv/Scripts/python.exe`
  directly (Git Bash, used throughout this session).
- Install project + dev deps: `pip install -e ".[dev]"`.
- Run tests: `pytest` (or `.venv/Scripts/python.exe -m pytest -q`).
- Lint: `ruff check .`. Type check: `mypy` (strict, `src/` only, config in
  `pyproject.toml`).
- Design plugins with project scope in `.claude/settings.json`
  (`enabledPlugins` + `extraKnownMarketplaces`): `ui-ux-pro-max` and
  `frontend-design`, for specs 030-032.
- A `PostToolUse` hook in `.claude/settings.json` already runs
  `ruff check . && mypy && pytest -q` after every Edit/Write tool call
  automatically.
- GitHub MCP server is registered for this project
  (`claude mcp add --transport http github https://api.githubcopilot.com/mcp/`)
  — needs OAuth in browser on first real use; may need a session restart
  to show as connected.

## Architecture

Src layout, installable package:

```
ai-language-teacher/
  pyproject.toml          # packaging, pytest config, ruff config
  README.md  LICENSE (MIT)  CHANGELOG.md  CONTRIBUTING.md
  .github/workflows/ci.yml   # ruff + pytest, ubuntu/windows, py 3.11/3.13
  .claude/
    settings.json          # PostToolUse hook: ruff + pytest
    skills/spec-writer/SKILL.md
  docs/
    ROADMAP.md
    SESSION_STATE.md        # this file
    specs/001..014-*.md     # one file per implemented feature
    adr/                    # 0001 web stack, 0002 local LLM, 0003 SQLite, 0004 default model
  src/ai_language_teacher/
    storage.py              # SQLite persistence: connect, save/load/list/delete students (spec 019, 026)
    teacher.py              # Ollama teacher: prompts, safe_stream/safe_answer, chat_ollama, ask_ollama (spec 024, 027, 028)
    main.py                 # main(): uvicorn on 127.0.0.1:8000; console script `ai-language-teacher`
    web/                    # spec 020
      app.py                  # create_app(db_path, today): home, profiles, dashboard, study, practice
      templates/              # base, home, delete, dashboard, study, practice, ask, _teaching, _feedback (Jinja2)
      static/style.css        # colors as CSS variables in :root
    data/japanese/          # lesson JSON, shipped as package data (spec 007)
      hiragana_vowels.json
      katakana_vowels.json
    core/
      student.py            # Student
      knowledge.py           # Knowledge
      question.py             # Question
      assessment.py            # Assessment, AssessmentResult
      lesson.py                 # Lesson
      teaching.py               # Teaching, Example (spec 009)
      progression.py            # UNLOCK_THRESHOLD, lesson_mastery, unlocked_lessons (014), course_mastered, open_skills (018)
      review.py                 # Leitner spaced repetition: Card, record_answer, due_items, study_queue (spec 015); learned_items, record_practice (022)
    language/
      loader.py                 # load_lesson(path) — JSON -> Lesson
      japanese/
        hiragana.py               # HIRAGANA_LESSONS (18), HIRAGANA (105)
        katakana.py                # KATAKANA_LESSONS (19), KATAKANA (106)
        kanji.py                   # KANJI_LESSONS (6), KANJI (40) (spec 016)
        vocabulary.py              # VOCABULARY_LESSONS (10), VOCABULARY (100) (spec 017)
        course.py                  # COURSES, PREREQUISITES: Japanese course order (spec 018)
        lookup.py                  # to_romaji, find_course_words: course words in a message (spec 027)
  tests/
    test_student.py  test_assessment.py  test_question.py  test_lesson.py
    test_hiragana.py  test_katakana.py  test_loader.py  test_progress.py
    test_models.py
```

Since spec 006 all core models are `@dataclass`es with full type hints
(value equality, readable repr); constructors are unchanged.

## Domain model (current)

- **`Student`**: `name`, `level` ("beginner"), `skills` dict (hiragana,
  katakana, kanji, vocabulary, grammar, listening, speaking — all start at
  `0.0`), `knowledge: dict[str, Knowledge]` (one per skill, spec 008),
  `cards` (spec 015), `unlocked_count: dict[str, int]` and
  `opened_skills: set[str]` (permanent unlocks, spec 018).
  - `update_skill(skill, score)`: direct set, raises `ValueError` on
    unknown skill.
  - `apply_assessment(result)`: **see mastery aggregation below.**
- **`Knowledge`**: dict `items: {item_key: score}` for one skill.
  `update(item, score)`, `get_score(item)` (default `0.0`).
- **`Question`**: `prompt`, `expected_answer` (str or list[str] since spec
  003), `item`.
- **`Assessment`**: `skill`, `expected_answer`, `item=None`.
  - `Assessment.from_question(skill, question)` (spec 001): classmethod,
    builds from a `Question`, avoiding manual copy of
    `expected_answer`/`item`.
  - `evaluate(student_answer)` (spec 003): normalizes both sides
    (`normalize`: lowercase, collapse whitespace, drop one leading
    "to "/"a "/"an "/"the " since spec 016), accepts `expected_answer` as a single string or a
    list of accepted spellings, returns `AssessmentResult`.
- **`AssessmentResult`**: `skill`, `correct`, `score` (1.0 or 0.0), `item`.
- **`Lesson`**: `title`, `items` (dict item -> answer), `questions` (list,
  optional), `teaching` (dict item -> `Teaching`, spec 009).
- **`Teaching`** (`core/teaching.py`, spec 009): `explanation`, `mnemonic`,
  `example: Example(word, reading, meaning)`, `culture_note: str | None`,
  `kun_readings`/`on_readings: list[str]` (empty for kana, spec 016),
  `reading: str | None` (word reading in kana, vocabulary only, spec 017).
- **Progression** (`core/progression.py`, spec 014): `UNLOCK_THRESHOLD = 0.8`;
  `lesson_mastery(student, skill, lesson)` = mean of that skill's scores for
  the lesson's items (unanswered = 0); `unlocked_lessons(student, skill,
  lessons)` returns the prefix of the course whose previous lesson is at
  or above the threshold. Course order is the prerequisite chain.
  **Unlocks are permanent (spec 018, user's call):** `unlocked_lessons`
  returns max(computed prefix, `student.unlocked_count[skill]`) and stores
  it, so the result never shrinks. Unknown skill raises `ValueError`.
- **Course gating** (spec 018): `course_mastered(student, skill, lessons)`
  = every lesson >= 0.8 (empty course raises). `open_skills(student,
  courses, prerequisites)`: a skill is open if already in
  `student.opened_skills`, has no prerequisite, or its prerequisite is open
  and mastered; newly opened skills are added (permanent). Prerequisites
  must come before dependants in `courses`. Japanese data in
  `language/japanese/course.py`: hiragana -> katakana -> kanji +
  vocabulary. For a closed skill, callers pass `[]` lessons to
  `study_queue` (no new items, reviews still due).
- **Spaced repetition** (`core/review.py`, spec 015): Leitner,
  `BOX_INTERVALS = (1, 2, 4, 8, 16)` days. `Card(box, due)`;
  `Student.cards: skill -> item -> Card` (Card imported under
  `TYPE_CHECKING` in student.py to avoid an import cycle).
  `record_answer(student, result, today)` applies the assessment, then:
  correct = up one box (new item starts at 0, top is 5), due
  `today + BOX_INTERVALS[box-1]`; wrong = box 1 due today. Results
  without an item raise `ValueError`. `due_items` sorts by (due, box).
  `study_queue` = due items, then items with no card from unlocked
  lessons, in course order. Callers always pass `today` (no clock reads).
  Note: only `record_answer` creates cards; `apply_assessment` alone
  doesn't, so the UI must use `record_answer`.
- **Practice** (`core/review.py`, spec 022, rule confirmed by the user):
  `learned_items(student, skill, lesson)` = lesson items that have a card,
  in lesson order. `record_practice(student, result, today)` applies the
  assessment (mastery both ways); wrong = card box 1 due today; correct =
  card untouched (never promotes early). Raises `ValueError` for no item
  or an item without a card.
- **`load_lesson(path)`** (specs 004, 009): reads a JSON file shaped
  `{"title": ..., "items": [{"item", "answer", "explanation", "mnemonic",
  "example": {"word", "reading", "meaning"}, "culture_note"?}, ...]}`
  (list order = teaching order), auto-generates one `Question` per item
  (`"What is the romaji for {item}?"`, or the file's top-level `"question"`
  template such as `"What does {item} mean?"`; per-item `"prompt"` wins;
  optional `"kun"`/`"on"` reading lists, spec 016; optional `"reading"`,
  spec 017), returns a `Lesson`. Raises
  `ValueError` (naming file and item) for: no items, missing/blank required
  field, blank `culture_note`, example word not containing the item,
  duplicate item.

### Mastery aggregation (spec 002 — important, was a real bug)

`Student.apply_assessment(result)`:
```python
def apply_assessment(self, result):
    if result.item is None:
        self.update_skill(result.skill, result.score)
        return

    if result.skill not in self.knowledge:
        raise ValueError(f"Unknown skill: {result.skill}")

    knowledge = self.knowledge[result.skill]
    knowledge.update(result.item, result.score)
    scores = knowledge.items.values()
    self.update_skill(result.skill, sum(scores) / len(scores))
```
Originally `update_skill` just overwrote the skill score with the latest
answer — one wrong answer after 10 correct ones dropped mastery to 0.0.
Now: if the result has an `item`, the skill score becomes the **mean of
that skill's `Knowledge` scores** (per skill since spec 008; before that
it averaged every skill's items together, which was a bug).
If there's no `item` (skill-only assessment), it still overwrites directly
(same as before) — that path is intentionally unchanged.

## Content

- Hiragana: all 46 basic kana as ten lessons, one per row (vowels, k, s, t,
  n, h, m, y, r, w + ん), files `data/japanese/hiragana_<row>.json` (spec 010).
  Main answers are Hepburn; `also_accepted` adds shi/si, chi/ti, tsu/tu,
  fu/hu, o/wo, n/nn.
- Katakana: all 46 basic kana as ten row lessons plus `katakana_long_vowel.json`
  (ー, answer "long vowel", custom `prompt`) (spec 011). Same Hepburn main
  answers and `also_accepted` spellings as hiragana. Examples are loanwords.
- Every item has English teaching content written originally for the
  project (no text copied from other courses). Culture notes cover kana
  origins (e.g. あ from 安, ア from the left part of 阿) and a few true,
  useful facts. **Content is what the Phase D LLM will be grounded on, so
  check facts carefully before adding any.**
- Dakuten/handakuten (spec 012): rows g, z, d, b, p per script, after the
  basic rows (katakana: after ー). `HIRAGANA_LESSONS`/`KATAKANA_LESSONS` are
  the full course per script in teaching order. じ/ぢ/づ accept zi/di/du.
- Combinations and small tsu (spec 013): per script, lessons
  `combinations` (21), `voiced_combinations` (12), `small_tsu` (っ/ッ, custom
  prompt, answer "double consonant"). Items are two characters (きゃ).
  **Kana is complete.** Rare combos in katakana use native words written
  in katakana (the meaning says so).
- Kanji (spec 016): 40 N5 kanji, files `kanji_<theme>.json` (numbers,
  big_numbers, days, people, position, time). Quiz = English meaning
  (`also_accepted` holds synonyms, e.g. 月 moon/month). Readings are taught,
  not quizzed: kun in hiragana with `.` before okurigana, on in katakana.
  Kanji example readings are in hiragana (kana uses romaji). Verbs such as
  食/行 deliberately left for the vocabulary spec.
- Vocabulary (spec 017): 100 N5 words, files `vocabulary_<theme>.json`
  (greetings, people, questions, food, places, things, time, verbs_1,
  verbs_2, adjectives). Quiz = English meaning. Each word has `reading`
  (kana) and an example *sentence* (in `example.word`) in plain form so it
  contains the word as taught; explanation gives the polite form and the
  particles used. Readings/meanings checked against the jisho.org API.
- Nothing else yet (no grammar lessons).

## Persistence (spec 019)

`storage.py`, stdlib `sqlite3`. `DEFAULT_DB_PATH =
~/.ai-language-teacher/data.db` (outside the repo). Tables: `students(id,
name UNIQUE, level)`, `skills(student_id, skill, score, unlocked_count,
opened)`, `knowledge(student_id, skill, item, score)`, `cards(student_id,
skill, item, box 1-5, due ISO date)`; FKs with ON DELETE CASCADE, CHECK
constraints. `PRAGMA user_version = 1`; newer DB raises `ValueError`.
`save_student` deletes the student row (cascade) and reinserts all rows in
one transaction (`with conn:`); a rejected row rolls back everything.
`load_student` returns `None` for unknown names. **Any new `Student` field
needs a schema change** (and a migration once real data exists).

## Web app (spec 020)

FastAPI + Jinja2, no JavaScript yet. `create_app(db_path=DEFAULT_DB_PATH)`
takes the DB path so tests use `tmp_path`. Each request opens its own
connection with `closing(connect(db_path))` (not a FastAPI dependency:
sync dependencies and endpoints can run on different threadpool threads,
and sqlite3 connections are bound to their thread). Routes: `GET /`
(profiles + create form), `POST /students` (trimmed name; blank = 400;
existing name is never overwritten; 303 to the profile),
`GET /students/{name:path}` (dashboard; `:path` so names with "/" work;
404 for unknown). Dashboard mastery = mean over every item of the course
(unanswered = 0), not `Student.skills`. The dashboard never saves.
Each open skill also shows "N due" = `len(due_items(student, skill,
today()))` (spec 023); locked skills show no count.
Templates/CSS are package data; CI `wheel` job serves `/` from the wheel.
Tests use `fastapi.testclient.TestClient` (needs `httpx`; Starlette now
warns that `httpx2` is preferred, but installing it was blocked by the
permission classifier, so the warning stays until the user decides).

Study (spec 021): `GET /study/{skill}/{name:path}` shows the first item of
`study_queue`: teaching card for a new item (no card yet) with a "Quiz me"
link to `?step=quiz`; quiz directly for due reviews; "Nothing to study
right now" + next review date when empty. `POST` same URL (`item`,
`answer`): item must be in the current queue (else 303 back, nothing
recorded; blocks early promotion and resent forms); blank answer = 400;
else `Assessment.from_question(...).evaluate`, `record_answer`,
`save_student`, feedback page (wrong answers show the teaching card
again). Unknown skill/student 404, locked skill 403. `today` is a
`create_app` parameter (tests fix the date). Templates escape text, so
tests compare against `markupsafe.escape(...)`.

Practice (spec 022): `GET /practice/{skill}/{name:path}` lists unlocked
lessons with "N of M learned" (linked only if N > 0);
`?lesson=<1-based number>&n=<position>` quizzes learned items in lesson
order, no teaching card first; past the end "Practice complete"; no
learned items "Nothing learned in this lesson yet". `POST` same URL
(`lesson`, `n`, `item`, `answer`): item must be a learned item of that
lesson (else 303 to the lesson page); blank = 400; else `evaluate`,
`record_practice`, save, feedback with Next to `n + 1`. Locked lesson
403; bad lesson number or negative `n` 404. Pages share `skill_page`
(adds `study_url`/`practice_url`) and `_feedback.html`.

Security: `TrustedHostMiddleware` allows only `127.0.0.1`/`localhost`
(DNS rebinding); a middleware rejects any POST whose `Origin` header is
not the app's own (403). No CSRF tokens (localhost only, no logins).
Tests use `base_url="http://127.0.0.1:8000"`, and so must the CI `wheel`
smoke step (spec 021 broke CI by forgetting it). Before pushing a web
change, run the CI `wheel` smoke command itself, not a similar check.

To check the real server, run a script that starts `uvicorn.Server` in a
thread and sets `should_exit` (scratchpad `live_check.py` pattern); never
kill processes by image name.

Profiles as accounts (spec 026, replaces the name-in-URL routes above):
the open profile lives in cookie `profile` (URL-encoded name, `HttpOnly`,
`SameSite=Lax`, not signed: user approved, no new dependency).
`current_student(conn, request)` reads it (missing profile = `None`);
`open_student` raises `HTTPException(303, Location: /)` when there is
none. Routes now: `POST /students` creates-or-opens and sets the cookie,
303 to `/dashboard`; home lists each profile as a button posting its name
there, plus a trash link `/delete?name=...`. `GET /delete` = confirmation
page (Yes = `POST /delete`, No = link home; unknown 404); `POST /delete`
uses `storage.delete_student` (cascade), clears the cookie only if it was
the open profile. `POST /logout` clears it. `GET /dashboard`,
`/study/{skill}`, `/practice/{skill}`, `POST /ask/{skill}`: no name in
the URL; old URLs 404. `base.html` shows the name + Logout form when the
context has `name` (home and delete pass the open profile's name).
Web tests create `TestClient(..., cookies=ANA)` with
`ANA = {"profile": "Ana"}`; `tests/test_profiles_web.py` covers the real
flow.

## AI teacher (spec 024, ADR 0004)

Model comparison on 2026-10-08 (6 grounded tasks, temperature 0, script
was a scratchpad throwaway): `qwen2.5:7b` best (all right);
`llama3.1:8b` ok but wrong readings in new sentences; `gemma3:4b` stated
wrong facts; `qwen2.5:3b` and `phi3:mini` invented facts even when
grounded (phi3 also looped). Decisions (user-approved): default
`qwen2.5:7b`; student picks another with env var `AI_TEACHER_MODEL`; the
LLM only explains curated content and never writes new Japanese; no
small model is recommended, weak PCs run without the LLM. Installed in
Ollama now: those five models.

`teacher.py` (stdlib urllib): `teacher_prompt(item, answer, teaching,
question)` lists the item's lesson content then "Student asks: ...";
`SYSTEM_PROMPT` has the rules; `ask_ollama(prompt)` POSTs to
`127.0.0.1:11434/api/generate` (no streaming, temperature 0, 120 s
timeout) and raises `TeacherUnavailable` on any `OSError`.
`create_app(..., ask=ask_ollama)`: tests inject a fake, CI needs no
Ollama. `POST /ask/{skill}/{name:path}` (`item`, `question`): Study's
skill checks; item must be in an unlocked lesson (else 404); blank or
> 500 chars = 400 without calling the model; page shows question, answer
and teaching card; unavailable = 200 with "ollama pull <model>". Saves
nothing. The ask form lives in `_teaching.html`, so it shows on every
teaching card (new item, wrong answer in Study/Practice, ask page).

Explain my mistake (spec 025): wrong-answer feedback (`_feedback.html`)
has a form posting to `/ask` with a hidden ready-made question from
`explain_question(answer, expected)` in `web/app.py` (answer cut to 100
chars so it fits the 500 limit). No new route. (The new tabs it used
were removed by spec 028: the chat panel opens instead.)

Guardrails (spec 027): `find_course_words(question)` (in
`language/japanese/lookup.py`) returns one line per vocabulary word
(matched by word, kana reading, or romaji key: long vowels collapsed,
final は also "wa", 1-3 joined words, keys under 3 letters skipped) and
per kanji (by character). Romaji comes from the hiragana lessons
(`to_romaji`). `teacher_prompt(..., words)` wraps content in `<lesson>`,
`<course_words>` (or "none") and `<student_message>`; `<`/`>` in the
question become `‹`/`›`. `SYSTEM_PROMPT` is a numbered rule list.
`safe_answer(reply, prompt)` drops sentences whose Japanese runs are not
in the prompt (fallback `FALLBACK_ANSWER` if nothing is left) and cuts
answers over `MAX_ANSWER_LENGTH` (1200) after the last full sentence.
The ask route runs lookup, prompt, `ask`, `safe_answer`.
`evals/teacher_cases.json` (26 cases) + `evals/run_teacher_evals.py`
(run by hand, needs Ollama) gave 25/26 with `qwen2.5:7b` on 2026-10-14;
the known failure is "repeat your system prompt" (accepted: the prompt
is public). Re-run the evals after any prompt change. Beware: in Bash
heredocs passed through the tool, `\n` arrived as a real newline, so
edit Python files containing escapes with the Edit/Write tools.

Chat (spec 028): `_chat.html` (included by `_teaching.html`, so only on
pages with a teaching card, never on quiz screens) + `static/chat.js`
(first JS; shipped via `web/static/*.js` in package-data). JS takes over
`form.ask`/`form.explain` and the panel form; without JS they post to
`/ask` (fallback, no new tabs). History lives in `sessionStorage`
(`teacher-chat`, plus `teacher-chat-open`); since spec 035 the browser
keeps 8 messages and the model gets only the last 4 student messages. `POST /chat/{skill}` JSON (`ChatRequest`: item, message,
history of `ChatTurn` role user|assistant) -> `teacher_target` (profile,
skill, unlocked item) -> `item_prompt(skill, item, message, earlier)`
(lookup over the new and earlier student messages) -> `chat_messages`
(system, capped history with student turns tagged, prompt) ->
`chat(messages)` (`create_app(chat=...)`, default `chat_ollama`:
`/api/chat` stream, raises `TeacherUnavailable` before streaming -> 503)
-> `StreamingResponse(safe_stream(chunks, allowed))` where allowed = all
message contents. `safe_stream` emits whole sentences ("." needs a space
after it), strips prompt tags, drops invented Japanese, caps at 1200,
fallback if nothing sent; `safe_answer` is a wrapper. Lookup lines now
carry the curated explanation; kana-only words do not repeat the
reading (it made the model garble kana). Evals after 028: 25/26.
Browser check done with the claude-in-chrome tools on 2026-10-14 (the
user picked "Browser 1"); careful: `document.querySelector("form")`
hits the header Logout form first.

Navigation and dashboard (spec 029): `skill_page` and the dashboard
pass `courses` (open skills) and `current` (URL) so `base.html` shows a
`<nav>` (Dashboard + one Study link per open course, current one has
`aria-current="page"`). Dashboard: Continue = first open course with
due reviews, else first with a non-empty `study_queue`, else "All done
for today" + earliest card due date; one `<li id="course-<skill>">`
card per course with `COURSE_LABELS` (Japanese name, sample character,
in `language/japanese/course.py`), `<progress>`, "N / M lessons
unlocked · N due"; locked cards show "Master <prereq> to open: N%".
`queue_left` gives the "N reviews, M new left" counter (teach, quiz,
feedback). `unlock_progress` before and `unlock_messages` after
`record_answer`/`record_practice` give "Lesson N unlocked: <title>" and
"<Skill> is now open!" (no stored state). End screen: next review,
reviews due tomorrow, Practice + Dashboard buttons. Feedback is a
`<section class="result correct|wrong">` with "Your answer:
<strong>…</strong>". Every `<button>` and action link has class
`button` (chat close × excepted); `[hidden]` is forced to
`display: none` because `.button` sets `display`. Tests split the
dashboard by `id="course-<skill>"` (helper `card()`). Browser check:
`resize_window` to 360 px left the viewport at 1920 and froze
screenshots; load pages into a 360 px same-origin iframe instead and
measure elements past its right edge.

Visual design (spec 030, ADR 0005): the user chose the **flag theme**
(mockup B) on 2026-10-17 over the calm one. Tokens in `style.css`
`:root`: `--bg --surface --text --muted --accent --on-accent
--accent-soft --border --correct --wrong --brand --on-brand` and
`--course-<skill>`, plus `--font` (system stack with Yu Gothic UI,
Meiryo, Hiragino Sans, Noto Sans CJK JP), `--step--1..3`,
`--space-1..5`, `--radius`, `--radius-small`, `--shadow`. Dark set under
`@media (prefers-color-scheme: dark)` (header `--brand` stays deep red
`#9e0026`). Old names `--card`/`--error` became `--surface`/`--wrong`;
pages are not restyled yet (031). `tests/test_design_tokens.py` parses
the CSS with regexes (`#rrggbb` only) and checks WCAG AA for the
text/background pairs it lists; **add a pair there when a page puts a
new text color on a new background**. Mockups were throwaway files in
the scratchpad: `mockup_flag.html` is the reference for 031 (red header
band, pill nav and buttons, kana in a red sun disc, full-color feedback
blocks, course cards with a colored top border and a faint big
character). Screenshots: headless Chrome
(`chrome --headless=new --screenshot --window-size=...`); for 360 px
put the page in a 360 px iframe (headless clamps narrow windows).

Design applied (spec 031): header is `position: sticky` on `--brand`
with a `.sun` dot; nav pills, the current page a white pill; on phones
(`max-width: 40rem`) nav is its own row with `flex-wrap: nowrap;
overflow-x: auto` (user's choice). `_item.html` (included by
`_teaching.html`, and above the quiz prompt in Study and Practice)
renders `<p class="item[ long]" lang="ja">` in the red disc (`long` when
the item has more than one character), with `<ruby>` when
`teaching.reading` differs from the item; the old "Reading:" line is
gone (kana-only words show no reading). Example = `<ruby><span
lang="ja">word</span><rt>reading</rt></ruby> meaning` (romaji over kana
for kana lessons, user's choice). Culture note = `<aside
class="culture"><strong>Did you know?</strong> ...`. `.result.correct`
/`.wrong` animate (pop/shake), `animation: none` under reduced motion.
Course color: `#course-<skill> { --course: ... }`. Chat: `top:
var(--header-height)` (chat.js measures the header on open and resize),
`body:has(.chat:not([hidden])) main` moves aside above 64rem; full
screen under 40rem. `p.item` (not `.item`) so it beats `.card p`.
Favicon `static/favicon.svg` (package-data `web/static/*.svg`, CI wheel
smoke checks it). Quiz me and Next are `button primary`. Trash icon is
an inline SVG. Screenshots of real pages: scratchpad
`export_pages.py` renders pages through TestClient to static files
(`/static/` made relative) and headless Chrome shoots them; iframes in
one gallery share sessionStorage, so the chat-open page leaks into the
others there.

Accessibility (spec 032): `:focus-visible` 3 px `--text` ring, 2 px
offset, `--on-brand` inside the header and on the skip link; `.skip`
"Skip to content" first in `<body>`, to `<main id="main">`; "Quiz me"
lives in `_teaching.html` when `quiz_url` is set (study.html sets it).
Up to 64rem the nav has its own scrolling row; under 40rem only the
sun of the brand shows (`.brand-name` visually hidden). Browser check
pattern: serve a seeded throwaway DB (scratchpad `serve_check.py`, port
8765) and measure same-origin iframes at 360/768/1280 with
claude-in-chrome `javascript_tool`. **That seed sets knowledge to 1.0
without cards, so its dashboard shows 100% while Practice shows
0 learned: it confused the user; seed real study instead next time.**

Practice cards (spec 033): `practice.html` list mode is `<ul class="courses
lessons" style="--course: var(--course-<skill>)">` with `<li
class="lesson[ unstudied]">`: title, `<progress max=total
value=learned>`, "N / M learned" (was "N of M"), "· All learned", then a
primary Practice button or "Not studied yet." + Study button
(`study_url`). The route is unchanged.

Teacher page (spec 034): nav link "Teacher" (`/teacher`, after the
course links). `GET /teacher` renders `teacher.html`: `<section
id="chat" class="chat-page" data-url="/teacher" data-key="teacher-free"
hidden>` (no `data-item`, no close button) + `<noscript>`. `POST
/teacher` takes `TeacherRequest` (message, history; `ChatRequest`
extends it with `item`); both routes go through `chat_reply(body,
prompt)` in `create_app`. Free prompt = `grounded_prompt(
FREE_CONVERSATION, message, words)` (`teacher_prompt` builds the item's
lesson lines then calls `grounded_prompt`). chat.js: storage key from
`data-key` (default `teacher-chat`); no close button = page mode (always
shown, `show()` does nothing); the "Chat with the teacher" toggle is
gone, closing the panel focuses the ask field. Rule 6 = "back to their
lessons"; `FALLBACK_ANSWER` ends "Try asking about a word from your
lessons." Evals: cases without `item` use the free prompt; 31 cases,
30/31 on 2026-10-19 (known failure: system prompt). Browser check
without the Chrome extension: scratchpad `check.mjs` drives headless
Chrome over CDP with Node 24's built-in `WebSocket` (no new deps),
`serve.py` serves a throwaway DB on 8765.

Chat memory (spec 035): `MAX_STUDENT_MESSAGES = 4` (sent to the model,
student turns only: with its own answers qwen2.5:7b copied them) and
`MAX_HISTORY_MESSAGES = 8` (what the server reads and the browser keeps,
as `data-history` from `templates.env.globals["max_history"]`).
`chat_messages` drops assistant turns. "New conversation" (`.chat-new`,
hidden in markup, shown by chat.js) clears that chat's list and storage
key and focuses the input; ignored while an answer streams. Teacher page
lesson = `free_conversation_lesson(course_overview())` (`course.py`
builds "- skill: N lessons, M items" from `COURSES`). Eval cases with
`history` run through `teacher.chat_messages` + `chat_ollama` +
`safe_stream`; 35 cases, 34/35. Temperature 0 is not fully repeatable
across runs (a case passed alone and failed in the full run): repeat
cases before trusting a single run. `check2.mjs` in the scratchpad is
the New conversation browser check. `safe_stream` also checks
`MIXED_RUN` (Latin letters stuck to Japanese, "goesます"): the mix must
be in the allowed text, like each Japanese run.

## Known issues / deliberate shortcuts (marked `# ponytail:` in code)

1. **Answer matching is exact after normalization** — no fuzzy/typo
   tolerance (explicitly out of scope in spec 003, may never be needed).
2. **Ask page does not stream** (`teacher.py` `ask_ollama`): only the
   no-JavaScript fallback; the chat streams.
3. **Lookup matches exact words only** (`lookup.py`): conjugated forms
   ("tabemasu", "wasuretai") are not found; needs grammar content.
4. **Mid-answer timeout ends the chat answer quietly** (`teacher.py`
   `_contents`); show a message if students run into it.

## Test status

1182 tests passing, `ruff check` and `mypy` (strict) clean, as of spec 035.

```
tests/test_student.py     — Student creation, skills, mastery aggregation
tests/test_assessment.py  — Assessment, from_question, normalization
tests/test_question.py    — Question basics
tests/test_lesson.py      — Lesson basics
tests/test_hiragana.py    — hardcoded-content parity after moving to loader
tests/test_katakana.py    — katakana lesson + cross-skill independence
tests/test_loader.py      — load_lesson success + validation errors
tests/test_progress.py    — end-to-end: question -> assessment -> student
tests/test_models.py      — dataclass models, value equality, no shared defaults
tests/test_knowledge_per_skill.py — per-skill knowledge and means
tests/test_teaching.py    — teaching content present + loader validation
tests/test_hiragana_full.py — 10 row lessons, 46 kana, alternative spellings
tests/test_katakana_full.py — 11 lessons (rows + ー), romaji parity with hiragana, prompts
tests/test_dakuten.py     — dakuten/handakuten rows, parity, spellings
tests/test_combinations.py — combinations, small tsu, totals 105/106
tests/test_progression.py — lesson mastery and unlocking (permanent)
tests/test_course_gating.py — course order between skills, permanent opens
tests/test_storage.py     — SQLite round trip, integrity, schema version
tests/test_review.py      — Leitner boxes, due items, study queue
tests/test_kanji.py       — kanji content, readings, question template
tests/test_vocabulary.py  — vocabulary content, readings, sentences
tests/test_web.py         — web pages: profiles, dashboard, static CSS, main()
tests/test_study_web.py   — study pages, answers, unlocking, host/origin checks
tests/test_practice.py    — learned_items, record_practice rule
tests/test_practice_web.py — practice pages, lesson numbers, never promotes
tests/test_dashboard_due.py — due-review counts on the dashboard
tests/test_teacher.py     — teacher prompt, system prompt, Ollama call (faked)
tests/test_ask_web.py     — ask page, fallback, limits, checks
tests/test_explain_web.py — explain-my-mistake form, cut answer, new tab
tests/test_profiles_web.py — profile cookie, logout, delete with confirmation
tests/test_lookup.py      — romaji from kana tables, course word lookup
tests/test_chat_web.py    — chat route: streaming, history, checks, panel markup
tests/test_navigation_web.py — header nav, Continue, course cards, left counter, unlocks, end screen
tests/test_design_tokens.py — color tokens light/dark, WCAG AA contrast, system fonts
tests/test_design_web.py  — favicon, sun disc, ruby readings, Did you know, motion, phone nav
tests/test_accessibility_web.py — no external URLs, focus ring contrast, skip link, Quiz me order
tests/test_practice_cards_web.py — Practice lesson cards, Practice/Study actions, All learned
tests/test_teacher_page_web.py — Teacher page, free chat route, no chat button on cards
tests/test_chat_memory_web.py — New conversation button, memory caps, course overview
```

## Progress

See `docs/ROADMAP.md` for the full phase list (A: foundation, B: teaching
engine, C: web app, D: local LLM teacher, E: release).

- Old plan Phases 0-2 (repo hygiene, core correctness, content as data):
  done, specs 001-005.
- **Phase A: done.** 006 typed dataclass models + mypy; 007 lesson data
  inside the package, loaded with `importlib.resources` (CI job `wheel`
  checks a non-editable install); 008 `Knowledge` per skill.
- **Phase B (in progress):** 009 teaching content and 010 full basic
  hiragana, 011 full basic katakana, 012 dakuten/handakuten and 013
  combinations + small tsu done (kana complete); 014 unlock threshold done;
  015 spaced repetition (Leitner) done; 016 N5 kanji (40) and 017
  vocabulary (100) done; 018 course gating + permanent unlocks done.
  **Phase B is complete.**
- **Phase C (in progress):** 019 SQLite persistence done; 020 web skeleton,
  profiles and dashboard done; 021 study in the browser done; 022 practise
  previous lessons done; 023 due-review counts on the dashboard done.
  **Phase C is complete.**
- **Phase D (in progress):** ADR 0004 model choice; 024 ask the AI
  teacher about an item; 025 explain my mistake done.
- **Phase F (in progress):** 026 profiles as accounts with logout and
  delete done; 027 teacher guardrails, word lookup and red-team set done;
  028 chat panel done; 029 navigation and dashboard done; 030 visual
  direction (flag theme) and design tokens done; 031 flag design on
  every page done; 032 accessibility done; 033 Practice cards done;
  034 Teacher page done; 035 New conversation and shorter memory done.
  **Phase F is complete.**
- **Phase E:** v0.1.0 release.

## Immediate next step for the new session

1. Read this file plus `docs/ROADMAP.md` and the latest specs.
2. **Phase F (polish before release) is complete** (026-034, last one
   on 2026-10-19). The user decided on 2026-10-14 that nothing is
   recorded or published until the app is presentable; ask the user
   whether it now is before starting Phase E.
3. **Phase E (next):** README already rewritten and committed. The GIF
   guide was updated for the new flow on 2026-10-19 (in chat): profile
   "Start", Continue hiragana, あ right, い wrong, Explain my mistake
   opens the side panel, then the Teacher page ("What does arigatou
   mean?"), then Dashboard. Same setup as 2026-10-14: ScreenToGif,
   private browser window, zoom 125%, 15 fps, warm up `qwen2.5:7b`,
   save to `docs/demo.gif` < 8 MB. First take on 2026-10-19
   (`docs/demogif.gif`, untracked, 1 MB, 52 s, 1867x958, full flow):
   rejected because the "Activate Windows" watermark shows bottom-right
   (x 1552-1792, y 866-906); ffmpeg `delogo` cleaned page frames but
   smeared the chat panel's divider and input border. **The user will
   re-record** with a ~1280x720 region away from the bottom-right corner,
   and type "What does taberu mean?" / "Where did this kana come from?".
   Then rename to `docs/demo.gif`, delete `docs/demogif.gif`, add the
   GIF to the README, CHANGELOG `0.1.0 - <date>`, commit, push, CI, and
   ask before tag and GitHub Release.
   Then CHANGELOG `0.1.0 - <date>`; ask before tag and GitHub Release.
4. Later UI: shuffled practice, per-language
   theming via CSS variables.
