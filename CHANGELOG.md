# Changelog

## Unreleased
- Move to `src/` layout, add `pyproject.toml`, README, LICENSE.
- Add `Assessment.from_question(skill, question)` (spec 001).
- Fix: skill mastery is now the mean of all knowledge item scores instead
  of just the last answer (spec 002).
- Answers are now normalized (case, whitespace) and `expected_answer` can
  be a list of accepted spellings (spec 003).
