# 012: Dakuten and handakuten, both scripts

## Problem
The basic kana cover 46 sounds per script, but Japanese writes 25 more by
adding marks to them: dakuten ゛ voices a consonant (か ka -> が ga) and
handakuten ゜ turns h into p (は ha -> ぱ pa). They appear in everyday
words from the start (ごはん, rice; ビール, beer), so the kana are not
complete without them.

## Behavior
- Five new lessons per script, one per row, taught after the basic rows
  (and, for katakana, after the long vowel mark lesson):
  G (が/ガ), Z (ざ/ザ), D (だ/ダ), B (ば/バ), P (ぱ/パ).
  Files: `data/japanese/hiragana_<row>.json` and
  `katakana_<row>.json` for rows `g`, `z`, `d`, `b`, `p`.
- `HIRAGANA_LESSONS` and `KATAKANA_LESSONS` stay the full course for each
  script in teaching order, so they grow to 15 and 16 lessons.
  `HIRAGANA` and `KATAKANA` grow to 71 and 72 items.
- Main answers are Hepburn. Accepted alternatives:
  じ/ジ ji/zi, ぢ/ヂ ji/di, づ/ヅ zu/du.
- Teaching content as in spec 009. The first item of each lesson explains
  the mark: dakuten voices the consonant (k->g, s->z, t->d, h->b),
  handakuten turns h into p. Explanations flag the two sound collisions:
  ぢ sounds like じ and づ sounds like ず, and ぢ/づ are rare (used mostly
  when a word's pieces force them, as in はなぢ, nosebleed). Katakana items
  point to the matching hiragana, and examples are loanwords.

## Acceptance Criteria
- [x] `HIRAGANA_LESSONS` has 15 lessons: the 10 basic rows, then G, Z, D,
      B, P; `HIRAGANA` has 71 items with none repeated.
- [x] `KATAKANA_LESSONS` has 16 lessons: the 10 basic rows, ー, then G, Z,
      D, B, P; `KATAKANA` has 72 items with none repeated.
- [x] Every new item has teaching content that passes the spec 009 checks.
- [x] Every new katakana maps to the same main romaji as its hiragana.
- [x] The alternative spellings listed above are accepted in both scripts.
- [x] Tests from specs 010 and 011 that count lessons or items (10/46 for
      hiragana, 11/47 for katakana) are updated to check that the basic
      rows are still the first lessons with the same items, plus the new
      totals. The CI wheel smoke check expects 71 and 72 items. No other
      existing test changes.

## Out of Scope
- Combinations (きゃ, ぎゃ...) and small っ/ッ (spec 013).
- Extended katakana for foreign sounds (ヴ, ファ, ティ...).
- Pitch accent.
