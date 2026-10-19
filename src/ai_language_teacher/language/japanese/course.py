from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.language.japanese.hiragana import HIRAGANA_LESSONS
from ai_language_teacher.language.japanese.kanji import KANJI_LESSONS
from ai_language_teacher.language.japanese.katakana import KATAKANA_LESSONS
from ai_language_teacher.language.japanese.vocabulary import VOCABULARY_LESSONS

COURSES: dict[str, list[Lesson]] = {
    "hiragana": HIRAGANA_LESSONS,
    "katakana": KATAKANA_LESSONS,
    "kanji": KANJI_LESSONS,
    "vocabulary": VOCABULARY_LESSONS,
}

# Japanese name and a sample character for each course card (spec 029).
COURSE_LABELS: dict[str, tuple[str, str]] = {
    "hiragana": ("ひらがな", "あ"),
    "katakana": ("カタカナ", "ア"),
    "kanji": ("漢字", "漢"),
    "vocabulary": ("語彙", "語"),
}


def course_overview() -> str:
    """One line per course for the Teacher page prompt (spec 035)."""
    return "\n".join(
        f"- {skill}: {len(lessons)} lessons, {sum(len(each.items) for each in lessons)} items"
        for skill, lessons in COURSES.items()
    )


PREREQUISITES: dict[str, str | None] = {
    "hiragana": None,
    "katakana": "hiragana",
    "kanji": "katakana",
    "vocabulary": "katakana",
}
