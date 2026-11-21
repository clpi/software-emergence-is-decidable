#!/usr/bin/env python3
"""Rung 3 views of joint replicate 1 (registration.md, "Views").

For each formation tick and each of the level-1, level-2, and
joint views: components are per-block held-out mean scores scored
from folds of the recorded log (counterfactual folds, rung 2's
view method — the system is never re-run). Hyperedges are
per-tick counterfactual component sets. Live/engaged/mu/lambda/
rho follow F1 (hma SPEC sections 2-4) via single-axis sensitivity
over the configuration folds; exact when the view has <= 11 axes
(all subset configurations folded), otherwise computed over the
registered subfamily and labeled, with emergent-dead never
declared from a restricted family.
"""
import hashlib
import itertools
import json
import math
import os
import random
import sys

NULL = 10 ** 9
SPLIT = {"field": 2026112199, "region": 2026112299}
FTICKS = (8, 16, 24)


def gen_field(seed, n):
    rng = random.Random(seed ^ 0xF1E1D)
    phases = [rng.uniform(0, 2 * math.pi) for _ in range(3)]
    amps = [60, 35, 20]
    return [int(round(sum(a * math.sin(2 * math.pi * (k + 1) * i / n + phases[k])
                           for k, a in enumerate(amps)))) for i in range(n)]


