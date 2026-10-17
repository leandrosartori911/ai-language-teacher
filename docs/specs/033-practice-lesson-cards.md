# 033: Practice page with lesson cards

> Status: **done on 2026-10-17**, approved the same day (from the user's review on
> 2026-10-17).

## Problem
The Practice page is a plain list. A lesson whose items were never
studied is plain text with no link, and nothing on the page says why:
the user tried to click "Hiragana K row" to learn it and could not.
Practice only reviews items that already have a card, and cards are
made by Study (spec 022), but the page does not explain that. It is
also the only page left without the flag design (specs 030-031).

## Behavior
- One line at the top explains the page: "Practice reviews what you
  already studied. New items come from Study."
- Each unlocked lesson is a card (`<li class="lesson">`) in the flag
  style: its number and title, a `<progress>` bar in the course color
  with "N / M learned", and one action:
  - N > 0: a primary "Practice" button to that lesson (same URL as
    today, `?lesson=<number>`);
  - N = 0: "Not studied yet." and a "Study" button to Study for that
    course.
- A lesson where every item is learned says so ("All learned") next to
  its bar; nothing else changes.
- The cards sit in the same responsive grid as the dashboard courses.
- Locked lessons are still not listed (unchanged).

## Acceptance Criteria
- [x] The page shows the line explaining Practice and Study.
- [x] Each unlocked lesson is a card with its title, a `<progress>`
      bar and "N / M learned".
- [x] A lesson with learned items has a "Practice" button to
      `?lesson=<number>`.
- [x] A lesson with nothing learned says "Not studied yet." and links
      to Study for that course, not to a practice quiz.
- [x] A fully learned lesson says "All learned".
- [x] No horizontal scrolling at 360, 768 and 1280 px (checked in the
      browser).

## Out of Scope
- What Practice does once a lesson is opened (spec 022, unchanged).
- Listing locked lessons, or studying a chosen lesson out of course
  order (Study keeps its order).
- Shuffled practice (Later list).
