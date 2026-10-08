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

Open the app, create a profile, and study: new items come with a teaching
card, reviews come back when they are due, and the next lesson unlocks at
80% mastery. Any unlocked lesson can also be practised freely; practice
never pushes a review further away.

## Quickstart

```powershell
git clone <repo-url>
cd ai-language-teacher
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest
ai-language-teacher   # web app on http://127.0.0.1:8000
```

Progress is saved locally in `~/.ai-language-teacher/data.db`. The app only
listens on `127.0.0.1` and has no login.

## AI teacher (optional)

Every teaching card has an "Ask the teacher" box. Questions go to a local
LLM through [Ollama](https://ollama.com), grounded on the lesson content;
nothing leaves your machine. Without Ollama the app works the same, just
without that box answering.

```powershell
ollama pull qwen2.5:7b                 # default model, 4.7 GB
$env:AI_TEACHER_MODEL = "llama3.1:8b"  # optional: use another model
ai-language-teacher
```

Models tested on Japanese teaching tasks (see
[ADR 0004](docs/adr/0004-default-llm-model.md)):

| Model | Download | Verdict |
|---|---|---|
| `qwen2.5:7b` | 4.7 GB | Recommended. Needs a GPU with ~6 GB VRAM, or ~16 GB RAM on the CPU (slower). |
| `llama3.1:8b` | 4.9 GB | Usable; made mistakes writing new Japanese. |
| `gemma3:4b` | 3.3 GB | Not recommended: stated wrong facts. |
| `qwen2.5:3b`, `phi3:mini` | ~2 GB | Not recommended: invented facts even when grounded. |

On weaker machines, skip the LLM: the lesson cards and spaced repetition
work without it.

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md). Features are described in
[docs/specs](docs/specs) before they are built.

## License

MIT. See [LICENSE](LICENSE).
