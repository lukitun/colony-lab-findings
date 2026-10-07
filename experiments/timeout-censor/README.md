# Timeout censoring: a slow model is not a dead model

**Question.** Our long-running model-availability sweep used a short per-call timeout. Some models flagged
"dead" might just be slow. How many?

**Design.**
- 11 models: every model the sweep had flagged, plus controls.
- 3 calls each with a 180 s timeout. Prompt: "say hi in two words". Concurrency 4.
- A model is CENSORED if it fails under the sweep's timeout but answers within 180 s.

**Result (2026-10-01).**
- 3 of the 10 models the sweep had flagged answered within 180 s (0.30). Their call times were 48 s; 52, 71 and
  99 s; and 113 and 150 s, with one timeout.
- Cut-off check, on the 7 slow successful calls: a 60 s timeout would catch 2 of them, 120 s would catch 5,
  and 180 s catches all 7.
- Corrected for this, the headline failure rate for one sweep round fell from 80.4% to 78.6% (one confirmed
  correction). The worst case is 75.0%.

**What we take from it.**
- A short timeout turns latency into apparent death.
- Report a SLOW-ALIVE class (answers only beyond the sweep timeout) next to the main series, rather than folding
  it into "failed".

**Limits.** 3 calls per model; latency on shared hosted endpoints varies by hour; one prompt.

**Reproduce.**
```
python3 probe.py --reps 3 --timeout 180 --cutoffs 20,60,120 MODEL_1 MODEL_2 ...
```
