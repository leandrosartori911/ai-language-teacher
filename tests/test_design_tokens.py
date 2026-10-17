"""Design tokens in style.css: light and dark colors, contrast, fonts (spec 030)."""

import re
from importlib.resources import files

import pytest

CSS = (files("ai_language_teacher.web") / "static" / "style.css").read_text(encoding="utf-8")

DARK = re.compile(r"@media\s*\(prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}")

COLOR_TOKENS = [
    "bg", "surface", "text", "muted", "accent", "on-accent", "accent-soft",
    "border", "correct", "wrong", "brand", "on-brand",
    "course-hiragana", "course-katakana", "course-kanji", "course-vocabulary",
]

# (text, background) pairs as the pages use them; WCAG AA for normal text.
TEXT_PAIRS = [
    ("text", "bg"), ("text", "surface"), ("text", "accent-soft"),
    ("muted", "bg"), ("muted", "surface"), ("muted", "accent-soft"),
    ("accent", "bg"), ("accent", "surface"), ("accent", "accent-soft"),
    ("on-accent", "accent"), ("on-accent", "correct"), ("on-accent", "wrong"),
    ("on-brand", "brand"),
    ("correct", "bg"), ("correct", "surface"),
    ("wrong", "bg"), ("wrong", "surface"),
]

# Course colors fill bars and borders: WCAG AA for UI components is 3:1.
COURSE_COLORS = ["course-hiragana", "course-katakana", "course-kanji", "course-vocabulary"]


def tokens(block: str) -> dict[str, str]:
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})\b", block))


def theme(name: str) -> dict[str, str]:
    light = re.search(r":root\s*\{([^}]*)\}", CSS)
    assert light, "no :root block"
    colors = tokens(light.group(1))
    if name == "dark":
        dark = DARK.search(CSS)
        assert dark, "no dark :root block"
        colors |= tokens(dark.group(1))
    return colors


def luminance(color: str) -> float:
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def test_contrast_formula_matches_known_values():
    assert contrast("#000000", "#ffffff") == pytest.approx(21)
    assert contrast("#777777", "#ffffff") == pytest.approx(4.48, abs=0.01)


def test_light_theme_defines_every_color_token():
    assert set(COLOR_TOKENS) <= set(theme("light"))


def test_dark_theme_redefines_every_color_token():
    dark = DARK.search(CSS)
    assert dark
    assert set(COLOR_TOKENS) <= set(tokens(dark.group(1)))


@pytest.mark.parametrize("name", ["light", "dark"])
@pytest.mark.parametrize(("fg", "bg"), TEXT_PAIRS)
def test_text_pairs_reach_wcag_aa(name, fg, bg):
    colors = theme(name)
    assert contrast(colors[fg], colors[bg]) >= 4.5


@pytest.mark.parametrize("name", ["light", "dark"])
@pytest.mark.parametrize("course", COURSE_COLORS)
def test_course_colors_stand_out_from_the_surface(name, course):
    colors = theme(name)
    assert contrast(colors[course], colors["surface"]) >= 3


def test_font_stack_is_system_fonts_covering_japanese():
    stack = re.search(r"--font:\s*([^;]+);", CSS)
    assert stack
    for font in ["Yu Gothic UI", "Meiryo", "Hiragino Sans", "Noto Sans CJK JP"]:
        assert font in stack.group(1)
    assert "@font-face" not in CSS
    assert "@import" not in CSS
    assert "url(" not in CSS


def test_body_uses_the_font_token():
    body = re.search(r"\bbody\s*\{([^}]*)\}", CSS)
    assert body
    assert "var(--font)" in body.group(1)


@pytest.mark.parametrize(
    "token", ["step-0", "step-1", "step-2", "step-3", "space-1", "space-3", "radius", "shadow"]
)
def test_scale_tokens_exist(token):
    assert re.search(rf"--{token}:", CSS)
