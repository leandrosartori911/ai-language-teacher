# 029: Navigation and a friendlier dashboard

> Approved by the user on 2026-10-14; implementation starts next
> session. Structure and flow only; the look is spec 030.

## Problem
The user found the profile's main page confusing: one line per course
with "Study" and "Practice" buttons and dense numbers
(`hiragana · 14% · 4 / 18 lessons · 1 due`), then the other courses as
grey text. Moving around relies on clicking "AI Language Teacher" in
the header or the name in a small breadcrumb. A screenshot review on
2026-10-14 (desktop and phone widths) found more:

- On a phone-sized screen the dashboard's Practice button is pushed off
  the screen, and the quiz question heading is cut off (to confirm in a
  real browser).
- Form buttons (Check, Ask, Explain my mistake) are unstyled browser
  buttons, while Study/Practice/Next are styled links: two button looks.
- "Practise" (page title) and "Practice" (button) are both used.
- The practice breadcrumb repeats the title ("Ana · practice hiragana").
- Study shows no progress inside a session (how many reviews and new
  items are left) and never says when a new lesson unlocks.
- "Nothing to study right now" is a dead end with one small link.
- The feedback page lists "Your answer" and "Expected" as plain lines;
  the result is easy to miss.

## Behavior
- **Header navigation** on every profile page: Dashboard, the open
  courses, the profile name and Logout (spec 026). The current page is
  marked (`aria-current="page"`).
- **Dashboard as a home screen:**
  - A main **Continue** button: the first course, in course order, with
    reviews due; otherwise the first open course with new items;
    otherwise "All done for today" with the date of the next review
    (no link).
  - One card per course with its Japanese name and a sample character
    (ひらがな あ, カタカナ ア, 漢字 漢, 語彙 語), a progress bar
    (`<progress>`), lessons unlocked, reviews due, and Study and
    Practice buttons.
  - Locked courses as cards that say what opens them and the progress
    toward it ("Master hiragana to open: 14%").
- **Study progress:** every study screen shows "N reviews, M new left",
  counted from the existing study queue (reviews due plus new items of
  the unlocked lessons). The new count can grow when a lesson unlocks;
  the unlock message explains the jump.
- **Unlock messages:** the feedback page compares the unlocked lessons
  and open courses before and after the answer, and says what was
  unlocked ("Lesson 2 unlocked: hiragana k row", "Katakana is now
  open!"). No new stored state.
- **End screen** (nothing left to study): the next review date, how many
  reviews are due tomorrow, and buttons to Practice and the Dashboard.
  No per-session statistics (they would need stored session state).
- **Feedback:** correct or wrong shown at a glance in a result block,
  with the student's answer next to the expected one.
- **One word, one meaning:** "Practice" everywhere; page titles and
  back links consistent; the practice breadcrumb no longer repeats the
  title.
- **One button style:** every action, link or form button, uses the
  same `button` class (the look itself is spec 030).
- All of this works at 360 px wide with no horizontal scrolling.

## Acceptance Criteria
- [ ] Every profile page has the header navigation with the current
      page marked.
- [ ] Continue goes to the first course with due reviews, else the first
      open course with new items, else shows "All done for today" and
      the next review date.
- [ ] Each course card shows its Japanese name, progress, lessons
      unlocked and reviews due; locked cards say what opens them and the
      progress toward it.
- [ ] Study screens show how many reviews and new items are left.
- [ ] Answering the item that unlocks a lesson or opens a course shows a
      message saying so; other answers show none.
- [ ] The end screen shows the next review, tomorrow's review count, and
      links to Practice and the Dashboard.
- [ ] "Practise" no longer appears; all actions share the button class.
- [ ] Checked by hand in a browser at 360 px wide: no horizontal
      scrolling, no cut-off headings or buttons.

## Decisions (user, 2026-10-14)
- Continue order: due reviews first (course order), then new items,
  then "All done for today".
- The left counter comes from the existing study queue.
- End screen without per-session statistics.
- Unlock messages from a before/after comparison on the feedback page.

## Out of Scope
- Colors, typography, illustrations and animation (spec 030).
- New learning features (shuffled practice, kana input exercises).
