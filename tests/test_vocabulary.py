import json

import pytest

from ai_language_teacher.core.assessment import Assessment
from ai_language_teacher.core.progression import unlocked_lessons
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.hiragana import HIRAGANA_LESSONS
from ai_language_teacher.language.japanese.kanji import KANJI_LESSONS
from ai_language_teacher.language.japanese.katakana import KATAKANA_LESSONS
from ai_language_teacher.language.japanese.vocabulary import VOCABULARY, VOCABULARY_LESSONS
from ai_language_teacher.language.loader import load_lesson

EXPECTED_LESSONS = [
    "おはようございます こんにちは こんばんは さようなら おやすみなさい"
    " ありがとう すみません いただきます はい いいえ",
    "私 あなた 先生 学生 友だち 家族 子ども 兄 姉 名前",
    "何 だれ どこ いつ どれ どの いくら いくつ どう どうして",
    "水 お茶 ご飯 パン 肉 魚 野菜 卵 コーヒー おいしい",
    "学校 家 駅 店 病院 銀行 会社 トイレ 部屋 国",
    "本 車 電車 電話 お金 傘 かばん 時計 テレビ 写真",
    "今日 明日 昨日 毎日 朝 昼 夜 今 時間 今年",
    "食べる 飲む 行く 来る 見る 聞く 話す 読む 書く 買う",
    "する ある いる 起きる 寝る 帰る 分かる 待つ 会う 休む",
    "大きい 小さい 高い 安い 新しい 古い 暑い 寒い 好き 楽しい",
]

ALL_QUESTIONS = [(lesson, q) for lesson in VOCABULARY_LESSONS for q in lesson.questions]
ALL_TEACHING = [(w, t) for lesson in VOCABULARY_LESSONS for w, t in lesson.teaching.items()]
SENTENCE_MARKS = set(" 、。")


def is_kana(text):
    return all("ぁ" <= char <= "ヿ" or char in SENTENCE_MARKS for char in text)


def accepted(question):
    answers = question.expected_answer
    return [answers] if isinstance(answers, str) else answers


def test_ten_lessons_with_the_expected_words_in_order():
    assert [list(lesson.items) for lesson in VOCABULARY_LESSONS] == [
        words.split() for words in EXPECTED_LESSONS
    ]


def test_hundred_words_none_repeated():
    assert len(VOCABULARY) == 100
    assert sum(len(lesson.items) for lesson in VOCABULARY_LESSONS) == 100


@pytest.mark.parametrize(("lesson", "question"), ALL_QUESTIONS)
def test_question_asks_for_the_meaning_and_accepts_every_listed_meaning(lesson, question):
    assert question.prompt == f"What does {question.item} mean?"
    assert lesson.items[question.item] in accepted(question)

    for meaning in accepted(question):
        assessment = Assessment("vocabulary", question.expected_answer, question.item)
        assert assessment.evaluate(meaning.upper()).correct


def test_verbs_accept_meaning_with_or_without_to():
    eat = next(q for _, q in ALL_QUESTIONS if q.item == "食べる")
    assessment = Assessment("vocabulary", eat.expected_answer, "食べる")

    assert assessment.evaluate("to eat").correct
    assert assessment.evaluate("eat").correct


@pytest.mark.parametrize(("word", "teaching"), ALL_TEACHING)
def test_every_word_has_a_kana_reading(word, teaching):
    assert teaching.reading
    assert is_kana(teaching.reading)
    assert " " not in teaching.reading


@pytest.mark.parametrize(("word", "teaching"), ALL_TEACHING)
def test_example_is_a_short_sentence_with_kana_reading(word, teaching):
    assert teaching.explanation.strip()
    assert teaching.mnemonic.strip()
    assert word in teaching.example.word
    assert teaching.example.word.endswith("。")
    assert is_kana(teaching.example.reading)
    assert teaching.example.meaning.strip()


def test_kana_and_kanji_lessons_have_no_word_reading():
    for lesson in HIRAGANA_LESSONS + KATAKANA_LESSONS + KANJI_LESSONS:
        for teaching in lesson.teaching.values():
            assert teaching.reading is None


def test_new_student_has_only_greetings_lesson_unlocked():
    student = Student("Test")

    assert unlocked_lessons(student, "vocabulary", VOCABULARY_LESSONS) == [VOCABULARY_LESSONS[0]]


ITEM = {
    "item": "水",
    "answer": "water",
    "explanation": "Water.",
    "mnemonic": "A stream.",
    "example": {"word": "水を飲む。", "reading": "みずをのむ。", "meaning": "I drink water."},
}


def write(tmp_path, item):
    path = tmp_path / "lesson.json"
    path.write_text(json.dumps({"title": "Test", "items": [item]}), encoding="utf-8")
    return path


def test_loader_reads_word_reading(tmp_path):
    lesson = load_lesson(write(tmp_path, {**ITEM, "reading": "みず"}))

    assert lesson.teaching["水"].reading == "みず"


def test_loader_without_reading_gives_none(tmp_path):
    assert load_lesson(write(tmp_path, ITEM)).teaching["水"].reading is None


@pytest.mark.parametrize("bad", ["", "  ", 1])
def test_loader_rejects_blank_reading(tmp_path, bad):
    with pytest.raises(ValueError, match="水"):
        load_lesson(write(tmp_path, {**ITEM, "reading": bad}))
