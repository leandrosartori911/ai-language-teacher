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

## Phase F: Polish before release
The user decided on 2026-10-14 to publish the GIF and the release only
when the app is presentable. Specs 030-032 (the release's face, split
on 2026-10-15): 030-034 done (033 and 034 from the user's review on 2026-10-17); 035 from the user's test on 2026-10-19 done. All three use the
`ui-ux-pro-max` and `frontend-design` skills. Order:
- [x] Profiles work like accounts, with logout and delete (spec 026)
- [x] AI teacher guardrails, course word lookup and a red-team test set (spec 027)
- [x] Chat with the AI teacher, streamed and checked sentence by sentence (spec 028)
- [x] Navigation and a friendlier dashboard (spec 029)
- [x] Visual direction from mockups and design tokens, with dark mode (spec 030, ADR 0005)
- [x] Apply the design to every page: components, furigana, chat layout, favicon (spec 031)
- [x] Accessibility, offline and three-width check before the GIF (spec 032)
- [x] Practice page with lesson cards that say what to study first (spec 033)
- [x] A Teacher page for free conversation; one way into the item chat (spec 034)
- [x] New conversation button and a teacher that drifts less (spec 035)

## Phase E: Release (after Phase F)
- [x] Demo GIF in the README
- [x] v0.1.0 tag and GitHub Release (2026-10-20)

## Later
- Per-language themed interface (e.g. Japanese in flag colors)
- More languages, deeper kanji, grammar, speech assessment
- Exercises that ask for kana (produce, not only recognise), with a hint
  to enable the Japanese IME and an on-screen kana table
