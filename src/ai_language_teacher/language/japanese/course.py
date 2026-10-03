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

PREREQUISITES: dict[str, str | None] = {
    "hiragana": None,
    "katakana": "hiragana",
    "kanji": "katakana",
    "vocabulary": "katakana",
}
