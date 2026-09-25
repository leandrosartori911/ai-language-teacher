from pathlib import Path

from ai_language_teacher.language.loader import load_lesson

# ponytail: path climbs out of src/ to the repo-root data/ folder, so this
# only works for an editable/dev install. Move data/ under the package (or
# add it as package_data) before shipping a real wheel.
DATA_FILE = Path(__file__).resolve().parents[4] / "data" / "japanese" / "hiragana_vowels.json"

HIRAGANA_VOWELS_LESSON = load_lesson(DATA_FILE)
HIRAGANA = HIRAGANA_VOWELS_LESSON.items
