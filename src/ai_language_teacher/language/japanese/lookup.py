"""Find course words in a student's message, to ground the AI teacher (spec 027)."""

import re
import unicodedata

from ai_language_teacher.language.japanese.hiragana import HIRAGANA
from ai_language_teacher.language.japanese.kanji import KANJI_LESSONS
from ai_language_teacher.language.japanese.vocabulary import VOCABULARY_LESSONS

# Romaji straight from the course's kana lessons; っ and ー are handled below.
ROMAJI = {kana: romaji for kana, romaji in HIRAGANA.items() if kana != "っ"}
# Shorter romaji keys ("do" for どう, "ie" for いえ) collide with English words.
MIN_ROMAJI_KEY = 3


def to_romaji(kana: str) -> str:
    # Katakana and hiragana blocks are 0x60 apart; ー stays as it is.
    text = "".join(chr(ord(char) - 0x60) if "ァ" <= char <= "ヶ" else char for char in kana)
    romaji = ""
    double = False
    i = 0
    while i < len(text):
        if text[i] == "っ":
            double, i = True, i + 1
            continue
        if text[i : i + 2] in ROMAJI:
            syllable, i = ROMAJI[text[i : i + 2]], i + 2
        elif text[i] == "ー":
            syllable, i = romaji[-1:], i + 1
        else:
            syllable, i = ROMAJI.get(text[i], text[i]), i + 1
        if double:
            # Small っ doubles the next consonant; before "ch" romaji writes "t".
            syllable = ("t" if syllable.startswith("ch") else syllable[:1]) + syllable
            double = False
        romaji += syllable
    return romaji


def _ascii(text: str) -> str:
    # Drops macrons too: "kōhī" -> "kohi".
    return "".join(c for c in unicodedata.normalize("NFKD", text.lower()) if c.isascii())


def _key(romaji: str) -> str:
    # Long vowels are ignored: "arigatou" = "arigato", "koohii" = "kohi".
    return re.sub(r"([aiueo])\1+|ou", lambda match: match.group(0)[0], _ascii(romaji))


def _vocabulary() -> list[tuple[str, str, set[str], str]]:
    entries = []
    for lesson in VOCABULARY_LESSONS:
        for item, meaning in lesson.items.items():
            reading = lesson.teaching[item].reading or item
            romaji = to_romaji(reading)
            keys = {_key(romaji)}
            if reading.endswith("は"):  # こんにちは is said "konnichiwa"
                keys.add(_key(romaji[:-2] + "wa"))
            keys = {key for key in keys if len(key) >= MIN_ROMAJI_KEY}
            entries.append((item, reading, keys, f"{item} ({reading}, {romaji}): {meaning}"))
    return entries


def _kanji() -> list[tuple[str, str]]:
    entries = []
    for lesson in KANJI_LESSONS:
        for item, meaning in lesson.items.items():
            teaching = lesson.teaching[item]
            readings = [
                f"{name}: {', '.join(values)}"
                for name, values in [("kun", teaching.kun_readings), ("on", teaching.on_readings)]
                if values
            ]
            entries.append((item, f"{item}: {meaning} ({'; '.join(readings)})"))
    return entries


VOCABULARY_ENTRIES = _vocabulary()
KANJI_ENTRIES = _kanji()


def find_course_words(message: str) -> list[str]:
    """One line per course word in the message: vocabulary first, then kanji."""
    # ponytail: exact words only; conjugated forms ("tabemasu") need grammar
    # the course does not teach yet.
    tokens = re.findall("[a-z]+", _ascii(message))
    # Single words plus two or three joined words, for "ohayou gozaimasu".
    keys = {
        _key("".join(tokens[i : i + n])) for n in (1, 2, 3) for i in range(len(tokens) - n + 1)
    }
    found = [
        line
        for item, reading, romaji_keys, line in VOCABULARY_ENTRIES
        if item in message or (len(reading) > 1 and reading in message) or romaji_keys & keys
    ]
    return found + [line for item, line in KANJI_ENTRIES if item in message]
