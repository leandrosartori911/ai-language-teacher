# 025: Explain my mistake

## Problem
After a wrong answer, the student sees the expected answer and the
teaching card, but not why their own answer was wrong. Typing "me" for
ぬ usually means the two kana were confused; the card says how to tell
them apart, but the student has to make the connection alone. ADR 0002
promised error explanations from the AI teacher, and spec 024 already
has everything needed to ask for one.

## Behavior
- The wrong-answer feedback page, in Study and in Practice, gets an
  "Explain my mistake" button. Correct answers do not get it.
- The button is a form posting to the existing `/ask/<skill>/<name>`
  route (spec 024) with the item and a ready-made question:
  `I answered "<answer>", but the right answer is "<expected>". Why is
  my answer wrong, and how can I remember the right one?`
  - `<expected>` is the item's main answer.
  - `<answer>` is the student's answer, cut to 100 characters so the
    question always fits the 500-character limit.
- The `/ask` route, its checks and its fallback when Ollama is not
  running stay as in spec 024. Nothing is saved.
- On feedback pages, the explain button and the "Ask the teacher" box
  open the answer in a new tab (labelled "opens in a new tab"), so the
  student keeps the feedback page and its Next link. In practice this
  keeps their place in the lesson, which the "Back to Study" link of the
  ask page would lose. Elsewhere (new item in Study, the ask page) the
  ask box opens in the same tab, as today.

## Acceptance Criteria
- [x] A wrong answer in Study shows an "Explain my mistake" form posting
      to `/ask/<skill>/<name>` with the item and a question containing
      the student's answer and the expected answer.
- [x] A wrong answer in Practice shows the same form.
- [x] A correct answer shows no "Explain my mistake" form.
- [x] A student answer longer than 100 characters is cut, and posting
      the resulting question is accepted (200).
- [x] Posting the explain question sends both answers and the item's
      lesson content to the teacher, and saves nothing.
- [x] On feedback pages the explain and ask forms have
      `target="_blank"`; on the new-item teaching card the ask form does
      not.

## Out of Scope
- Explaining automatically, without the student asking.
- Sending the student's earlier mistakes on the same item (history).
- Any change to grading, mastery or review cards.
- Kana input (roadmap "Later").