def gen_labels(seed, n):
    rng = random.Random(seed ^ 0x5E6)
    lengths = [n // 6 + rng.randint(-4, 4) for _ in range(6)]
    while sum(lengths) != n:
        if sum(lengths) < n:
            lengths[rng.randrange(6)] += 1
        else:
            i = max(range(6), key=lambda k: lengths[k])
            lengths[i] -= 1
    labels = []
    for s, ln in enumerate(lengths):
        labels += [s % 3] * ln
    return labels


def held_out(family, i, d, direction):
    h = hashlib.sha256(
        f"{SPLIT[family]}:{i}:{d}:{direction}".encode()).digest()
    return h[0] % 2 == 0


def median(vals):
    s = sorted(vals)
    return s[len(s) // 2]


def mode(vals):
    cnt = {}
    for v in vals:
        cnt[v] = cnt.get(v, 0) + 1
    return min(cnt, key=lambda v: (-cnt[v], v))


def build_view(records, family, truth, n, partition, kind, tj, tnext):
    """kind in {"l1", "l2", "joint"}. Returns the view dict."""
    B = len(partition)
    block_of = {m: bi for bi, blk in enumerate(partition) for m in blk}
    # held-out tasks per block
    block_tasks = []
    for blk in partition:
        tasks = []
        for i in blk:
            for d in range(1, 7):
                for dirn in (-1, 1):
                    if held_out(family, i, d, dirn):
                        tasks.append((i, (i + dirn * d) % n))
        block_tasks.append(tasks)
    task_pairs = {(i, s) for tasks in block_tasks for (i, s) in tasks}

    def included(rec):
        if kind == "l1":
            return rec["lvl"] == 1 and rec["tick"] < tnext
        if kind == "l2":
            if rec["lvl"] == 1:
                return rec["tick"] < tnext
            return tj <= rec["tick"] < tnext
        return tj <= rec["tick"] < tnext

    # entries: (dst, site) -> list of (src_block, lvl, tick, value)
    entries = {}
    delivered = {}  # tick -> delivered count at the view's levels
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
            if v != NULL:
                site = (c + rec["vals_recv"][2 * j]) % n
                if site != dst and (dst, site) in task_pairs:
                    entries.setdefault((dst, site), []).append(
                        (sb, rec["lvl"], rec["tick"], v))
        lvls = (1,) if kind == "l1" else (2,) if kind == "l2" else (1, 2)
        if rec["lvl"] in lvls:
            delivered[rec["tick"]] = delivered.get(rec["tick"], 0) + 1

    est = median if family == "field" else mode

    def score1(pred, site):
        if family == "field":
            return max(0.0, 1.0 - abs(pred - truth[site]) / 120.0)
        return 1.0 if pred == truth[site] else 0.0

    def components(include, drop_tick=None, drop_lvls=()):
        out = []
        for tasks in block_tasks:
            s = 0.0
            for (i, site) in tasks:
                vals = []
                for (sb, lvl, tick, v) in entries.get((i, site), ()):
                    if not include(sb, lvl):
                        continue
                    if drop_tick is not None and tick == drop_tick \
                            and lvl in drop_lvls:
                        continue
                    vals.append(v)
                pred = est(vals) if vals else 0
                s += score1(pred, site)
            out.append(s / len(tasks))
        return out

    if kind == "l1":
        def inc_full(sb, lvl):
            return lvl == 1

        def inc_mask(mask):
            return lambda sb, lvl: lvl == 1 and (mask >> sb) & 1
        edge_ticks = list(range(0, tnext))
        drop_lvls = (1,)
    elif kind == "l2":
        def inc_full(sb, lvl):
            return True

        def inc_mask(mask):
            return lambda sb, lvl: lvl == 1 or (mask >> sb) & 1
        edge_ticks = list(range(tj, tnext))
        drop_lvls = (2,)
    else:
        def inc_full(sb, lvl):
            return True

        def inc_mask(mask):
            return lambda sb, lvl: (mask >> sb) & 1
        edge_ticks = list(range(tj, tnext))
        drop_lvls = (1, 2)

    full_comp = components(inc_full)

    # hyperedges: per-tick counterfactuals at the full configuration
    edges = []
    for t in edge_ticks:
        comp_t = components(inc_full, drop_tick=t, drop_lvls=drop_lvls)
        edge = frozenset(b for b in range(B) if comp_t[b] != full_comp[b])
        edges.append({"tick": t, "edge": sorted(edge),
                      "weight": delivered.get(t, 0)})

    # configuration folds and sensitivity
    exact = B <= 11
    if exact:
        masks = list(range(1 << B))
    else:
        # registered subfamily (registration amendment v2): empty,
        # full, singletons, pairs, leave-one-out, leave-two-out
        fam = {0, (1 << B) - 1}
        for a in range(B):
            fam.add(1 << a)
            fam.add(((1 << B) - 1) ^ (1 << a))
            for b in range(a + 1, B):
                fam.add((1 << a) | (1 << b))
                fam.add(((1 << B) - 1) ^ (1 << a) ^ (1 << b))
        masks = sorted(fam)
    comps = {}
    for mask in masks:
        comps[mask] = components(inc_mask(mask))
    sens = {a: set() for a in range(B)}
    for mask in masks:
        for a in range(B):
            other = mask ^ (1 << a)
            if other in comps:
                for b in range(B):
                    if comps[mask][b] != comps[other][b]:
                        sens[a].add(b)

    def live(mask):
        out = set()
        for a in range(B):
            if (mask >> a) & 1:
                out |= sens[a]
        return out

    def mu_lambda(mask):
        lv = live(mask)
        mu = sum(e["weight"] for e in edges
                 if len(e["edge"]) >= 2 and set(e["edge"]) <= lv)
        return mu, len(lv), sorted(lv)

    full = (1 << B) - 1
    mu_a, lam_a, live_a = mu_lambda(full)
    table = {}
    if exact:
        for mask in masks:
            mu, lam, lv = mu_lambda(mask)
            table[str(mask)] = {"live": lv, "mu": mu, "lambda": lam,
                                "rho": [mu, lam]}
        sufficient = [m for m in masks if table[str(m)]["mu"] == mu_a]
        minimal = [m for m in sufficient
                   if not any(o != m and (o & m) == o
                              and table[str(o)]["mu"] == mu_a
                              for o in sufficient)]
        best = max((table[str(m)]["rho"] for m in minimal), default=None)
        highest = [m for m in minimal if table[str(m)]["rho"] == best]
    else:
        minimal, highest = [], []
    dead = []
    if exact and kind == "l2":
        for g in range(B):
            if live(full ^ (1 << g)) == live(full):
                dead.append(g)
    matrix = [[0] * B for _ in range(B)]
    for e in edges:
        for b in e["edge"]:
            for b2 in e["edge"]:
                matrix[b][b2] += e["weight"]

    def names(mask):
        return [f"block{g}" for g in range(B) if (mask >> g) & 1]

    return {
        "kind": kind, "formation_tick": tj, "axes": B, "exact": exact,
        "blocks": partition,
        "full_components": full_comp,
        "edges": edges,
        "sensitivity": {f"block{a}": sorted(sens[a]) for a in range(B)},
        "live_full": live_a, "mu_full": mu_a, "lambda_full": lam_a,
        "minimal_sufficient": [{"axes": names(m),
                                "rho": table[str(m)]["rho"]}
                               for m in minimal] if exact else None,
        "highest_minimal": [{"axes": names(m),
                             "rho": table[str(m)]["rho"]}
                            for m in highest] if exact else None,
        "dead_blocks": dead if (exact and kind == "l2") else None,
        "interaction_matrix": matrix,
        "table": table if exact else None,
    }


def main(battery):
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "results", battery)
    summ = json.load(open(os.path.join(base, "joint-rep1.json")))
    records = [json.loads(l) for l in
               open(os.path.join(base, "joint-rep1.jsonl"))]
    family, n, seed = summ["family"], summ["n"], summ["seed"]
    truth = gen_field(seed, n) if family == "field" else gen_labels(seed, n)
    parts = summ["partitions"]
    views = []
    bounds = [(FTICKS[0], FTICKS[1]), (FTICKS[1], FTICKS[2]),
              (FTICKS[2], summ["ticks"])]
    for tj, tnext in bounds:
        partition = parts[str(tj)]
        for kind in ("l1", "l2", "joint"):
            v = build_view(records, family, truth, n, partition,
                           kind, tj, tnext)
            views.append(v)
            print(f"{battery} {kind} view @t{tj}: B={v['axes']} "
                  f"exact={v['exact']} mu={v['mu_full']} "
                  f"lambda={v['lambda_full']} "
                  f"dead={v['dead_blocks']}", flush=True)
    # cross-check of the view machinery (not of any single view):
    # entries over the FULL log under the final partition, folded
    # at the full configuration, must reproduce the run's recorded
    # cap. (A single interval view deliberately folds only its
    # included records — see registration.md — so it is not
    # expected to reproduce the cap.)
    p3 = parts[str(FTICKS[2])]
    block_of = {m: bi for bi, blk in enumerate(p3) for m in blk}
    ent = {}
    for rec in records:
        if rec["vals_recv"] is None:
            continue
        dst = rec["dst_actual"]
        c = rec["src_interp"]
        for j in range(8):
            v = rec["vals_recv"][2 * j + 1]
            if v != NULL:
                site = (c + rec["vals_recv"][2 * j]) % n
                if site != dst:
                    ent.setdefault((dst, site), []).append(v)
    est = median if family == "field" else mode
    tot = 0
    wsum = 0.0
    for i in range(n):
        for d in range(1, 7):
            for dirn in (-1, 1):
                if not held_out(family, i, d, dirn):
                    continue
                site = (i + dirn * d) % n
                vals = ent.get((i, site), [])
                pred = est(vals) if vals else 0
                if family == "field":
                    wsum += max(0.0, 1.0 - abs(pred - truth[site]) / 120.0)
                else:
                    wsum += 1.0 if pred == truth[site] else 0.0
                tot += 1
    cap_check = abs(wsum / tot - summ["cap"])
    result = {"battery": battery, "run": "joint-rep1", "seed": seed,
              "family": family, "cap_agreement_abs_diff": cap_check,
              "views": views}
    out_path = os.path.join(base, "view3.json")
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=1)
    print(f"{battery}: cap agreement |diff| = {cap_check:.2e}; "
          f"wrote {out_path}")


if __name__ == "__main__":
    main(sys.argv[1])
