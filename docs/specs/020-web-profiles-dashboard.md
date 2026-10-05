# 020: Web app skeleton, profiles and skill dashboard

## Problem
The teaching engine (Phase B) and persistence (spec 019) work, but the only
way to use them is from Python code. The MVP is a web app (ADR 0001), and
nothing serves pages yet. This is the first web slice: open the app, pick
or create a profile, and see where you stand. Studying comes in spec 021.

## Behavior
- New runtime dependencies (the project's first): `fastapi`, `jinja2`,
  `uvicorn` and `python-multipart` (FastAPI needs it to read HTML form
  posts). New dev dependency: `httpx` (needed by FastAPI's `TestClient`).
- New module `ai_language_teacher/web/app.py` with
  `create_app(db_path=DEFAULT_DB_PATH) -> FastAPI`. The database path is a
  parameter so tests use a temporary file, never the real
  `~/.ai-language-teacher/data.db`. Each request opens its own connection
  with `storage.connect` and closes it afterwards.
- Pages are Jinja2 templates in `web/templates/`, styled by one
  stylesheet `web/static/style.css` whose colors are CSS variables in
  `:root` (cheap per-language theming later). No JavaScript in this slice.
  Templates and stylesheet ship as package data, like the lesson JSON.
- `GET /`: lists existing profiles (from `list_students`) as links, plus a
  form with a name field to create a new one.
- `POST /students` (form field `name`): trims the name. A blank name
  re-renders the home page with an error and status 400. A new name is
  saved as a new `Student`; an existing name is left untouched (its
  progress is never overwritten). Either way it redirects (303) to the
  profile page.
- `GET /students/{name}`: the dashboard. Unknown name returns 404. For
  each skill in the Japanese course (`COURSES`, in course order) it shows:
  - open skills (`open_skills`): mastery as a percentage and lessons
    unlocked out of total (e.g. "hiragana · 35% · 4 / 18 lessons").
    Mastery here is the mean score over **every item of the course**
    (unanswered = 0), not `Student.skills`, which only averages answered
    items and would show 100% after one correct answer;
  - closed skills: shown as locked, naming the prerequisite
    ("locked: master katakana first").
  The page only reads; it does not save.
- `main()` starts the server with uvicorn on `127.0.0.1:8000` only (never
  `0.0.0.0`). A console script `ai-language-teacher` runs `main()`, so
  after `pip install` the app starts with one command.
- The CI `wheel` job also checks the installed wheel can serve `/`
  (templates and stylesheet are packaged).

## Acceptance Criteria
- [x] `GET /` with an empty database shows the create-profile form and no
      profiles; with saved profiles it lists their names as links.
- [x] `POST /students` with a new name saves the student and redirects
      (303) to `/students/<name>`.
- [x] `POST /students` with an existing name redirects to it and keeps the
      saved progress unchanged.
- [x] `POST /students` with a blank or whitespace name returns 400 and
      shows an error; nothing is saved.
- [x] `GET /students/<name>` for a new student shows hiragana open at 0%
      with 1 of 18 lessons unlocked, and katakana, kanji and vocabulary
      locked with their prerequisite named.
- [x] A student who has mastered hiragana sees katakana open.
- [x] `GET /students/<unknown>` returns 404.
- [x] Names with spaces or Japanese characters work (link, redirect, page).
- [x] `GET /static/style.css` returns the stylesheet, which defines its
      colors as CSS variables.
- [x] `main()` runs uvicorn with host `127.0.0.1` (checked without
      starting a real server).
- [x] The wheel built by CI serves `GET /` with status 200 from outside
      the repo.

## Out of Scope
- Studying: teaching cards, quiz, `record_answer`, saving answers (spec 021).
- Review of previous lessons, due-review counts on the dashboard.
- Renaming or deleting profiles, login/auth (no auth in the MVP).
- JavaScript, per-language themes, a skill without a Japanese course
  (grammar, listening, speaking are not shown).
- CSRF protection: a page on another site could still make the browser
  post to `127.0.0.1`, but the worst it can do in this slice is create a
  profile. Revisit in spec 021, when posts start changing progress.
