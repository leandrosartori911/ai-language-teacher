# 008: Knowledge tracked per skill

## Problem
`Student.knowledge` is one flat `Knowledge` map for every skill. When an
assessment with an `item` is applied, the skill's score becomes the mean
of *all* items in that map, whatever skill they belong to. So a student
who gets all five hiragana vowels right (hiragana = 1.0) and then misses
one katakana vowel ends up with katakana = 5/6 ≈ 0.83 instead of 0.0, and
their hiragana items keep inflating katakana from then on. Progress numbers
are wrong as soon as a student studies two skills, which the MVP needs
(hiragana, katakana, kanji, vocabulary).

Item keys can also collide across skills later: `日` can be a kanji item
and the start of a vocabulary item.

## Behavior
- `Student.knowledge` becomes a `dict[str, Knowledge]` with one empty
  `Knowledge` per skill in `SKILLS`, e.g. `student.knowledge["hiragana"]`.
  Each student gets its own dict and its own `Knowledge` objects.
- `Student.apply_assessment(result)` with an `item`:
  1. rejects an unknown skill with `ValueError` (as `update_skill` does
     today), before touching any knowledge;
  2. stores the item score in `student.knowledge[result.skill]`;
  3. sets `student.skills[result.skill]` to the mean of that skill's item
     scores only.
- `apply_assessment` without an `item` is unchanged (sets the skill score
  directly).
- The `Knowledge` class itself is unchanged (`update`, `get_score`,
  `items`).
- The `# ponytail:` note about the flat map is removed.

## Acceptance Criteria
- [x] A new `Student` has an empty `Knowledge` for each of the seven
      skills.
- [x] All five hiragana vowels right, then one katakana vowel wrong:
      hiragana stays `1.0` and katakana is `0.0`.
- [x] The same item key under two skills keeps two separate scores.
- [x] An item assessment for an unknown skill raises `ValueError` and
      changes no knowledge.
- [x] Two students never share knowledge (updated test from spec 006).
- [x] Existing tests that read `student.knowledge` directly are updated to
      `student.knowledge[<skill>]`; no other existing test changes. That
      is 3 tests: `test_student_has_knowledge`,
      `test_student_knowledge_is_updated_from_an_assessed_question`,
      `test_students_do_not_share_skills_or_knowledge`.

## Out of Scope
- Mastery of a single lesson (a subset of a skill's items), which the
  unlock threshold needs; spec 011 decides that.
- Weighting, decay or history of scores (spaced repetition, spec 012).
- Persistence (spec 014).
