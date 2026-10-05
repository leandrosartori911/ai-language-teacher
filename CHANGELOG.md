# Changelog

## Unreleased
- Move to `src/` layout, add `pyproject.toml`, README, LICENSE.
- Add `Assessment.from_question(skill, question)` (spec 001).
- Fix: skill mastery is now the mean of all knowledge item scores instead
  of just the last answer (spec 002).
- Answers are now normalized (case, whitespace) and `expected_answer` can
  be a list of accepted spellings (spec 003).
- Lesson content moves from hardcoded Python to JSON files under `data/`,
  loaded and validated by `language.loader.load_lesson` (spec 004).
- Add Katakana vowels lesson, mirroring the Hiragana one (spec 005).
- Core models are now typed dataclasses (value equality, readable repr);
  `mypy --strict` runs in CI (spec 006).
- Lesson JSON files now live inside the package
  (`ai_language_teacher/data/`) and load via `importlib.resources`, so a
  normally installed wheel works; CI checks it (spec 007).
- Fix: knowledge is tracked per skill, so a skill's mastery is the mean of
  its own items only; studying katakana no longer changes hiragana scores
  and vice versa (spec 008).
- Lessons now teach, not only quiz: every item has an explanation with
  pronunciation guidance, an original mnemonic, an example word and an
  optional culture note. The lesson JSON format changes to a list of item
  objects, validated by the loader (spec 009).
- All 46 basic hiragana, taught as ten lessons (one per row) with full
  teaching content. Lesson items can list `also_accepted` spellings
  (e.g. し accepts "shi" and "si") (spec 010).
- All 46 basic katakana in ten row lessons plus a lesson on the long vowel
  mark ー, with loanword examples and notes on easily confused pairs
  (シ/ツ, ソ/ン...). Lesson items can set a custom question `prompt`
  (spec 011).
- Dakuten and handakuten (が, ざ, だ, ば, ぱ rows and their katakana), five
  lessons per script with teaching content; じ/ぢ/づ accept zi/di/du (spec 012).
- Combinations (きゃ, しゅ, ちょ... and voiced ぎゃ, じゃ, びょ, ぴゃ...) and
  small っ/ッ for both scripts, completing the kana course: 105 hiragana and
  106 katakana items (spec 013).
- Lesson unlocking: a lesson opens once the previous lesson in the course
  reaches 0.8 mastery (`core.progression`: `lesson_mastery`,
  `unlocked_lessons`) (spec 014).
- Spaced repetition with Leitner boxes (intervals 1/2/4/8/16 days):
  `core.review` adds `Card`, `record_answer`, `due_items` and
  `study_queue` (due reviews first, then new items from unlocked lessons);
  `Student` gains `cards`. `lesson_mastery` now raises `ValueError` for an
  unknown skill instead of `KeyError` (spec 015).
- 40 essential JLPT N5 kanji in six themed lessons (numbers, big numbers
  and money, days of the week, people, position and size, time). The quiz
  asks for the meaning; kun'yomi and on'yomi readings are taught with an
  example word. Lesson files can set a `question` template and per-item
  `kun`/`on` readings. Answer matching now also ignores a leading
  "to"/"a"/"an"/"the" and repeated spaces (spec 016).
- 100 starter words in ten themed lessons (greetings, people, question
  words, food, places, things, time, two verb lessons, adjectives). The
  quiz asks for the meaning; each word has its kana reading and a short
  example sentence in plain form, with notes on the polite form and the
  grammar it uses. Lesson items can set a `reading` (spec 017).
- Courses open in order: katakana after all hiragana is mastered, kanji
  and vocabulary after all katakana (`open_skills`, `course_mastered`,
  `language.japanese.course`). Unlocks are now permanent for skills and
  lessons: a drop in mastery no longer locks content again; forgotten
  items come back through spaced repetition (spec 018).
- Student progress is saved in a local SQLite database
  (`~/.ai-language-teacher/data.db`, standard library only): several
  profiles by name, integrity enforced by the schema, one transaction per
  save (`storage.connect`, `save_student`, `load_student`,
  `list_students`). ADR 0003 records the choice (spec 019).
- First web slice (FastAPI + Jinja2, ADR 0001): `ai-language-teacher` starts
  the app on `127.0.0.1:8000`. Pick or create a profile and see a dashboard
  with each skill's course mastery and unlocked lessons, or which skill must
  be mastered first. First runtime dependencies: fastapi, jinja2, uvicorn,
  python-multipart (spec 020).
