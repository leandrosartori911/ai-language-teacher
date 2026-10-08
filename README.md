# AI Language Teacher

An open-source, local AI language teacher, starting with Japanese. It
teaches, not only quizzes: every item comes with an explanation, a
mnemonic, an example and, often, a note on history or culture. Spaced
repetition brings items back when you are about to forget them, and an
optional local LLM answers your questions about each lesson.

Everything runs on your machine, free: no account, no cloud service, no
data leaves your computer.

> Status: v0.1.0, first release. Japanese only.

## What you can learn

| Course | Content |
|---|---|
| Hiragana | All 105 items: basic rows, dakuten/handakuten (が, ぱ...), combinations (きゃ, しょ...) and small っ |
| Katakana | All 106 items: the same, plus the long vowel mark ー; examples are loanwords |
| Kanji | 40 essential JLPT N5 kanji: meaning quiz, kun and on readings taught |
| Vocabulary | 100 N5 words with readings and example sentences |

All teaching content was written in English for this project.

## How it works

- **Study:** a new item first shows its teaching card, then a quiz. Reviews
  come back on a Leitner schedule (1, 2, 4, 8, 16 days); a wrong answer
  brings the item back today.
- **Mastery-based progression:** the next lesson unlocks at 80% mastery
  of the previous one, and katakana opens once hiragana is mastered
  (then kanji and vocabulary). Unlocks are permanent.
- **Practice:** go back over any unlocked lesson. Practice never pushes a
  review further away.
- **Dashboard:** mastery, unlocked lessons and reviews due today, per
  course. Several profiles can share one computer.
- **AI teacher (optional):** ask a question on any teaching card, or press
  "Explain my mistake" after a wrong answer. A local model answers from
  that item's lesson content only.

## Quickstart

Needs Python 3.11 or newer.

```powershell
git clone https://github.com/leandrosartori911/ai-language-teacher.git
cd ai-language-teacher
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # macOS/Linux: source .venv/bin/activate
pip install .
ai-language-teacher               # then open http://127.0.0.1:8000
```

Progress is saved in `~/.ai-language-teacher/data.db`. The app only
listens on `127.0.0.1` and has no login.

## AI teacher (optional)

Questions go to a local LLM through [Ollama](https://ollama.com), together
with the item's lesson content; the model is told to use only that
content and never to write new Japanese sentences. Without Ollama the app
works the same, and the teacher page says how to start it.

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

## How it is built

- Python, FastAPI and Jinja2 templates, SQLite (standard library), no
  JavaScript. Lesson content is JSON shipped inside the package.
- Spec-driven: every feature starts as a short spec in
  [docs/specs](docs/specs), tests come from its acceptance criteria and
  are written before the code. Design decisions are recorded in
  [docs/adr](docs/adr).
- CI runs `ruff`, `mypy --strict` and `pytest` on Ubuntu and Windows
  (Python 3.11 and 3.13), and checks that an installed wheel serves the app.

For development:

```powershell
pip install -e ".[dev]"
ruff check . ; mypy ; pytest
```

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) and [CHANGELOG.md](CHANGELOG.md).

## License

MIT. See [LICENSE](LICENSE).
