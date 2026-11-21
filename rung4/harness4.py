#!/usr/bin/env python3
"""Rung 4 harness: transfer — interaction structure into a
held-out family.

Implements the battery registered in registration.md (read it
first). The gossip system is rungs 2-3's single-level protocol
v3 system, imported from harness3.py (its names are its own).
This file adds: the group view of a log (axes = 8 ring arcs,
components = per-group held-out means, hyperedges = per-tick
counterfactuals), extraction of the structure artifact, the
control and null artifacts, and the target configuration
search the artifact is carried into. Verification lives in
check4.py, an independent code path that imports nothing here.
"""
import bisect
import hashlib
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "emergence-rung3-scratch"))
import harness3 as base

NULL = 10 ** 9
G = 8                 # groups (registration: 8 arcs of 32)
N = 256
TICKS = 32
SEEDS = [2026112100 + r for r in range(1, 9)]
BUDGET = 32           # search evaluations per arm per seed (E)
NULLS = 32            # permutation null replicates per pair
SPLIT = {"field": base.SPLIT_A, "region": base.SPLIT_B}
PAIRS = [("field", "region"), ("region", "field")]


# ---------------- the gossip run (live arm, protocol v3) ----------------

def noise(sends, family, truth, n, rng):
    """Rung 3's level-1 channel, record for record in form."""
    pdrop, pcorr, pmis = base.NOISE
    out = []
    for s in sends:
        r1 = rng.random()
        if r1 < pdrop:
            out.append({**s, "dst_actual": None, "src_interp": None,
                        "vals_recv": None, "ann": "dropped",
                        "corr": False})
            continue
        corr = False
        vals = list(s["vals_sent"])
        if rng.random() < pcorr:
            corr = True
            vals = base.corrupt_vals(vals, s["src"], family, truth, n, rng)
        if r1 < pdrop + pmis:
            actual = rng.randrange(n)
            while actual == s["dst_intended"]:
                actual = rng.randrange(n)
            interp = (actual + rng.choice((-1, 1))) % n
            out.append({**s, "dst_actual": actual, "src_interp": interp,
                        "vals_recv": vals, "ann": "misdelivered",
                        "corr": corr})
        else:
            out.append({**s, "dst_actual": s["dst_intended"],
                        "src_interp": s["src"], "vals_recv": vals,
                        "ann": "delivered", "corr": corr})
    return out


def run(seed, family, n=N, ticks=TICKS):
    """One live gossip run. Returns (summary, records)."""
    if family == "field":
        truth = base.gen_field(seed, n)
        obs = base.gen_obs_a(seed, n, truth)
    else:
        truth = base.gen_labels(seed, n)
        obs = base.gen_obs_b(seed, n, truth)
    reports = [{a: [obs[a]]} for a in range(n)]
    pe = base.make_point_est(family, reports, obs)
    pick = base.state_hash if family == "field" else base.state_hash_b
    tal = base.new_tally()
    tal1 = base.new_tally()
    records = []
    steps = 0
    sent = 0
    delivered = 0
    cuts = {8, 16, 24, ticks}
    hashes = {}
    rng = random.Random(repr((seed, "live4")))
    matrix = {}
    for tick in range(ticks):
        sends = []
        for a in range(n):
            steps += 1
            bundle = base.make_bundle(pe, a, tick, n)
            for dirc in (-1, 1):
                sends.append({"tick": tick, "lvl": 1, "src": a,
                              "dst_intended": (a + dirc) % n,
                              "vals_sent": list(bundle)})
            sent += 2 * base.MSG_BITS
        recs = noise(sends, family, truth, n, rng)
        recs.sort(key=lambda r: (r["src"],
                                 -1 if r["dst_actual"] is None
                                 else r["dst_actual"]))
        for rec in recs:
            done = 0
            if rec["vals_recv"] is not None:
                done = base.apply_delivery(reports, rec, n)
                delivered += base.MSG_BITS
                key = (rec["src"], rec["dst_actual"])
                matrix[key] = matrix.get(key, 0) + 1
            base.tally_record(tal, rec, done)
            base.tally_record(tal1, rec, done)
            records.append(rec)
        if tick + 1 in cuts:
            hashes[str(tick + 1)] = pick(reports)
    if family == "field":
        cap, work, cov = base.score_a(reports, truth, n)
    else:
        cap, work, cov = base.score_b(reports, truth, n)
    summary = {
        "arm": "live", "seed": seed, "n": n, "ticks": ticks,
        "family": family, "cap": cap, "work": work, "coverage": cov,
        "steps": steps, "sent": sent, "delivered": delivered,
        "tally": tal, "tally1": tal1, "tally2": base.new_tally(),
        "hashes": hashes, "final": hashes[str(ticks)],
        "pairs": sorted([a, b, c] for (a, b), c in matrix.items()),
    }
    return summary, records


