# 014: Lesson unlock threshold

## Problem
The kana courses now have 18 (hiragana) and 19 (katakana) lessons, but
nothing decides which ones a student may study. The MVP promise is a tutor
that "checks real mastery before unlocking the next stage": a student
should not jump to combinations before they can read the basic rows.

## Behavior
- New module `core/progression.py` with:
  - `UNLOCK_THRESHOLD = 0.8`
  - `lesson_mastery(student, skill, lesson) -> float`: the mean of the
    student's scores for the lesson's items in `student.knowledge[skill]`.
    Items the student has never answered count as `0.0`. A lesson with no
    items raises `ValueError`.
  - `unlocked_lessons(student, skill, lessons) -> list[Lesson]`: walks a
    course (a list of lessons in teaching order) and returns the lessons
    the student may study: the first lesson is always unlocked, and each
    following lesson is unlocked when the lesson before it has mastery
    >= `UNLOCK_THRESHOLD`. The walk stops at the first locked lesson, so
    the result is always a prefix of the course.
- The course order *is* the prerequisite chain; lessons get no new field.
  (This replaces the earlier idea of an `unlocked_after` field on
  `Lesson`: now that each script's course is an ordered list, the order
  already says what comes before what.)
- Nothing else changes: scoring, knowledge and lesson files stay as they
  are.

## Acceptance Criteria
- [x] `lesson_mastery` is `0.0` for a new student and `1.0` when every item
      was last answered correctly.
- [x] `lesson_mastery` counts unanswered items as `0.0` (4 of 5 correct and
      one never answered = `0.8`).
- [x] `lesson_mastery` only reads the given skill's knowledge (katakana
      answers do not count towards a hiragana lesson).
- [x] `lesson_mastery` raises `ValueError` for a lesson with no items.
- [x] A new student has exactly the first lesson of a course unlocked.
- [x] Mastery of exactly `0.8` on lesson 1 unlocks lesson 2; `0.6` does not.
- [x] Mastering lessons 1 and 2 unlocks 3, and lesson 4 stays locked while
      lesson 3 is below the threshold, even if lesson 4's own items were
      answered correctly (no skipping ahead).
- [x] Works on the real `HIRAGANA_LESSONS` course: answering every vowel
      correctly unlocks the K row.

## Out of Scope
- Unlocking across courses (e.g. katakana requiring hiragana) or
  cross-skill prerequisites.
- Remembering unlocks. Unlocking is computed from current mastery, so if a
  student's mastery of lesson 1 later drops below the threshold (a wrong
  answer on review), lesson 2 locks again until lesson 1 is back above
  it. Storing unlocks permanently needs persistence (spec 017) and can be
  added there if this feels too strict in practice.
- A per-lesson or per-student threshold; one constant is enough now.
- Showing locked/unlocked state in a UI (Phase C).
