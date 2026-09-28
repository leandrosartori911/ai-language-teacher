# AI Language Teacher

An open-source, local AI language teacher, starting with Japanese.

The goal is a tutor that checks real mastery before unlocking the next stage,
adapts lessons to student performance, and later supports speaking practice,
all without paid cloud services.

> Status: early development (v0.1.0). Complete hiragana and katakana.

## Features (current)

- Teaching content for every item: explanation, mnemonic, example word
  and culture notes, written in English for this project
- Item-level knowledge tracking, kept separately per skill
- Mastery-based progression: the next lesson unlocks at 80% mastery of the
  previous one
- Questions, assessments and lessons as small, tested building blocks
- Lessons: complete hiragana and katakana: basic rows, dakuten/handakuten
  (が, ぱ...), combinations (きゃ, しょ...), small っ and the long vowel mark ー

## Quickstart

```powershell
git clone <repo-url>
cd ai-language-teacher
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
```

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md). Features are described in
[docs/specs](docs/specs) before they are built.

## License

MIT. See [LICENSE](LICENSE).
