#!/usr/bin/env python3
"""Rung 5 harness: compounding over time on one append-only log.

Implements the battery registered in registration.md (read it
first). The gossip system is rungs 2-4's single-level protocol v3
system, imported from harness3.py (its names are its own); the
group view machinery is harness4.py's, re-entered here with the
cut length as a parameter. One run is one append-only log of 128
ticks; checkpoints are cuts of that log, scored in place as the
run passes them. Verification lives in check5.py, an independent
code path that imports nothing here.
"""
import json
import os
import random
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "emergence-rung3-scratch"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "emergence-rung4-scratch"))
import harness3 as base
import harness4 as h4

NULL = 10 ** 9
G = 8
N = 256
TICKS = 128
CHECKPOINTS = (1, 2, 4, 8, 16, 32, 64, 128)
SEEDS = [2026112100 + r for r in range(1, 9)]
ARMS = ("live", "isolated", "frozen", "shuffled")
SPLIT = {"field": base.SPLIT_A, "region": base.SPLIT_B}
EPS = {"field": 1.0 / 1488960, "region": 1.0 / 12352}
GENOFF = 777000


# ---------------- arm transforms (level 1, rung-2 form) ----------------

def noise(sends, family, truth, n, rng):
    """The live channel: rungs 3-4's level-1 noise, record for
    record in form (drop, corrupt, misdeliver at the registered
    rates)."""
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


def filler(sends):
    return [{**s, "dst_actual": None, "src_interp": None,
             "vals_recv": None, "ann": "filler", "corr": False}
            for s in sends]


def clean(sends):
    return [{**s, "dst_actual": s["dst_intended"],
             "src_interp": s["src"], "vals_recv": list(s["vals_sent"]),
             "ann": "delivered", "corr": False} for s in sends]


def shuffled(sends, n, rng):
    """The run's own sends, clean, destinations permuted within
    the tick (per-destination counts preserved), each delivered
    value attributed to a neighbouring site."""
    dsts = [s["dst_intended"] for s in sends]
    perm = list(range(len(sends)))
    rng.shuffle(perm)
    out = []
    for idx, s in enumerate(sends):
        actual = dsts[perm[idx]]
        interp = (actual + rng.choice((-1, 1))) % n
        out.append({**s, "dst_actual": actual, "src_interp": interp,
                    "vals_recv": list(s["vals_sent"]),
                    "ann": "shuffled", "corr": False})
    return out


# ---------------- the run ----------------

def run5(arm, seed, family, gen=None, n=N, ticks=TICKS,
         checkpoints=CHECKPOINTS):
    """One run of one arm over the registered horizon. gen: for
    the frozen arm, the generator run's records grouped by tick.
    Returns (summary, records). Checkpoints are cuts of this one
    log, snapshotted as the run passes them."""
    if family == "field":
        truth = base.gen_field(seed, n)
        obs = base.gen_obs_a(seed, n, truth)
    else:
        truth = base.gen_labels(seed, n)
        obs = base.gen_obs_b(seed, n, truth)
    reports = [{a: [obs[a]]} for a in range(n)]
    pe = base.make_point_est(family, reports, obs)
    pick = base.state_hash if family == "field" else base.state_hash_b
    score = base.score_a if family == "field" else base.score_b
    tal = base.new_tally()
    records = []
    steps = 0
    sent = 0
    delivered = 0
    cuts = {}
    rng = random.Random(repr((seed, arm)))
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
        if arm == "live":
            recs = noise(sends, family, truth, n, rng)
        elif arm == "isolated":
            recs = filler(sends)
        elif arm == "frozen":
            recs = [dict(r) for r in gen[tick]]
        elif arm == "shuffled":
            recs = shuffled(sends, n, rng)
        elif arm == "clean":
            recs = clean(sends)
        else:
            raise ValueError(arm)
        recs.sort(key=lambda r: (r["src"],
                                 -1 if r["dst_actual"] is None
                                 else r["dst_actual"]))
        for rec in recs:
            done = 0
            if rec["vals_recv"] is not None:
                done = base.apply_delivery(reports, rec, n)
                delivered += base.MSG_BITS
            base.tally_record(tal, rec, done)
            records.append(rec)
        if tick + 1 in checkpoints:
            cap, work, cov = score(reports, truth, n)
            cuts[str(tick + 1)] = {"cap": cap, "work": work,
                                   "coverage": cov,
                                   "hash": pick(reports),
                                   "tally": dict(tal)}
    cap, work, cov = score(reports, truth, n)
    summary = {
        "arm": arm, "seed": seed, "n": n, "ticks": ticks,
        "family": family, "cap": cap, "work": work, "coverage": cov,
        "steps": steps, "sent": sent, "delivered": delivered,
        "tally": tal, "cuts": cuts, "final": cuts[str(ticks)]["hash"],
    }
    return summary, records


