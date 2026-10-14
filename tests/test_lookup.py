import pytest

from ai_language_teacher.language.japanese.lookup import find_course_words, to_romaji


@pytest.mark.parametrize(
    ("kana", "romaji"),
    [
        ("たべる", "taberu"),
        ("しゃしん", "shashin"),
        ("きって", "kitte"),
        ("マッチ", "matchi"),
        ("コーヒー", "koohii"),
        ("おはようございます", "ohayougozaimasu"),
        ("じゅう", "juu"),
        ("ん", "n"),
    ],
)
def test_romaji_follows_the_course_kana_tables(kana, romaji):
    assert to_romaji(kana) == romaji


def items(text):
    return [line.split(" ")[0].rstrip(":") for line in find_course_words(text)]


@pytest.mark.parametrize(
    ("message", "word"),
    [
        ("What is the meaning of taberu?", "食べる"),
        ("what does arigatou mean", "ありがとう"),
        ("what does arigato mean", "ありがとう"),
        ("Konnichiwa!", "こんにちは"),
        ("Ohayou gozaimasu?", "おはようございます"),
        ("ohayo gozaimasu", "おはようございます"),
        ("kōhī", "コーヒー"),
        ("koohii", "コーヒー"),
        ("kohi", "コーヒー"),
        ("たべる means?", "食べる"),
        ("食べる means?", "食べる"),
        ("Is hai yes?", "はい"),
    ],
)
def test_finds_vocabulary_by_kana_kanji_or_romaji(message, word):
    assert word in items(message)


def test_found_vocabulary_line_has_reading_romaji_and_meaning():
    assert "食べる (たべる, taberu): to eat" in find_course_words("taberu")


def test_finds_kanji_by_character_with_readings():
    lines = find_course_words("Why does 四 look like that?")

    line = next(line for line in lines if line.startswith("四:"))
    assert "four" in line
    assert "kun:" in line and "on:" in line


def test_a_romaji_sentence_finds_each_course_word():
    found = items("What does watashi wa gakusei desu mean?")

    assert "私" in found
    assert "学生" in found


@pytest.mark.parametrize(
    "message", ["Thailand animal", "What do you mean?", "the meaning of wasuretai", "tabemasu"]
)
def test_no_match_inside_longer_words_short_keys_or_conjugations(message):
    assert find_course_words(message) == []


def test_each_word_is_listed_once():
    lines = find_course_words("taberu たべる 食べる")

    assert len([line for line in lines if line.startswith("食べる ")]) == 1
