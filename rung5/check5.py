#!/usr/bin/env python3
"""Rung 5 checker: an independent code path.

Imports nothing from harness3, harness4 or harness5. Recomputes
from the persisted artifacts, following registration.md section
10: replay of every log, checkpoint cut folds (hash and
capability), append-cut equality (a from-scratch batch tally of
each prefix against the harness's online tally snapshot at that
cut), restarts at every checkpoint of every battery run, budget
shapes, replicate 1's live cut views, evaluation in reverse
checkpoint order, the frozen logs against their generator logs,
and the decision record.
"""
import hashlib
import json
import math
import os
import random
import sys

NULL = 10 ** 9
G = 8
N = 256
TICKS = 128
CHECKPOINTS = (1, 2, 4, 8, 16, 32, 64, 128)
SEEDS = [2026112100 + r for r in range(1, 9)]
SPLIT = {"field": 2026112199, "region": 2026112299}
EPS = {"field": 1.0 / 1488960, "region": 1.0 / 12352}
ARMS = ("live", "isolated", "frozen", "shuffled")

fails = []
counts = {"replay": 0, "cuts": 0, "dettal": 0, "restart": 0,
          "budget": 0, "views": 0, "order": 0, "frozenlog": 0,
          "decision": 0}


def bad(msg):
    fails.append(msg)
    print("FAIL:", msg, flush=True)


# ---------------- generators and scoring (registered formulas) ----

def gen_field(seed, n):
    rng = random.Random(seed ^ 0xF1E1D)
    phases = [rng.uniform(0, 2 * math.pi) for _ in range(3)]
    amps = [60, 35, 20]
    return [int(round(sum(a * math.sin(2 * math.pi * (k + 1) * i / n
                                        + phases[k])
                           for k, a in enumerate(amps))))
            for i in range(n)]


def gen_obs_a(seed, n, f):
    rng = random.Random(seed ^ 0x0B5EED)
    return [f[i] + rng.randint(-25, 25) for i in range(n)]


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


def gen_obs_b(seed, n, labels):
    rng = random.Random(seed ^ 0x0B5EED)
    obs = []
    for i in range(n):
        r = rng.random()
        if r < 0.7:
            obs.append(labels[i])
        elif r < 0.85:
            obs.append((labels[i] + 1) % 3)
        else:
            obs.append((labels[i] + 2) % 3)
    return obs


def held_out(split, i, d, direction):
    h = hashlib.sha256(f"{split}:{i}:{d}:{direction}".encode()).digest()
    return h[0] % 2 == 0


