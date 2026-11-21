#!/usr/bin/env python3
"""Rung 4 independent checker.

Reads only the persisted artifacts (family battery dirs and
pair search records under results/) and verifies, by its own
code path written from registration.md (nothing imported from
harness4.py or harness3.py):

  - budget shape of every persisted gossip run;
  - replay exactness: folding each log from the seed-derived
    initial state reproduces the recorded final hash;
  - restart exactness from the cuts at ticks 8, 16, 24;
  - DET = TAL at every registered append cut, and agreement
    with the harness's online tally at the final record;
  - view agreement: the interaction view of each family's
    replicate-1 log recomputed here (matrix, components, mu,
    lambda) equals the harness's persisted view;
  - extraction agreement: A* recomputed from that matrix
    equals the persisted artifact, bit for bit under the
    canonical encoding;
  - artifact facts: |U| = |R*| = |zero| = |A*| in bits; U's
    and every null's entry multiset equals A*'s;
  - search agreement: every arm's, null's, and the ceiling's
    order prefix, evaluated working scores, selected subset,
    and capability recomputed from the persisted target logs
    and artifacts, compared exactly;
  - the selection-only spot property: the per-subset working
    score table of a target seed is one artifact-free table,
    recomputed once here and checked against every arm's
    recorded evaluations of the same subsets.
"""
import bisect
import hashlib
import itertools
import json
import math
import os
import random
import sys
import time

NULL = 10 ** 9
G = 8
N = 256
TICKS = 32
SEEDS = [2026112100 + r for r in range(1, 9)]
SPLIT = {"field": 2026112199, "region": 2026112299}
PAIRS = [("field", "region"), ("region", "field")]


# ---------------- generation (own code, registration formulas) ----

def field(seed, n):
    rng = random.Random(seed ^ 0xF1E1D)
    phases = [rng.uniform(0, 2 * math.pi) for _ in range(3)]
    amps = [60, 35, 20]
    return [int(round(sum(a * math.sin(2 * math.pi * (k + 1) * i / n
                                        + phases[k])
                           for k, a in enumerate(amps))))
            for i in range(n)]


