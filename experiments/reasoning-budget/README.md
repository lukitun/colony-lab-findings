# Reasoning budget: an empty reply is not a dead model

**Question.** Some open-weight models reason before they answer, and the reasoning counts against
`max_tokens`. A health check with a small budget can get back an empty answer and record the model as broken.
How often does that happen?

**Design.**
- Prompt: "Say hi in 3 words or fewer.", temperature 0.3.
- 5 calls at `max_tokens=80` and 5 at `max_tokens=1024`, 120 s timeout.
- A reply counts as non-empty if visible text remains after any `<think>` block is removed.
- We also log `finish_reason` and token usage.

**Result (2026-10-02, 3 models).**

| model | non-empty at 80 | non-empty at 1024 | note |
|---|---|---|---|
| gpt-oss-20b | 0/5 (all `length`) | 5/5 | 68–115 completion tokens |
| muse-glimmer-30b | 0/5 (all `length`) | 5/5 | 286–373 completion tokens |
| glm-5.3 | 5/5 | 5/5 | slow: 6.7–46.9 s per call |

- Both reasoning models used up an 80-token budget before writing a word, so they returned nothing.
  At 1024 tokens both answered every time.
- In a further model, `max_tokens` did not cap the reasoning at all.

**What we take from it.**
- A liveness sweep needs a separate class, BUDGET-STARVED: empty content with `finish_reason=length`.
  Those models should be re-tested at a larger budget before they are called broken.

**Limits.** 5 calls per cell; one prompt; hosted endpoints can change their defaults.

**Reproduce.**
```
python3 probe.py --budgets 80,1024 --reps 5 MODEL_1 MODEL_2 ...
```
