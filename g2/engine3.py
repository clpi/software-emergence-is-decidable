#!/usr/bin/env python3
"""Indexed exact views for rung 3 joint logs (G2).

Replicates view3.py's build_view definitions exactly, but answers
every counterfactual from one index instead of rescanning the
entry lists for every tick and every configuration mask:

- entries are built once per view, keyed by (dst, site), with each
  value tagged (source block, level, tick);
- tick edges come from per-key leave-one-tick-out estimators;
- configuration components come from per-key subset scores over
  the key's gated source blocks (level-1 entries are ungated
  background in level-2 views, per view3.py's include functions);
- sensitivity is decided by the coefficient (Moebius) test of
  G2.md, exact at any axis count, so views above the baseline's
  11-axis subset-enumeration cap get exact sensitivity, exact
  live and mu at the full configuration, and exact dead blocks
  where the baseline reported a restricted-family lower bound
  or null.

All score arithmetic is exact: field scores are integer
numerators over 120 (median estimator), region scores are 0/1
(mode estimator). Float full components are also replicated in
the baseline's task order for byte comparison.

Usage: engine3.py BATTERY OUTFILE
(BATTERY is a rung 3 results directory name, e.g. field3.)
"""
import json
import os
import random
import sys
import time
from collections import Counter
from fractions import Fraction

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "rung3"))
sys.path.insert(0, os.path.expanduser("~/workspace/emergence-rung3-scratch"))
import view3 as V

FTICKS = V.FTICKS
COUNT = {"entries": 0, "keytickpairs": 0, "subscores": 0,
         "coefterms": 0, "spotchecks": 0, "spotfailures": 0}


