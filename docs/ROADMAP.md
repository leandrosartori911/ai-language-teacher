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
- [ ] Kanji and vocabulary open only after katakana is mastered (spec 018)

## Phase C: Web app
- [ ] SQLite persistence (spec 019)
- [ ] Web UI: FastAPI + Jinja2 templates (spec 020+)

## Phase D: Local LLM teacher
- [ ] Conversational teacher via Ollama, grounded on curated content, with a
      rule-based fallback when no model is running

## Phase E: Release
- [ ] v0.1.0 release, demo GIF

## Later
- Per-language themed interface (e.g. Japanese in flag colors)
- More languages, deeper kanji, grammar, speech assessment
