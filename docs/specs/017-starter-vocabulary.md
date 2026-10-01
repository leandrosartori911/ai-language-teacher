# 017: Starter vocabulary (100 words, meaning quiz)

## Problem
The student can read kana and 40 kanji, but knows almost no words, and
words are what make reading useful. The `vocabulary` skill exists on
`Student` but has no content. Kanji readings were deliberately not
quizzed in spec 016; vocabulary is where those readings come back, in
real words and sentences.

## Behavior
- 100 common N5 words in ten themed lessons of ten, in this teaching order:
  1. Greetings: おはようございます こんにちは こんばんは さようなら
     おやすみなさい ありがとう すみません いただきます はい いいえ
  2. People: 私 あなた 先生 学生 友だち 家族 子ども 兄 姉 名前
  3. Question words: 何 だれ どこ いつ どれ どの いくら いくつ どう どうして
  4. Food and drink: 水 お茶 ご飯 パン 肉 魚 野菜 卵 コーヒー おいしい
  5. Places: 学校 家 駅 店 病院 銀行 会社 トイレ 部屋 国
  6. Things: 本 車 電車 電話 お金 傘 かばん 時計 テレビ 写真
  7. Time: 今日 明日 昨日 毎日 朝 昼 夜 今 時間 今年
  8. Verbs 1: 食べる 飲む 行く 来る 見る 聞く 話す 読む 書く 買う
  9. Verbs 2: する ある いる 起きる 寝る 帰る 分かる 待つ 会う 休む
  10. Adjectives: 大きい 小さい 高い 安い 新しい 古い 暑い 寒い 好き 楽しい
- Each item is the word as it is normally written (kanji, kana, or both),
  so the student meets kanji in real use. Files
  `data/japanese/vocabulary_<theme>.json`; module
  `language/japanese/vocabulary.py` exposes `VOCABULARY_LESSONS` and
  `VOCABULARY` (word -> main meaning).
- **The quiz asks for the meaning in English** ("What does 食べる mean?"),
  with the same `"question"` template and `also_accepted` synonyms as
  kanji. Spec 016 normalization already accepts "eat" for "to eat".
- New optional field: every word has its **reading in kana** (`"reading"`
  in JSON, `Teaching.reading: str | None`, `None` for kana and kanji
  lessons), shown alongside the word.
- **The example is a short sentence** containing the word, with its
  reading in kana and an English translation (same `example` fields as
  before: `word` holds the sentence). Sentences use the **plain
  (dictionary) form**, e.g. 毎朝コーヒーを飲む。, so the word appears in
  them exactly as taught and the loader's "example contains the item"
  check still holds. The explanation gives the polite form (飲みます) and
  any grammar the sentence uses (を, は, に...) in one line.
- Explanations note pitfalls a beginner hits: こんにちは is written with
  は but said "wa"; 家 can also be read うち; どの needs a noun after it,
  unlike どれ; 好き is a na-adjective, not a verb.
- Content is original and fact-checked like spec 016: readings and
  meanings are checked against the jisho.org dictionary before commit.
- Unlocking (spec 014) and spaced repetition (spec 015) work inside the
  `vocabulary` skill as they do for kana and kanji.

## Acceptance Criteria
- [x] `VOCABULARY_LESSONS` has ten lessons with exactly the words above, in
      that order; `VOCABULARY` has 100 entries and no word appears twice.
- [x] Every question asks "What does <word> mean?" and accepts each of its
      listed meanings, case-insensitively.
- [x] Every word has a non-empty kana-only `reading`; kana and kanji
      lessons have `reading` `None`.
- [x] Every word has explanation, mnemonic, and an example sentence that
      contains the word and ends with 。, with a kana-only reading and an
      English translation.
- [x] The loader reads an optional `"reading"` and rejects a blank one,
      naming the file and item.
- [x] A new student has only the greetings lesson unlocked in
      `VOCABULARY_LESSONS`.
- [x] The CI `wheel` job also checks `len(VOCABULARY) == 100`.

## Out of Scope
- Gating vocabulary behind katakana mastery (spec 018).
- Quizzing readings or production (English -> Japanese); conjugation
  drills; polite-form example sentences.
- Grammar lessons: particles and verb forms are only mentioned in
  explanations, not taught or tested.
- Furigana rendering (UI, Phase C); audio.
