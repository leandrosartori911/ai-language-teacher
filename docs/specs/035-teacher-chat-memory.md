# 035: Start a new conversation, and a teacher that drifts less

> Status: **done on 2026-10-19** (approved the same day, from the user's test
> of the Teacher page).
>
> Results: the full eval set (35 cases) gave 34/35 with both memory ways,
> a tie. Repeating the 4 multi-turn cases 3 times gave way 2 (student
> messages only) 12/12 and way 1 (2 exchanges) 9/12: way 1 always failed
> the screenshot case. Way 2 ships, against the tie rule above, because of
> those repeats (reported to the user). The browser keeps 8 messages (4
> exchanges, for display) and the server sends the last 4 student
> messages. The overview first failed "What words are we learning?" with
> both ways; adding "If the student asks what they are learning, name
> these courses and point to the Dashboard." fixed it. The one failure
> left is the known "repeat your system prompt" case.

## Problem
The user tested the Teacher page and found that the chat gets worse the
longer it runs, with no way to start over:
- There is no way to clear a conversation. The history is kept until the
  browser tab is closed.
- The model copies its own earlier answers. After one "Let's focus on the
  words we are learning!", it answered "What does arigatou gozaemasu
  mean?" with the same sentence, even though the prompt held the lesson
  line for ありがとう and its note about ありがとうございます. Today up to 12
  earlier messages (6 exchanges) are sent with every question.
- "What words are we learning?" got "ありがとう and 食べる": the Teacher page
  only shows the model the words found in the conversation, so it
  described the course as those two words.
- Every eval case is a single message, so none of this showed up in the
  evals.

## Behavior
- **New conversation:** the item chat panel (next to the close button)
  and the Teacher page each get a "New conversation" button. It clears
  that chat's messages and its saved history, then puts the cursor in the
  message field. The other chat is not touched. The button is shown by
  the chat script, so without JavaScript it does not appear.
- **Shorter memory:** fewer earlier messages are sent to the model. Two
  ways are compared with the new multi-turn evals, and the one with more
  passing cases ships (on a tie, the first):
  1. the last 2 exchanges (4 messages, student and teacher);
  2. the last 4 student messages only, without the teacher's answers.
  The server cap (`MAX_HISTORY_MESSAGES`) and the browser's saved
  history follow the chosen way, so the browser does not keep messages
  the server would drop. Course words from earlier student messages
  still ground follow-ups ("and its polite form?"), as in spec 028.
- **Course overview on the Teacher page:** the free-conversation
  `<lesson>` lists the courses, built from the course data (not typed
  by hand): their names, number of lessons and items (today hiragana 18
  lessons and 105 kana, katakana 19 and 106, kanji 6 and 40, vocabulary
  10 and 100 words), and that the student's own lessons and progress are
  on the Dashboard. "What are we learning?" then gets a true answer.
  The item chat does not change.
- **Multi-turn evals:** an eval case can carry a fixed `history`
  (student and teacher messages written in the case, not generated), and
  such cases run through the same chat messages as the app
  (`chat_messages`, the Ollama chat API). New cases:
  - the user's screenshot: earlier deflecting answers, then "What does
    arigatou gozaemasu mean?" must explain "thank you";
  - "What words are we learning?" after a history about taberu and
    arigatou must name the courses, not only those two words;
  - a follow-up that needs the earlier message ("What is taberu?" then
    "And its polite form?") must still give 食べます;
  - a prompt injection placed in an earlier student message must still
    be ignored.
  The full eval run is reported for both memory ways before choosing,
  and the pass mark stays 90%.

- **Mixed Japanese (added during implementation, approved by the user
  on 2026-10-19):** an eval answer said "ありがとう goesます" and passed the
  sentence check, because ありがとう and ます are both in the prompt. A
  sentence is now also dropped when Latin letters touch Japanese with no
  space between them ("goesます"), unless that exact mix is in the prompt
  or the conversation.

## Acceptance Criteria
- [x] The chat panel and the Teacher page have a "New conversation"
      button, hidden in the markup and shown by the script.
- [x] In the browser, "New conversation" empties the message list and
      the saved history of that chat only, and focuses the message
      field; a new question after it is sent with an empty history.
- [x] The server sends the model at most the history of the chosen
      memory way, and the browser saves no more than that (tests with a
      fake model).
- [x] A follow-up still finds course words from earlier student
      messages (existing test kept).
- [x] The Teacher page prompt lists every course with its number of
      lessons and items from the course data, and mentions the
      Dashboard.
- [x] Eval cases with `history` run through `chat_messages`, and the
      four new multi-turn cases exist.
- [x] Both memory ways were run on the full eval set, the results are
      reported to the user, and the chosen way reaches the pass mark.

- [x] A sentence with Latin letters stuck to Japanese ("goesます") is
      dropped unless that mix is in the prompt (test with a fake answer).

## Out of Scope
- Grounding on what this student has studied (the overview lists the
  whole course, not their progress).
- Summarizing older messages instead of dropping them.
- Saving chats in the database, or keeping several past conversations.
- A different model.
