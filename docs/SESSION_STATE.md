# Session State — read this first in a new session

Last updated: 2026-09-27. Repo is clean, all work committed and pushed.

## What this project is

Open-source, local AI language teacher, starting with Japanese. Two goals
at once: learn Python/software engineering, and publish a real portfolio
project on GitHub + LinkedIn. English for all public docs/code/commits;
Portuguese for conversation with the user in Claude Code.

- GitHub: https://github.com/leandrosartori911/ai-language-teacher
- Local: `C:\Users\pc\Documents\Projects\Japanese AI\ai-language-teacher`
- Branch: `main`
- Full phased plan: `C:\Users\pc\.claude\plans\theres-a-paste-named-cached-panda.md`
  (Phase 0 through Phase 5 + Later). This file tracks progress against it.

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
  `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`
- **`git push` after every commit** (remote `origin` is set, `gh` is
  authenticated as `leandrosartori911`).
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
- Lint: `ruff check .`.
- A `PostToolUse` hook in `.claude/settings.json` already runs
  `ruff check . && pytest -q` after every Edit/Write tool call
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
    specs/001..005-*.md     # one file per implemented feature
    adr/                    # empty so far, reserved for architecture decisions
  data/japanese/
    hiragana_vowels.json
    katakana_vowels.json
  src/ai_language_teacher/
    main.py                 # stub: prints a banner, not a real CLI yet
    core/
      student.py            # Student
      knowledge.py           # Knowledge
      question.py             # Question
      assessment.py            # Assessment, AssessmentResult
      lesson.py                 # Lesson
    language/
      loader.py                 # load_lesson(path) — JSON -> Lesson
      japanese/
        hiragana.py               # loads hiragana_vowels.json via loader
        katakana.py                # loads katakana_vowels.json via loader
  tests/
    test_student.py  test_assessment.py  test_question.py  test_lesson.py
    test_hiragana.py  test_katakana.py  test_loader.py  test_progress.py
```

## Domain model (current)

- **`Student`**: `name`, `level` ("beginner"), `skills` dict (hiragana,
  katakana, kanji, vocabulary, grammar, listening, speaking — all start at
  `0.0`), `knowledge: Knowledge`.
  - `update_skill(skill, score)`: direct set, raises `ValueError` on
    unknown skill.
  - `apply_assessment(result)`: **see mastery aggregation below.**
- **`Knowledge`**: flat dict `items: {item_key: score}`.
  `update(item, score)`, `get_score(item)` (default `0.0`).
  ⚠️ Not namespaced by skill — see Known Issues.
- **`Question`**: `prompt`, `expected_answer` (str or list[str] since spec
  003), `item`.
- **`Assessment`**: `skill`, `expected_answer`, `item=None`.
  - `Assessment.from_question(skill, question)` (spec 001): classmethod,
    builds from a `Question`, avoiding manual copy of
    `expected_answer`/`item`.
  - `evaluate(student_answer)` (spec 003): normalizes both sides
    (`.strip().lower()`), accepts `expected_answer` as a single string or a
    list of accepted spellings, returns `AssessmentResult`.
- **`AssessmentResult`**: `skill`, `correct`, `score` (1.0 or 0.0), `item`.
- **`Lesson`**: `title`, `items` (dict), `questions` (list, optional).
- **`load_lesson(path)`** (spec 004): reads a JSON file shaped
  `{"title": ..., "items": {item: romaji, ...}}`, auto-generates one
  `Question` per item (`"What is the romaji for {item}?"`), returns a
  `Lesson`. Raises `ValueError` if `items` is empty or any answer is blank.

### Mastery aggregation (spec 002 — important, was a real bug)

`Student.apply_assessment(result)`:
```python
def apply_assessment(self, result):
    if result.item is None:
        self.update_skill(result.skill, result.score)
        return

    self.knowledge.update(result.item, result.score)
    scores = self.knowledge.items.values()
    self.update_skill(result.skill, sum(scores) / len(scores))
```
Originally `update_skill` just overwrote the skill score with the latest
answer — one wrong answer after 10 correct ones dropped mastery to 0.0.
Now: if the result has an `item`, the skill score becomes the **mean of
all `Knowledge` scores** (not just that skill's items — see Known Issues).
If there's no `item` (skill-only assessment), it still overwrites directly
(same as before) — that path is intentionally unchanged.

## Content

- Hiragana vowels: あ→a, い→i, う→u, え→e, お→o (`data/japanese/hiragana_vowels.json`).
- Katakana vowels: ア→a, イ→i, ウ→u, エ→e, オ→o (`data/japanese/katakana_vowels.json`).
- Nothing else yet (no consonant rows, no kanji, no vocab, no grammar).

## Known issues / deliberate shortcuts (marked `# ponytail:` in code)

