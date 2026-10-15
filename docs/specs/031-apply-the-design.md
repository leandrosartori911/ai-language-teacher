# 031: Apply the design to every page

> Status: **draft, not approved yet** (split from spec 030 on
> 2026-10-15). Starts after 030's direction and tokens are approved.

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
- **Japanese as the hero:** the item is large and centered on teaching
  and quiz cards; each course card uses its course color.
- **Readings with `<ruby>`:** kana readings sit above the word (native
  HTML furigana) wherever a word and its reading are shown together
  (vocabulary readings, example words). No library.
- **Culture notes** in a distinct "Did you know?" box.
- **Feedback animation:** a short animation on the result block
  (correct and wrong differ), turned off under
  `prefers-reduced-motion: reduce`.
- **Chat panel:** restyled with the tokens. On wide screens it opens
  below the header and the page content narrows to make room, so the
  header and Logout stay usable; on a phone it stays full screen.
- **Favicon:** a small SVG icon shipped as package data and linked from
  `base.html`.

## Design skills
Use `ui-ux-pro-max:ui-ux-pro-max` and `frontend-design:frontend-design`
as described in spec 030; the project's rules win over their
suggestions.

## Acceptance Criteria
- [ ] Every page uses the tokens; no unstyled `input` or `button`
      remains.
- [ ] Vocabulary readings and example readings are shown with `<ruby>`.
- [ ] Culture notes appear in a "Did you know?" box.
- [ ] The feedback animation is disabled under
      `prefers-reduced-motion: reduce` (a test checks the CSS rule).
- [ ] With the chat open on a wide screen, the header and Logout stay
      visible and clickable.
- [ ] The favicon is served from the installed package (CI `wheel`
      smoke step) and linked from every page.

## Out of Scope
- Choosing the look (spec 030).
- Keyboard focus and the final three-width check (spec 032).
- Changing what pages do (specs 026-029 own behavior).
