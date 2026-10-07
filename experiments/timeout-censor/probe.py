#!/usr/bin/env python3
"""Timeout-censor probe: how many models that a short-timeout sweep calls 'dead' are only slow?
Calls each model N times with a long timeout and reports, for each candidate cut-off, how many
successful calls would have been censored."""
import argparse, os, sys, concurrent.futures as cf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from common import chat, log

PROMPT = "Say hi in two words."

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="+")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--cutoffs", default="20,60,120")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="out/timeout_censor.jsonl")
    a = ap.parse_args()
    jobs = [(m, i) for m in a.models for i in range(a.reps)]
    def run(j):
        m, i = j
        r = chat(m, [{"role": "user", "content": PROMPT}], max_tokens=1024, temperature=0.3,
                 timeout=a.timeout, retries=0)
        log(a.out, dict(model=m, rep=i, timeout=a.timeout, **r))
        return m, r
    res = {}
    with cf.ThreadPoolExecutor(a.workers) as ex:
        for m, r in ex.map(run, jobs):
            res.setdefault(m, []).append(r)
    cuts = [int(x) for x in a.cutoffs.split(",")]
    for m, rs in res.items():
        ok = [r["elapsed"] for r in rs if r["ok"]]
        cens = {c: sum(e > c for e in ok) for c in cuts}
        alive_at = {c: any(e <= c for e in ok) for c in cuts}
        tag = "DEAD" if not ok else ("SLOW-ALIVE" if not alive_at[min(cuts)] else "ALIVE")
        print(f"{m:45s} ok {len(ok)}/{len(rs)} times {sorted(ok)} censored-by-cutoff {cens} -> {tag}", flush=True)

if __name__ == "__main__":
    main()