1. **`Knowledge` is one flat map, not namespaced by skill.**
   `Student.apply_assessment` averages *all* `Knowledge` scores into
   whichever skill the current result names. Fine today because a given
   `Student` in the tests only ever has items from one skill loaded. **If a
   real student studies both hiragana and katakana, their scores will mix
   into both `skills["hiragana"]` and `skills["katakana"]` incorrectly.**
   This is flagged in specs 002 and 005 as deliberately out of scope — fix
   before building the CLI/persistence layer (Phase 4) or it will produce
   visibly wrong progress numbers.
2. **Data file path resolution is dev-only.**
   `hiragana.py` / `katakana.py` do
   `Path(__file__).resolve().parents[4] / "data" / "japanese" / "*.json"`
   to climb from `src/ai_language_teacher/language/japanese/` up to the
   repo root's `data/` folder. This only works for an editable/dev install
   (`pip install -e .`). A real built wheel would not include `data/`
   unless it's moved under the package or declared as `package_data`.
   Needs fixing before any real PyPI release.
3. **Answer matching is exact after normalization** — no fuzzy/typo
   tolerance (explicitly out of scope in spec 003, may never be needed).

## Test status

34 tests passing, `ruff check` clean, as of commit `ca47e04`.

```
tests/test_student.py     — Student creation, skills, mastery aggregation
tests/test_assessment.py  — Assessment, from_question, normalization
tests/test_question.py    — Question basics
tests/test_lesson.py      — Lesson basics
tests/test_hiragana.py    — hardcoded-content parity after moving to loader
tests/test_katakana.py    — katakana lesson + cross-skill independence
tests/test_loader.py      — load_lesson success + validation errors
tests/test_progress.py    — end-to-end: question -> assessment -> student
```

## Git log (specs completed so far, newest first)

```
ca47e04 Add Katakana vowels lesson (spec 005)
190afeb Load lesson content from JSON data files (spec 004)
8425449 Normalize answers and allow multiple accepted spellings (spec 003)
d57e98b Fix skill mastery to average knowledge items, do not overwrite (spec 002)
423c998 Add Assessment.from_question (spec 001)
5b019ee Restructure to src layout and add packaging, docs, CI
ad6cb0e Add hiragana lesson and knowledge tracking   (pre-restructure)
c6978da Add student model and tests                  (pre-restructure)
7b8a416 Initial project structure                    (pre-restructure)
```

## Plan progress vs. `theres-a-paste-named-cached-panda.md`

- **Phase 0 (repo hygiene): done.** src layout, pyproject.toml, README,
  LICENSE, CI, docs scaffolding, `.claude/` hook + skill, GitHub repo
  created and pushed.
- **Phase 1 (core correctness, specs 001-003): done.**
  `Assessment.from_question`, mastery aggregation fix, answer
  normalization + multi-answer support.
- **Phase 2 (content as data, specs 004-005): done.** JSON loader with
  validation, hiragana migrated to it, katakana vowels added.
- **Phase 3 (progression engine, specs 006-007): NOT STARTED.** This is
  the next work. Two specs planned:
  - **006 — unlock threshold**: next lesson requires mastery ≥ some
    threshold (plan suggested 0.8) on the prior lesson's items before it
    unlocks. Last message before this session ended proposed: threshold
    `0.8`, and a simple `unlocked_after: Lesson | None` field on `Lesson`
    checked against mean mastery of the prior lesson's items — **no lesson
    dependency graph, just a single optional predecessor link.** This was
    proposed to the user but **not yet confirmed** — confirm this approach
    first in the new session before writing the spec.
  - **007 — spaced repetition**: simple algorithm (Leitner or SM-2) to
    pick what to review next. This is explicitly the "adaptive" learning
    piece and the main ML/algorithms learning opportunity in the project;
    no external library needed.
  - **Note:** before designing 006/007, the Known Issue #1 above
    (`Knowledge` not namespaced by skill) likely needs addressing, since
    unlock/review logic will need per-skill mastery to be correct once
    more than one skill's content exists in the same student. Consider
    whether it becomes spec 006 and renumber the rest, or is folded into
    006's design — flag this to the user before deciding.
- **Phase 4 (CLI + persistence, specs 008-009): not started.** CLI
  (`learn`/`review`/`progress` commands, Typer or argparse — not yet
  decided), SQLite persistence via stdlib `sqlite3`, demo GIF for README.
- **Phase 5 (release): not started.** `v0.1.0` tag, GitHub release, badges,
  demo GIF, LinkedIn post.
- **Later (deferred, no specs yet):** kanji, vocabulary, grammar, local
  LLM-generated exercises/feedback (Ollama), speech/pronunciation
  assessment (local Whisper), web UI.

## Immediate next step for the new session

1. Read this file plus `docs/ROADMAP.md` and the latest spec files in
   `docs/specs/` for full technical detail.
2. Resolve the open question above: does the `Knowledge` per-skill
   namespacing fix happen before or as part of spec 006? Ask the user or
   propose a default and flag it before coding (per the workflow rule
   above).
3. Write spec 006 (lesson unlock threshold), get approval, then follow the
   test-first workflow as in specs 001-005.
4. Continue to spec 007 (spaced repetition), then Phase 4.
