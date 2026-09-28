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
