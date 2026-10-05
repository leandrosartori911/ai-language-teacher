# 021: Study a skill in the browser

## Problem
The web app (spec 020) shows where a student stands, but nothing can be
studied yet: the teaching cards, quiz, spaced repetition and unlocking
from Phase B are only reachable from Python code. This slice makes the
core loop work in the browser: learn an item, answer it, come back when
it is due. Because these pages now change saved progress, the app also
needs basic protection against other websites posting to it.

## Behavior
- Dashboard: each open skill gets a "Study" link to
  `/study/<skill>/<name>`. Skill first and the name last, so names
  containing "/" stay unambiguous (the name uses the `:path` converter,
  as in spec 020).
- `GET /study/<skill>/<name>` shows the first item of `study_queue` (due
  reviews first, then new items from unlocked lessons, in course order):
  - **New item** (no review card yet): a teaching card with the item, its
    explanation, mnemonic, example (word, reading, meaning), culture note
    if any, kun/on readings (kanji) and word reading (vocabulary), and a
    "Quiz me" link to the same page with `?step=quiz`. The answer form is
    not on this page, so the answer is not visible while answering.
  - **Due review**, or a new item with `?step=quiz`: the question prompt
    (e.g. "What is the romaji for あ?") and a text field to answer.
  - **Queue empty**: "Nothing to study right now", the date of the next
    review if any card exists, and a link back to the dashboard.
- `POST /study/<skill>/<name>` (form fields `item` and `answer`):
  - The item must be in the current study queue. If not (for example the
    form was sent twice), nothing is recorded and it redirects (303) back
    to the study page. This also means an item can never be promoted
    before it is due.
  - A blank answer returns 400 and shows the quiz again; nothing is
    recorded.
  - Otherwise the answer is checked with `Assessment.from_question(...)
    .evaluate`, applied with `record_answer(student, result, today)`, and
    the student is saved. The feedback page says whether it was correct,
    shows the student's answer and the main expected answer; after a
    wrong answer it also shows the teaching card again. A "Next" link
    goes back to the study page.
  - Unlocking needs no extra code: the next `study_queue` call already
    includes items from a newly unlocked lesson.
- Unknown student or skill: 404. A skill that is not open: 403.
- "Today" comes from `create_app(db_path, today=date.today)`, so tests
  can fix the date; the app never reads the clock elsewhere.
- Security (new, applies to every page):
  - **Host check** with Starlette's built-in `TrustedHostMiddleware`:
    only `127.0.0.1` and `localhost` are accepted (others get 400). This
    blocks DNS rebinding, where a malicious site points its own domain at
    `127.0.0.1` to read and post to the app.
  - **Origin check** on every `POST` (also `POST /students`): if the
    browser sends an `Origin` header that is not this app's own
    (`http://<host>`), the request gets 403 and nothing is saved.
    Requests without `Origin` (non-browser clients) are allowed.
  - Existing spec 020 tests switch the test client to
    `http://127.0.0.1:8000`, since its default host `testserver` is
    rejected now.

## Acceptance Criteria
- [x] The dashboard shows a Study link for each open skill and none for
      locked skills.
- [x] A new student studying hiragana sees the teaching card for あ
      (explanation, mnemonic, example, culture note) and a "Quiz me" link,
      but no answer form.
- [x] `?step=quiz` shows "What is the romaji for あ?" and an answer form
      for あ.
- [x] An item whose review is due is quizzed directly, without the
      teaching card, before any new item.
- [x] A correct answer is saved: the item's knowledge is 1.0 and its card
      moves up a box, due according to `BOX_INTERVALS`; the page says it
      was correct.
- [x] A wrong answer is saved: card in box 1 due today; the page shows the
      expected answer and the teaching card.
- [x] Answers are checked like the core assessment (e.g. "SHI" and "si"
      are both accepted for し).
- [x] Posting an item that is not in the study queue records nothing and
      redirects (303) to the study page.
- [x] Posting a blank answer returns 400 and records nothing.
- [x] After every item of the first hiragana lesson is answered
      correctly, the study page offers the first item of the second
      lesson.
- [x] With nothing due and nothing new, the page says so and shows the
      next review date.
- [x] A kanji teaching card shows kun and on readings; a vocabulary card
      shows the word's reading.
- [x] Studying a locked skill returns 403; an unknown skill or student
      returns 404.
- [x] A request with a host other than `127.0.0.1` or `localhost`
      returns 400.
- [x] A `POST` (to `/students` or a study page) with a foreign `Origin`
      returns 403 and saves nothing; the same post with the app's own
      `Origin` works.

## Out of Scope
- Free practice of any unlocked lesson (separate "review previous
  lessons" spec, still to confirm: never promotes cards early).
- Due-review counts on the dashboard, "lesson unlocked" messages, a
  session summary or daily goal.
- JavaScript, keyboard shortcuts, audio, typo tolerance.
- CSRF tokens: the Origin and host checks cover a localhost-only app
  without logins; add tokens if the app ever runs on a network.
- Choosing between several due items differently than `study_queue`
  already does.
