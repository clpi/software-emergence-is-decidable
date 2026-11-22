#!/usr/bin/env python3
"""Brute-force per-message dependence: one full fold per record.

The literal section 1.5 scan at the fold the batteries use, run
with no indexing, as the independent check of engine2's per-message
output. Usage: brute_message.py LOGFILE N SEED ENGINE_JSON OUTFILE
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.expanduser("~/workspace/emergence-rung2-scratch"))
import harness as H

PROTO = 3


def main():
    logfile, n, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    eng = json.load(open(sys.argv[4]))
    records = [json.loads(l) for l in open(logfile)]
    f = H.gen_field(seed, n)
    obs = H.gen_obs(seed, n, f)
    groups = [list(range((n // 8) * i, (n // 8) * (i + 1))) for i in range(8)]

    def fold(recs):
        reports = [{a: [obs[a]]} for a in range(n)]
        for rec in recs:
            if rec["vals_recv"] is not None:
                H.apply_delivery(reports, rec, n, PROTO)
        return reports

    def components(reports):
        out = []
        for grp in groups:
            s = 0.0
            c = 0
            for i in grp:
                for d in range(1, 7):
                    for dirn in (-1, 1):
                        if not H.held_out(i, d, dirn):
                            continue
                        site = (i + dirn * d) % n
                        vals = reports[i].get(site)
                        pred = H.median(vals) if vals else 0
                        s += max(0.0, 1.0 - abs(pred - f[site]) / 120.0)
                        c += 1
            out.append(s / c)
        return out

    t0 = time.perf_counter()
    full = components(fold(records))
    mine = {}
    for ri, rec in enumerate(records):
        if rec["vals_recv"] is None:
            mine[str(ri)] = []
            continue
        edited = records[:ri] + records[ri + 1:]
        comp = components(fold(edited))
        mine[str(ri)] = sorted(b for b in range(8) if comp[b] != full[b])
    wall = time.perf_counter() - t0
    theirs = eng["permessage"]["edges"]
    agree = mine == theirs
    dep = sum(1 for v in mine.values() if v)
    with open(sys.argv[5], "w") as fh:
        json.dump({"agree": agree, "wall": wall,
                   "dependent": dep, "records": len(records)}, fh)
    print(f"brute per-message: agree={agree} dependent={dep} wall={wall:.1f}s")


if __name__ == "__main__":
    main()
