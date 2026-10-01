# 016: Essential JLPT N5 kanji (meaning quiz)

## Problem
Kana is complete, but the student cannot read a single kanji, and almost
every real Japanese sentence uses them. The `kanji` skill exists on
`Student` but has no content. Kanji also need something kana did not: a
kanji has several readings that depend on the word it appears in, so
quizzing "the" reading of a lone kanji is misleading.

## Behavior
- 40 essential N5 kanji in six themed lessons, in this teaching order:
  1. Numbers: 一 二 三 四 五 六 七 八 九 十
  2. Big numbers and money: 百 千 万 円
  3. Days of the week: 日 月 火 水 木 金 土
  4. People: 人 子 女 男 父 母 友
  5. Position and size: 上 下 中 大 小 左 右
  6. Time: 年 時 分 半 今
- Files `data/japanese/kanji_<theme>.json`; new module
  `language/japanese/kanji.py` exposes `KANJI_LESSONS` (the course, in
  order) and `KANJI` (kanji -> main meaning), like hiragana/katakana.
- **The quiz asks for the meaning in English** ("What does 水 mean?"),
  and accepts every listed meaning (水: "water"; 月: "moon" or "month").
  Readings are taught, not quizzed: every kanji lists its kun'yomi
  (native Japanese readings, written in hiragana, with a `.` before
  okurigana as dictionaries do) and on'yomi (Chinese-derived readings,
  written in katakana), and its example word shows one of them in use.
- Teaching content keeps the spec 009 shape (explanation, mnemonic,
  example, optional culture note). Example readings for kanji are written
  in **hiragana** instead of romaji, since the student already knows kana.
  The explanation says which reading the example uses and when the other
  appears. Content is original and fact-checked: it grounds the Phase D
  LLM.
- Format changes, all backwards compatible:
  - `Teaching` gains `kun_readings: list[str]` and `on_readings:
    list[str]`, empty by default; the loader reads them from optional
    `"kun"` and `"on"` lists on each item.
  - A lesson file can set a top-level `"question"` template such as
    `"What does {item} mean?"`, used as the prompt for every item; a
    per-item `"prompt"` still wins. Without it, the romaji prompt is
    unchanged.
- Answer normalization (spec 003) also collapses repeated spaces and
  ignores a leading "to ", "a ", "an " or "the " on both sides, so meaning
  answers are less brittle ("The moon" matches "moon"). Kana answers are
  unaffected (no romaji answer starts with one of those words followed by
  a space).
- Kanji follow the existing lesson unlocking (spec 014) and spaced
  repetition (spec 015) inside the `kanji` skill. Opening kanji only after
  katakana is mastered is spec 018.

## Acceptance Criteria
- [x] `KANJI_LESSONS` has six lessons with exactly the kanji above, in that
      order; `KANJI` has 40 entries and no kanji appears twice.
- [x] Every kanji question asks "What does <kanji> mean?" and accepts each
      of its listed meanings, case-insensitively.
- [x] Every kanji has at least one reading; kun readings contain only
      hiragana and `.`, on readings only katakana.
- [x] Every kanji has explanation, mnemonic and an example word that
      contains it, with a hiragana-only example reading.
- [x] The loader reads optional `"kun"`/`"on"` lists into `Teaching` and
      rejects a non-list or a blank reading, naming the file and item;
      lessons without them get empty lists.
- [x] A top-level `"question"` template sets every prompt; a per-item
      `"prompt"` overrides it; existing kana prompts are unchanged.
- [x] `evaluate` ignores a leading "to "/"a "/"an "/"the " and repeated
      spaces; all existing kana tests still pass.
- [x] A new student has only the numbers lesson unlocked in
      `KANJI_LESSONS`.
- [x] The CI `wheel` job also checks `len(KANJI) == 40`.

## Out of Scope
- Quizzing readings (on'yomi/kun'yomi); readings come back through
  vocabulary (spec 017).
- Gating kanji and vocabulary behind katakana mastery (spec 018).
- The full N5 kanji list (~80-100), verbs such as 食 or 行, stroke order,
  handwriting, radicals.
- Synonym or typo tolerance beyond `also_accepted` and the normalization
  above; an LLM judge for near-miss meanings is Phase D.
