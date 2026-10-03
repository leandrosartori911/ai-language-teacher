# 018: Course gating between skills, permanent unlocks

## Problem
Lessons unlock one after another inside a skill (spec 014), but the four
Japanese courses are independent: a brand-new student can open katakana,
kanji and vocabulary on day one. The agreed order is hiragana, then
katakana, then kanji and vocabulary together, because vocabulary and
kanji readings are written in kana.

Also, unlocks are computed live today, so a lesson closes again when the
previous lesson drops below 0.8. That punishes a student exactly when
they are forgetting, which is when they most need to practise. Forgetting
is handled by spaced repetition (spec 015), not by locking content again.

## Behavior
- **Unlocks are permanent.** Once a lesson or a skill opens, it stays
  open, even if mastery later drops. Forgotten items come back through
  scheduled reviews.
- Lessons: `Student` gains `unlocked_count: dict[str, int]` (skill -> how
  many lessons of the course have been unlocked, 0 for every skill at
  first). Unlocked lessons are always the first ones of the course, so
  one number per skill is enough. `unlocked_lessons(student, skill,
  lessons)` returns the longer of the stored prefix and the prefix
  computed as in spec 014, and stores the new length. Its result never
  shrinks.
- Skills: `Student` gains `opened_skills: set[str]`, empty at first.
  `core/progression.py` gains:
  - `course_mastered(student, skill, lessons) -> bool`: true when every
    lesson of the course has mastery at or above `UNLOCK_THRESHOLD` (0.8).
    An empty course raises `ValueError`.
  - `open_skills(student, courses, prerequisites) -> list[str]`: the
    skills the student can study, in the order of `courses`. `courses`
    maps skill -> lessons; `prerequisites` maps skill -> the skill that
    must be mastered first, or `None`. A skill is open when it is already
    in `opened_skills`, has no prerequisite, or its prerequisite is open
    and mastered. Newly opened skills are added to `opened_skills`.
- New module `language/japanese/course.py` holds the Japanese order as
  data, keeping language-specific choices out of `core`:
  - `COURSES = {"hiragana": HIRAGANA_LESSONS, "katakana": KATAKANA_LESSONS,
    "kanji": KANJI_LESSONS, "vocabulary": VOCABULARY_LESSONS}`
  - `PREREQUISITES = {"hiragana": None, "katakana": "hiragana",
    "kanji": "katakana", "vocabulary": "katakana"}`
- A closed skill offers no new items: callers pass an empty lesson list
  to `study_queue` for it. Scheduled reviews still come back when due.
- Skills with no course yet (grammar, listening, speaking) never open.

## Acceptance Criteria
- [x] `course_mastered` is false for a new student, true once every lesson
      is at 0.8 or above, and false if a single lesson is below 0.8; an
      empty course raises `ValueError`.
- [x] For a new student, `open_skills` on the Japanese course is
      `["hiragana"]`.
- [x] Mastering all hiragana opens katakana; kanji and vocabulary stay
      closed.
- [x] Mastering all katakana as well opens kanji and vocabulary.
- [x] Mastering katakana without hiragana opens nothing beyond hiragana
      (no skipping ahead).
- [x] Once open, katakana, kanji and vocabulary stay open after hiragana
      and katakana mastery drop below 0.8.
- [x] Once unlocked, a lesson stays unlocked after the previous lesson
      drops below 0.8 (this replaces the relocking test from spec 014).
- [x] Unlocks are kept per student and per skill.
- [x] `COURSES` and `PREREQUISITES` cover the same skills, and every
      prerequisite is one of them.

## Out of Scope
- Placement tests or letting an experienced student skip ahead.
- Saving unlocks between runs (spec 019 persistence must store
  `unlocked_count` and `opened_skills` along with `cards`).
- Partial gating, such as opening vocabulary after hiragana only.
- "Review previous lessons" (picking any unlocked lesson to practise
  freely) and a combined "what to study next" across skills: web UI,
  spec 020+. The data is already there (`unlocked_lessons`, lesson
  questions); that spec decides how free practice affects review cards.
