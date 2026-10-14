# 029: Navigation and a friendlier dashboard

> Status: **draft, not approved yet** (recorded 2026-10-14). Review and
> approve before tests. Structure and flow only; the look is spec 030.

## Problem
The user found the profile's main page confusing: one line per course
with "Study" and "Practice" buttons and dense numbers
(`hiragana · 14% · 4 / 18 lessons · 1 due`), then the other courses as
grey text. Moving around relies on clicking "AI Language Teacher" in
the header or the name in a small breadcrumb. A screenshot review on
2026-10-14 (desktop and phone widths) found more:

- On a phone-sized screen the dashboard's Practice button is pushed off
  the screen, and the quiz question heading is cut off (to confirm in a
  real browser's device mode).
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
  marked. Real buttons, no reliance on the logo link.
- **Dashboard as a home screen:**
  - A main "Continue" action that starts the most useful thing now
    (due reviews first, otherwise new items of the current course).
  - One card per course with its Japanese name and sample character
    (ひらがな あ, カタカナ ア, 漢字, 語彙), a progress bar, lessons
    unlocked, reviews due, and Study / Practice buttons.
  - Locked courses as cards that say what opens them, with the progress
    toward it ("Master hiragana: 14%").
- **Study session flow:** a progress indicator ("3 reviews, 5 new
  left"), a clear message when a lesson or a course unlocks, and an end
  screen with what was done and what comes next, linking to Practice or
  the dashboard.
- **Feedback:** correct/wrong shown at a glance, the student's answer
  next to the expected one.
- **One word, one meaning:** "Practice" everywhere; consistent page
  titles and back buttons.
- All of this works at phone width (no horizontal scrolling).

## Acceptance Criteria
- [ ] Every profile page has the header navigation with the current
      page marked.
- [ ] The dashboard has a Continue action that goes to due reviews
      first, then new items.
- [ ] Each course card shows progress, lessons unlocked and reviews due;
      locked cards say what opens them and the progress toward it.
- [ ] Study shows how many reviews and new items are left.
- [ ] Answering the item that unlocks a lesson or a course shows a
      message saying so.
- [ ] The study end screen links to Practice and the dashboard.
- [ ] No page scrolls horizontally at 360 px wide (checked in tests by
      structure, and by hand in a browser).

## Out of Scope
- Colors, typography, illustrations and animation (spec 030).
- New learning features (shuffled practice, kana input exercises).
