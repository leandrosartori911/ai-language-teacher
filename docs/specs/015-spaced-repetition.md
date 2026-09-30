# 015: Spaced repetition (Leitner boxes)

## Problem
The tutor can unlock lessons, but it has no idea *when* a student should
see an item again. Without that, a student either re-drills what they
already know or forgets what they learned last week. Reviewing items just
before they would be forgotten, at growing intervals, is the adaptive core
of the teacher.

## Behavior
- New module `core/review.py`, standard library only, using the Leitner
  system: every item a student has answered sits in one of five boxes;
  higher boxes are reviewed less often.
  - `BOX_INTERVALS = (1, 2, 4, 8, 16)`: days until the next review for
    boxes 1 to 5.
  - `@dataclass Card(box: int, due: date)`.
  - `Student` gains `cards: dict[str, dict[str, Card]]` (skill -> item ->
    card), one empty dict per skill, like `knowledge`.
- `record_answer(student, result, today)`:
  1. applies the result to knowledge and mastery exactly as
     `student.apply_assessment` does today;
  2. updates the item's card: a correct answer moves it up one box (a new
     item starts from box 0, so its first correct answer puts it in box
     1; box 5 is the top) and makes it due `BOX_INTERVALS[box - 1]` days
     after `today`; a wrong answer puts it back in box 1, due `today`, so
     it comes back in the same session.
  Results without an `item` raise `ValueError`: only items can be
  scheduled.
- `due_items(student, skill, today) -> list[str]`: items whose card is due
  on or before `today`, most overdue first, then lowest box first.
- `study_queue(student, skill, lessons, today) -> list[str]`: what to study
  next in a course: all due items first (as `due_items`), then items the
  student has never answered from the unlocked lessons (spec 014), in
  course order. Items that are not due and already scheduled are left out.
- The caller always passes `today`; nothing in this module reads the
  clock, so behaviour is deterministic and easy to test.
- Small fix carried over from spec 014: `lesson_mastery` with an unknown
  skill raises `ValueError` (it raised `KeyError`), matching `Student`.

## Acceptance Criteria
- [x] A first correct answer puts the item in box 1, due tomorrow.
- [x] Each further correct answer moves it up one box with the matching
      interval (box 2: 2 days, box 3: 4, box 4: 8, box 5: 16); box 5 stays
      at 5.
- [x] A wrong answer, from any box, puts it in box 1 due today.
- [x] `record_answer` updates knowledge and skill mastery the same way as
      `apply_assessment`, and rejects a result without an item.
- [x] Cards are kept per skill (the same item key in two skills has two
      cards), and two students never share cards.
- [x] `due_items` returns only due items, most overdue first, ties broken
      by lower box.
- [x] `study_queue` for a new student on `HIRAGANA_LESSONS` is the five
      vowels, in order.
- [x] `study_queue` puts due items before new ones, skips scheduled items
      that are not due yet, and never includes items from locked lessons.
- [x] `lesson_mastery` with an unknown skill raises `ValueError`.

## Out of Scope
- SM-2 or other algorithms with per-item ease factors; Leitner is enough
  for kana and easy to explain. The algorithm lives in one small module,
  so it can be swapped later.
- Limits on new items per day or session length (UI concern, Phase C).
- Saving cards between runs (spec 017, persistence).
- Time zones or times of day: scheduling works in whole days.