# ---------------- folds of a log, by group and by tick ----------------

def entries(records, n=N):
    """(dst, site) -> list of (group, tick, value), in log order.
    A record's contribution is exactly the harness's append rule:
    every non-null component about a site other than dst."""
    ent = {}
    for rec in records:
        if rec["vals_recv"] is None:
            continue
        dst = rec["dst_actual"]
        c = rec["src_interp"]
        vals = rec["vals_recv"]
        g = rec["src"] // (n // G)
        for j in range(8):
            v = vals[2 * j + 1]
            if v != NULL:
                site = (c + vals[2 * j]) % n
                if site != dst:
                    ent.setdefault((dst, site), []).append(
                        (g, rec["tick"], v))
    return ent


def table(records, family, truth, n=N):
    """One row per task (actor, distance, direction): the site,
    the split flag, and the fold data — per-group sorted values
    (field) or per-group label counts (region), plus the
    tick-tagged values for counterfactual folds."""
    ent = entries(records, n)
    rows = []
    for i in range(n):
        for d in range(1, 7):
            for dirn in (-1, 1):
                site = (i + dirn * d) % n
                held = base.held_out(SPLIT[family], i, d, dirn)
                ev = ent.get((i, site), [])
                if family == "field":
                    by = {}
                    for (g, t, v) in ev:
                        by.setdefault(g, []).append(v)
                    for g in by:
                        by[g].sort()
                    data = by
                else:
                    by = {}
                    for (g, t, v) in ev:
                        by.setdefault(g, [0, 0, 0])[v] += 1
                    data = by
                rows.append({"actor": i, "site": site, "held": held,
                             "by": data,
                             "bytick": [(t, v) for (g, t, v) in ev]})
    return rows


def kth(lists, k):
    """k-th smallest (0-indexed) across sorted lists of ints."""
    lo = min(l[0] for l in lists)
    hi = max(l[-1] for l in lists)
    while lo < hi:
        mid = (lo + hi) // 2
        cnt = 0
        for l in lists:
            cnt += bisect.bisect_right(l, mid)
        if cnt > k:
            hi = mid
        else:
            lo = mid + 1
    return lo


