# 028: Chat with the AI teacher

> Status: **draft, not approved yet** (recorded 2026-10-14). Review and
> approve before tests. Depends on spec 027 (guardrails).

## Problem
Asking the teacher today is a small text box that posts a form and opens
another page (sometimes a new tab) with one answer. It feels strange
next to every other AI chat the user knows, there is no follow-up
question, and the student leaves the lesson to read the answer.

## Behavior
- A chat panel, like a normal AI chat: message bubbles for the student
  and the teacher, an input at the bottom, Enter to send, the answer
  appearing in the same panel without leaving the page.
- The panel is available on study and practice pages, opened by a
  button (on a phone it takes the full screen). It knows the item on
  screen; the conversation follows the student from item to item, and
  each message is grounded on the item being studied when it was sent.
- "Explain my mistake" opens the panel with the explanation request
  already sent, instead of a new tab.
- Follow-up questions work: the last few turns are sent to the model
  (Ollama `/api/chat` with a message list), capped so the prompt stays
  small.
- The answer streams in word by word, so slow machines show progress.
- The guardrails of spec 027 apply to every turn.
- When Ollama is not running, the panel says how to start it; the rest
  of the page keeps working.
- This needs JavaScript for the first time in the project: a small,
  dependency-free script served from `static/`.
- The ask page and the new-tab behavior of specs 024-025 are removed.

## Acceptance Criteria
- [ ] Sending a message adds the student's bubble, then the teacher's
      answer, without a page reload.
- [ ] A follow-up question is sent with the previous turns (capped), and
      the current item's lesson content.
- [ ] "Explain my mistake" opens the panel with the explanation.
- [ ] The answer streams; a slow answer shows progress.
- [ ] Ollama not running shows the start instructions in the panel.
- [ ] The panel works with the keyboard alone and on a phone-sized
      screen.
- [ ] Nothing in the chat changes progress; the conversation is not
      stored in the database.

## Open questions
- Should the conversation be saved per profile (history across days)?
  Proposal: no in this spec; it would need a schema change.
- A general chat about Japanese, not tied to an item, needs a way to
  find the right lesson content (search over the lessons). Proposal:
  later spec; this one always grounds on the current item.

## Out of Scope
- Voice input or output.
- Saving conversations.
- The final visual style of the panel (spec 030 restyles it).
