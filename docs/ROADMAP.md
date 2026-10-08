# Roadmap

MVP goal: a local, zero-cost AI teacher that really teaches Japanese
(language and culture), with a web interface. Features are specified in
[specs](specs) before they are built.

## Done
- [x] Core models: Student, Knowledge, Question, Assessment, Lesson
- [x] Hiragana vowels lesson
- [x] Core correctness: `Assessment.from_question`
- [x] Mastery aggregation (skill = mean of knowledge items)
- [x] Answer normalization and multiple accepted answers
- [x] Content as data (JSON) with a validating loader
- [x] Katakana vowels

## Phase A: Foundation
- [x] Typed dataclass core models, `mypy` in CI (spec 006)
- [x] Lesson data shipped inside the package (spec 007)
- [x] Knowledge tracked per skill (spec 008)

## Phase B: Teaching engine
- [x] Teaching content per item: explanation, mnemonic, example, culture note (spec 009)
- [x] Full basic hiragana, one lesson per row, alternative spellings (spec 010)
- [x] Full basic katakana and the long vowel mark ー (spec 011)
- [x] Dakuten and handakuten, both scripts (spec 012)
- [x] Combinations (yoon) and small tsu, both scripts (spec 013); kana complete
- [x] Lesson unlock threshold (spec 014)
- [x] Spaced repetition, Leitner boxes (spec 015)
- [x] 40 essential JLPT N5 kanji, meaning quiz, readings taught (spec 016)
- [x] Starter vocabulary, 100 words with example sentences (spec 017)
- [x] Course order hiragana -> katakana -> kanji + vocabulary; unlocks are permanent (spec 018)

## Phase C: Web app
- [x] SQLite persistence, several profiles (spec 019)
- [x] Web app skeleton, profiles and skill dashboard (spec 020)
- [x] Study a skill in the browser: teaching card, quiz, spaced repetition (spec 021)
- [x] Practise previous lessons: any unlocked lesson, never promotes early (spec 022)
- [x] Due-review counts per skill on the dashboard (spec 023)

## Phase D: Local LLM teacher
- [x] Default model chosen by comparing five local models (ADR 0004)
- [x] Ask the AI teacher about an item, grounded on the lesson content,
      with a fallback message when Ollama is not running (spec 024)
- [x] Explain my mistake after a wrong answer (spec 025)

## Phase E: Release
- [ ] v0.1.0 release, demo GIF

## Later
- Per-language themed interface (e.g. Japanese in flag colors)
- More languages, deeper kanji, grammar, speech assessment
- Exercises that ask for kana (produce, not only recognise), with a hint
  to enable the Japanese IME and an on-screen kana table