def est(row, mask, family):
    """The fold estimate for one task row under a group mask."""
    if family == "field":
        lists = [lst for g, lst in row["by"].items() if (mask >> g) & 1]
        total = sum(len(l) for l in lists)
        if total == 0:
            return 0
        return kth(lists, total // 2)
    counts = [0, 0, 0]
    for g, c in row["by"].items():
        if (mask >> g) & 1:
            for lab in range(3):
                counts[lab] += c[lab]
    if sum(counts) == 0:
        return 0
    return min(range(3), key=lambda lab: (-counts[lab], lab))


def estdrop(row, tick, family):
    """The fold estimate with one tick's values removed (full
    mask; the view's counterfactual unit)."""
    vals = [v for (t, v) in row["bytick"] if t != tick]
    if not vals:
        return 0
    if family == "field":
        vals.sort()
        return vals[len(vals) // 2]
    counts = [0, 0, 0]
    for v in vals:
        counts[v] += 1
    return min(range(3), key=lambda lab: (-counts[lab], lab))


def score1(family, pred, want):
    if family == "field":
        return max(0.0, 1.0 - abs(pred - want) / 120.0)
    return 1.0 if pred == want else 0.0


def score(rows, family, truth, mask, held, only=None, drop=None):
    """Mean score over rows with the given split flag (and,
    if `only` is set, only that actor group's rows). With
    `drop`, the fold removes that tick's values instead."""
    s = 0.0
    c = 0
    for row in rows:
        if row["held"] != held:
            continue
        if only is not None and row["actor"] // (N // G) != only:
            continue
        if drop is None:
            pred = est(row, mask, family)
        else:
            pred = estdrop(row, drop, family)
        s += score1(family, pred, truth[row["site"]])
        c += 1
    return s / c


# ---------------- the view of a log (registration: view grain) ----

def view(records, family, truth, n=N):
    rows = table(records, family, truth, n)
    full = [score(rows, family, truth, 255, True, only=b)
            for b in range(G)]
    delivered = {}
    for rec in records:
        if rec["vals_recv"] is not None:
            delivered[rec["tick"]] = delivered.get(rec["tick"], 0) + 1
    edges = []
    for t in range(TICKS):
        comp = [score(rows, family, truth, 255, True, only=b, drop=t)
                for b in range(G)]
        edge = sorted(b for b in range(G) if comp[b] != full[b])
        edges.append({"tick": t, "edge": edge,
                      "weight": delivered.get(t, 0)})
    matrix = [[0] * G for _ in range(G)]
    for e in edges:
        for b in e["edge"]:
            for b2 in e["edge"]:
                matrix[b][b2] += e["weight"]
    # exact sensitivity over all 256 configurations
    comps = {}
    for mask in range(256):
        comps[mask] = [score(rows, family, truth, mask, True, only=b)
                       for b in range(G)]
    sens = {a: set() for a in range(G)}
    for mask in range(256):
        for a in range(G):
            other = mask ^ (1 << a)
            if other < mask:
                continue
            for b in range(G):
                if comps[mask][b] != comps[other][b]:
                    sens[a].add(b)

    def live(mask):
        out = set()
        for a in range(G):
            if (mask >> a) & 1:
                out |= sens[a]
        return out

    def mulam(mask):
        lv = live(mask)
        mu = sum(e["weight"] for e in edges
                 if len(e["edge"]) >= 2 and set(e["edge"]) <= lv)
        return mu, len(lv), sorted(lv)

    tab = {}
    for mask in range(256):
        mu, lam, lv = mulam(mask)
        tab[mask] = {"live": lv, "mu": mu, "lambda": lam,
                     "rho": [mu, lam]}
    mua = tab[255]["mu"]
    suff = [m for m in range(256) if tab[m]["mu"] == mua]
    mini = [m for m in suff
            if not any(o != m and (o & m) == o and tab[o]["mu"] == mua
                       for o in suff)]
    best = max((tab[m]["rho"] for m in mini), default=None)
    high = [m for m in mini if tab[m]["rho"] == best]
    dead = [a for a in range(G) if live(255 ^ (1 << a)) == live(255)]

    def names(mask):
        return [f"group{g}" for g in range(G) if (mask >> g) & 1]

    return {
        "family": family, "components": full, "edges": edges,
        "matrix": matrix,
        "sensitivity": {f"group{a}": sorted(sens[a]) for a in range(G)},
        "live": tab[255]["live"], "mu": mua,
        "lambda": tab[255]["lambda"],
        "minimal": [{"axes": names(m), "rho": tab[m]["rho"]}
                    for m in mini],
        "highest": [{"axes": names(m), "rho": tab[m]["rho"]}
                    for m in high],
        "dead": dead,
        "tab": {str(m): tab[m] for m in range(256)},
    }


# ---------------- artifacts (registration: extraction, controls) ----

def extract(matrix):
    """A*: the matrix reindexed by descending diagonal rank,
    ties by ascending index. Returns (artifact, rank order)."""
    rank = sorted(range(G), key=lambda b: (-matrix[b][b], b))
    art = [[matrix[rank[i]][rank[j]] for j in range(G)] for i in range(G)]
    return art, rank


def encode(matrix, w):
    """Canonical bytes: header (dim, width, pad as 2 bytes) then
    row-major entries at w bytes each."""
    out = bytearray([G, w, 0, 0])
    for i in range(G):
        for j in range(G):
            out += matrix[i][j].to_bytes(w, "big")
    return bytes(out)


def widthof(matrix):
    top = max(max(row) for row in matrix)
    return max(1, (top.bit_length() + 7) // 8)


def flat(matrix):
    return [matrix[i][j] for i in range(G) for j in range(G)]


def unflat(vals):
    return [vals[i * G:(i + 1) * G] for i in range(G)]


def artifacts(matrix, pair):
    """A* and its registered controls and nulls for one pair."""
    art, rank = extract(matrix)
    w = widthof(art)
    top = max(flat(art))
    rng = random.Random(2026112501 + pair)
    vals = flat(art)
    rng.shuffle(vals)
    unstr = unflat(vals)
    rng = random.Random(2026112601 + pair)
    rand = [[rng.randint(0, top) for _ in range(G)] for _ in range(G)]
    zero = [[0] * G for _ in range(G)]
    nulls = []
    for j in range(1, NULLS + 1):
        rng = random.Random(2026112701 + 1000 * pair + j)
        perm = list(range(G))
        rng.shuffle(perm)
        nulls.append({"perm": perm,
                      "matrix": [[art[perm[i]][perm[j2]]
                                  for j2 in range(G)]
                                 for i in range(G)]})
    return {"star": art, "rank": rank, "w": w,
            "bits": 8 * len(encode(art, w)),
            "hash": hashlib.sha256(encode(art, w)).hexdigest(),
            "unstructured": unstr, "random": rand, "zero": zero,
            "nulls": nulls,
            "sizes": {"star": 8 * len(encode(art, w)),
                      "unstructured": 8 * len(encode(unstr, w)),
                      "random": 8 * len(encode(rand, w)),
                      "zero": 8 * len(encode(zero, w))}}


# ---------------- the target configuration search ----------------

def prio(matrix, mask):
    """Total artifact weight over the subset's component pairs
    (registration amendment v2; was the mean weight)."""
    if mask == 0:
        return -1
    s = 0
    for i in range(G):
        if (mask >> i) & 1:
            for j in range(G):
                if (mask >> j) & 1:
                    s += matrix[i][j]
    return s


def order(matrix):
    """All 256 subsets in the arm's search order."""
    if matrix is None:
        # uniform order: nonempty by decreasing size then mask;
        # empty last
        return sorted(range(256),
                      key=lambda m: (m == 0, -bin(m).count("1"), m))
    return sorted(range(256),
                  key=lambda m: (-prio(matrix, m),
                                 -bin(m).count("1"), m))


def search(rows, family, truth, matrix, budget=BUDGET):
    """Evaluate the first `budget` subsets of the arm's order on
    the working set; select the best; return the record. The
    score table is artifact-free: identical rows give identical
    scores under every artifact."""
    seq = order(matrix)[:budget]
    scored = []
    best = None
    for mask in seq:
        w = score(rows, family, truth, mask, False)
        scored.append([mask, w])
        if best is None or w > best[1]:
            best = (mask, w)
    cap = score(rows, family, truth, best[0], True)
    return {"order": seq, "scored": scored, "picked": best[0],
            "work": best[1], "cap": cap}


# ---------------- batteries ----------------

def write(outdir, tag, summary, records):
    path = os.path.join(outdir, tag + ".jsonl")
    with open(path, "w") as fh:
        for rec in records:
            fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
    summary["bytes"] = os.path.getsize(path)
    summary["file"] = tag + ".jsonl"
    with open(os.path.join(outdir, tag + ".json"), "w") as fh:
        json.dump(summary, fh, indent=1)


def battery(family, outdir):
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "config.json"), "w") as fh:
        json.dump({"battery": family, "family": family, "n": N,
                   "ticks": TICKS, "seeds": SEEDS,
                   "split": SPLIT[family], "groups": G}, fh, indent=1)
    summaries = []
    rows = {}
    for seed in SEEDS:
        rep = seed - 2026112100
        t0 = time.time()
        summary, records = run(seed, family)
        summary["wall"] = round(time.time() - t0, 3)
        write(outdir, f"live-rep{rep}", summary, records)
        summaries.append(summary)
        if family == "field":
            truth = base.gen_field(seed, N)
        else:
            truth = base.gen_labels(seed, N)
        rows[seed] = (table(records, family, truth), truth)
        print(f"{family} live-rep{rep}: cap={summary['cap']:.4f} "
              f"wall={summary['wall']}s", flush=True)
    with open(os.path.join(outdir, "summaries.json"), "w") as fh:
        json.dump(summaries, fh, indent=1)
    return summaries, rows


def pair(pairidx, srcfam, tgtfam, srcview, tgtrows, outdir):
    os.makedirs(outdir, exist_ok=True)
    arts = artifacts(srcview["matrix"], pairidx)
    arms = {"star": arts["star"], "unstructured": arts["unstructured"],
            "random": arts["random"], "nothing": None}
    result = {"pair": pairidx, "source": srcfam, "target": tgtfam,
              "artifacts": arts, "arms": {}, "nulls": [],
              "ceiling": {}}
    for name, matrix in arms.items():
        per = {}
        for seed in SEEDS:
            rows, truth = tgtrows[seed]
            per[str(seed)] = search(rows, tgtfam, truth, matrix)
        result["arms"][name] = per
        caps = [per[str(s)]["cap"] for s in SEEDS]
        print(f"pair{pairidx} {name}: caps="
              f"{[round(c, 4) for c in caps]}", flush=True)
    for j, null in enumerate(arts["nulls"]):
        per = {}
        for seed in SEEDS:
            rows, truth = tgtrows[seed]
            per[str(seed)] = search(rows, tgtfam, truth, null["matrix"])
        caps = [per[str(s)]["cap"] for s in SEEDS]
        result["nulls"].append({"j": j + 1, "perm": null["perm"],
                                "caps": caps,
                                "picked": {str(s): per[str(s)]["picked"]
                                           for s in SEEDS}})
        print(f"pair{pairidx} null{j + 1}: mean="
              f"{sum(caps) / len(caps):.4f}", flush=True)
    for seed in SEEDS:
        rows, truth = tgtrows[seed]
        result["ceiling"][str(seed)] = search(rows, tgtfam, truth,
                                              None, budget=256)
    with open(os.path.join(outdir, "search.json"), "w") as fh:
        json.dump(result, fh, indent=1)
    return result


def decide(result):
    """The registered decision, from a pair's search record."""
    def caps(name):
        return [result["arms"][name][str(s)]["cap"] for s in SEEDS]

    def mean(vals):
        return sum(vals) / len(vals)

    def spread(vals):
        return max(vals) - min(vals)

    star = caps("star")
    ctrls = {name: caps(name)
             for name in ("unstructured", "random", "nothing")}
    cmax = max(mean(v) for v in ctrls.values())
    dt = mean(star) - cmax
    delta = max(spread(v) for v in ctrls.values())
    nulldts = [mean(n["caps"]) - cmax for n in result["nulls"]]
    perarm = all(mean(star) > mean(v) + spread(v)
                 for v in ctrls.values())
    paired = []
    for idx, s in enumerate(SEEDS):
        best = max(result["arms"][name][str(s)]["cap"]
                   for name in ctrls)
        paired.append(star[idx] - best)
    return {
        "caps": {"star": star, **ctrls},
        "means": {"star": mean(star),
                  **{k: mean(v) for k, v in ctrls.items()}},
        "spreads": {k: spread(v) for k, v in ctrls.items()},
        "dt": dt, "delta": delta,
        "win_primary": dt > delta and all(dt > d for d in nulldts),
        "null_dts": nulldts,
        "null_max": max(nulldts),
        "win_perarm": perarm and all(dt > d for d in nulldts),
        "paired": paired,
    }


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "results")
    views = {}
    rows = {}
    for family in ("field", "region"):
        summaries, famrows = battery(family,
                                     os.path.join(root, family))
        rows[family] = famrows
        rep1 = [json.loads(l) for l in open(
            os.path.join(root, family, "live-rep1.jsonl"))]
        truth = (base.gen_field(SEEDS[0], N) if family == "field"
                 else base.gen_labels(SEEDS[0], N))
        t0 = time.time()
        v = view(rep1, family, truth)
        v["wall"] = round(time.time() - t0, 3)
        views[family] = v
        with open(os.path.join(root, family, "view.json"), "w") as fh:
            json.dump(v, fh, indent=1)
        print(f"{family} view: mu={v['mu']} lambda={v['lambda']} "
              f"dead={v['dead']} wall={v['wall']}s", flush=True)
    decisions = {}
    for idx, (srcfam, tgtfam) in enumerate(PAIRS):
        result = pair(idx, srcfam, tgtfam, views[srcfam],
                      rows[tgtfam], os.path.join(root, f"pair{idx}"))
        dec = decide(result)
        decisions[f"pair{idx}"] = dec
        with open(os.path.join(root, f"pair{idx}", "decision.json"),
                  "w") as fh:
            json.dump(dec, fh, indent=1)
        print(f"pair{idx}: DT={dec['dt']:.4f} delta={dec['delta']:.4f} "
              f"null_max={dec['null_max']:.4f} "
              f"win={dec['win_primary']} perarm={dec['win_perarm']}",
              flush=True)
    both = all(d["win_primary"] for d in decisions.values())
    print(f"RUNG4 CLAIM: {'TRANSFER ESTABLISHED' if both else 'NO TRANSFER (claim dead as registered)'}")
    with open(os.path.join(root, "decisions.json"), "w") as fh:
        json.dump(decisions, fh, indent=1)


if __name__ == "__main__":
    main()
