# 022: Practise previous lessons

## Problem
Study (spec 021) only offers what spaced repetition says is due. A student
who wants to go back over an earlier lesson (before a test, or because a
row of kana feels shaky) has no way to do it. Free practice must not
break the schedule: a lucky streak of correct answers must never push a
card's next review further away.

## Behavior
- Rule (confirmed by the user): in practice, a **wrong** answer demotes
  the item's card and counts toward mastery; a **correct** answer counts
  toward mastery but **never moves the card** (box and due date stay).
- Practice covers only **learned items**: items that already have a
  review card (seen at least once in Study). Items never studied stay for
  Study, which shows their teaching card first.
- Core, in `core/review.py`:
  - `learned_items(student, skill, lesson) -> list[str]`: the lesson's
    items that have a card, in lesson order.
  - `record_practice(student, result, today)`: applies the assessment
    (mastery), then on a wrong answer sets the card to box 1 due today
    (same as a wrong answer in Study). A correct answer leaves the card
    untouched. Raises `ValueError` for a result without an item or for an
    item that has no card.
- Web:
  - Dashboard: each open skill also gets a "Practice" link to
    `/practice/<skill>/<name>`.
  - `GET /practice/<skill>/<name>`: lists the skill's unlocked lessons
    by number and title with "N of M learned". Lessons with learned items
    link to `?lesson=<number>` (numbers start at 1, in course order).
  - `GET /practice/<skill>/<name>?lesson=<number>&n=<position>`
    (`n` defaults to 0): quizzes the learned item at that position, in
    lesson order, showing "item 2 / 5". No teaching card before the
    question (these items are already learned). If `n` is past the end:
    "Practice complete" with links to the lesson list and to Study. If
    the lesson has no learned items: "Nothing learned in this lesson
    yet" with a link to Study.
  - `POST /practice/<skill>/<name>` (form fields `lesson`, `n`, `item`,
    `answer`): checks the answer with the core assessment, calls
    `record_practice` and saves. The feedback page matches Study's
    (correct or not, your answer, expected answer, teaching card after a
    wrong answer) with a "Next" link to position `n + 1`.
    - The item must be a learned item of that lesson; otherwise nothing
      is recorded and it redirects (303) to the lesson's practice page.
    - A blank answer returns 400 and shows the question again.
  - A lesson that is not unlocked returns 403; a lesson number that is
    not a number or out of range returns 404. Unknown skill or student:
    404; skill not open: 403 (as in Study).
- Order is the lesson's own order, not shuffled, so the page needs no
  stored session state; the position travels in the URL.

## Acceptance Criteria
- [x] `learned_items` returns only the lesson's items that have a card,
      in lesson order.
- [x] `record_practice` with a wrong answer sets knowledge to 0.0 and the
      card to box 1 due today, even from a high box.
- [x] `record_practice` with a correct answer sets knowledge to 1.0 and
      leaves the card's box and due date unchanged.
- [x] `record_practice` raises `ValueError` for an item without a card
      and for a result without an item.
- [x] The dashboard shows a Practice link for each open skill only.
- [x] The lesson list shows each unlocked lesson with "N of M learned",
      links only lessons with learned items, and does not list locked
      lessons.
- [x] `?lesson=1` quizzes the first learned item with "item 1 / N" and no
      teaching card; `n` picks later items.
- [x] A correct practice answer is saved (knowledge 1.0), the card is
      unchanged, and the feedback links to the next position.
- [x] A wrong practice answer is saved (card box 1 due today) and the
      page shows the expected answer and the teaching card.
- [x] Past the last item the page says "Practice complete"; a lesson with
      no learned items says "Nothing learned in this lesson yet".
- [x] Posting an item that is not a learned item of the lesson records
      nothing and redirects (303); a blank answer returns 400 and records
      nothing.
- [x] A locked lesson returns 403; a lesson number that is out of range
      or not a number returns 404; a locked skill returns 403.
- [x] A practice post with a foreign `Origin` returns 403 (spec 021
      middleware).

## Out of Scope
- Shuffling items, practising a whole skill or several lessons at once.
- A session score or summary at the end.
- Practising items never studied (Study teaches them first).
- Due-review counts on the dashboard (separate spec) and the Ollama
  teacher (Phase D, separate specs).
