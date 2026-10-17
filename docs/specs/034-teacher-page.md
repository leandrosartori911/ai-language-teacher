# 034: A page of its own for chatting with the teacher

> Status: **approved by the user on 2026-10-17** (from the user's review on
> 2026-10-17; the user chose "a page of its own in the menu").

## Problem
Every teaching card offers two ways into the same chat: the "Ask the
teacher about <item>" form and the "Chat with the teacher" button.
With JavaScript, the form already opens the chat panel, so the button
is a duplicate. A student also has no way to talk to the teacher
outside a teaching card, for example to ask about a course word while
looking at the dashboard.

## Behavior
- **Teaching card:** the "Chat with the teacher" button is removed.
  "Ask the teacher about <item>" stays and still opens the side panel
  about that item (spec 028, unchanged); asking again reopens a closed
  panel with its history.
- **Teacher page:** the header menu gets a "Teacher" link to
  `GET /teacher` (open profile required, like the other pages). It
  shows a full-page chat, not tied to any item: a message list and one
  field. The same chat script drives it; its history is kept apart
  from the item chat (its own `sessionStorage` key).
- **Grounding:** `POST /teacher` (JSON: message and history, the same
  shape and limits as `POST /chat/{skill}` minus the item) builds the
  prompt with `<lesson>` set to "none: free conversation, not about one
  item" and `<course_words>` from the course word lookup over the new
  and earlier student messages (spec 027). The system prompt rules and
  the sentence checks (`safe_stream`) are the same, so the teacher still
  only uses Japanese from the course and says when the lessons do not
  cover something. Rule 6 ("bring the student back to the lesson")
  reads "to their Japanese study" so it fits both places.
- **Without JavaScript** the Teacher page says that the chat needs
  JavaScript and points to the ask form on any teaching card.
- **Ollama not running:** the same message as the item chat.
- **Evals:** `evals/teacher_cases.json` gets free-conversation cases
  (no item: course words, a word outside the course, an off-topic
  message, a prompt injection); `run_teacher_evals.py` runs them through
  the Teacher page's prompt. All cases are re-run before commit and the
  result is reported (needs Ollama; the pass mark stays 90%).

## Acceptance Criteria
- [ ] No "Chat with the teacher" button on teaching cards; the ask form
      still opens the panel (checked in the browser).
- [ ] The header menu links to `/teacher` on pages with an open profile.
- [ ] `GET /teacher` without a profile redirects home; with one it shows
      the chat page.
- [ ] `POST /teacher` streams an answer from a prompt with no item, the
      course words found in the messages and the student's text inside
      `<student_message>`.
- [ ] `POST /teacher` rejects a blank or too long message (400) and
      a damaged history (422), like `/chat/{skill}`.
- [ ] When Ollama is not running, `POST /teacher` answers 503 with the
      `ollama pull` message.
- [ ] Invented Japanese is dropped from Teacher answers (test with a
      fake model).
- [ ] The free-conversation eval cases exist, and the full eval run
      reaches the pass mark (reported to the user).

## Out of Scope
- Grounding on what the student has studied so far (the whole course
  lookup is used).
- Saving chat history in the database.
- Voice, or answers in Japanese.
