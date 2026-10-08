# 023: Due-review counts on the dashboard

## Problem
The dashboard shows mastery and unlocked lessons per skill, but not
whether any reviews are waiting. A student has to open Study for each
skill to find out if spaced repetition (spec 015) has something due
today. Reviews left waiting pile up and get forgotten.

## Behavior
- Each open skill on the dashboard also shows how many review cards are
  due today, e.g. "3 due". The count is `len(due_items(student, skill,
  today))`, the same rule Study uses, with the app's `today`.
- With nothing due the skill shows "0 due" (no special wording).
- New items (no card yet) are not counted; only reviews.
- Locked skills show no count: a skill can only have cards after it was
  open, and opens are permanent (spec 018).
- The dashboard stays read-only: nothing is saved.

## Acceptance Criteria
- [x] A student with no cards sees "0 due" on each open skill.
- [x] Cards due today or earlier are counted; cards due later are not.
- [x] Counts are per skill: a due hiragana card does not change the
      katakana count.
- [x] Locked skills show no due count.
- [x] The count uses the `today` passed to `create_app` (tests fix the
      date).

## Out of Scope
- Counting new (never studied) items, or a total across skills.
- Highlighting skills with reviews due, notifications or reminders.
- Showing the next review date on the dashboard (Study already shows it
  when nothing is due).
