# 030: Web UI design (the release's face)

> Status: **draft, not approved yet** (recorded 2026-10-14). **Top
> priority for quality**: the user wants this done last and done with
> care, because the public demo GIF and the release depend on it.
> Probably split into smaller specs once the design is agreed.

## Problem
The app works but looks like a bare HTML document: a white page, a thin
red line, default fonts and browser buttons. Nothing feels like
studying Japanese, and nothing invites a visitor of the repository to
try it. The project rule is to publish the GIF and the release only
when the app is presentable: good-looking and working well.

## Behavior
- **Design first, then code:** before implementation, agree on a visual
  direction with the user using mockups (static HTML pages or images of
  the dashboard, a study card, feedback and the chat). Two or three
  directions to choose from, for example: calm and minimal (paper,
  ink, one red accent, like Japanese stationery); warm and playful
  (rounded cards, gentle color per course); bold flag theme (red and
  white, the "theme per language" idea from the roadmap).
- **A small design system in CSS variables** (already the pattern in
  `style.css`): color tokens, a type scale, spacing, radius, shadows,
  one button style with primary/secondary variants, form fields, cards,
  progress bars, and dark mode.
- **Japanese text that looks good:** a Japanese-capable font stack, big
  and clear characters on teaching and quiz cards; readings shown above
  or under the word in a consistent way.
- **Immersion:** course colors and Japanese names, the character as the
  hero of every card, subtle feedback (a short animation on correct or
  wrong), culture notes styled as a distinct "Did you know?" box.
- **Works everywhere:** phone, tablet and desktop; keyboard navigation
  with visible focus; WCAG AA contrast; respects reduced motion.
- **Still zero cost and offline:** no CDN or web font downloads at
  runtime (the app must work without internet); any font is either the
  system's or bundled with a free license. No CSS framework unless the
  design agreement shows a clear need.
- **Chat panel (spec 028):** restyle it; on a wide screen it currently
  covers the header, including the Logout button, while open.

## Acceptance Criteria
- [ ] A design direction is chosen by the user from mockups, and saved
      in an ADR with the tokens.
- [ ] Every page uses the shared tokens and components; no raw browser
      buttons or fields remain.
- [ ] Every page works at 360 px, 768 px and 1280 px wide.
- [ ] Contrast meets WCAG AA; all actions work by keyboard with visible
      focus; motion respects `prefers-reduced-motion`.
- [ ] The app works with the network disconnected.
- [ ] The user approves the result in the browser before the GIF is
      recorded.

## Out of Scope
- Changing what the pages do (specs 026-029 own behavior).
- More languages (the theme tokens keep that cheap later).
