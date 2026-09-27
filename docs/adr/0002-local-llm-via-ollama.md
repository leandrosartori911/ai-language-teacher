# 0002: The AI teacher uses a local LLM via Ollama, on top of a rule-based core

- Status: accepted
- Date: 2026-09-27

## Context
The teacher should really teach Japanese, including culture, history and
beliefs, not only quiz. Cloud LLM APIs teach well but cost money per use,
and the project has a hard zero-cost constraint. The developer machine
has an RTX 5060 (8 GB VRAM) and 32 GB RAM, and Ollama is already
installed.

## Decision
1. Build a rule-based teacher first: hand-written explanations,
   mnemonics, examples and culture notes stored as lesson data,
   rule-based feedback, spaced repetition.
2. Add a local LLM through Ollama on top of it, for conversation, error
   explanations and cultural discussion. Prompts are grounded on the
   curated content, because small models invent facts about culture and
   history.
3. If Ollama is not running, the app falls back to the rule-based teacher.

The model is chosen later by comparing 2-3 candidates for Japanese
quality on this hardware.

## Consequences
- Zero running cost, and no student data leaves the machine.
- The app works without a GPU or a model, just with less depth.
- Answer quality is limited by what an ~8B model can do; curated content
  carries the factual weight.
- A public online demo with the LLM is not free (it needs a GPU server),
  so the portfolio demo is a local run plus a recorded GIF.

## Alternatives considered
- Cloud API (e.g. Claude): better teaching quality, but paid per use.
- No LLM at all: simpler, but the culture and conversation goals would
  feel thin.
