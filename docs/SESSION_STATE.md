# Session State — read this first in a new session

Last updated: 2026-09-30. Repo is clean, all work committed and pushed
after spec 016.

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
    adr/                    # 0001 web stack, 0002 local LLM
  src/ai_language_teacher/
    main.py                 # stub: prints a banner, not a real CLI yet
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
      progression.py            # UNLOCK_THRESHOLD, lesson_mastery, unlocked_lessons (spec 014)
      review.py                 # Leitner spaced repetition: Card, record_answer, due_items, study_queue (spec 015)
    language/
      loader.py                 # load_lesson(path) — JSON -> Lesson
      japanese/
        hiragana.py               # HIRAGANA_LESSONS (18), HIRAGANA (105)
        katakana.py                # KATAKANA_LESSONS (19), KATAKANA (106)
        kanji.py                   # KANJI_LESSONS (6), KANJI (40) (spec 016)
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
  `0.0`), `knowledge: dict[str, Knowledge]` (one per skill, spec 008).
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
  `kun_readings`/`on_readings: list[str]` (empty for kana, spec 016).
- **Progression** (`core/progression.py`, spec 014): `UNLOCK_THRESHOLD = 0.8`;
  `lesson_mastery(student, skill, lesson)` = mean of that skill's scores for
  the lesson's items (unanswered = 0); `unlocked_lessons(student, skill,
  lessons)` returns the prefix of the course whose previous lesson is at
  or above the threshold. Course order is the prerequisite chain. Unlocks
  are computed live, not stored: a drop below 0.8 relocks the next lesson
  (user approved; revisit with persistence in spec 019 if too strict).
  Unknown skill raises `ValueError` (fixed in spec 015).
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
- **`load_lesson(path)`** (specs 004, 009): reads a JSON file shaped
  `{"title": ..., "items": [{"item", "answer", "explanation", "mnemonic",
  "example": {"word", "reading", "meaning"}, "culture_note"?}, ...]}`
  (list order = teaching order), auto-generates one `Question` per item
  (`"What is the romaji for {item}?"`, or the file's top-level `"question"`
  template such as `"What does {item} mean?"`; per-item `"prompt"` wins;
  optional `"kun"`/`"on"` reading lists, spec 016), returns a `Lesson`. Raises
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
- Nothing else yet (no vocab or grammar).

## Known issues / deliberate shortcuts (marked `# ponytail:` in code)

1. **Answer matching is exact after normalization** — no fuzzy/typo
   tolerance (explicitly out of scope in spec 003, may never be needed).

## Test status

492 tests passing, `ruff check` and `mypy` (strict) clean, as of spec 016.

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
tests/test_progression.py — lesson mastery and unlocking
tests/test_review.py      — Leitner boxes, due items, study queue
tests/test_kanji.py       — kanji content, readings, question template
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
  015 spaced repetition (Leitner) done; 016 N5 kanji (40) done. Next: 017
  starter vocabulary, 018 course gating (kanji/vocab only after katakana).
- **Phase C:** 019 SQLite persistence (stdlib `sqlite3`), 020+ web UI.
- **Phase D:** Ollama teacher. **Phase E:** v0.1.0 release.

## Immediate next step for the new session

1. Read this file plus `docs/ROADMAP.md` and the latest specs.
2. Write spec 017 (starter vocabulary, ~100 words) and get approval before
   tests. Agreed with the user on 2026-10-01: the quiz asks the English
   meaning (same format as kanji: `"question"` template, `also_accepted`
   synonyms); the word is shown as normally written (kanji/kana) with its
   kana reading taught. Include common N5 verbs (食べる, 行く...) here.
   Consider whether vocab examples are sentences rather than words.
3. Spec 018: hiragana -> katakana -> (kanji and vocabulary together).
   Agreed rule: kanji and vocab open when every katakana lesson has
   mastery >= 0.8 (reuse `lesson_mastery`). User accepted ~210 kana before
   any vocab.
4. Then Phase C: 019 SQLite persistence (must also save `cards`), 020+ web
   UI with FastAPI + Jinja2.