def labels(seed, n):
    rng = random.Random(seed ^ 0x5E6)
    lens = [n // 6 + rng.randint(-4, 4) for _ in range(6)]
    while sum(lens) != n:
        if sum(lens) < n:
            lens[rng.randrange(6)] += 1
        else:
            i = max(range(6), key=lambda k: lens[k])
            lens[i] -= 1
    out = []
    for s, ln in enumerate(lens):
        out += [s % 3] * ln
    return out


def obs(seed, n, truth, family):
    rng = random.Random(seed ^ 0x0B5EED)
    if family == "field":
        return [truth[i] + rng.randint(-25, 25) for i in range(n)]
    out = []
    for i in range(n):
        r = rng.random()
        if r < 0.7:
            out.append(truth[i])
        elif r < 0.85:
            out.append((truth[i] + 1) % 3)
        else:
            out.append((truth[i] + 2) % 3)
    return out


def truthof(seed, family, n=N):
    return field(seed, n) if family == "field" else labels(seed, n)


def median(vals):
    return sorted(vals)[len(vals) // 2]


def mode(vals):
    cnt = {}
    for v in vals:
        cnt[v] = cnt.get(v, 0) + 1
    return min(cnt, key=lambda v: (-cnt[v], v))


def hashstate(reports, family):
    est = median if family == "field" else mode
    canon = [sorted((site, est(v)) for site, v in t.items() if v)
             for t in reports]
    return hashlib.sha256(
        json.dumps(canon, separators=(",", ":")).encode()).hexdigest()


def start(seed, n, family):
    truth = truthof(seed, family, n)
    o = obs(seed, n, truth, family)
    return [{a: [o[a]]} for a in range(n)]


def sites(rec, n):
    if rec["vals_recv"] is None:
        return []
    dst = rec["dst_actual"]
    c = rec["src_interp"]
    out = []
    for j in range(8):
        v = rec["vals_recv"][2 * j + 1]
        if v != NULL:
            site = (c + rec["vals_recv"][2 * j]) % n
            if site != dst:
                out.append((site, v))
    return out


def fold(records, seed, n, family, upto=None):
    reports = start(seed, n, family)
    steps = 0
    for rec in records:
        if upto is not None and rec["tick"] >= upto:
            break
        steps += 1
        for (site, v) in sites(rec, n):
            reports[rec["dst_actual"]].setdefault(site, []).append(v)
            steps += 1
    return reports, steps


# ---------------- tally (DET and TAL, own code) ----------------

def tally0():
    return {"records": 0, "delivered_class": 0, "ann_delivered": 0,
            "dropped": 0, "corr": 0, "misdelivered": 0, "frozen": 0,
            "shuffled": 0, "filler": 0, "reports": 0, "sum_abs_recv": 0}


def tallyadd(t, rec, n):
    t["records"] += 1
    if rec["vals_recv"] is not None:
        t["delivered_class"] += 1
        t["sum_abs_recv"] += sum(
            abs(rec["vals_recv"][2 * j + 1]) for j in range(8)
            if rec["vals_recv"][2 * j + 1] != NULL)
        t["reports"] += len(sites(rec, n))
    ann = rec["ann"]
    if ann == "delivered":
        t["ann_delivered"] += 1
    elif ann in ("dropped", "misdelivered", "frozen", "shuffled",
                 "filler"):
        t[ann] += 1
    if rec["corr"]:
        t["corr"] += 1


def tallybatch(records, n):
    t = tally0()
    for r in records:
        tallyadd(t, r, n)
    return t


# ---------------- folds by group and tick (own code) ----------------

def held(family, i, d, dirn):
    h = hashlib.sha256(
        f"{SPLIT[family]}:{i}:{d}:{dirn}".encode()).digest()
    return h[0] % 2 == 0


def rows(records, family, n=N):
    ent = {}
    for rec in records:
        if rec["vals_recv"] is None:
            continue
        dst = rec["dst_actual"]
        g = rec["src"] // (n // G)
        for (site, v) in sites(rec, n):
            ent.setdefault((dst, site), []).append((g, rec["tick"], v))
    out = []
    for i in range(n):
        for d in range(1, 7):
            for dirn in (-1, 1):
                site = (i + dirn * d) % n
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
                out.append({"actor": i, "site": site,
                            "held": held(family, i, d, dirn),
                            "by": data,
                            "bytick": [(t, v) for (g, t, v) in ev]})
    return out


def kth(lists, k):
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


def one(family, pred, want):
    if family == "field":
        return max(0.0, 1.0 - abs(pred - want) / 120.0)
    return 1.0 if pred == want else 0.0


def score(rows_, family, truth, mask, isheld, only=None, drop=None):
    s = 0.0
    c = 0
    for row in rows_:
        if row["held"] != isheld:
            continue
        if only is not None and row["actor"] // (N // G) != only:
            continue
        pred = (est(row, mask, family) if drop is None
                else estdrop(row, drop, family))
        s += one(family, pred, truth[row["site"]])
        c += 1
    return s / c


def view(records, family, truth, n=N):
    rs = rows(records, family, n)
    full = [score(rs, family, truth, 255, True, only=b)
            for b in range(G)]
    delivered = {}
    for rec in records:
        if rec["vals_recv"] is not None:
            delivered[rec["tick"]] = delivered.get(rec["tick"], 0) + 1
    edges = []
    for t in range(TICKS):
        comp = [score(rs, family, truth, 255, True, only=b, drop=t)
                for b in range(G)]
        edge = sorted(b for b in range(G) if comp[b] != full[b])
        edges.append({"tick": t, "edge": edge,
                      "weight": delivered.get(t, 0)})
    matrix = [[0] * G for _ in range(G)]
    for e in edges:
        for b in e["edge"]:
            for b2 in e["edge"]:
                matrix[b][b2] += e["weight"]
    comps = {}
    for mask in range(256):
        comps[mask] = [score(rs, family, truth, mask, True, only=b)
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
        return mu, len(lv)

    mu, lam = mulam(255)
    dead = [a for a in range(G) if live(255 ^ (1 << a)) == live(255)]
    return {"components": full, "matrix": matrix, "mu": mu,
            "lambda": lam, "dead": dead}


# ---------------- artifacts and search (own code) ----------------

def encode(matrix, w):
    out = bytearray([G, w, 0, 0])
    for i in range(G):
        for j in range(G):
            out += matrix[i][j].to_bytes(w, "big")
    return bytes(out)


def prio(matrix, mask):
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
    if matrix is None:
        return sorted(range(256),
                      key=lambda m: (m == 0, -bin(m).count("1"), m))
    return sorted(range(256),
                  key=lambda m: (-prio(matrix, m),
                                 -bin(m).count("1"), m))


def search(rows_, family, truth, matrix, budget, cache):
    seq = order(matrix)[:budget]
    scored = []
    best = None
    for mask in seq:
        if mask not in cache:
            cache[mask] = score(rows_, family, truth, mask, False)
        w = cache[mask]
        scored.append([mask, w])
        if best is None or w > best[1]:
            best = (mask, w)
    cap = score(rows_, family, truth, best[0], True)
    return {"order": seq, "scored": scored, "picked": best[0],
            "work": best[1], "cap": cap}


# ---------------- family battery checks ----------------

def checkfamily(root, family):
    bdir = os.path.join(root, family)
    cfg = json.load(open(os.path.join(bdir, "config.json")))
    n = cfg["n"]
    out = {"battery": family, "runs": {}, "failures": [],
           "cuts": 0, "agree": 0, "restarts": 0, "restartok": 0}
    tags = sorted(fn[:-5] for fn in os.listdir(bdir)
                  if fn.endswith(".json") and fn not in
                  ("config.json", "summaries.json", "view.json",
                   "checks.json"))
    for tag in tags:
        summ = json.load(open(os.path.join(bdir, tag + ".json")))
        raw = open(os.path.join(bdir, summ["file"]), "rb").readlines()
        records = [json.loads(l) for l in raw]
        sizes = [len(l) for l in raw]
        run = {"shape": summ["steps"] == n * TICKS
               and summ["sent"] == 2 * n * TICKS * 336
               and len(records) == 2 * n * TICKS}
        if not run["shape"]:
            out["failures"].append(f"{tag}: budget shape")
        reps, fsteps = fold(records, summ["seed"], n, family)
        run["replay"] = hashstate(reps, family) == summ["final"]
        run["fold"] = fsteps
        if not run["replay"]:
            out["failures"].append(f"{tag}: replay hash mismatch")
        state = tally0()
        cuts = {len(records)}
        k = 4096
        while k < len(records):
            cuts.add(k)
            k += 4096
        seen = set()
        for idx, r in enumerate(records):
            if r["tick"] in (0, 1, 2) and r["tick"] not in seen:
                seen.add(r["tick"])
                cuts.add(idx)
        agree = 0
        for idx, r in enumerate(records, start=1):
            tallyadd(state, r, n)
            if idx in cuts:
                out["cuts"] += 1
                if tallybatch(records[:idx], n) == state:
                    agree += 1
                    out["agree"] += 1
                else:
                    out["failures"].append(f"{tag}: DET!=TAL cut {idx}")
        run["tally"] = state == summ["tally"]
        if not run["tally"]:
            out["failures"].append(f"{tag}: final TAL != online")
        run["restarts"] = {}
        for cut in (8, 16, 24):
            reps_c, steps_c = fold(records, summ["seed"], n, family,
                                   upto=cut)
            ok = hashstate(reps_c, family) == summ["hashes"][str(cut)]
            nbytes = sum(b for l, b in zip(records, sizes)
                         if l["tick"] < cut)
            run["restarts"][str(cut)] = {"ok": ok, "bytes": nbytes,
                                         "fold": steps_c}
            out["restarts"] += 1
            if ok:
                out["restartok"] += 1
            else:
                out["failures"].append(f"{tag}: restart cut {cut}")
        out["runs"][tag] = run
        print(f"checked {family} {tag}: shape={run['shape']} "
              f"replay={run['replay']} tally={run['tally']} "
              f"cuts={agree}", flush=True)
    # view agreement on replicate 1
    rep1 = [json.loads(l) for l in open(
        os.path.join(bdir, "live-rep1.jsonl"))]
    truth = truthof(SEEDS[0], family)
    mine = view(rep1, family, truth)
    theirs = json.load(open(os.path.join(bdir, "view.json")))
    out["view"] = {"matrix": mine["matrix"] == theirs["matrix"],
                   "components": mine["components"]
                   == theirs["components"],
                   "mu": mine["mu"] == theirs["mu"],
                   "lambda": mine["lambda"] == theirs["lambda"],
                   "dead": mine["dead"] == theirs["dead"]}
    if not all(out["view"].values()):
        out["failures"].append(f"{family}: view mismatch {out['view']}")
    out["matrix"] = mine["matrix"]
    with open(os.path.join(bdir, "checks.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"{family}: cuts {out['agree']}/{out['cuts']}, restarts "
          f"{out['restartok']}/{out['restarts']}, view={out['view']}, "
          f"failures={out['failures']}", flush=True)
    return out


# ---------------- pair checks ----------------

def checkpair(root, pairidx, matrices):
    srcfam, tgtfam = PAIRS[pairidx]
    pdir = os.path.join(root, f"pair{pairidx}")
    rec = json.load(open(os.path.join(pdir, "search.json")))
    arts = rec["artifacts"]
    out = {"pair": pairidx, "failures": [], "maxdiff": 0.0}
    # extraction agreement: A* from the checker's own source matrix
    matrix = matrices[srcfam]
    rank = sorted(range(G), key=lambda b: (-matrix[b][b], b))
    star = [[matrix[rank[i]][rank[j]] for j in range(G)]
            for i in range(G)]
    out["extract"] = star == arts["star"] and rank == arts["rank"]
    if not out["extract"]:
        out["failures"].append("extraction mismatch")
    w = arts["w"]
    out["hash"] = (hashlib.sha256(encode(star, w)).hexdigest()
                   == arts["hash"])
    if not out["hash"]:
        out["failures"].append("artifact hash mismatch")
    sizes = {k: 8 * len(encode(arts[k], w))
             for k in ("star", "unstructured", "random", "zero")}
    out["sizes"] = sizes == arts["sizes"] and len(set(sizes.values())) == 1
    if not out["sizes"]:
        out["failures"].append(f"artifact sizes {sizes} vs {arts['sizes']}")

    def multiset(m):
        return sorted(itertools.chain.from_iterable(m))

    out["multisets"] = (
        multiset(arts["unstructured"]) == multiset(star)
        and all(multiset(n["matrix"]) == multiset(star)
                for n in arts["nulls"]))
    if not out["multisets"]:
        out["failures"].append("entry multiset mismatch")
    # search agreement per seed, with one artifact-free score
    # table per seed (the selection-only spot property)
    tdir = os.path.join(root, tgtfam)
    arms = {"star": arts["star"],
            "unstructured": arts["unstructured"],
            "random": arts["random"], "nothing": None}
    checked = 0
    for seed in SEEDS:
        rep = seed - 2026112100
        records = [json.loads(l) for l in open(
            os.path.join(tdir, f"live-rep{rep}.jsonl"))]
        truth = truthof(seed, tgtfam)
        rs = rows(records, tgtfam)
        cache = {}
        for name, matrix in arms.items():
            mine = search(rs, tgtfam, truth, matrix, 32, cache)
            theirs = rec["arms"][name][str(seed)]
            ok = (mine["order"] == theirs["order"]
                  and mine["picked"] == theirs["picked"])
            for (m1, w1), (m2, w2) in zip(mine["scored"],
                                          theirs["scored"]):
                out["maxdiff"] = max(out["maxdiff"], abs(w1 - w2))
                ok = ok and m1 == m2 and w1 == w2
            out["maxdiff"] = max(out["maxdiff"],
                                 abs(mine["cap"] - theirs["cap"]))
            ok = ok and mine["cap"] == theirs["cap"]
            checked += 1
            if not ok:
                out["failures"].append(
                    f"pair{pairidx} {name} seed {seed}: search mismatch")
        for j, null in enumerate(arts["nulls"]):
            mine = search(rs, tgtfam, truth, null["matrix"], 32, cache)
            theirs = rec["nulls"][j]
            ok = mine["cap"] == theirs["caps"][rep - 1] \
                and mine["picked"] == theirs["picked"][str(seed)]
            out["maxdiff"] = max(out["maxdiff"],
                                 abs(mine["cap"] - theirs["caps"][rep - 1]))
            checked += 1
            if not ok:
                out["failures"].append(
                    f"pair{pairidx} null{j + 1} seed {seed}: mismatch")
        mine = search(rs, tgtfam, truth, None, 256, cache)
        theirs = rec["ceiling"][str(seed)]
        if not (mine["picked"] == theirs["picked"]
                and mine["cap"] == theirs["cap"]):
            out["failures"].append(
                f"pair{pairidx} ceiling seed {seed}: mismatch")
        checked += 1
    out["searches"] = checked
    with open(os.path.join(pdir, "checks.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"pair{pairidx}: extract={out['extract']} hash={out['hash']} "
          f"sizes={out['sizes']} multisets={out['multisets']} "
          f"searches={checked} maxdiff={out['maxdiff']} "
          f"failures={out['failures']}", flush=True)
    return out


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "results")
    matrices = {}
    total = {"failures": []}
    for family in ("field", "region"):
        res = checkfamily(root, family)
        matrices[family] = res["matrix"]
        total["failures"] += res["failures"]
        total[family] = {k: res[k] for k in
                         ("cuts", "agree", "restarts", "restartok")}
    for idx in (0, 1):
        res = checkpair(root, idx, matrices)
        total["failures"] += res["failures"]
        total[f"pair{idx}"] = {k: res[k] for k in
                               ("extract", "hash", "sizes", "multisets",
                                "searches", "maxdiff")}
    print("TOTAL failures:", total["failures"])
    with open(os.path.join(root, "checks-total.json"), "w") as fh:
        json.dump(total, fh, indent=1)


if __name__ == "__main__":
    main()
