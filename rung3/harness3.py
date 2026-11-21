#!/usr/bin/env python3
"""Rung 3 harness: composition — emergent groups as actors.

Implements the battery registered in registration.md (read it
first). Level-1 is rung 2's protocol v3 system; level-2 runs the
same protocol between group actors formed by the registered rule
G over the level-1 log. Both levels write to one append-only log,
records distinguished by a level field. Verification lives in
check3.py, an independent code path; views in view3.py.
"""
import hashlib
import json
import math
import os
import random
import sys
import time

NULL = 10 ** 9
SPLIT_A = 2026112199
SPLIT_B = 2026112299
MSG_BITS = 336   # 8 components x (8-bit offset + 32-bit value) + 16-bit header
TAG_BITS = 16    # level-2 tag: block id + member rank
L2_BITS = MSG_BITS + TAG_BITS
FTICKS = (8, 16, 24)
KAPPA = 1  # registration amendment v2 (was 2; see registration.md)
NOISE = (0.15, 0.15, 0.10)  # drop, corrupt, misdeliver (both levels)
ARMS = ["joint", "flat", "frozen-partition", "isolated", "frozen",
        "shuffled", "freeze-1", "freeze-2"]
SEEDS = [2026112100 + r for r in range(1, 9)]


def relay_offsets(tick):
    return [-(2 + tick % 8), -(2 + (tick + 3) % 8), 2 + tick % 8,
            2 + (tick + 3) % 8, (1 if tick % 2 == 0 else -1) * (2 + (tick + 5) % 8)]


def offsets(tick):
    return [-1, 0, 1] + relay_offsets(tick)


# ---------------- family A: field reconstruction (rung 2, unchanged) ----

def gen_field(seed, n):
    rng = random.Random(seed ^ 0xF1E1D)
    phases = [rng.uniform(0, 2 * math.pi) for _ in range(3)]
    amps = [60, 35, 20]
    return [int(round(sum(a * math.sin(2 * math.pi * (k + 1) * i / n + phases[k])
                           for k, a in enumerate(amps)))) for i in range(n)]


def gen_obs_a(seed, n, f):
    rng = random.Random(seed ^ 0x0B5EED)
    return [f[i] + rng.randint(-25, 25) for i in range(n)]


def held_out(split, i, d, direction):
    h = hashlib.sha256(f"{split}:{i}:{d}:{direction}".encode()).digest()
    return h[0] % 2 == 0


