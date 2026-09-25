# 002: Mastery aggregation instead of overwrite

## Problem
`Student.update_skill` sets `self.skills[skill] = score`, replacing the
previous value. When applied through `apply_assessment`, one wrong answer
after many correct ones drops the skill straight to `0.0`, and one correct
answer after many wrong ones jumps it straight to `1.0`. The skill level does
not reflect actual mastery across all practiced items.

## Behavior
When an assessment result has an `item`, applying it updates that item's
score in `Knowledge` as before, then recomputes the skill's score as the
mean of all scores currently in `Knowledge` (`sum(scores) / len(scores)`).
When a result has no `item` (skill-level-only assessment), the skill is
still set directly to the result's score, as today.

## Acceptance Criteria
- [x] Applying one correct answer (item "あ") sets `skills["hiragana"] == 1.0`.
- [x] Applying a second, wrong answer for a different item ("い") sets
      `skills["hiragana"] == 0.5` (mean of `1.0` and `0.0`), not `0.0`.
- [x] Re-answering the same item updates its score in place (not counted
      twice in the mean): correct "あ", correct "い", wrong "あ" again →
      `skills["hiragana"] == 0.5`.
- [x] A result with `item=None` still sets the skill directly to the result
      score (unchanged behavior), covered by an existing test
      (`test_student_applies_assessment`).

## Out of Scope
- Tracking which skill each `Knowledge` item belongs to. `Knowledge` stays a
  single flat map; this spec assumes one skill's items live there at a time
  (true today: only hiragana). Multi-skill separation is a future spec if
  katakana/kanji items are added to the same student.
- Weighting recent answers more than old ones (e.g. spaced repetition). That
  is Phase 3 in the roadmap.