def estof(vals, family):
    if not vals:
        return None
    if family == "field":
        s = sorted(vals)
        return s[len(s) // 2]
    return V.mode(vals)


def estout(sortedbase, removed, family):
    if family == "field":
        out = []
        j = 0
        rem = sorted(removed)
        for v in sortedbase:
            if j < len(rem) and v == rem[j]:
                j += 1
            else:
                out.append(v)
        return out[len(out) // 2] if out else None
    cnt = Counter(sortedbase)
    for v in removed:
        cnt[v] -= 1
        if cnt[v] == 0:
            del cnt[v]
    if not cnt:
        return None
    return min(cnt, key=lambda v: (-cnt[v], v))


def scoreof(pred, truth, family):
    if family == "field":
        return max(0, 120 - abs((pred or 0) - truth)), 120
    return (1 if (pred or 0) == truth else 0), 1


def build(records, family, truth, n, partition, kind, tj, tnext):
    B = len(partition)
    block_of = {m: bi for bi, blk in enumerate(partition) for m in blk}
    block_tasks = []
    for blk in partition:
        tasks = []
        for i in blk:
            for d in range(1, 7):
                for dirn in (-1, 1):
                    if V.held_out(family, i, d, dirn):
                        tasks.append((i, (i + dirn * d) % n))
        block_tasks.append(tasks)
    task_pairs = {(i, s) for tasks in block_tasks for (i, s) in tasks}
    task_group = {}
    for bi, tasks in enumerate(block_tasks):
        for t in tasks:
            task_group[t] = bi

    def included(rec):
        if kind == "l1":
            return rec["lvl"] == 1 and rec["tick"] < tnext
        if kind == "l2":
            if rec["lvl"] == 1:
                return rec["tick"] < tnext
            return tj <= rec["tick"] < tnext
        return tj <= rec["tick"] < tnext

    entries = {}
    delivered = {}
    for rec in records:
        if not included(rec) or rec["vals_recv"] is None:
            continue
        if kind == "l1" and rec["lvl"] != 1:
            continue
        dst = rec["dst_actual"]
        c = rec["src_interp"]
        sb = block_of[rec["src"]]
        for j in range(8):
            v = rec["vals_recv"][2 * j + 1]
            if v != V.NULL:
                site = (c + rec["vals_recv"][2 * j]) % n
                if site != dst and (dst, site) in task_pairs:
                    entries.setdefault((dst, site), []).append(
                        (sb, rec["lvl"], rec["tick"], v))
                    COUNT["entries"] += 1
        lvls = (1,) if kind == "l1" else (2,) if kind == "l2" else (1, 2)
        if rec["lvl"] in lvls:
            delivered[rec["tick"]] = delivered.get(rec["tick"], 0) + 1

    if kind == "l1":
        edgeticks = list(range(0, tnext))
        droplvls = (1,)
    elif kind == "l2":
        edgeticks = list(range(tj, tnext))
        droplvls = (2,)
    else:
        edgeticks = list(range(tj, tnext))
        droplvls = (1, 2)

    def gated(sb, lvl):
        """Whether a mask bit gates this entry, per view3 include."""
        if kind == "l2":
            return lvl == 2
        return True

    # per-key structures
    keys = {}
    for key, evs in entries.items():
        bg = [v for (sb, lvl, tick, v) in evs if not gated(sb, lvl)]
        bygroup = {}
        bytick = {}
        allv = []
        for (sb, lvl, tick, v) in evs:
            allv.append(v)
            if gated(sb, lvl):
                bygroup.setdefault(sb, []).append(v)
            if tick in edgeticks and lvl in droplvls:
                bytick.setdefault(tick, []).append(v)
        keys[key] = {"bg": bg, "bygroup": bygroup, "bytick": bytick,
                     "all": allv,
                     "sorted": sorted(allv) if family == "field" else None,
                     "counter": Counter(allv) if family == "region" else None}
    for key in task_pairs:
        if key not in keys:
            keys[key] = {"bg": [], "bygroup": {}, "bytick": {}, "all": [],
                         "sorted": [] if family == "field" else None,
                         "counter": Counter() if family == "region" else None}

    def fullpred(key):
        k = keys[key]
        if family == "field":
            return k["sorted"][len(k["sorted"]) // 2] if k["sorted"] else None
        return estof(k["all"], family)

    def keynum(key, pred):
        dst, site = key
        return scoreof(pred, truth[site], family)

    # full components: exact and float replica in task order
    fullcomp = []
    fullfloat = []
    for bi, tasks in enumerate(block_tasks):
        tot = 0
        den = 1
        sf = 0.0
        for (i, site) in tasks:
            num, den = keynum((i, site), fullpred((i, site)))
            tot += num
            pred = fullpred((i, site))
            if family == "field":
                sf += max(0.0, 1.0 - abs((pred or 0) - truth[site]) / 120.0)
            else:
                sf += 1.0 if (pred or 0) == truth[site] else 0.0
        fullcomp.append(Fraction(tot, den * len(tasks)))
        fullfloat.append(sf / len(tasks))

    # tick edges via per-key leave-one-tick-out
    delta = {t: [Fraction(0) for _ in range(B)] for t in edgeticks}
    for key, k in keys.items():
        if key not in task_group:
            continue
        bi = task_group[key]
        dst, site = key
        fnum, den = keynum(key, fullpred(key))
        cnt = len(block_tasks[bi])
        base = k["sorted"] if family == "field" else k["all"]
        for t, vs in k["bytick"].items():
            COUNT["keytickpairs"] += 1
            pred = estout(base, vs, family)
            num, _ = scoreof(pred, truth[site], family)
            if num != fnum:
                delta[t][bi] += Fraction(fnum - num, den * cnt)
    edges = []
    for t in edgeticks:
        edge = sorted(b for b in range(B) if delta[t][b] != 0)
        edges.append({"tick": t, "edge": edge, "weight": delivered.get(t, 0)})

    # per-key subset scores over gated groups (background fixed)
    subscores = {}
    for key, k in keys.items():
        present = sorted(k["bygroup"].keys())
        pos = {grp: i for i, grp in enumerate(present)}
        scores = {}
        for mask in range(1 << len(present)):
            vals = list(k["bg"])
            for grp in present:
                if mask & (1 << pos[grp]):
                    vals.extend(k["bygroup"][grp])
            pred = estof(vals, family)
            scores[mask] = keynum(key, pred)[0]
            COUNT["subscores"] += 1
        subscores[key] = (present, pos, scores)

    def compof(mask):
        out = []
        for bi, tasks in enumerate(block_tasks):
            tot = 0
            den = 1
            for (i, site) in tasks:
                present, pos, scores = subscores[(i, site)]
                sub = 0
                for grp in present:
                    if mask & (1 << grp):
                        sub |= 1 << pos[grp]
                tot += scores[sub]
                den = keynum((i, site), None)[1]
            out.append(Fraction(tot, den * len(tasks)))
        return out

    # direct spot checks of compof against entry scans
    rng = random.Random(2026112199 + B + tj)
    for _ in range(12):
        mask = rng.randrange(1 << B)

        def incmask(sb, lvl):
            if kind == "l1":
                return lvl == 1 and (mask >> sb) & 1
            if kind == "l2":
                return lvl == 1 or (mask >> sb) & 1
            return (mask >> sb) & 1

        direct = []
        for bi, tasks in enumerate(block_tasks):
            tot = 0
            den = 1
            for (i, site) in tasks:
                vals = [v for (sb, lvl, tick, v) in entries.get((i, site), ())
                        if incmask(sb, lvl)]
                pred = estof(vals, family)
                num, den = scoreof(pred, truth[site], family)
                tot += num
            direct.append(Fraction(tot, den * len(tasks)))
        COUNT["spotchecks"] += 1
        if direct != compof(mask):
            COUNT["spotfailures"] += 1

    # sensitivity by the coefficient test
    sens = {a: set() for a in range(B)}
    for a in range(B):
        compcoefs = {b: {} for b in range(B)}
        for key, k in keys.items():
            if key not in task_group:
                continue
            b = task_group[key]
            present, pos, scores = subscores[key]
            if a not in present:
                continue
            others = [grp for grp in present if grp != a]
            opos = {grp: i for i, grp in enumerate(others)}
            d = {}
            for mask in range(1 << len(others)):
                subwith = 0
                subwithout = 0
                for grp in present:
                    bit = 1 << pos[grp]
                    if grp == a:
                        subwith |= bit
                    elif mask & (1 << opos[grp]):
                        subwith |= bit
                        subwithout |= bit
                d[mask] = scores[subwith] - scores[subwithout]
            coeff = dict(d)
            for i in range(len(others)):
                for mask in range(1 << len(others)):
                    if mask & (1 << i):
                        coeff[mask] -= coeff[mask ^ (1 << i)]
            for m, c in coeff.items():
                if c == 0:
                    continue
                mono = frozenset(others[i] for i in range(len(others))
                                 if m & (1 << i))
                compcoefs[b][mono] = compcoefs[b].get(mono, 0) + c
                COUNT["coefterms"] += 1
        for b in range(B):
            if any(c != 0 for c in compcoefs[b].values()):
                sens[a].add(b)

    def live(mask):
        out = set()
        for a in range(B):
            if (mask >> a) & 1:
                out |= sens[a]
        return out

    full_mask = (1 << B) - 1
    live_full = live(full_mask)
    mu_full = sum(e["weight"] for e in edges
                  if len(e["edge"]) >= 2 and set(e["edge"]) <= live_full)
    dead = None
    if kind == "l2":
        dead = [grp for grp in range(B)
                if live(full_mask ^ (1 << grp)) == live_full]
    matrix = [[0] * B for _ in range(B)]
    for e in edges:
        for b in e["edge"]:
            for b2 in e["edge"]:
                matrix[b][b2] += e["weight"]
    return {
        "kind": kind, "formation_tick": tj, "axes": B,
        "full_components": fullfloat,
        "edges": edges,
        "sensitivity": {f"block{a}": sorted(sens[a]) for a in range(B)},
        "live_full": sorted(live_full), "mu_full": mu_full,
        "lambda_full": len(live_full),
        "dead_blocks": dead,
        "interaction_matrix": matrix,
    }


def main():
    battery, outfile = sys.argv[1], sys.argv[2]
    root = (sys.argv[3] if len(sys.argv) > 3 else
            os.path.expanduser("~/workspace/emergence-rung3-scratch/results"))
    base = os.path.join(root, battery)
    summ = json.load(open(os.path.join(base, "joint-rep1.json")))
    records = [json.loads(l) for l in open(os.path.join(base, "joint-rep1.jsonl"))]
    family, n, seed = summ["family"], summ["n"], summ["seed"]
    truth = V.gen_field(seed, n) if family == "field" else V.gen_labels(seed, n)
    parts = summ["partitions"]
    t0 = time.perf_counter()
    views = []
    bounds = [(FTICKS[0], FTICKS[1]), (FTICKS[1], FTICKS[2]),
              (FTICKS[2], summ["ticks"])]
    for tj, tnext in bounds:
        partition = parts[str(tj)]
        for kind in ("l1", "l2", "joint"):
            v = build(records, family, truth, n, partition,
                                   kind, tj, tnext)
            views.append(v)
            print(f"{battery} {kind} @t{tj}: B={v['axes']} mu={v['mu_full']} "
                  f"lambda={v['lambda_full']} dead={v['dead_blocks']}", flush=True)
    wall = time.perf_counter() - t0
    with open(outfile, "w") as fh:
        json.dump({"views": views, "wall": wall, "counters": COUNT}, fh, indent=1)
    print(f"engine3 {battery}: wall={wall:.3f}s counters={COUNT}")


if __name__ == "__main__":
    main()
