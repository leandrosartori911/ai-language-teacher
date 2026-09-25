# 004: Lesson content as data files

## Problem
Lesson content (characters, romaji, questions) is hardcoded in Python
(`hiragana.py`). Adding katakana, then kanji, vocabulary, and grammar means
writing more Python modules that mix content with code, and there is no
validation that content is well-formed (no duplicate items, every item has
an answer).

## Behavior
- Lesson content lives in JSON files under `data/japanese/<lesson-id>.json`,
  shaped as:
  ```json
  {
    "title": "Hiragana vowels",
    "items": {"あ": "a", "い": "i", "う": "u", "え": "e", "お": "o"}
  }
  ```
- `app.language.loader.load_lesson(path)` reads that JSON and returns a
  `Lesson` with one auto-generated `Question` per item (prompt
  `"What is the romaji for {item}?"`, matching today's hiragana questions).
- The loader raises `ValueError` if `items` is empty, or if any item's
  romaji is an empty string.
- `data/japanese/hiragana_vowels.json` replaces the hardcoded content in
  `hiragana.py`; `HIRAGANA_VOWELS_LESSON` is now built by calling the loader
  on that file, so existing imports keep working.

## Acceptance Criteria
- [x] `load_lesson("data/japanese/hiragana_vowels.json")` returns a `Lesson`
      with the same title, items, and per-item questions as today's
      `HIRAGANA_VOWELS_LESSON`.
- [x] A JSON file with an empty `items` object raises `ValueError`.
- [x] A JSON file with an item mapped to `""` raises `ValueError`.
- [x] `HIRAGANA_VOWELS_LESSON` and `HIRAGANA` still exist and behave the
      same for existing importers (`tests/test_hiragana.py` passes
      unmodified).

Used JSON instead of YAML (stdlib `json`, no new dependency; `pyyaml` isn't
installed and the plan allowed either format).

## Out of Scope
- Adding katakana content (spec 005).
- Any schema beyond the flat `{item: romaji}` map (grammar/kanji content
  will likely need a richer shape — a later spec).
