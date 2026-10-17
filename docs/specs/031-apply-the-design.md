# 031: Apply the design to every page

> Status: **done on 2026-10-17**, approved the same day (split from spec 030 on
> 2026-10-15). Builds on the flag theme and tokens of spec 030 (ADR 0005).

## Problem
Once the look is chosen (spec 030), the pages still use default fields,
plain text for readings and culture notes, and a chat panel that covers
the header (including Logout) on wide screens. The browser tab shows no
icon, and every page load asks for a `/favicon.ico` that returns 404.

## Behavior
- **Components from the tokens:** buttons (primary and secondary
  variants of the one `button` class from spec 029), text fields,
  cards, progress bars, the result block and the header menu all use
  the spec 030 tokens; no raw browser fields remain.
- **The flag look (ADR 0005, user's choice on 2026-10-17):** the header
  is a red band (`--brand`) with a small sun disc beside the name;
  navigation links and buttons are pill-shaped; the current page is a
  white pill.
- **Japanese as the hero:** the item is large, white, inside the red sun
  disc on teaching and quiz cards (a long word stretches the disc into a
  pill with a smaller font). Each course card has a top border in its
  course color and its sample character large and faint in the corner.
- **Header on a phone (user's choice):** the navigation stays one row
  and scrolls sideways when it does not fit, instead of wrapping into a
  column.
- **Feedback** is one full block of color: green for correct, red for
  wrong, with the text in `--on-accent`.
- **Readings with `<ruby>`:** the reading sits above the word (native
  HTML furigana) wherever a word and its reading are shown together: the
  example word or sentence (romaji over kana for kana lessons, user's
  choice; kana over kanji for kanji and vocabulary) and a vocabulary
  word whose reading differs from it (a word written only in kana gets
  no ruby and no separate reading line). No library.
- **Culture notes** in a distinct "Did you know?" box.
- **Feedback animation:** a short animation on the result block
  (correct and wrong differ), turned off under
  `prefers-reduced-motion: reduce`.
- **Chat panel:** restyled with the tokens. The header stays at the top
  of the window while scrolling. On wide screens the chat opens below
  the header and the page content moves aside to make room, so the
  header and Logout stay usable; on a phone it stays full screen.
- **Favicon:** a small SVG icon shipped as package data and linked from
  `base.html`.

## Design skills
Use `ui-ux-pro-max:ui-ux-pro-max` and `frontend-design:frontend-design`
as described in spec 030; the project's rules win over their
suggestions.

## Acceptance Criteria
- [x] Every page uses the tokens; no unstyled `input` or `button`
      remains.
- [x] Example readings (kana and kanji lessons) and vocabulary readings
      that differ from the word are shown with `<ruby>`.
- [x] The item is shown in the sun disc on teaching and quiz cards.
- [x] On a phone the header navigation is one row that scrolls sideways
      (a test checks the CSS rule).
- [x] Culture notes appear in a "Did you know?" box.
- [x] The feedback animation is disabled under
      `prefers-reduced-motion: reduce` (a test checks the CSS rule).
- [x] With the chat open on a wide screen, the header and Logout stay
      visible and clickable.
- [x] The favicon is served from the installed package (CI `wheel`
      smoke step) and linked from every page.
- [x] Any new text/background pair is added to the contrast test.

## Out of Scope
- Choosing the look (spec 030).
- Keyboard focus and the final three-width check (spec 032).
- Changing what pages do (specs 026-029 own behavior).
