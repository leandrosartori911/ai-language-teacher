# 032: Accessibility and the final check before the GIF

> Status: **done on 2026-10-17**, approved the same day; the user
> approved the result in the browser (split from spec 030
> on 2026-10-15). Last spec before the release (Phase E).

## Problem
After the redesign (specs 030-031) the app must be usable by keyboard,
readable, working offline, and good at every common screen size before
the demo GIF is recorded. Without one explicit final pass, small
regressions slip into the public release.

## Behavior
- **Keyboard:** every action can be reached and used with Tab, Enter
  and Escape (Escape closes the chat); focus is always visible
  (`:focus-visible` outline from the tokens), and the order follows
  the page.
- **Focus ring:** 3 px outline, 2 px offset, `--text` on the pages and
  `--on-brand` inside the red header (a red ring would vanish there);
  the contrast test checks it at 3:1 against each background it
  appears on.
- **Skip link:** the first element of every page is a "Skip to content"
  link to `<main id="main">`, visible only when it has focus.
- **Teaching card order:** "Quiz me", the main action, comes right
  after the card, before the ask form and the chat button.
- **Offline:** no template or stylesheet refers to another host; a test
  scans templates, CSS and JS for `http://` or `https://` URLs
  (localhost, the Ollama address and the SVG namespace
  `http://www.w3.org/2000/svg`, which is not a request, excepted).
  The browser's network log of every page shows only requests to
  `127.0.0.1`; the user may also open the app once with the network
  disconnected.
- **Three widths:** every page checked in the browser at 360 px, 768 px
  and 1280 px, light and dark: no horizontal scrolling (measured by a
  script in the browser), nothing cut off. Keyboard use is tried for
  real in the browser (claude-in-chrome).
- **The user approves** the result in the browser; then the demo GIF
  guide (given on 2026-10-14) is updated for the new flow.

## Design skills
Use `ui-ux-pro-max:ui-ux-pro-max` and `frontend-design:frontend-design`
as described in spec 030; the project's rules win over their
suggestions.

## Acceptance Criteria
- [x] All actions work by keyboard with visible focus; Escape closes
      the chat.
- [x] The focus ring reaches 3:1 against its backgrounds (test).
- [x] Every page starts with a working "Skip to content" link (test).
- [x] "Quiz me" comes before the ask form on the teaching card (test).
- [x] A test finds no external URL in templates, CSS or JS.
- [x] Every page requests only `127.0.0.1` (browser network log).
- [x] Every page checked at 360, 768 and 1280 px, light and dark.
- [x] The user approves the result in the browser before the GIF.

## Notes
- Fixed during the check: the page centers beside the open chat; the
  menu has its own row up to 1024 px; on a phone only the sun mark of
  the brand shows (the name stays for screen readers).
- Between 641 and 1024 px the open chat covers part of the page.
- The GIF guide update waits for the follow-up specs from the user's
  review (practice page, chat placement), which change the flow.

## Out of Scope
- New visual changes beyond fixing what the checks find (spec 031).
- Recording the GIF and the release (Phase E).