def median(vals):
    s = sorted(vals)
    return s[len(s) // 2]


def score_a(reports, f, n):
    ho_sum = ho_cnt = wk_sum = wk_cnt = 0.0
    ho_cov = 0
    for i in range(n):
        table = reports[i]
        for d in range(1, 7):
            for direction in (-1, 1):
                site = (i + direction * d) % n
                vals = table.get(site)
                pred = median(vals) if vals else 0
                s = max(0.0, 1.0 - abs(pred - f[site]) / 120.0)
                if held_out(SPLIT_A, i, d, direction):
                    ho_sum += s
                    ho_cnt += 1
                    if vals:
                        ho_cov += 1
                else:
                    wk_sum += s
                    wk_cnt += 1
    return ho_sum / ho_cnt, wk_sum / wk_cnt, ho_cov / ho_cnt


# ---------------- family B: region classification ----------------

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


def mode(vals):
    cnt = {}
    for v in vals:
        cnt[v] = cnt.get(v, 0) + 1
    return min(cnt, key=lambda v: (-cnt[v], v))


def score_b(reports, labels, n):
    ho_sum = ho_cnt = wk_sum = wk_cnt = 0.0
    ho_cov = 0
    for i in range(n):
        table = reports[i]
        for d in range(1, 7):
            for direction in (-1, 1):
                site = (i + direction * d) % n
                vals = table.get(site)
                pred = mode(vals) if vals else 0
                s = 1.0 if pred == labels[site] else 0.0
                if held_out(SPLIT_B, i, d, direction):
                    ho_sum += s
                    ho_cnt += 1
                    if vals:
                        ho_cov += 1
                else:
                    wk_sum += s
                    wk_cnt += 1
    return ho_sum / ho_cnt, wk_sum / wk_cnt, ho_cov / ho_cnt


# ---------------- shared protocol machinery (v3) ----------------

def make_point_est(family, reports, obs):
    if family == "field":
        def pe(a, site):
            if site == a:
                return obs[a]
            vals = reports[a].get(site)
            if not vals or len(vals) < 3:
                return NULL
            return median(vals)
    else:
        def pe(a, site):
            if site == a:
                return obs[a]
            vals = reports[a].get(site)
            if not vals or len(vals) < 3:
                return NULL
            return mode(vals)
    return pe


def make_bundle(pe, a, tick, n):
    flat = []
    for off in offsets(tick):
        flat.append(off)
        flat.append(pe(a, (a + off) % n))
    return flat


def apply_delivery(reports, rec, n):
    """Protocol v3 append rule; returns reports appended."""
    dst = rec["dst_actual"]
    c = rec["src_interp"]
    vals = rec["vals_recv"]
    appended = 0
    for j in range(8):
        v = vals[2 * j + 1]
        if v != NULL:
            site = (c + vals[2 * j]) % n
            if site == dst:
                continue
            reports[dst].setdefault(site, []).append(v)
            appended += 1
    return appended


def state_hash(reports):
    canon = []
    for a, table in enumerate(reports):
        row = sorted((site, median(vals)) for site, vals in table.items() if vals)
        canon.append(row)
    blob = json.dumps(canon, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def state_hash_b(reports):
    canon = []
    for a, table in enumerate(reports):
        row = sorted((site, mode(vals)) for site, vals in table.items() if vals)
        canon.append(row)
    blob = json.dumps(canon, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def new_tally():
    return {"records": 0, "delivered_class": 0, "ann_delivered": 0,
            "dropped": 0, "corr": 0, "misdelivered": 0, "frozen": 0,
            "shuffled": 0, "filler": 0, "reports": 0, "sum_abs_recv": 0}


def tally_record(tal, rec, appended):
    tal["records"] += 1
    if rec["vals_recv"] is not None:
        tal["delivered_class"] += 1
        tal["sum_abs_recv"] += sum(abs(rec["vals_recv"][2 * j + 1])
                                   for j in range(8)
                                   if rec["vals_recv"][2 * j + 1] != NULL)
    ann = rec["ann"]
    if ann == "delivered":
        tal["ann_delivered"] += 1
    elif ann in ("dropped", "misdelivered", "frozen", "shuffled", "filler"):
        tal[ann] += 1
    if rec["corr"]:
        tal["corr"] += 1
    tal["reports"] += appended


# ---------------- formation (registered rule G) ----------------

def partition_from_reach(d, n, kappa=KAPPA):
    """Blocks = connected components of the ring adjacency graph
    where neighbours are linked iff mutual first-reach <= kappa.
    d[site][holder] = first tick holder held a report about site."""
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a in range(n):
        b = (a + 1) % n
        if (d[a][b] is not None and d[a][b] <= kappa
                and d[b][a] is not None and d[b][a] <= kappa):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb
    blocks = {}
    for a in range(n):
        blocks.setdefault(find(a), []).append(a)
    return sorted((sorted(m) for m in blocks.values()), key=lambda m: m[0])


# ---------------- the run ----------------

def corrupt_vals(vals, src, family, truth, n, rng):
    out = list(vals)
    for j in range(8):
        v = out[2 * j + 1]
        if v != NULL:
            site = (src + out[2 * j]) % n
            if family == "field":
                out[2 * j + 1] = v + 300 if v >= truth[site] else v - 300
            else:
                out[2 * j + 1] = (truth[site] + 1
                                  + (0 if rng.random() < 0.5 else 1)) % 3
    return out


def run_arm3(arm, seed, n, t_ticks, family, gen_by_tick=None,
             isolate=None, rng_arm=None):
    """Run one arm. gen_by_tick: {(tick, lvl): [records]} generator
    stream for frozen / freeze-1. isolate: (member set, from_tick)
    — joint mechanics with those members isolated from from_tick.
    rng_arm: arm name used for the noise stream (ablations use
    'joint' so their stream matches the joint run's exactly)."""
    if family == "field":
        truth = gen_field(seed, n)
        obs = gen_obs_a(seed, n, truth)
    else:
        truth = gen_labels(seed, n)
        obs = gen_obs_b(seed, n, truth)
    reports = [{a: [obs[a]]} for a in range(n)]
    pe = make_point_est(family, reports, obs)
    hash_fn = state_hash if family == "field" else state_hash_b
    tal, tal1, tal2 = new_tally(), new_tally(), new_tally()
    matrix1, matrix2 = {}, {}
    records = []
    steps = 0
    bits_sent = 0
    bits_delivered = 0
    cut_ticks = {FTICKS[0], FTICKS[1], FTICKS[2], t_ticks}
    hashes = {}
    rng = random.Random(repr((seed, rng_arm or arm)))
    # provenance reach over level-1 deliveries: d[site][holder]
    d = [[None] * n for _ in range(n)]
    sites_held = [set([a]) for a in range(n)]
    partitions = {}
    partition = None
    block_index = {}
    rank_of = {}

    def set_partition(p):
        nonlocal partition, block_index, rank_of
        partition = p
        block_index = {m: bi for bi, blk in enumerate(p) for m in blk}
        rank_of = {m: r for blk in p for r, m in enumerate(blk)}

    def interp_for(actual, lvl):
        if lvl == 1:
            return (actual + rng.choice((-1, 1))) % n
        nb = len(partition)
        bi = block_index[actual]
        adj = partition[(bi + rng.choice((-1, 1))) % nb]
        return adj[min(rank_of[actual], len(adj) - 1)]

    def filler_records(sends):
        return [{**s, "dst_actual": None, "src_interp": None,
                 "vals_recv": None, "ann": "filler", "corr": False}
                for s in sends]

    def noise_records(sends, lvl):
        p_drop, p_corr, p_mis = NOISE
        out = []
        for s in sends:
            if s["dst_intended"] is None:
                out.append({**s, "dst_actual": None, "src_interp": None,
                            "vals_recv": None, "ann": "filler",
                            "corr": False})
                continue
            r1 = rng.random()
            if r1 < p_drop:
                out.append({**s, "dst_actual": None, "src_interp": None,
                            "vals_recv": None, "ann": "dropped",
                            "corr": False})
                continue
            corr = False
            vals_recv = list(s["vals_sent"])
            if rng.random() < p_corr:
                corr = True
                vals_recv = corrupt_vals(vals_recv, s["src"], family,
                                         truth, n, rng)
            if r1 < p_drop + p_mis:
                actual = rng.randrange(n)
                while actual == s["dst_intended"]:
                    actual = rng.randrange(n)
                out.append({**s, "dst_actual": actual,
                            "src_interp": interp_for(actual, lvl),
                            "vals_recv": vals_recv,
                            "ann": "misdelivered", "corr": corr})
            else:
                out.append({**s, "dst_actual": s["dst_intended"],
                            "src_interp": s["src"],
                            "vals_recv": vals_recv,
                            "ann": "delivered", "corr": corr})
        return out

    def shuffled_records(sends, lvl):
        real = [s for s in sends if s["dst_intended"] is not None]
        dsts = [s["dst_intended"] for s in real]
        perm = list(range(len(real)))
        rng.shuffle(perm)
        out = filler_records([s for s in sends
                              if s["dst_intended"] is None])
        for idx, s in enumerate(real):
            actual = dsts[perm[idx]]
            out.append({**s, "dst_actual": actual,
                        "src_interp": interp_for(actual, lvl),
                        "vals_recv": list(s["vals_sent"]),
                        "ann": "shuffled", "corr": False})
        return out

    def replay_records(tick, lvl):
        return [dict(r) for r in gen_by_tick[(tick, lvl)]]

    for tick in range(t_ticks):
        # formation at the start of a formation tick, from the
        # level-1 reach accumulated so far (own log only)
        if tick in FTICKS:
            if arm == "frozen-partition":
                if tick == FTICKS[0]:
                    set_partition(partition_from_reach(d, n))
                    partitions[str(tick)] = partition
            else:
                set_partition(partition_from_reach(d, n))
                partitions[str(tick)] = partition

        # 1. generate level-1 sends (every arm, every tick)
        sends1 = []
        for a in range(n):
            steps += 1
            bundle = make_bundle(pe, a, tick, n)
            for dirc in (-1, 1):
                sends1.append({"tick": tick, "lvl": 1, "src": a,
                               "dst_intended": (a + dirc) % n,
                               "vals_sent": list(bundle)})
            bits_sent += 2 * MSG_BITS
        # 2. generate level-2 sends (every arm, ticks >= t1)
        sends2 = []
        if tick >= FTICKS[0]:
            nb = len(partition) if partition else 0
            for a in range(n):
                steps += 1
                bundle = make_bundle(pe, a, tick, n)
                if arm == "flat" or partition is None:
                    dsts = [(a - 1) % n, (a + 1) % n]
                elif nb == 1:
                    dsts = [None, None]
                else:
                    bi = block_index[a]
                    dsts = []
                    for nbi in ((bi - 1) % nb, (bi + 1) % nb):
                        blk = partition[nbi]
                        dsts.append(blk[min(rank_of[a], len(blk) - 1)])
                for dst in dsts:
                    sends2.append({"tick": tick, "lvl": 2, "src": a,
                                   "dst_intended": dst,
                                   "vals_sent": list(bundle)})
                bits_sent += 2 * L2_BITS

        # 3. transform sends into records, per arm
        if arm in ("joint", "freeze-2") or isolate is not None:
            recs1 = noise_records(sends1, 1)
        elif arm == "flat":
            recs1 = noise_records(sends1, 1)
        elif arm == "frozen-partition":
            recs1 = (noise_records(sends1, 1) if tick < FTICKS[0]
                     else filler_records(sends1))
        elif arm == "isolated":
            recs1 = filler_records(sends1)
        elif arm == "frozen":
            recs1 = replay_records(tick, 1)
        elif arm == "shuffled":
            recs1 = shuffled_records(sends1, 1)
        elif arm == "freeze-1":
            recs1 = (noise_records(sends1, 1) if tick < FTICKS[0]
                     else replay_records(tick, 1))
        else:
            raise ValueError(arm)

        if tick >= FTICKS[0]:
            if arm in ("joint", "frozen-partition", "freeze-1") \
                    or isolate is not None:
                recs2 = noise_records(sends2, 2)
            elif arm == "flat":
                recs2 = filler_records(sends2)
            elif arm == "isolated":
                recs2 = filler_records(sends2)
            elif arm == "frozen":
                recs2 = replay_records(tick, 2)
            elif arm in ("shuffled", "freeze-2"):
                recs2 = shuffled_records(sends2, 2)
            else:
                raise ValueError(arm)
        else:
            recs2 = []

        tick_records = recs1 + recs2

        # 4. ablation isolation (post-processing, consumes no draws)
        if isolate is not None and tick >= isolate[1]:
            members = isolate[0]
            fixed = []
            for rec in tick_records:
                if (rec["src"] in members
                        or rec["dst_intended"] in members
                        or rec["dst_actual"] in members):
                    fixed.append({**rec, "dst_actual": None,
                                  "src_interp": None, "vals_recv": None,
                                  "ann": "filler", "corr": False})
                else:
                    fixed.append(rec)
            tick_records = fixed

        # 5. deliveries, in (level, source, destination) order
        tick_records.sort(key=lambda r: (r["lvl"], r["src"],
                                         -1 if r["dst_actual"] is None
                                         else r["dst_actual"]))
        for rec in tick_records:
            appended = 0
            if rec["vals_recv"] is not None:
                appended = apply_delivery(reports, rec, n)
                bits_delivered += MSG_BITS if rec["lvl"] == 1 else L2_BITS
                key = (rec["src"], rec["dst_actual"])
                mtx = matrix1 if rec["lvl"] == 1 else matrix2
                mtx[key] = mtx.get(key, 0) + 1
                if rec["lvl"] == 1:
                    dst = rec["dst_actual"]
                    c = rec["src_interp"]
                    vals = rec["vals_recv"]
                    for j in range(8):
                        v = vals[2 * j + 1]
                        if v != NULL:
                            site = (c + vals[2 * j]) % n
                            if site != dst and site not in sites_held[dst]:
                                sites_held[dst].add(site)
                                if d[site][dst] is None:
                                    d[site][dst] = tick
            tally_record(tal, rec, appended)
            tally_record(tal1 if rec["lvl"] == 1 else tal2, rec, appended)
            records.append(rec)
        if tick + 1 in cut_ticks:
            hashes[str(tick + 1)] = hash_fn(reports)

    if family == "field":
        cap, work, cov = score_a(reports, truth, n)
    else:
        cap, work, cov = score_b(reports, truth, n)
    summary = {
        "arm": arm if isolate is None else "joint-abl",
        "seed": seed, "n": n, "ticks": t_ticks, "family": family,
        "cap": cap, "work_mean": work, "coverage": cov,
        "steps": steps, "bits_sent": bits_sent,
        "bits_delivered": bits_delivered,
        "tally": tal, "tally1": tal1, "tally2": tal2,
        "hashes": hashes, "final_hash": hashes[str(t_ticks)],
        "partitions": partitions,
        "matrix1_pairs": sorted([a, b, c] for (a, b), c in matrix1.items()),
        "matrix2_pairs": sorted([a, b, c] for (a, b), c in matrix2.items()),
    }
    if isolate is not None:
        summary["isolated_members"] = sorted(isolate[0])
        summary["isolate_from"] = isolate[1]
    return summary, records


def group_gen(records):
    by = {}
    for r in records:
        by.setdefault((r["tick"], r["lvl"]), []).append(r)
    return by


BATTERIES = {
    "field3": {"family": "field", "n": 256, "ticks": 32},
    "region3": {"family": "region", "n": 256, "ticks": 32},
}


def write_run(outdir, tag, summary, records):
    logpath = os.path.join(outdir, tag + ".jsonl")
    with open(logpath, "w") as fh:
        for rec in records:
            fh.write(json.dumps(rec, separators=(",", ":")) + "\n")
    summary["log_bytes"] = os.path.getsize(logpath)
    summary["log_file"] = tag + ".jsonl"
    with open(os.path.join(outdir, tag + ".json"), "w") as fh:
        json.dump(summary, fh, indent=1)


def run_battery(name, outdir):
    cfg = BATTERIES[name]
    n, t_ticks, family = cfg["n"], cfg["ticks"], cfg["family"]
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "config.json"), "w") as fh:
        json.dump({"battery": name, "family": family, "n": n,
                   "ticks": t_ticks, "seeds": SEEDS,
                   "split_seed": SPLIT_A if family == "field" else SPLIT_B,
                   "arms": ARMS, "fticks": list(FTICKS), "kappa": KAPPA},
                  fh, indent=1)
    summaries = []
    for seed in SEEDS:
        rep = seed - 2026112100
        t0 = time.time()
        gsum, grecords = run_arm3("joint", seed + 777000, n, t_ticks, family)
        gen_by_tick = group_gen(grecords)
        write_run(outdir, f"generator-rep{rep}", gsum, grecords)
        print(f"{name} generator-rep{rep}: blocks="
              f"{[len(p) for p in gsum['partitions'].values()]} "
              f"wall={time.time() - t0:.1f}s", flush=True)
        for arm in ARMS:
            t0 = time.time()
            summary, records = run_arm3(
                arm, seed, n, t_ticks, family,
                gen_by_tick=gen_by_tick if arm in ("frozen", "freeze-1")
                else None)
            summary["wall_s"] = round(time.time() - t0, 3)
            tag = f"{arm}-rep{rep}"
            write_run(outdir, tag, summary, records)
            summaries.append(summary)
            print(f"{name} {tag}: cap={summary['cap']:.4f} "
                  f"blocks={[len(p) for _, p in sorted(summary['partitions'].items())]} "
                  f"wall={summary['wall_s']}s", flush=True)
    with open(os.path.join(outdir, "summaries.json"), "w") as fh:
        json.dump(summaries, fh, indent=1)
    return summaries


def run_ablations(battery, outdir):
    cfg = BATTERIES[battery]
    n, t_ticks, family = cfg["n"], cfg["ticks"], cfg["family"]
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "results", battery)
    ref = json.load(open(os.path.join(base, "joint-rep1.json")))
    p3 = ref["partitions"][str(FTICKS[2])]
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "config.json"), "w") as fh:
        json.dump({"battery": battery + "-abl", "family": family,
                   "n": n, "ticks": t_ticks,
                   "seeds": SEEDS[:4], "blocks": p3,
                   "isolate_from": FTICKS[2]}, fh, indent=1)
    summaries = []
    for gi, block in enumerate(p3):
        for seed in SEEDS[:4]:
            rep = seed - 2026112100
            t0 = time.time()
            summary, records = run_arm3(
                "joint", seed, n, t_ticks, family,
                isolate=(set(block), FTICKS[2]), rng_arm="joint")
            summary["wall_s"] = round(time.time() - t0, 3)
            summary["abl_block"] = gi
            tag = f"abl{gi}-rep{rep}"
            write_run(outdir, tag, summary, records)
            summaries.append(summary)
            print(f"{battery}-abl {tag}: cap={summary['cap']:.4f} "
                  f"wall={summary['wall_s']}s", flush=True)
    with open(os.path.join(outdir, "summaries.json"), "w") as fh:
        json.dump(summaries, fh, indent=1)
    return summaries


if __name__ == "__main__":
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    which = sys.argv[1]
    if which.endswith("-abl"):
        run_ablations(which[:-4], os.path.join(base, which))
    else:
        run_battery(which, os.path.join(base, which))
