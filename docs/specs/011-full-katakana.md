# 011: Full basic katakana, one lesson per row

## Problem
Katakana stops at the five vowels. Katakana is how Japanese writes
loanwords, foreign names and many brand names, so a learner meets it
constantly on menus, signs and packaging. Loanwords also rely on the long
vowel mark ー (コーヒー, kōhī, coffee), which is not a kana but cannot be
read without being taught.

## Behavior
- Katakana is taught as ten lessons mirroring hiragana (spec 010): vowels
  (ア), K (カ), S (サ), T (タ), N (ナ), H (ハ), M (マ), Y (ヤ), R (ラ),
  W + ン (ワ, ヲ, ン). Files are `data/japanese/katakana_<row>.json`
  (`katakana_vowels.json` keeps its name and content).
- An eleventh lesson, "Katakana long vowel mark", teaches ー. Its item is
  `ー` with the answer "long vowel" (what the mark does, since it has no
  sound of its own); the quiz asks what the mark means rather than for
  romaji. Its example is a loanword that uses it.
- `language/japanese/katakana.py` exposes, like hiragana:
  - `KATAKANA_LESSONS: list[Lesson]`, the eleven lessons in order;
  - `KATAKANA_VOWELS_LESSON`, unchanged;
  - `KATAKANA: dict[str, str]`, now all 46 basic katakana plus ー.
- Accepted spellings match hiragana: シ shi/si, チ chi/ti, ツ tsu/tu,
  フ fu/hu, ヲ o/wo, ン n/nn.
- Every item gets full teaching content (spec 009). Katakana explanations
  point to the matching hiragana (`カ` = `か`) and to the pairs learners
  confuse most: シ/ツ, ソ/ン, ク/ケ/タ, ヌ/ス, ウ/ワ/フ. Example words are
  real loanwords or names written in katakana; culture notes cover which
  kanji each katakana came from and, where true and useful, where a
  loanword came from.
- The loader's question prompt is taken from the lesson file when given
  (`"prompt"` on the item), so the ー item can ask "What does ー mean in
  katakana words?" Items without `"prompt"` keep the current
  "What is the romaji for {item}?".

## Acceptance Criteria
- [x] `KATAKANA_LESSONS` has 11 lessons: the ten rows in order, then the
      long vowel mark lesson; 47 items in total, none repeated.
- [x] `KATAKANA` has all 46 basic katakana and ー and equals the union of
      the lessons' items.
- [x] Every katakana item has teaching content that passes the spec 009
      checks.
- [x] Every basic katakana maps to the same main romaji as its hiragana
      (e.g. `KATAKANA["カ"] == HIRAGANA["か"]`).
- [x] The alternative spellings listed above are accepted.
- [x] The question for ー uses its custom prompt; every other question in
      every lesson keeps the default prompt.
- [x] The loader rejects a blank `"prompt"`.
- [x] The existing test that expects `KATAKANA` to be exactly the five
      vowels (`test_katakana_contains_basic_vowels`) and the two that
      compare the vowels lesson to `KATAKANA` now use
      `KATAKANA_VOWELS_LESSON.items`; no other existing test changes. The
      CI wheel smoke check also expects 47 katakana items.

## Out of Scope
- Dakuten/handakuten (ガ, パ...) and combinations (キャ...) (specs 012, 013).
- Extended katakana for foreign sounds (ファ, ティ, ヴ...), a later spec if
  needed.
- Small ッ (double consonant), taught with combinations.
