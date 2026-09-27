# 007: Lesson data shipped inside the package

## Problem
Lesson JSON files live in the repo-root `data/` folder, outside the
Python package. `hiragana.py` and `katakana.py` find them with
`Path(__file__).resolve().parents[4] / "data" / ...`, which climbs out of
`src/` to the repo root. This only works for an editable install
(`pip install -e .`). A normally installed package (a built wheel) does
not contain `data/`, so importing the hiragana or katakana module crashes
with `FileNotFoundError`. The web app and any release need the package to
work when installed normally.

## Behavior
- Lesson files move from `data/japanese/` to
  `src/ai_language_teacher/data/japanese/` (same file names, same
  content). The repo-root `data/` folder is removed.
- `pyproject.toml` declares the JSON files as package data, so they are
  included in the built wheel.
- `hiragana.py` and `katakana.py` locate their file with the standard
  library's `importlib.resources.files("ai_language_teacher")`, not with
  `parents[4]`. The `# ponytail:` notes about dev-only paths are removed.
- `load_lesson` accepts a `str`, a `Path`, or an `importlib.resources`
  resource, and reads it as UTF-8 text. Its validation and question
  generation do not change.
- CI builds a wheel, installs it (not editable) into a fresh virtual
  environment, and imports the hiragana and katakana lessons from outside
  the repo folder.

## Acceptance Criteria
- [x] `HIRAGANA` and `KATAKANA` load with the same content as before.
- [x] The lesson files are read from inside the installed
      `ai_language_teacher` package (a test checks the resolved file is
      under the package directory).
- [x] `load_lesson` works with a `str` path, a `Path`, and an
      `importlib.resources` resource.
- [x] No code refers to the repo-root `data/` folder any more.
- [x] A wheel built from the repo contains both JSON files, and importing
      the lessons from a non-editable install works (checked locally once
      and in CI).
- [x] All other existing tests pass. The one test that opens
      `"data/japanese/hiragana_vowels.json"` by a repo-relative path is
      updated to the new location; no other test changes.

## Out of Scope
- New lesson content or changes to the JSON format (spec 009 adds
  teaching content).
- Discovering lessons automatically from a folder; each language module
  still names its own files.
- Publishing to PyPI.
