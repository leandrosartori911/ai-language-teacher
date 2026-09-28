# AI Language Teacher

An open-source, local AI language teacher, starting with Japanese.

The goal is a tutor that checks real mastery before unlocking the next stage,
adapts lessons to student performance, and later supports speaking practice,
all without paid cloud services.

> Status: early development (v0.1.0). Hiragana and katakana with dakuten.

## Features (current)

- Teaching content for every item: explanation, mnemonic, example word
  and culture notes, written in English for this project
- Item-level knowledge tracking, kept separately per skill
- Questions, assessments and lessons as small, tested building blocks
- Lessons: all basic hiragana and katakana plus dakuten/handakuten (が, ぱ...),
  one lesson per row, and the katakana long vowel mark ー

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
