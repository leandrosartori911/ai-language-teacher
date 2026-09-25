# 005: Katakana vowels content

## Problem
The tutor only teaches Hiragana. Katakana is the other basic Japanese
script and the roadmap's next content step; the loader from spec 004
already supports any `{item: romaji}` lesson, so adding katakana is a data
file, not new code.

## Behavior
- `data/japanese/katakana_vowels.json` holds the five Katakana vowels:
  `ア→a, イ→i, ウ→u, エ→e, オ→o`, same shape as `hiragana_vowels.json`.
- `ai_language_teacher/language/japanese/katakana.py` mirrors
  `hiragana.py`: loads that file via `load_lesson` and exposes `KATAKANA`
  and `KATAKANA_VOWELS_LESSON`.

## Acceptance Criteria
- [x] `KATAKANA == {"ア": "a", "イ": "i", "ウ": "u", "エ": "e", "オ": "o"}`.
- [x] `KATAKANA_VOWELS_LESSON.title == "Katakana vowels"`.
- [x] `KATAKANA_VOWELS_LESSON` has one question per item, same pattern as
      the hiragana lesson.
- [x] Applying a correct katakana assessment updates
      `student.skills["katakana"]` (skill field is independent from
      `"hiragana"`, using the mastery aggregation from spec 002).

## Out of Scope
- Full Katakana syllabary (only the 5 vowels, matching hiragana's current
  scope).
- Cross-skill `Knowledge` separation: as noted in spec 002, `Knowledge` is
  one flat map. If a single student studies both hiragana and katakana
  vowels, both skills' averages would mix in that student's `Knowledge`.
  This spec adds katakana content only; per-skill knowledge separation is
  a future spec if/when it's actually needed (the katakana tests below use
  a fresh `Knowledge`/`Student` so the mixing doesn't surface yet).
