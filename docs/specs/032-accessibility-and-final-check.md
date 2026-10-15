# 032: Accessibility and the final check before the GIF

> Status: **draft, not approved yet** (split from spec 030 on
> 2026-10-15). Last spec before the release (Phase E).

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
- **Offline:** no template or stylesheet refers to another host; a test
  scans templates, CSS and JS for `http://` or `https://` URLs
  (localhost and the Ollama address excepted). The app is also opened
  once with the network disconnected.
- **Three widths:** every page checked in the browser at 360 px, 768 px
  and 1280 px, light and dark: no horizontal scrolling, nothing cut
  off.
- **The user approves** the result in the browser; then the demo GIF
  guide (given on 2026-10-14) is updated for the new flow.

## Design skills
Use `ui-ux-pro-max:ui-ux-pro-max` and `frontend-design:frontend-design`
as described in spec 030; the project's rules win over their
suggestions.

## Acceptance Criteria
- [ ] All actions work by keyboard with visible focus; Escape closes
      the chat.
- [ ] A test finds no external URL in templates, CSS or JS.
- [ ] The app works with the network disconnected (checked by hand).
- [ ] Every page checked at 360, 768 and 1280 px, light and dark.
- [ ] The user approves the result in the browser before the GIF.

## Out of Scope
- New visual changes beyond fixing what the checks find (spec 031).
- Recording the GIF and the release (Phase E).
