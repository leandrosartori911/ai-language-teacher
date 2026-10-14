# 028: Chat with the AI teacher

## Problem
Asking the teacher today is a small text box that posts a form and opens
another page (sometimes a new tab) with one answer. It feels strange
next to every other AI chat the user knows, there is no follow-up
question, and the student leaves the lesson to read the answer.

## Behavior
- **Chat panel** wherever a teaching card is shown (new item, wrong
  answer in Study and Practice, the ask page): message bubbles for the
  student and the teacher, an input at the bottom, Enter to send, the
  answer appearing in the panel without leaving the page. On a wide
  screen it is a side panel; on a phone it takes the full screen.
  Escape or the close button hides it.
- It is not offered on quiz screens, where the teaching card is hidden
  on purpose: the chat knows the item, so it could give the answer away.
- Asking from the teaching card or pressing "Explain my mistake" opens
  the panel and sends the question there. Without JavaScript these forms
  still post to the ask page as before, but never in a new tab.
- **Follow-ups:** the conversation lives in the browser tab
  (`sessionStorage`): it follows the student from item to item and is
  gone when the tab is closed. Each message sends the last 6 exchanges
  with it; the server keeps nothing and cuts longer histories to 12
  messages of up to 1200 characters each. Each new message is grounded
  on the item of the page it was sent from, through the same lookup and
  prompt as spec 027; course words are looked up in the new message and
  in the student's earlier messages, so "and its polite form?" still
  knows the word. Earlier student messages are wrapped in
  `<student_message>` tags too.
- **Streaming, sentence by sentence:** the server uses Ollama's
  `/api/chat` with streaming, collects each full sentence, runs the
  spec 027 output check on it and only then sends it. The student sees
  progress and invented Japanese never reaches the screen. The 1200
  character cap applies to the whole answer.
- When Ollama is not running, the panel shows how to start it (HTTP
  503); the rest of the page keeps working.
- New route `POST /chat/<skill>` with a JSON body (`item`, `message`,
  `history`), with the same checks as the ask page: open profile, open
  skill, item in an unlocked lesson, message of 1 to 500 characters.
  It saves nothing.
- First JavaScript in the project: `static/chat.js`, small and without
  dependencies.

## Acceptance Criteria
- [ ] `POST /chat/<skill>` streams the checked answer as plain text,
      sentence by sentence.
- [ ] The model gets the system prompt, the capped earlier turns
      (student turns tagged) and the current item's prompt with course
      words.
- [ ] A sentence with invented Japanese is not sent; an answer with
      nothing left sends the fallback.
- [ ] Ollama not running answers 503 with the start instructions.
- [ ] Blank or overlong message: 400 without calling the model; invalid
      history: 422; no profile, locked skill, item outside unlocked
      lessons and foreign Origin are refused like the ask page. Nothing
      is saved.
- [ ] Pages with a teaching card include the panel and `chat.js`; quiz
      pages do not.
- [ ] Feedback forms no longer open a new tab.
- [ ] Checked by hand in a browser: sending adds both bubbles without a
      reload, the answer appears in steps, a follow-up uses the earlier
      turns, "Explain my mistake" opens the panel, keyboard only works,
      and the panel fills a phone-sized screen.

## Decisions (user, 2026-10-14)
- Stream sentence by sentence so the output check still applies.
- History in `sessionStorage`, server stateless, last 6 exchanges.
- Keep the ask page as the no-JavaScript fallback, without new tabs.
- Conversations are not saved per profile (would need a schema change).
- The history comes from the browser, so a student could edit it; that
  only affects their own chat on their own computer.

## Results (2026-10-14, checked in Chrome with `qwen2.5:7b`)
- Asking from the teaching card opened the panel and answered without a
  reload ("taberu means "to eat"..."). The chat survived a page reload
  in the same tab. "Explain my mistake" opened the panel, and the Next
  link stayed on the page. Escape closed the panel and returned focus to
  the "Chat with the teacher" button; Enter on it reopened the panel with
  focus in the input. Quiz screens showed no panel. At 390 px wide the
  panel filled the screen with no sideways scrolling. A timed request
  received the answer in four steps, one sentence each, the first after
  0.6 s.
- The first follow-up ("And what is its polite form?") got the fallback:
  the model answered 食べます, but the new message did not name the word,
  so the lookup found nothing and the output check removed it. Fixes,
  with tests: the chat also looks up course words in the student's
  earlier messages, and each word found now includes its curated
  explanation (polite form, particles). Afterwards the same follow-up
  got "The polite form of 食べる (taberu) is 食べます (tabemasu)."
- The red-team set then showed two side effects, both fixed with a test:
  the model sometimes copied prompt tags into its answer (they are now
  removed from answers), and a reading repeated for kana-only words
  ("ありがとう (ありがとう, arigatou)") led it to garble the kana (the
  repeat is dropped). Result: 25 of 26 again, same known failure.

## Out of Scope
- Voice input or output.
- Saving conversations.
- A general chat not tied to an item.
- The final visual style of the panel (spec 030 restyles it).
