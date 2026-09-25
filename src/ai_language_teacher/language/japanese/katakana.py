from pathlib import Path

from ai_language_teacher.language.loader import load_lesson

# ponytail: see the matching note in hiragana.py — editable/dev install only.
DATA_FILE = Path(__file__).resolve().parents[4] / "data" / "japanese" / "katakana_vowels.json"

KATAKANA_VOWELS_LESSON = load_lesson(DATA_FILE)
KATAKANA = KATAKANA_VOWELS_LESSON.items
