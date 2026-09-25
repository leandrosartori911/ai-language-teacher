# 001: Assessment.from_question

## Problem
Building an `Assessment` for a `Question` today means copying `expected_answer`
and `item` by hand from the question into the assessment call. This repeats
data that already lives on `Question` and risks copy mistakes (e.g. wrong
`item`, so an answer updates the wrong knowledge entry).

## Behavior
`Assessment` gains a class method `from_question(skill, question)` that
builds an `Assessment` using `question.expected_answer` and `question.item`,
so callers only pass the skill and the question.

## Acceptance Criteria
- [x] `Assessment.from_question(skill, question)` returns an `Assessment` with
      `skill` set to the given skill, `expected_answer` set to
      `question.expected_answer`, and `item` set to `question.item`.
- [x] The result of `.evaluate(answer)` on that assessment behaves exactly
      like building the `Assessment` manually with the same values.
- [x] Test suite grows from 17 to 19 passed (two tests added, one per
      criterion above; `test_progress.py` also updated to use
      `from_question` instead of the manual copy it demonstrated).

## Out of Scope
- Changing how `Assessment.evaluate` scores answers.
- Normalizing or validating the student answer (spec 003).
