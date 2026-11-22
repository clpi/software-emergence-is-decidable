#!/usr/bin/env python3
"""Indexed exact dependence scan for rung 2 style views (G2).

One pass over the log builds, for every scored key (dst, site), the
multiset of delivered values partitioned by tick and by source
group. Every counterfactual the baseline scan folds from scratch
is then answered from that index:

- tick edges: per key, the median of the multiset with one tick's
  values removed, combined over the component's tasks in exact
  rational arithmetic (scores are integer numerators over 120);
- per-message dependence: per key, the median with one record's
  values removed, for every record that touches the key;
- sensitivity: per key, the score as a function of the subset of
  its source groups present, for every subset of those groups.
  A component's sensitivity to an axis is decided by the
  coefficient test documented in G2.md: the toggle difference,
  summed over the component's keys, is a sum of functions of small
  group subsets; it is identically zero on the whole subset cube
  iff every coefficient of its multilinear (Moebius) expansion is
  zero. Coefficients are exact integers, so the test is exact at
  any axis count. When the axis count is at most 11 the result is
  also checked against brute-force subset evaluation.

The fold this indexes is the rung 2 view fold: applying a record
appends its fixed delivered values to per-key lists, and the
component estimator (median) and scorer read only those lists.
Appends commute and the estimator is a function of the multiset,
so a counterfactual fold equals the indexed multiset with the
removed part taken out. That is the only fact the speedup uses.

Usage: engine2.py LOGFILE N T G SEED OUTFILE [--per-message]
"""
import json
import os
import sys
import time
from fractions import Fraction

sys.path.insert(0, os.path.expanduser("~/workspace/emergence-rung2-scratch"))
import harness as H

PROTO = 3
COUNT = {"indexentries": 0, "keytickpairs": 0, "keyrecordpairs": 0,
         "subscores": 0, "coefterms": 0}


