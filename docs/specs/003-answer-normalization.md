# 003: Answer normalization and multiple accepted answers

## Problem
`Assessment.evaluate` compares `student_answer == self.expected_answer`
exactly. A student who types `"A"`, `" a"`, or `"a "` for あ is marked wrong
even though the answer is correct. Some romaji also have more than one
accepted spelling (e.g. し is both "shi" and "si"), which a single
`expected_answer` string cannot represent.

## Behavior
- Before comparing, both the student answer and each expected answer are
  normalized: stripped of leading/trailing whitespace and lowercased.
- `Assessment.expected_answer` accepts either a single string (unchanged,
  most lessons need only one answer) or a list of strings (any one of them
  counts as correct).
- `evaluate` returns `correct=True` if the normalized student answer equals
  any normalized expected answer.

## Acceptance Criteria
- [x] `Assessment("hiragana", "a").evaluate("A")` is correct.
- [x] `Assessment("hiragana", "a").evaluate(" a ")` is correct.
- [x] `Assessment("hiragana", "a").evaluate("i")` is still wrong.
- [x] `Assessment("hiragana", ["shi", "si"]).evaluate("si")` is correct.
- [x] `Assessment("hiragana", ["shi", "si"]).evaluate("SHI")` is correct.
- [x] `Assessment("hiragana", ["shi", "si"]).evaluate("shu")` is wrong.
- [x] `Assessment.from_question` still works unchanged when
      `question.expected_answer` is a plain string.

## Out of Scope
- Fuzzy/typo-tolerant matching (e.g. Levenshtein distance).
- Changing existing lesson content to use multiple accepted answers; this
  spec only adds the capability.
