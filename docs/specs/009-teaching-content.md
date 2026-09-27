# 009: Teaching content per item

## Problem
A lesson today is only `{item: romaji}` plus auto-generated questions
("What is the romaji for あ?"). The tutor can quiz, but it cannot teach:
there is nothing to show a student *before* asking, no way to help them
remember a character, and no link to real words or to Japanese culture.
The MVP goal is a teacher that really teaches (language and culture), and
the local LLM planned for Phase D needs curated, correct content to ground
its answers on (ADR 0002).

## Behavior
- Lesson JSON files change shape. `items` becomes a list of objects, one
  per item, in teaching order:

  ```json
  {
    "title": "Hiragana vowels",
    "items": [
      {
        "item": "あ",
        "answer": "a",
        "explanation": "How it sounds and what to notice.",
        "mnemonic": "A memory hook tied to the character's shape.",
        "example": {"word": "あめ", "reading": "ame", "meaning": "rain"},
        "culture_note": "Optional: history or culture behind it."
      }
    ]
  }
  ```

- New dataclasses in `core/teaching.py`:
  - `Example(word: str, reading: str, meaning: str)`
  - `Teaching(explanation: str, mnemonic: str, example: Example, culture_note: str | None = None)`
- `Lesson` gains `teaching: dict[str, Teaching]` (item -> teaching),
  defaulting to an empty dict. `Lesson.items` stays `dict[str, str]`
  (item -> answer), and questions are generated as before, so
  `HIRAGANA`, `KATAKANA` and all quiz code keep working unchanged.
- `load_lesson` validates every item and raises `ValueError` naming the
  file and the item when:
  - `item`, `answer`, `explanation`, `mnemonic` or `example` is missing
    or blank (`example` needs non-blank `word`, `reading` and `meaning`);
  - the example word does not contain the item (the example must actually
    show the character being taught);
  - the same item appears twice in one lesson.
  `culture_note` is optional; when present it must not be blank.
- The old `{item: romaji}` shape is no longer accepted; both existing
  lesson files move to the new shape.
- Content is written in English, originally for this project (no text
  copied from other courses). Both vowel lessons get full teaching content
  for all ten items: explanation with pronunciation guidance, an original
  mnemonic, a kana-only example word, and a culture note where there is a
  true, useful one (for example, which kanji each kana developed from).

## Acceptance Criteria
- [x] Every item in both vowel lessons has an explanation, a mnemonic and
      an example whose word contains the item.
- [x] `HIRAGANA_VOWELS_LESSON.teaching["あ"]` is a `Teaching` whose example
      is an `Example`.
- [x] `Lesson.items` and the generated questions are unchanged for both
      lessons (existing hiragana and katakana tests pass unmodified).
- [x] `load_lesson` raises `ValueError` for: a missing required field, a
      blank required field, a blank example field, an example word that
      does not contain the item, a duplicate item, and a blank
      `culture_note`.
- [x] A lesson without `culture_note` on an item loads, with
      `culture_note is None`.
- [x] The two existing loader validation tests that write old-shape JSON
      to a temp file (`test_load_lesson_rejects_empty_items`,
      `test_load_lesson_rejects_blank_answer`) are updated to the new
      shape; no other existing test changes.

## Out of Scope
- Showing the teaching content to a student (web UI, Phase C) or the order
  of "teach, then quiz" in a session; this spec only makes the content
  exist and be valid.
- Audio, stroke order, images.
- Multiple accepted answers in lesson JSON (`Question` already supports
  them; the file format adds it when a lesson needs it).
- Full kana (spec 010), kanji and vocabulary (spec 013).
