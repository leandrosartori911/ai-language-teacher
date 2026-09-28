# 013: Combinations (yoon) and small っ, both scripts

## Problem
The kana course still misses two pieces that almost every real text uses:
- combinations (yoon): an i-column kana plus a small ゃ, ゅ or ょ forms one
  syllable (き + ゃ -> きゃ kya), as in きょう (kyō, today) or
  しゃしん (shashin, photo);
- small っ (sokuon), which doubles the next consonant, as in きって
  (kitte, stamp) versus きて (kite, come).
Without them a learner cannot read common words, and kana is not
complete.

## Behavior
- Three new lessons per script, after the dakuten rows:
  1. "Combinations": きゃ きゅ きょ, しゃ しゅ しょ, ちゃ ちゅ ちょ,
     にゃ にゅ にょ, ひゃ ひゅ ひょ, みゃ みゅ みょ, りゃ りゅ りょ (21);
  2. "Voiced combinations": ぎゃ ぎゅ ぎょ, じゃ じゅ じょ, びゃ びゅ びょ,
     ぴゃ ぴゅ ぴょ (12);
  3. "Small tsu": っ (one item).
  Katakana mirrors them (キャ ... ピョ, ッ). Files:
  `<script>_combinations.json`, `<script>_voiced_combinations.json`,
  `<script>_small_tsu.json`.
- Each combination is one item (two characters, e.g. `きゃ`) with its
  Hepburn romaji. Accepted alternatives: しゃ/しゅ/しょ sya/syu/syo,
  ちゃ/ちゅ/ちょ tya/tyu/tyo, じゃ/じゅ/じょ zya/zyu/zyo and jya/jyu/jyo
  (same for katakana).
- The small tsu item uses a custom prompt ("What does a small っ do?"),
  answer "double consonant", also accepting "doubles the next consonant"
  and "pause". Its example contrasts a word with and without it.
- Teaching content as in spec 009. The first item of each combination
  lesson explains that the second kana is written small and merges into
  one beat; explanations warn that きや (ki-ya, two beats) and きゃ (kya,
  one beat) are different. Katakana items point to the hiragana and use
  loanword examples where they exist.
- `HIRAGANA_LESSONS` grows to 18 lessons (105 items) and
  `KATAKANA_LESSONS` to 19 (106 items).

## Acceptance Criteria
- [x] Both courses end with the three new lessons in the order above, with
      21, 12 and 1 items.
- [x] `HIRAGANA` has 105 items and `KATAKANA` 106, none repeated.
- [x] Every new item has teaching content that passes the spec 009 checks.
- [x] Every katakana combination maps to the same romaji as its hiragana.
- [x] The alternative spellings above are accepted in both scripts.
- [x] The small tsu questions use the custom prompt and accept the listed
      answers.
- [x] The test from spec 012 that checks the dakuten rows are the last
      lessons (and the 71/72 totals) is updated to check they come right
      before the new lessons, plus the new totals; the CI wheel check
      expects 105 and 106. No other existing test changes.
- [x] (Found during implementation.) The spec 011 test that required every
      katakana question except ー to use the default prompt now also exempts
      ッ, whose custom prompt is checked by the new tests.

## Out of Scope
- ぢゃ/ぢゅ/ぢょ (almost never used).
- Extended katakana for foreign sounds (ファ, ティ, ウィ, ヴ...), which also
  use small kana; a later spec if needed.
- Small ぁ ぃ ぅ ぇ ぉ outside combinations.
