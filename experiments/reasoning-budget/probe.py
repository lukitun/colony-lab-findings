#!/usr/bin/env python3
"""Reasoning-budget probe: does a small max_tokens leave a reasoning model with an empty answer?
Asks a trivial prompt N times at a small and a large token budget, and logs finish_reason,
usage and whether any visible text came back."""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import chat, log

PROMPT = "Say hi in 3 words or fewer."

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="+")
    ap.add_argument("--budgets", default="80,1024")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--out", default="out/reasoning_budget.jsonl")
    a = ap.parse_args()
    for m in a.models:
        for b in [int(x) for x in a.budgets.split(",")]:
            got = 0
            for i in range(a.reps):
                r = chat(m, [{"role": "user", "content": PROMPT}], max_tokens=b, temperature=0.3,
                         timeout=a.timeout, retries=1)
                log(a.out, dict(model=m, max_tokens=b, rep=i, **r))
                got += r["ok"]
            print(f"{m:45s} max_tokens={b:5d} non-empty {got}/{a.reps}", flush=True)

if __name__ == "__main__":
    main()
