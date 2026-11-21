#!/usr/bin/env python3
"""Section 6.3 derivation-graph audit, T5.4 dynamic half.

Re-executes, at audit time, the derivation checks over the
persisted rung-5 battery artifacts, using only the independent
checker's fold (check5.py imports nothing from the harness):

1. Prefix folds: for replicate 1's live run in each family, the
   state folded from each checkpoint prefix by the checker's
   fold equals the checkpoint hash the harness recorded.
2. Restart closure: continuing the fold from each checkpoint
   state over the remaining records reproduces the final hash —
   no state is carried anywhere but in the fold of the log.
3. Append-only shape: the persisted log's tick sequence is
   non-decreasing and every checkpoint prefix is a literal list
   prefix of the full log.
4. Influence probe: for a sample of delivered records, removing
   the record from the fold changes the folded report lists
   exactly (the derived state itself, not its median/mode hash
   quotient) whenever the record appends at least one value —
   every appending record is a premise of the derived state,
   and the fold is the only route by which it gets there.

Prints one verdict line per check family and a final AUDIT54
line. Exit 0 iff every check passes.
"""
import importlib.util
import json
import os
import sys

R5 = os.path.expanduser("~/workspace/emergence-rung5-scratch")
spec = importlib.util.spec_from_file_location(
    "check5", os.path.join(R5, "check5.py"))
c5 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c5)

N = c5.N
TICKS = c5.TICKS
CHECKPOINTS = c5.CHECKPOINTS
fails = []


def foldto(family, records, upto, truth, obs):
    reports = [{a: [obs[a]]} for a in range(N)]
    for rec in records[:upto]:
        c5.apply(rec, reports)
    return reports


for family in ("field", "region"):
    home = os.path.join(R5, "results", family + "5")
    summary = json.load(open(os.path.join(home, "live-rep1.json")))
    records = [json.loads(l) for l in open(
        os.path.join(home, "live-rep1.jsonl"))]
    truth, obs = c5.truth_obs(family, summary["seed"])

    # 3. append-only shape
    ticks = [r["tick"] for r in records]
    if ticks != sorted(ticks) or len(records) != 2 * N * TICKS:
        fails.append(f"{family}: log not tick-ordered append-only")
    else:
        print(f"{family}: append-only shape OK "
              f"({len(records)} records, ticks non-decreasing)")

    # 1 + 2. prefix folds and restart closure at every checkpoint
    folded = rejoined = 0
    for t in CHECKPOINTS:
        upto = 2 * N * t
        reports = foldto(family, records, upto, truth, obs)
        if c5.state_hash(family, reports) == summary["cuts"][str(t)]["hash"]:
            folded += 1
        else:
            fails.append(f"{family}: prefix fold mismatch at t={t}")
        state = c5.copy_reports(reports)
        for rec in records[upto:]:
            c5.apply(rec, state)
        if c5.state_hash(family, state) == summary["final"]:
            rejoined += 1
        else:
            fails.append(f"{family}: restart from t={t} mismatch")
    print(f"{family}: prefix folds {folded}/{len(CHECKPOINTS)}, "
          f"restarts {rejoined}/{len(CHECKPOINTS)}")

    # 4. influence probe: 24 delivered records spread over the log
    delivered = [i for i, r in enumerate(records)
                 if r["vals_recv"] is not None and c5.appended_of(r) > 0]
    step = max(1, len(delivered) // 24)
    sample = delivered[::step][:24]
    full = foldto(family, records, len(records), truth, obs)
    infl = 0
    for i in sample:
        reduced = records[:i] + records[i + 1:]
        state = foldto(family, reduced, len(reduced),
                            truth, obs)
        if state != full:
            infl += 1
        else:
            fails.append(f"{family}: record {i} appends values but "
                         f"its removal leaves the folded state unchanged")
    print(f"{family}: influence probe {infl}/{len(sample)} sampled "
          f"appending records change the final state when removed")

if fails:
    for f in fails:
        print("FAIL", f)
    print("AUDIT54: FAIL")
    sys.exit(1)
print("AUDIT54: PASS")
