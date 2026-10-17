# 030: Visual direction and design tokens

> Status: **done on 2026-10-17**: the user chose the flag theme (ADR 0005).
> Approved on 2026-10-15. Reviewed with the user on 2026-10-15 and split in three:
> 030 (this spec: direction and tokens), 031 (apply them to every page)
> and 032 (accessibility and the final check). Together they are the release's face, so they come last and
> are done with care.

## Problem
The app works but looks like a bare HTML document: a white page, a thin
red line, default fonts and browser fields. Nothing feels like studying
Japanese, and nothing invites a visitor of the repository to try it.
The project rule is to publish the GIF and the release only when the
app is presentable. Before restyling pages, the look has to be chosen
and written down once, so every page follows the same rules.

## Behavior
- **Mockups first:** two static HTML mockups, each showing the
  dashboard, a teaching card, a feedback screen and the open chat, at
  1280 px and 360 px wide, opened in the browser and shown to the user
  as screenshots. The two directions (user's choice, 2026-10-15):
  - **Calm and minimal:** paper and ink, one red accent, like Japanese
    stationery.
  - **Bold flag theme:** strong red and white, the roadmap's "theme per
    language" idea.
  Mockups are throwaway files in the session scratchpad, not committed.
- **The user picks one** (or a mix); the choice and its tokens are
  recorded in `docs/adr/0005-visual-design.md`.
- **Design tokens in `style.css` `:root`**, the existing pattern:
  colors (background, surface, text, muted text, accent, correct,
  wrong, border, one color per course), a type scale, spacing, radius
  and shadow.
- **Dark mode** follows the system (`prefers-color-scheme: dark`) by
  redefining the color tokens; no toggle.
- **Fonts:** the system's own fonts only, with a Japanese-capable stack
  (Yu Gothic / Meiryo on Windows, Hiragino on macOS, Noto Sans CJK on
  Linux). Nothing is downloaded, nothing is bundled.
- **Contrast is tested:** a test reads the color tokens from
  `style.css` (light and dark) and checks that each text color on each
  background it is used on reaches WCAG AA (4.5:1 for normal text).

## Design skills (user's request, 2026-10-15)
Use both skills for every web UI step of specs 030-032. They are
installed as Claude Code plugins with project scope (declared in
`.claude/settings.json`, so a fresh clone offers them):
- **`ui-ux-pro-max:ui-ux-pro-max`** (plugin `ui-ux-pro-max` from
  `nextlevelbuilder/ui-ux-pro-max-skill`, MIT): run its
  `--design-system` search for the visual direction, then `--domain`
  searches (`color`, `typography`, `ux`) for tokens, contrast,
  focus, motion and responsive checks. Its scripts need only Python.
- **`frontend-design:frontend-design`** (Anthropic's plugin from
  `claude-plugins-official`): to give each mockup a distinct,
  deliberate look instead of a generic one.
The project's rules win over their suggestions: system fonts only (no
Google Fonts or other downloads), no CSS framework, no new dependency,
FastAPI + Jinja2 + vanilla JS unchanged.

## Acceptance Criteria
- [x] Two mockups (calm, flag), made with the two design skills, shown
      to the user at 1280 px and 360 px.
- [x] The user's choice and its tokens are recorded in ADR 0005.
- [x] `style.css` defines the chosen tokens in `:root`, with a dark set
      under `prefers-color-scheme: dark`.
- [x] The font stack uses system fonts only and covers Japanese on
      Windows, macOS and Linux.
- [x] A test checks WCAG AA contrast for the text/background token
      pairs, light and dark.

## Out of Scope
- Restyling the pages themselves (spec 031).
- Keyboard focus, final checks at three widths, offline check (spec 032).
- A dark mode toggle; bundled or downloaded fonts; CSS frameworks.
- More languages (the tokens keep that cheap later).
