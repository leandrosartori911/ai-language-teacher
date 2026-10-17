# 0005: Flag theme, system fonts, automatic dark mode

- Status: accepted
- Date: 2026-10-17

## Context
Before the release the app looked like a bare HTML document (spec 030).
Two static mockups were made in the session scratchpad and shown to the
user at 1280 px and 360 px, in light and dark: each showed the
dashboard, a teaching card, the feedback screen and the open chat, with
real lesson content (か).

- **A, calm and minimal:** cool paper background, ink text, one seal
  red; the kana in a Mincho font inside a calligraphy practice square;
  a 正 stamp for a correct answer; thin borders, 4 px radius.
- **B, bold flag:** white and the flag's red (`#bc002d`); a solid red
  header with pill-shaped navigation and buttons; the kana in white
  inside the red sun disc; feedback as a full block of green or red;
  14 px radius, heavy headings.

The `ui-ux-pro-max` design-system search suggested claymorphism in
indigo with downloaded children's fonts; it was set aside because it
breaks the project's rules (system fonts only) and ignores the two
directions the user had already chosen.

## Decision
1. The user chose **B, the flag theme**, on 2026-10-17.
2. The tokens live in `style.css` `:root` (values below); a
   per-language theme later only overrides them.
3. Dark mode follows the system (`prefers-color-scheme: dark`) by
   redefining the color tokens; there is no toggle. In dark mode the
   header keeps a deep red (`--brand: #9e0026`) instead of the light
   pink accent, which was too loud as a full band.
4. System fonts only, with a Japanese-capable stack: Segoe UI and
   Yu Gothic UI / Meiryo on Windows, Hiragino Sans on macOS, Noto Sans
   CJK JP on Linux. Nothing is downloaded or bundled.
5. `tests/test_design_tokens.py` checks every text/background pair the
   pages use for WCAG AA (4.5:1) in both schemes, and the course colors
   for 3:1 against the surface (they fill bars and borders, not text).

| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#ffffff` | `#181818` | page background |
| `--surface` | `#ffffff` | `#222222` | cards, panels |
| `--text` | `#222222` | `#f2f2f2` | body text |
| `--muted` | `#5c5c5c` | `#b0b0b0` | secondary text |
| `--accent` | `#bc002d` | `#ff5c72` | links, buttons, highlights |
| `--on-accent` | `#ffffff` | `#181818` | text on accent, correct and wrong fills |
| `--accent-soft` | `#fbe9ec` | `#3a1c22` | soft red panels ("Did you know?") |
| `--border` | `#e4e4e4` | `#383838` | borders |
| `--correct` | `#1b7f3b` | `#6fd38e` | correct answer |
| `--wrong` | `#bc002d` | `#ff5c72` | wrong answer, errors |
| `--brand` | `#bc002d` | `#9e0026` | header band |
| `--on-brand` | `#ffffff` | `#ffffff` | text on the header |
| `--course-hiragana` | `#bc002d` | `#ff5c72` | course color |
| `--course-katakana` | `#1f4fa3` | `#84aaf0` | course color |
| `--course-kanji` | `#222222` | `#f2f2f2` | course color |
| `--course-vocabulary` | `#b25a00` | `#f0a65a` | course color |

Scales: type `--step--1` to `--step-3` (0.875, 1, 1.3, 1.8, 2.6 rem);
spacing `--space-1` to `--space-5` (0.25, 0.5, 1, 1.5, 2.5 rem);
`--radius` 14 px, `--radius-small` 10 px; `--shadow` a faint red-tinted
shadow in light mode, none in dark.

## Consequences
- Red means both "brand" and "wrong answer"; feedback must never rely on
  color alone (the heading says "Correct!" or "Not quite.").
- Spec 031 restyles every page with these tokens; until then the old
  page rules use the new tokens and already follow dark mode.
- A theme for another language is a new set of color tokens.

## Alternatives considered
- A, calm and minimal: liked, not chosen; its practice square for the
  kana could return as a detail later.
- Downloaded web fonts or a CSS framework: rejected, the app must work
  offline with zero cost and no new dependency.
- A dark mode toggle: rejected for now, the system setting is enough.