def median(vals):
    s = sorted(vals)
    return s[len(s) // 2]


def mode(vals):
    cnt = {}
    for v in vals:
        cnt[v] = cnt.get(v, 0) + 1
    return min(cnt, key=lambda v: (-cnt[v], v))


def truth_obs(family, seed):
    if family == "field":
        truth = gen_field(seed, N)
        return truth, gen_obs_a(seed, N, truth)
    truth = gen_labels(seed, N)
    return truth, gen_obs_b(seed, N, truth)


def score(family, reports, truth):
    ho_sum = ho_cnt = wk_sum = wk_cnt = 0.0
    ho_cov = 0
    for i in range(N):
        table = reports[i]
        for d in range(1, 7):
            for direction in (-1, 1):
                site = (i + direction * d) % N
                vals = table.get(site)
                if family == "field":
                    pred = median(vals) if vals else 0
                    s = max(0.0, 1.0 - abs(pred - truth[site]) / 120.0)
                else:
                    pred = mode(vals) if vals else 0
                    s = 1.0 if pred == truth[site] else 0.0
                if held_out(SPLIT[family], i, d, direction):
                    ho_sum += s
                    ho_cnt += 1
                    if vals:
                        ho_cov += 1
                else:
                    wk_sum += s
                    wk_cnt += 1
    return ho_sum / ho_cnt, wk_sum / wk_cnt, ho_cov / ho_cnt


def state_hash(family, reports):
    canon = []
    for a, table in enumerate(reports):
        if family == "field":
            row = sorted((site, median(vals))
                         for site, vals in table.items() if vals)
        else:
            row = sorted((site, mode(vals))
                         for site, vals in table.items() if vals)
        canon.append(row)
    blob = json.dumps(canon, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


# ---------------- the fold and the batch tally ----------------

def appended_of(rec):
    """Values one record appends, by the append rule alone."""
    if rec["vals_recv"] is None:
        return 0
    dst = rec["dst_actual"]
    c = rec["src_interp"]
    vals = rec["vals_recv"]
    k = 0
    for j in range(8):
        v = vals[2 * j + 1]
        if v != NULL and (c + vals[2 * j]) % N != dst:
            k += 1
    return k


def apply(rec, reports):
    if rec["vals_recv"] is None:
        return
    dst = rec["dst_actual"]
    c = rec["src_interp"]
    vals = rec["vals_recv"]
    for j in range(8):
        v = vals[2 * j + 1]
        if v != NULL:
            site = (c + vals[2 * j]) % N
            if site != dst:
                reports[dst].setdefault(site, []).append(v)


def batch_tally(records):
    """DET: a from-scratch tally of a record list, one pass, no
    state carried from anywhere."""
    tal = {"records": 0, "delivered_class": 0, "ann_delivered": 0,
           "dropped": 0, "corr": 0, "misdelivered": 0, "frozen": 0,
           "shuffled": 0, "filler": 0, "reports": 0, "sum_abs_recv": 0}
    for rec in records:
        tal["records"] += 1
        if rec["vals_recv"] is not None:
            tal["delivered_class"] += 1
            tal["sum_abs_recv"] += sum(
                abs(rec["vals_recv"][2 * j + 1]) for j in range(8)
                if rec["vals_recv"][2 * j + 1] != NULL)
        ann = rec["ann"]
        if ann == "delivered":
            tal["ann_delivered"] += 1
        elif ann in ("dropped", "misdelivered", "frozen", "shuffled",
                     "filler"):
            tal[ann] += 1
        if rec["corr"]:
            tal["corr"] += 1
        tal["reports"] += appended_of(rec)
    return tal


def copy_reports(reports):
    return [{site: list(vals) for site, vals in table.items()}
            for table in reports]


# ---------------- the view of a cut, recomputed ----------------

def entries(records):
    ent = {}
    for rec in records:
        if rec["vals_recv"] is None:
            continue
        dst = rec["dst_actual"]
        c = rec["src_interp"]
        vals = rec["vals_recv"]
        g = rec["src"] // (N // G)
        for j in range(8):
            v = vals[2 * j + 1]
            if v != NULL:
                site = (c + vals[2 * j]) % N
                if site != dst:
                    ent.setdefault((dst, site), []).append(
                        (g, rec["tick"], v))
    return ent


def kth(lists, k):
    import bisect
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


def view(records, family, truth, ticks):
    ent = entries(records)
    rows = []
    for i in range(N):
        for d in range(1, 7):
            for dirn in (-1, 1):
                site = (i + dirn * d) % N
                held = held_out(SPLIT[family], i, d, dirn)
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

    def est(row, mask):
        if family == "field":
            lists = [lst for g, lst in row["by"].items()
                     if (mask >> g) & 1]
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

    def estdrop(row, tick):
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

    def score1(pred, want):
        if family == "field":
            return max(0.0, 1.0 - abs(pred - want) / 120.0)
        return 1.0 if pred == want else 0.0

    def vscore(mask, only=None, drop=None):
        s = 0.0
        c = 0
        for row in rows:
            if not row["held"]:
                continue
            if only is not None and row["actor"] // (N // G) != only:
                continue
            pred = est(row, mask) if drop is None else estdrop(row, drop)
            s += score1(pred, truth[row["site"]])
            c += 1
        return s / c

    full = [vscore(255, only=b) for b in range(G)]
    delivered = {}
    for rec in records:
        if rec["vals_recv"] is not None:
            delivered[rec["tick"]] = delivered.get(rec["tick"], 0) + 1
    edges = []
    for t in range(ticks):
        comp = [vscore(255, only=b, drop=t) for b in range(G)]
        edge = sorted(b for b in range(G) if comp[b] != full[b])
        edges.append({"tick": t, "edge": edge,
                      "weight": delivered.get(t, 0)})
    comps = {}
    for mask in range(256):
        comps[mask] = [vscore(mask, only=b) for b in range(G)]
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

    lv = live(255)
    mu = sum(e["weight"] for e in edges
             if len(e["edge"]) >= 2 and set(e["edge"]) <= lv)
    return {"mu": mu, "lambda": len(lv), "live": sorted(lv),
            "edges": edges, "components": full,
            "dead": [a for a in range(G)
                     if live(255 ^ (1 << a)) == live(255)]}


# ---------------- per-run verification ----------------

def check_run(famdir, family, tag, is_battery):
    spath = os.path.join(famdir, tag + ".json")
    summary = json.load(open(spath))
    records = [json.loads(l) for l in open(
        os.path.join(famdir, tag + ".jsonl"))]
    if summary["steps"] != N * TICKS or summary["sent"] != N * TICKS * 2 * 336:
        bad(f"{tag}: budget shape steps={summary['steps']} "
            f"sent={summary['sent']}")
    else:
        counts["budget"] += 1
    if len(records) != N * TICKS * 2:
        bad(f"{tag}: {len(records)} records")
        return summary, records
    pertick = {}
    for rec in records:
        pertick[rec["tick"]] = pertick.get(rec["tick"], 0) + 1
    if any(pertick.get(t, 0) != 2 * N for t in range(TICKS)):
        bad(f"{tag}: per-tick record counts wrong")
    truth, obs = truth_obs(family, summary["seed"])
    reports = [{a: [obs[a]]} for a in range(N)]
    cutstate = {}
    pos = 0
    for t in CHECKPOINTS:
        target = 2 * N * t
        while pos < target:
            apply(records[pos], reports)
            pos += 1
        h = state_hash(family, reports)
        cap, work, cov = score(family, reports, truth)
        cut = summary["cuts"][str(t)]
        if h != cut["hash"] or cap != cut["cap"] or work != cut["work"] \
                or cov != cut["coverage"]:
            bad(f"{tag}: cut {t} hash/cap mismatch")
        else:
            counts["cuts"] += 1
        det = batch_tally(records[:target])
        if det != cut["tally"]:
            bad(f"{tag}: DET != TAL at cut {t}")
        else:
            counts["dettal"] += 1
        cutstate[t] = copy_reports(reports)
    while pos < len(records):
        apply(records[pos], reports)
        pos += 1
    if state_hash(family, reports) != summary["final"]:
        bad(f"{tag}: replay final hash mismatch")
    else:
        counts["replay"] += 1
    if summary["cap"] != summary["cuts"][str(TICKS)]["cap"]:
        bad(f"{tag}: summary cap != final cut cap")
    if is_battery:
        for t in CHECKPOINTS:
            state = cutstate[t]
            for rec in records[2 * N * t:]:
                apply(rec, state)
            if state_hash(family, state) != summary["final"]:
                bad(f"{tag}: restart from cut {t} mismatch")
            else:
                counts["restart"] += 1
    return summary, records


def check_family(family):
    famdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "results", family + "5")
    summaries = {}
    logs = {}
    for rep, seed in enumerate(SEEDS, start=1):
        for tag in [f"generator-rep{rep}"] + [f"{a}-rep{rep}" for a in ARMS]:
            s, recs = check_run(famdir, family, tag,
                                not tag.startswith("generator"))
            summaries[tag] = s
            logs[tag] = recs
            print(f"checked {family}5 {tag}", flush=True)
    # frozen logs are the generator logs, record for record
    for rep in range(1, 9):
        if logs[f"frozen-rep{rep}"] != logs[f"generator-rep{rep}"]:
            bad(f"{family}5 frozen-rep{rep}: log != generator log")
        else:
            counts["frozenlog"] += 1
    # evaluation order: replicate 1's live checkpoints, reverse order
    truth, obs = truth_obs(family, SEEDS[0])
    recs = logs["live-rep1"]
    live1 = summaries["live-rep1"]
    for t in reversed(CHECKPOINTS):
        reports = [{a: [obs[a]]} for a in range(N)]
        for rec in recs[:2 * N * t]:
            apply(rec, reports)
        cap, _, _ = score(family, reports, truth)
        if cap != live1["cuts"][str(t)]["cap"]:
            bad(f"{family}5 live-rep1: reverse-order cap at {t} differs")
        else:
            counts["order"] += 1
    # views of replicate 1's live cuts
    hvis = json.load(open(os.path.join(famdir, "views-live-rep1.json")))
    cviews = []
    for idx, t in enumerate(CHECKPOINTS):
        prefix = [r for r in recs if r["tick"] < t]
        v = view(prefix, family, truth, t)
        hv = hvis[idx]
        if v["mu"] != hv["mu"] or v["live"] != hv["live"] \
                or v["lambda"] != hv["lambda"] \
                or v["edges"] != hv["edges"] \
                or v["components"] != hv["components"] \
                or v["dead"] != hv["dead"]:
            bad(f"{family}5 view t={t}: checker view != harness view")
        else:
            counts["views"] += 1
        cviews.append(v)
        print(f"checked {family}5 view t={t}", flush=True)
    # the decision, recomputed (scope from the checker's own views)
    dec = json.load(open(os.path.join(famdir, "decision.json")))
    eps = EPS[family]
    arms = ["live", "isolated", "frozen", "shuffled"]
    curve = {arm: [[summaries[f"{arm}-rep{r}"]["cuts"][str(t)]["cap"]
                    for t in CHECKPOINTS] for r in range(1, 9)]
             for arm in arms}

    def mean(vals):
        return sum(vals) / len(vals)

    def spread(vals):
        return max(vals) - min(vals)

    means = {arm: [mean([curve[arm][r][i] for r in range(8)])
                   for i in range(len(CHECKPOINTS))] for arm in arms}
    gains = {arm: [curve[arm][r][-1] - curve[arm][r][0] for r in range(8)]
             for arm in arms}
    ctrls = ["isolated", "frozen", "shuffled"]
    delta = max(spread(gains[c]) for c in ctrls)
    delta_g = max(spread([curve[c][r][-1] for r in range(8)])
                  for c in ctrls)

    def edgeset(v):
        return {(e["tick"], tuple(e["edge"])) for e in v["edges"]}

    pairs = []
    for i in range(len(CHECKPOINTS)):
        for j in range(i + 1, len(CHECKPOINTS)):
            ei, ej = edgeset(cviews[i]), edgeset(cviews[j])
            removed = len(ei - ej)
            incl = set(cviews[i]["live"]) <= set(cviews[j]["live"])
            pairs.append({"i": CHECKPOINTS[i], "j": CHECKPOINTS[j],
                          "removed": removed, "in_scope":
                          removed == 0 and incl})
    in_pairs = [p for p in pairs if p["in_scope"]]
    mono = all(means["live"][CHECKPOINTS.index(p["i"])]
               - means["live"][CHECKPOINTS.index(p["j"])] <= eps
               for p in in_pairs)
    gain = mean(gains["live"])
    ok = (abs(delta - dec["delta"]) < 1e-15
          and abs(delta_g - dec["delta_g"]) < 1e-15
          and abs(gain - dec["gain"]) < 1e-15
          and mono == dec["mono"]
          and (mono and gain > delta) == dec["win"]
          and (mono and gain > delta_g) == dec["win_global"]
          and len(in_pairs) == sum(1 for p in dec["pairs"]
                                   if p["in_scope"])
          and all(p["removed"] == d["removed"]
                  for p, d in zip(pairs, dec["pairs"])))
    if not ok:
        bad(f"{family}5: decision recomputation disagrees")
    else:
        counts["decision"] += 1
    return {"family": family, "counts": dict(counts)}


def main():
    out = {}
    for family in ("field", "region"):
        out[family] = check_family(family)
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "results")
    with open(os.path.join(root, "checks.json"), "w") as fh:
        json.dump({"counts": counts, "fails": fails}, fh, indent=1)
    print("COUNTS:", json.dumps(counts))
    print("FAILS:", len(fails))
    if fails:
        sys.exit(1)
    print("CHECK5: ALL VERIFIED")


if __name__ == "__main__":
    main()
