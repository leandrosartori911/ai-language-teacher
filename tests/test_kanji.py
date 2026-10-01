import json

import pytest

from ai_language_teacher.core.assessment import Assessment
from ai_language_teacher.core.progression import unlocked_lessons
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.hiragana import HIRAGANA_LESSONS
from ai_language_teacher.language.japanese.kanji import KANJI, KANJI_LESSONS
from ai_language_teacher.language.japanese.katakana import KATAKANA_LESSONS
from ai_language_teacher.language.loader import load_lesson

EXPECTED_LESSONS = [
    ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"],
    ["百", "千", "万", "円"],
    ["日", "月", "火", "水", "木", "金", "土"],
    ["人", "子", "女", "男", "父", "母", "友"],
    ["上", "下", "中", "大", "小", "左", "右"],
    ["年", "時", "分", "半", "今"],
]

ALL_QUESTIONS = [(lesson, q) for lesson in KANJI_LESSONS for q in lesson.questions]
ALL_TEACHING = [(item, t) for lesson in KANJI_LESSONS for item, t in lesson.teaching.items()]


def is_hiragana(text):
    return all("ぁ" <= char <= "ゟ" for char in text)


def is_katakana(text):
    return all("ァ" <= char <= "ヿ" for char in text)


def accepted(question):
    answers = question.expected_answer
    return [answers] if isinstance(answers, str) else answers


def test_six_lessons_with_the_expected_kanji_in_order():
    assert [list(lesson.items) for lesson in KANJI_LESSONS] == EXPECTED_LESSONS


def test_forty_kanji_none_repeated():
    assert len(KANJI) == 40
    assert sum(len(lesson.items) for lesson in KANJI_LESSONS) == 40


@pytest.mark.parametrize(("lesson", "question"), ALL_QUESTIONS)
def test_question_asks_for_the_meaning_and_accepts_every_listed_meaning(lesson, question):
    assert question.prompt == f"What does {question.item} mean?"
    assert lesson.items[question.item] in accepted(question)

    for meaning in accepted(question):
        assessment = Assessment("kanji", question.expected_answer, question.item)
        assert assessment.evaluate(meaning.upper()).correct


def test_kanji_with_several_meanings_accepts_each():
    month = next(q for _, q in ALL_QUESTIONS if q.item == "月")
    assessment = Assessment("kanji", month.expected_answer, "月")

    assert assessment.evaluate("moon").correct
    assert assessment.evaluate("month").correct


@pytest.mark.parametrize(("item", "teaching"), ALL_TEACHING)
def test_readings_use_the_right_script(item, teaching):
    assert teaching.kun_readings or teaching.on_readings

    for reading in teaching.kun_readings:
        assert reading.replace(".", "") and is_hiragana(reading.replace(".", ""))
    for reading in teaching.on_readings:
        assert is_katakana(reading)


@pytest.mark.parametrize(("item", "teaching"), ALL_TEACHING)
def test_teaching_content_with_hiragana_example_reading(item, teaching):
    assert teaching.explanation.strip()
    assert teaching.mnemonic.strip()
    assert item in teaching.example.word
    assert is_hiragana(teaching.example.reading)
    assert teaching.example.meaning.strip()


def test_new_student_has_only_numbers_lesson_unlocked():
    assert unlocked_lessons(Student("Test"), "kanji", KANJI_LESSONS) == [KANJI_LESSONS[0]]


def test_kana_lessons_have_no_readings_and_romaji_prompts():
    for lesson in HIRAGANA_LESSONS + KATAKANA_LESSONS:
        for teaching in lesson.teaching.values():
            assert teaching.kun_readings == []
            assert teaching.on_readings == []

    assert HIRAGANA_LESSONS[0].questions[0].prompt == "What is the romaji for あ?"


ITEM = {
    "item": "水",
    "answer": "water",
    "explanation": "Water.",
    "mnemonic": "A stream.",
    "example": {"word": "水", "reading": "みず", "meaning": "water"},
}


def write(tmp_path, items, **top):
    path = tmp_path / "lesson.json"
    path.write_text(json.dumps({"title": "Test", **top, "items": items}), encoding="utf-8")
    return path


def test_loader_reads_kun_and_on_readings(tmp_path):
    lesson = load_lesson(write(tmp_path, [{**ITEM, "kun": ["みず"], "on": ["スイ"]}]))

    assert lesson.teaching["水"].kun_readings == ["みず"]
    assert lesson.teaching["水"].on_readings == ["スイ"]


def test_loader_without_readings_gives_empty_lists(tmp_path):
    teaching = load_lesson(write(tmp_path, [ITEM])).teaching["水"]

    assert teaching.kun_readings == []
    assert teaching.on_readings == []


@pytest.mark.parametrize("bad", [{"kun": "みず"}, {"on": ["スイ", " "]}, {"kun": [1]}])
def test_loader_rejects_bad_readings(tmp_path, bad):
    with pytest.raises(ValueError, match="水"):
        load_lesson(write(tmp_path, [{**ITEM, **bad}]))


def test_question_template_sets_every_prompt(tmp_path):
    fire = {**ITEM, "item": "火", "answer": "fire", "example": {**ITEM["example"], "word": "火"}}
    lesson = load_lesson(write(tmp_path, [ITEM, fire], question="What does {item} mean?"))

    assert [q.prompt for q in lesson.questions] == ["What does 水 mean?", "What does 火 mean?"]


def test_item_prompt_overrides_question_template(tmp_path):
    item = {**ITEM, "prompt": "Custom?"}
    lesson = load_lesson(write(tmp_path, [item], question="What does {item} mean?"))

    assert lesson.questions[0].prompt == "Custom?"
