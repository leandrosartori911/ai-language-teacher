# 0004: Default model qwen2.5:7b, chosen by the student, explaining only curated content

- Status: accepted
- Date: 2026-10-08

## Context
ADR 0002 left the model choice for later. The project is meant to run on
other people's machines, not only on the developer's (RTX 5060, 8 GB
VRAM), so the model should not assume strong hardware.

Five local models were compared on 2026-10-08 with the same six tasks,
each grounded on real lesson content: teach a new kana, correct a wrong
answer, answer a student question, a hallucination trap ("who invented
hiragana, and in which year?", which the content does not answer), write
a new example sentence, and reply to "こんにちは！" in hiragana only.
Temperature 0, one run per task, on the developer's GPU.

| Model | Size | Tokens/s | Result |
|---|---|---|---|
| qwen2.5:7b | 4.7 GB | ~84 | All six tasks right; natural Japanese (`水をください。`, `なまえは なんですか？`). |
| llama3.1:8b | 4.9 GB | ~80 | Grounded tasks good; wrong reading in a new sentence (`水を注ぐ` read "つく"); used kanji when asked for hiragana. |
| gemma3:4b | 3.3 GB | ~110 | Best answer to the trap, but stated "ぬ means dog" and wrote a wrong translation and a wrong romaji question. |
| qwen2.5:3b | 1.9 GB | ~165 | Invented a mnemonic and dated the Heian period 794-1868 (it ended in 1185); wrong reading `のびます`. |
| phi3:mini | 2.2 GB | ~155 | Read 月曜日 with つき, invented "made by monks", and ran away for 40 s producing broken Japanese. |

Most mistakes appeared when a model had to produce **new Japanese**
(tasks 5 and 6). Rephrasing curated content (tasks 1-4) was much safer,
except for the smallest models, which also invented facts there.

## Decision
1. The default model is `qwen2.5:7b`.
2. The student can choose another Ollama model with one setting (the
   spec that adds the LLM defines it). The README lists the tested models
   and what hardware they need.
3. The LLM explains and rephrases the curated lesson content and answers
   questions about it. It is told not to write new Japanese sentences;
   new Japanese stays in hand-checked lesson data.
4. No small model is recommended: below ~7B, the tested models invented
   facts even when grounded. On weaker machines the app runs without the
   LLM, using the rule-based teacher (ADR 0002, decision 3).

## Consequences
- Machines without a GPU with ~6 GB of VRAM can still run the 7B model on
  the CPU (about 16 GB RAM), only slower; or skip the LLM entirely.
- Students who know better models for their hardware are free to use
  them, at their own risk.
- Conversation practice in Japanese (task 6) is not part of the MVP.
- Model quality changes fast; this comparison should be re-run when a new
  candidate looks promising. The test script was a throwaway in the
  session scratchpad; the six tasks are described above.

## Alternatives considered
- Default to a small model (gemma3:4b, qwen2.5:3b) so more machines run
  it: rejected, a teacher that states wrong facts is worse than none.
- Fixed model, no choice: rejected, hardware varies too much.