def mediansorted(vals):
    s = sorted(vals)
    return s[len(s) // 2]


def medianout(sortedvals, removedsorted):
    """Median of sortedvals with the multiset removedsorted taken out."""
    out = []
    j = 0
    for v in sortedvals:
        if j < len(removedsorted) and v == removedsorted[j]:
            j += 1
        else:
            out.append(v)
    if not out:
        return None
    return out[len(out) // 2]


def score_num(pred, truth):
    """Field score as an integer numerator over 120 (exact)."""
    if pred is None:
        pred = 0
    return max(0, 120 - abs(pred - truth))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    permessage = "--per-message" in sys.argv
    logfile, n, tticks, g, seed, outfile = (
        args[0], int(args[1]), int(args[2]), int(args[3]),
        int(args[4]), args[5])
    groups = [list(range((n // g) * i, (n // g) * (i + 1))) for i in range(g)]
    groupof = {a: i for i, grp in enumerate(groups) for a in grp}
    records = [json.loads(l) for l in open(logfile)]
    f = H.gen_field(seed, n)
    obs = H.gen_obs(seed, n, f)

    # scored tasks per group, computed once (the baseline recomputes
    # the held-out hash inside every fold's component call)
    tasks = []
    keygroup = {}
    for gi, grp in enumerate(groups):
        tk = []
        for i in grp:
            for d in range(1, 7):
                for dirn in (-1, 1):
                    if H.held_out(i, d, dirn):
                        site = (i + dirn * d) % n
                        tk.append((i, site))
                        keygroup[(i, site)] = gi
        tasks.append(tk)

    t0 = time.perf_counter()
    # ---- one indexed pass over the log ----
    # key -> {"init": value or None, "bytick": {tick: [values]},
    #         "bygroup": {group: [values]},
    #         "byrecord": {record index: [values]}}
    index = {}
    delivered = {}
    for ri, rec in enumerate(records):
        if rec["vals_recv"] is None:
            continue
        delivered[rec["tick"]] = delivered.get(rec["tick"], 0) + 1
        dst = rec["dst_actual"]
        c = rec["src_interp"]
        sg = groupof[rec["src"]]
        for j in range(8):
            v = rec["vals_recv"][2 * j + 1]
            if v == H.NULL:
                continue
            site = (c + rec["vals_recv"][2 * j]) % n
            if PROTO >= 2 and site == dst:
                continue
            key = (dst, site)
            if key not in keygroup:
                continue
            ent = index.get(key)
            if ent is None:
                ent = index[key] = {"bytick": {}, "bygroup": {}, "byrecord": {}}
            ent["bytick"].setdefault(rec["tick"], []).append(v)
            ent["bygroup"].setdefault(sg, []).append(v)
            if permessage:
                ent["byrecord"].setdefault(ri, []).append(v)
            COUNT["indexentries"] += 1
    # initial own observations: key (a, a) carries obs[a] in every fold
    for a in range(n):
        key = (a, a)
        if key in keygroup:
            ent = index.get(key)
            if ent is None:
                ent = index[key] = {"bytick": {}, "bygroup": {}, "byrecord": {}}
            ent["init"] = obs[a]
    for ent in index.values():
        ent.setdefault("init", None)
        allv = []
        if ent["init"] is not None:
            allv.append(ent["init"])
        for vs in ent["bygroup"].values():
            allv.extend(vs)
        ent["sorted"] = sorted(allv)
        ent["full_pred"] = ent["sorted"][len(ent["sorted"]) // 2] if ent["sorted"] else None
        gi = None
        ent["fullnum"] = None

    def keyfullnum(key):
        dst, site = key
        return score_num(index[key]["full_pred"], f[site])

    # ---- full components (exact, and float replica in task order) ----
    fullcomp = []
    fullfloat = []
    for gi, tk in enumerate(tasks):
        tot = 0
        sf = 0.0
        for (i, site) in tk:
            ent = index.get((i, site))
            pred = ent["full_pred"] if ent else None
            tot += score_num(pred, f[site])
            sf += max(0.0, 1.0 - abs((pred or 0) - f[site]) / 120.0)
        fullcomp.append(Fraction(tot, 120 * len(tk)))
        fullfloat.append(sf / len(tk))

    # ---- tick edges from per-key leave-one-tick-out medians ----
    ticks = sorted({r["tick"] for r in records})
    delta = {t: [Fraction(0) for _ in range(g)] for t in ticks}
    for key, ent in index.items():
        gi = keygroup[key]
        dst, site = key
        fullnum = keyfullnum(key)
        cnt = len(tasks[gi])
        for t, vs in ent["bytick"].items():
            COUNT["keytickpairs"] += 1
            pred = medianout(ent["sorted"], sorted(vs))
            num = score_num(pred, f[site])
            if num != fullnum:
                delta[t][gi] += Fraction(fullnum - num, 120 * cnt)
    edges = []
    for t in ticks:
        edge = sorted(b for b in range(g) if delta[t][b] != 0)
        edges.append({"tick": t, "edge": edge,
                      "weight": delivered.get(t, 0)})

    # ---- per-message dependence (optional; the literal section 1.5
    # unit, at the fold the batteries use) ----
    msgedges = None
    if permessage:
        msgdelta = {}
        for key, ent in index.items():
            gi = keygroup[key]
            dst, site = key
            fullnum = keyfullnum(key)
            cnt = len(tasks[gi])
            for ri, vs in ent["byrecord"].items():
                COUNT["keyrecordpairs"] += 1
                pred = medianout(ent["sorted"], sorted(vs))
                num = score_num(pred, f[site])
                if num != fullnum:
                    msgdelta.setdefault(ri, Fraction(0))
                    msgdelta[ri] += Fraction(fullnum - num, 120 * cnt)
        msgedges = {}
        for ri, rec in enumerate(records):
            if rec["vals_recv"] is None or msgdelta.get(ri, Fraction(0)) == 0:
                msgedges[str(ri)] = []
            else:
                # a record delivers to one destination, so it can
                # move only that destination's group component
                msgedges[str(ri)] = [groupof[rec["dst_actual"]]]

    # ---- per-key subset scores ----
    # key -> (present groups list, {subset mask over present groups: num})
    subscores = {}
    for key, ent in index.items():
        dst, site = key
        present = sorted(ent["bygroup"].keys())
        pos = {grp: i for i, grp in enumerate(present)}
        scores = {}
        for mask in range(1 << len(present)):
            vals = []
            if ent["init"] is not None:
                vals.append(ent["init"])
            for grp in present:
                if mask & (1 << pos[grp]):
                    vals.extend(ent["bygroup"][grp])
            pred = mediansorted(vals) if vals else None
            scores[mask] = score_num(pred, f[site])
            COUNT["subscores"] += 1
        subscores[key] = (present, scores)

    def compof(mask):
        out = []
        for gi, tk in enumerate(tasks):
            tot = 0
            for (i, site) in tk:
                ent = index.get((i, site))
                if ent is None:
                    tot += score_num(None, f[site])
                    continue
                present, scores = subscores[(i, site)]
                sub = 0
                for grp in present:
                    if mask & (1 << grp):
                        sub |= 1 << present.index(grp)
                tot += scores[sub]
            out.append(Fraction(tot, 120 * len(tk)))
        return out

    # ---- sensitivity by the coefficient test ----
    # For axis a and component b: D(Y) = compb(Y + a) - compb(Y),
    # Y a subset of the other axes. D is a sum over b's keys that
    # contain a of per-key differences dk, each a function of
    # Y cap Q_k with Q_k = presentk \ {a}. The multilinear
    # coefficient of a monomial M in D is the sum of the per-key
    # Moebius coefficients of M over keys with Q_k containing M.
    # D is identically zero iff every coefficient is zero.
    def keycoefs(key, a):
        present, scores = subscores[key]
        if a not in present:
            return None
        others = [grp for grp in present if grp != a]
        opos = {grp: i for i, grp in enumerate(others)}
        d = {}
        for mask in range(1 << len(others)):
            subwith = 0
            subwithout = 0
            for grp in present:
                bit = 1 << present.index(grp)
                if grp == a:
                    subwith |= bit
                elif mask & (1 << opos[grp]):
                    subwith |= bit
                    subwithout |= bit
            d[mask] = scores[subwith] - scores[subwithout]
        # Moebius inversion over the subset lattice of others
        coeff = dict(d)
        for i in range(len(others)):
            for mask in range(1 << len(others)):
                if mask & (1 << i):
                    coeff[mask] -= coeff[mask ^ (1 << i)]
        return others, coeff

    sens = {a: set() for a in range(g)}
    witness = {}
    for a in range(g):
        # accumulate coefficients per component
        compcoefs = {b: {} for b in range(g)}
        keydata = {b: [] for b in range(g)}
        for key, ent in index.items():
            b = keygroup[key]
            kc = keycoefs(key, a)
            if kc is None:
                continue
            others, coeff = kc
            keydata[b].append((key, others, coeff))
            for m, c in coeff.items():
                if c == 0:
                    continue
                # monomial as a set of global axes
                mono = frozenset(others[i] for i in range(len(others))
                                 if m & (1 << i))
                compcoefs[b][mono] = compcoefs[b].get(mono, 0) + c
                COUNT["coefterms"] += 1
        for b in range(g):
            nz = [m for m, c in compcoefs[b].items() if c != 0]
            if nz:
                sens[a].add(b)
                # witness: a subset of the smallest nonzero monomial
                mono = min(nz, key=len)
                base = 0
                for grp in mono:
                    base |= 1 << grp
                found = None
                sub = base
                while True:
                    if compof(sub | (1 << a))[b] != compof(sub)[b]:
                        found = sub
                        break
                    if sub == 0:
                        break
                    sub = (sub - 1) & base
                witness[f"{a}->{b}"] = found

    # brute-force cross-check of sensitivity when the cube is small
    brutesens = None
    if g <= 11:
        brutesens = {a: set() for a in range(g)}
        comps = {mask: compof(mask) for mask in range(1 << g)}
        for mask in range(1 << g):
            for a in range(g):
                other = mask ^ (1 << a)
                if other < mask:
                    continue
                for b in range(g):
                    if comps[mask][b] != comps[other][b]:
                        brutesens[a].add(b)

    def live(mask):
        out = set()
        for a in range(g):
            if mask & (1 << a):
                out |= sens[a]
        return out

    def mulambda(mask):
        lv = live(mask)
        mu = sum(e["weight"] for e in edges
                 if len(e["edge"]) >= 2 and set(e["edge"]) <= lv)
        return mu, len(lv), sorted(lv)

    table = {}
    for mask in range(1 << g):
        mu, lam, lv = mulambda(mask)
        table[mask] = {"live": lv, "mu": mu, "lambda": lam, "rho": [mu, lam]}
    mua = table[(1 << g) - 1]["mu"]
    sufficient = [m for m in range(1 << g) if table[m]["mu"] == mua]
    minimal = [m for m in sufficient
               if not any(o != m and (o & m) == o and table[o]["mu"] == mua
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

    wall = time.perf_counter() - t0
    result = {
        "full_components": fullfloat,
        "edges": edges,
        "sensitivity": {f"group{a}": sorted(sens[a]) for a in range(g)},
        "live_full": table[(1 << g) - 1]["live"],
        "mu_full": mua,
        "lambda_full": table[(1 << g) - 1]["lambda"],
        "minimal_sufficient": [{"axes": names(m), "rho": table[m]["rho"]} for m in minimal],
        "highest_minimal": [{"axes": names(m), "rho": table[m]["rho"]} for m in highest],
        "interaction_matrix": matrix,
        "table": {str(m): table[m] for m in range(1 << g)},
    }
    out = {"result": result, "wall": wall, "counters": COUNT,
           "bruteagrees": (None if brutesens is None else
                                 all(sens[a] == brutesens[a] for a in range(g))),
           "witness": witness}
    if msgedges is not None:
        out["permessage"] = {
            "records": len(records),
            "dependent": sum(1 for v in msgedges.values() if v),
            "edges": msgedges}
    with open(outfile, "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"indexed entries={COUNT['indexentries']} keytick={COUNT['keytickpairs']} "
          f"subscores={COUNT['subscores']} wall={wall:.3f}s mu={mua} "
          f"bruteagrees={out['bruteagrees']}")


if __name__ == "__main__":
    main()
