---
name: spec-writer
description: Scaffold a new feature spec in docs/specs/ following this project's spec-driven workflow. Use when starting a new feature or fix that needs a spec before implementation.
---

# Spec Writer

Given a short feature description, create `docs/specs/NNN-short-name.md` where
`NNN` is the next unused 3-digit number in `docs/specs/`.

Use this exact template:

```markdown
# NNN: <Title>

## Problem
<Why this is needed. What is broken or missing today.>

## Behavior
<What the system does after this change, in plain language.>

## Acceptance Criteria
- [ ] <Testable statement>
- [ ] <Testable statement>

## Out of Scope
<What this spec explicitly does not cover.>
```

After writing the spec:
1. Show it to the user for approval before writing any test or code.
2. Once approved, write the test(s) from the acceptance criteria first, then
   the implementation, then run `pytest`.
3. Update `docs/ROADMAP.md` to check off the item if it was listed there.