# ---------------- the view of a cut (grain 8, scan unit tick) ----

def view5(records, family, truth, ticks, n=N):
    """harness4's view with the cut length as a parameter: axes =
    8 ring arcs, components = per-group held-out means of the
    fold of the given prefix, hyperedges = per-tick
    counterfactuals, exact sensitivity over all 256
    configurations."""
    rows = h4.table(records, family, truth, n)
    full = [h4.score(rows, family, truth, 255, True, only=b)
            for b in range(G)]
    delivered = {}
    for rec in records:
        if rec["vals_recv"] is not None:
            delivered[rec["tick"]] = delivered.get(rec["tick"], 0) + 1
    edges = []
    for t in range(ticks):
        comp = [h4.score(rows, family, truth, 255, True, only=b, drop=t)
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
        comps[mask] = [h4.score(rows, family, truth, mask, True, only=b)
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


# ---------------- decisions ----------------

def mean(vals):
    return sum(vals) / len(vals)


def spread(vals):
    return max(vals) - min(vals)


def edgeset(view):
    return {(e["tick"], tuple(e["edge"])) for e in view["edges"]}


def decide(family, summaries, views):
    """The registered decision for one family, from the battery
    summaries and replicate 1's live cut views."""
    eps = EPS[family]
    by = {}
    for s in summaries:
        by.setdefault(s["arm"], {})[s["seed"]] = s
    arms = ["live", "isolated", "frozen", "shuffled"]
    curve = {arm: [[by[arm][seed]["cuts"][str(t)]["cap"]
                    for t in CHECKPOINTS] for seed in SEEDS]
             for arm in arms}
    means = {arm: [mean([curve[arm][r][i] for r in range(8)])
                   for i in range(len(CHECKPOINTS))] for arm in arms}
    spreads = {arm: [spread([curve[arm][r][i] for r in range(8)])
                     for i in range(len(CHECKPOINTS))] for arm in arms}
    gains = {arm: [curve[arm][r][-1] - curve[arm][r][0] for r in range(8)]
             for arm in arms}
    ctrls = ["isolated", "frozen", "shuffled"]
    delta = max(spread(gains[c]) for c in ctrls)
    delta_g = max(spreads[c][-1] for c in ctrls)
    # scope from replicate 1's live cut views (registration section 9)
    pairs = []
    for i in range(len(CHECKPOINTS)):
        for j in range(i + 1, len(CHECKPOINTS)):
            vi, vj = views[i], views[j]
            ei, ej = edgeset(vi), edgeset(vj)
            removed = len(ei - ej)
            added = len(ej - ei)
            incl = set(vi["live"]) <= set(vj["live"])
            inscope = removed == 0 and incl
            pairs.append({
                "i": CHECKPOINTS[i], "j": CHECKPOINTS[j],
                "removed": removed, "added": added,
                "live_incl": incl, "in_scope": inscope,
                "mu_i": vi["mu"], "mu_j": vj["mu"],
                "mu_ok": vj["mu"] >= vi["mu"],
                "drop": means["live"][i] - means["live"][j],
            })
    in_pairs = [p for p in pairs if p["in_scope"]]
    worst_in = max((p["drop"] for p in in_pairs), default=None)
    worst_all = max(p["drop"] for p in pairs)
    mono = all(p["drop"] <= eps for p in in_pairs)
    gain = mean(gains["live"])
    win = mono and gain > delta
    win_global = mono and gain > delta_g
    attrib = {}
    for c in ctrls:
        cmono = all(means[c][CHECKPOINTS.index(p["j"])]
                    - means[c][CHECKPOINTS.index(p["i"])] >= -eps
                    for p in in_pairs)
        attrib[c] = {"mono": cmono, "gain": mean(gains[c]),
                     "satisfies": cmono and mean(gains[c]) > delta}
    return {
        "family": family, "eps": eps,
        "checkpoints": list(CHECKPOINTS),
        "curve": curve, "means": means, "spreads": spreads,
        "gains": gains, "delta": delta, "delta_g": delta_g,
        "pairs": pairs, "worst_in_scope_drop": worst_in,
        "worst_drop": worst_all, "mono": mono, "gain": gain,
        "win": win, "win_global": win_global, "attrib": attrib,
        "mus": [v["mu"] for v in views],
        "lives": [v["live"] for v in views],
        "lambdas": [v["lambda"] for v in views],
    }


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
        json.dump({"battery": family + "5", "family": family, "n": N,
                   "ticks": TICKS, "checkpoints": list(CHECKPOINTS),
                   "seeds": SEEDS, "split": SPLIT[family], "groups": G,
                   "arms": list(ARMS), "eps": EPS[family]}, fh, indent=1)
    summaries = []
    gens = []
    for seed in SEEDS:
        rep = seed - 2026112100
        t0 = time.time()
        gsum, grecords = run5("clean", seed + GENOFF, family)
        gsum["wall"] = round(time.time() - t0, 3)
        write(outdir, f"generator-rep{rep}", gsum, grecords)
        gens.append(gsum)
        gen = {}
        for r in grecords:
            gen.setdefault(r["tick"], []).append(r)
        print(f"{family}5 generator-rep{rep}: cap={gsum['cap']:.4f} "
              f"wall={gsum['wall']}s", flush=True)
        for arm in ARMS:
            t0 = time.time()
            summary, records = run5(arm, seed, family,
                                    gen=gen if arm == "frozen" else None)
            summary["wall"] = round(time.time() - t0, 3)
            write(outdir, f"{arm}-rep{rep}", summary, records)
            summaries.append(summary)
            print(f"{family}5 {arm}-rep{rep}: "
                  f"cap1={summary['cuts']['1']['cap']:.4f} "
                  f"cap128={summary['cap']:.4f} "
                  f"wall={summary['wall']}s", flush=True)
    with open(os.path.join(outdir, "summaries.json"), "w") as fh:
        json.dump(summaries, fh, indent=1)
    with open(os.path.join(outdir, "generators.json"), "w") as fh:
        json.dump(gens, fh, indent=1)
    # replicate 1's live cut views, from the persisted log prefixes
    rep1 = [json.loads(l) for l in open(
        os.path.join(outdir, "live-rep1.jsonl"))]
    truth = (base.gen_field(SEEDS[0], N) if family == "field"
             else base.gen_labels(SEEDS[0], N))
    views = []
    for t in CHECKPOINTS:
        prefix = [r for r in rep1 if r["tick"] < t]
        t0 = time.time()
        v = view5(prefix, family, truth, t)
        v["tick"] = t
        v["wall"] = round(time.time() - t0, 3)
        views.append(v)
        print(f"{family}5 view t={t}: mu={v['mu']} "
              f"lambda={v['lambda']} live={v['live']} "
              f"wall={v['wall']}s", flush=True)
    with open(os.path.join(outdir, "views-live-rep1.json"), "w") as fh:
        json.dump(views, fh, indent=1)
    dec = decide(family, summaries, views)
    with open(os.path.join(outdir, "decision.json"), "w") as fh:
        json.dump(dec, fh, indent=1)
    print(f"{family}5: delta={dec['delta']:.6f} "
          f"delta_g={dec['delta_g']:.6f} gain={dec['gain']:.6f} "
          f"mono={dec['mono']} win={dec['win']} "
          f"win_global={dec['win_global']}", flush=True)
    return dec


def smoke():
    """Code validation at reduced scale; decides nothing."""
    for family in ("field", "region"):
        s, recs = run5("live", SEEDS[0], family, n=64)
        caps = [s["cuts"][str(t)]["cap"] for t in CHECKPOINTS]
        print(f"smoke {family}: records={len(recs)} "
              f"caps={[round(c, 4) for c in caps]}", flush=True)
        assert len(recs) == 64 * TICKS * 2
        assert s["final"] == s["cuts"][str(TICKS)]["hash"]


def main():
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "results")
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        smoke()
        return
    decs = {}
    for family in ("field", "region"):
        decs[family] = battery(family, os.path.join(root, family + "5"))
    both = all(d["win"] for d in decs.values())
    bothg = all(d["win_global"] for d in decs.values())
    print(f"RUNG5 CLAIM (registered rule): "
          f"{'COMPOUNDING ESTABLISHED' if both else 'NO COMPOUNDING (claim dead as registered)'}")
    print(f"RUNG5 CLAIM (global rule): "
          f"{'COMPOUNDING ESTABLISHED' if bothg else 'NO COMPOUNDING'}")
    with open(os.path.join(root, "decisions.json"), "w") as fh:
        json.dump(decs, fh, indent=1)


if __name__ == "__main__":
    main()
