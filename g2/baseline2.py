#!/usr/bin/env python3
"""Faithful parameterized port of rung 2 view.py (the baseline scan).

Same algorithm, same order of operations: one full fold, one
counterfactual fold per tick, and one fold per configuration mask
(2^G), with components recomputed from scratch after every fold.
Counters record folds, record applications, and component calls so
cost can be stated in operations as well as wall time.

Usage: baseline2.py LOGFILE N T G SEED OUTFILE
Groups are G contiguous groups of N/G actors, as in rung 2.
"""
import itertools
import json
import os
import sys
import time

sys.path.insert(0, os.path.expanduser("~/workspace/emergence-rung2-scratch"))
import harness as H

PROTO = 3
COUNT = {"folds": 0, "record_apps": 0, "component_calls": 0}


def main():
    logfile, n, t_ticks, g, seed, outfile = (
        sys.argv[1], int(sys.argv[2]), int(sys.argv[3]),
        int(sys.argv[4]), int(sys.argv[5]), sys.argv[6])
    groups = [list(range((n // g) * i, (n // g) * (i + 1))) for i in range(g)]
    group_of = {a: i for i, grp in enumerate(groups) for a in grp}
    records = [json.loads(l) for l in open(logfile)]

    def fold(recs):
        COUNT["folds"] += 1
        f = H.gen_field(seed, n)
        obs = H.gen_obs(seed, n, f)
        reports = [{a: [obs[a]]} for a in range(n)]
        for rec in recs:
            if rec["vals_recv"] is not None:
                COUNT["record_apps"] += 1
                H.apply_delivery(reports, rec, n, PROTO)
        return reports, f

    def components(reports, f):
        COUNT["component_calls"] += 1
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
    full_reports, f = fold(records)
    full_comp = components(full_reports, f)

    ticks = sorted({r["tick"] for r in records})
    edges = []
    for t in ticks:
        edited = [r for r in records
                  if not (r["tick"] == t and r["vals_recv"] is not None)]
        rep_t, _ = fold(edited)
        comp_t = components(rep_t, f)
        edge = frozenset(b for b in range(g) if comp_t[b] != full_comp[b])
        w = sum(1 for r in records if r["tick"] == t and r["vals_recv"] is not None)
        edges.append({"tick": t, "edge": sorted(edge), "weight": w})

    folds = {}
    for mask in range(1 << g):
        active = {i for i in range(g) if mask & (1 << i)}
        edited = [r for r in records if group_of[r["src"]] in active]
        rep_t, _ = fold(edited)
        folds[mask] = components(rep_t, f)

    sens = {a: set() for a in range(g)}
    for mask in range(1 << g):
        for a in range(g):
            other = mask ^ (1 << a)
            if other < mask:
                continue
            for b in range(g):
                if folds[mask][b] != folds[other][b]:
                    sens[a].add(b)

    def live(mask):
        out = set()
        for a in range(g):
            if mask & (1 << a):
                out |= sens[a]
        return out

    def mu_lambda(mask):
        lv = live(mask)
        mu = sum(e["weight"] for e in edges
                 if len(e["edge"]) >= 2 and set(e["edge"]) <= lv)
        return mu, len(lv), sorted(lv)

    table = {}
    for mask in range(1 << g):
        mu, lam, lv = mu_lambda(mask)
        table[mask] = {"live": lv, "mu": mu, "lambda": lam, "rho": [mu, lam]}
    mu_a = table[(1 << g) - 1]["mu"]
    sufficient = [m for m in range(1 << g) if table[m]["mu"] == mu_a]
    minimal = [m for m in sufficient
               if not any(o != m and (o & m) == o and table[o]["mu"] == mu_a
                          for o in sufficient)]
    best_rho = max((table[m]["rho"]) for m in minimal) if minimal else None
    highest = [m for m in minimal if table[m]["rho"] == best_rho]
    matrix = [[0] * g for _ in range(g)]
    for e in edges:
        for b in e["edge"]:
            for b2 in e["edge"]:
                matrix[b][b2] += e["weight"]

    def names(mask):
        return [f"group{i}" for i in range(g) if mask & (1 << i)]

    result = {
        "full_components": full_comp,
        "edges": edges,
        "sensitivity": {f"group{a}": sorted(sens[a]) for a in range(g)},
        "live_full": table[(1 << g) - 1]["live"],
        "mu_full": mu_a,
        "lambda_full": table[(1 << g) - 1]["lambda"],
        "minimal_sufficient": [{"axes": names(m), "rho": table[m]["rho"]} for m in minimal],
        "highest_minimal": [{"axes": names(m), "rho": table[m]["rho"]} for m in highest],
        "interaction_matrix": matrix,
        "table": {str(m): table[m] for m in range(1 << g)},
    }
    wall = time.perf_counter() - t0
    with open(outfile, "w") as fh:
        json.dump({"result": result, "wall_s": wall, "counters": COUNT}, fh, indent=1)
    print(f"baseline folds={COUNT['folds']} record_apps={COUNT['record_apps']} "
          f"component_calls={COUNT['component_calls']} wall={wall:.3f}s mu={mu_a}")


if __name__ == "__main__":
    main()
