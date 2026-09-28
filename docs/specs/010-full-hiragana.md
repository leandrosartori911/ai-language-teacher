# 010: Full basic hiragana, one lesson per row

## Problem
The tutor only teaches the five hiragana vowels. The MVP needs the complete
kana (the 46 basic characters, then dakuten/handakuten and combinations,
for both scripts). This spec covers the 46 basic hiragana; katakana,
dakuten/handakuten and combinations follow in their own specs so each
batch of content stays small enough to review properly.

Some kana also have more than one accepted romanization (し is "shi" in
Hepburn but "si" in the Kunrei system many learners also see). `Question`
has accepted several spellings since spec 003, but the lesson file format
can only give one answer.

## Behavior
- Hiragana is taught as ten lessons, one per row of the kana table, in
  this order: vowels (あ), K (か), S (さ), T (た), N (な), H (は), M (ま),
  Y (や), R (ら), W + ん (わ, を, ん). Each lesson is its own file,
  `data/japanese/hiragana_<row>.json` (`hiragana_vowels.json` keeps its
  name and content).
- `language/japanese/hiragana.py` exposes:
  - `HIRAGANA_LESSONS: list[Lesson]`, the ten lessons in order;
  - `HIRAGANA_VOWELS_LESSON`, unchanged (the first lesson);
  - `HIRAGANA: dict[str, str]`, now *all* 46 characters mapped to their
    main romaji (previously only the vowels).
- Lesson items may have an optional `also_accepted` list of other correct
  spellings. `Lesson.items` keeps the main answer (for display); the
  generated `Question` accepts the main answer plus every `also_accepted`
  spelling. Items without `also_accepted` produce exactly the same
  `Question` as today. The loader rejects a blank `also_accepted` entry or
  one equal to the main answer.
- Accepted spellings: し shi/si, ち chi/ti, つ tsu/tu, ふ fu/hu, を o/wo,
  ん n/nn. Main answers use Hepburn romanization.
- Every item gets full teaching content as in spec 009 (explanation,
  original mnemonic, kana-only example word containing the item, culture
  note where there is a true, useful one). Explanations cover the sounds
  that surprise English speakers: し, ち, つ, ふ, the R row (a light tap,
  between English r, l and d), ん, and を. Particle readings (は read "wa",
  へ read "e", を read "o") are mentioned where they come up.

## Acceptance Criteria
- [x] `HIRAGANA_LESSONS` has 10 lessons in the row order above, with 46
      items in total and no item repeated across lessons.
- [x] `HIRAGANA` has all 46 basic hiragana and equals the union of the ten
      lessons' items.
- [x] Every item in every hiragana lesson has teaching content that passes
      the spec 009 checks.
- [x] The question for し accepts "shi" and "si"; the same holds for every
      spelling listed above. The question for か accepts only "ka".
- [x] `load_lesson` rejects a blank `also_accepted` entry and one equal to
      the main answer.
- [x] Existing tests that treated `HIRAGANA` as the vowels-only dict now
      compare against `HIRAGANA_VOWELS_LESSON.items` instead (in
      `test_hiragana.py` and `test_loader.py`); no other existing test
      changes.

## Out of Scope
- Katakana beyond the vowels (next spec).
- Dakuten/handakuten (が, ぱ...) and combinations (きゃ...) (later specs).
- Obsolete kana ゐ and ゑ.
- Lesson unlocking and review order (later specs).
