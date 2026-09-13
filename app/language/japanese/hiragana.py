from app.core.lesson import Lesson
from app.core.question import Question


HIRAGANA = {
    "あ": "a",
    "い": "i",
    "う": "u",
    "え": "e",
    "お": "o",
}


HIRAGANA_VOWELS_QUESTIONS = [
    Question("What is the romaji for あ?", "a", "あ"),
    Question("What is the romaji for い?", "i", "い"),
    Question("What is the romaji for う?", "u", "う"),
    Question("What is the romaji for え?", "e", "え"),
    Question("What is the romaji for お?", "o", "お"),
]


HIRAGANA_VOWELS_LESSON = Lesson(
    "Hiragana vowels",
    HIRAGANA,
    HIRAGANA_VOWELS_QUESTIONS,
)