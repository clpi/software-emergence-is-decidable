#!/usr/bin/env python3
"""Rung 3 independent checker.

Reads only the persisted artifacts of a battery (config.json, the
per-run summary JSONs, and the append-only JSONL logs) and
verifies, by its own code path (written from registration.md, not
imported from harness3.py):
  - replay exactness: folding each log from the seed-derived
    initial state reproduces the run's recorded final state hash;
  - restart exactness: folding each log prefix through a
    formation tick reproduces the online hash recorded at that
    cut (joint arm);
  - DET = TAL at every registered append cut, for the combined
    tally and for each level's tally separately, and the pair
    composition: combined tally = level-1 tally + level-2 tally
    componentwise at the final cut (T3.6's checkable content);
  - budget shape: steps, bits sent, and record count per the
    registration's formulas, identical for every arm;
  - formation agreement: partitions recomputed from each log's
    level-1 prefixes (registered rule G) equal the partitions
    recorded in the run's summary.
"""
import hashlib
import json
import math
import os
import random
import sys
import time

NULL = 10 ** 9
MSG_BITS = 336
L2_BITS = 352
FTICKS = (8, 16, 24)
KAPPA = 1  # registration amendment v2


def gen_field(seed, n):
    rng = random.Random(seed ^ 0xF1E1D)
    phases = [rng.uniform(0, 2 * math.pi) for _ in range(3)]
    amps = [60, 35, 20]
    return [int(round(sum(a * math.sin(2 * math.pi * (k + 1) * i / n + phases[k])
                           for k, a in enumerate(amps)))) for i in range(n)]


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


def median(vals):
    return sorted(vals)[len(vals) // 2]


def mode(vals):
    cnt = {}
    for v in vals:
        cnt[v] = cnt.get(v, 0) + 1
    return min(cnt, key=lambda v: (-cnt[v], v))


def state_hash(reports, family):
    est = median if family == "field" else mode
    canon = [sorted((site, est(v)) for site, v in table.items() if v)
             for table in reports]
    return hashlib.sha256(
        json.dumps(canon, separators=(",", ":")).encode()).hexdigest()


def initial_reports(seed, n, family):
    if family == "field":
        f = gen_field(seed, n)
        obs = gen_obs_a(seed, n, f)
    else:
        labels = gen_labels(seed, n)
        obs = gen_obs_b(seed, n, labels)
    return [{a: [obs[a]]} for a in range(n)]


def appended_sites(rec, n):
    """Sites a record appends reports about, by the v3 rule."""
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
                out.append(site)
    return out


def fold(records, seed, n, family, upto_tick=None):
    reports = initial_reports(seed, n, family)
    steps = 0
    for rec in records:
        if upto_tick is not None and rec["tick"] >= upto_tick:
            break
        steps += 1
        if rec["vals_recv"] is None:
            continue
        dst = rec["dst_actual"]
        c = rec["src_interp"]
        vals = rec["vals_recv"]
        for j in range(8):
            v = vals[2 * j + 1]
            if v != NULL:
                site = (c + vals[2 * j]) % n
                if site == dst:
                    continue
                reports[dst].setdefault(site, []).append(v)
                steps += 1
    return reports, steps


def empty_tally():
    return {"records": 0, "delivered_class": 0, "ann_delivered": 0,
            "dropped": 0, "corr": 0, "misdelivered": 0, "frozen": 0,
            "shuffled": 0, "filler": 0, "reports": 0, "sum_abs_recv": 0}


def tally_batch(records, n):
    """DET: the tally vector (combined + per level) over a prefix."""
    out = {"all": empty_tally(), "1": empty_tally(), "2": empty_tally()}
    for r in records:
        for key in ("all", str(r["lvl"])):
            t = out[key]
            t["records"] += 1
            if r["vals_recv"] is not None:
                t["delivered_class"] += 1
                t["sum_abs_recv"] += sum(
                    abs(r["vals_recv"][2 * j + 1]) for j in range(8)
                    if r["vals_recv"][2 * j + 1] != NULL)
                t["reports"] += len(appended_sites(r, n))
            ann = r["ann"]
            if ann == "delivered":
                t["ann_delivered"] += 1
            elif ann in ("dropped", "misdelivered", "frozen",
                         "shuffled", "filler"):
                t[ann] += 1
            if r["corr"]:
                t["corr"] += 1
    return out


def tally_step(state, rec, n):
    for key in ("all", str(rec["lvl"])):
        t = state[key]
        t["records"] += 1
        if rec["vals_recv"] is not None:
            t["delivered_class"] += 1
            t["sum_abs_recv"] += sum(
                abs(rec["vals_recv"][2 * j + 1]) for j in range(8)
                if rec["vals_recv"][2 * j + 1] != NULL)
            t["reports"] += len(appended_sites(rec, n))
        ann = rec["ann"]
        if ann == "delivered":
            t["ann_delivered"] += 1
        elif ann in ("dropped", "misdelivered", "frozen",
                     "shuffled", "filler"):
            t[ann] += 1
        if rec["corr"]:
            t["corr"] += 1


def partitions_from_log(records, n):
    """Registered rule G, recomputed from level-1 records alone."""
    d = [[None] * n for _ in range(n)]
    held = [set([a]) for a in range(n)]
    by_tick = {}
    for r in records:
        if r["lvl"] == 1:
            by_tick.setdefault(r["tick"], []).append(r)
    parts = {}
    ticks_sorted = sorted(by_tick)
    ti = 0
    for ft in FTICKS:
        while ti < len(ticks_sorted) and ticks_sorted[ti] < ft:
            t = ticks_sorted[ti]
            for rec in by_tick[t]:
                if rec["vals_recv"] is None:
                    continue
                dst = rec["dst_actual"]
                for site in appended_sites(rec, n):
                    if site not in held[dst]:
                        held[dst].add(site)
                        if d[site][dst] is None:
                            d[site][dst] = t
            ti += 1
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for a in range(n):
            b = (a + 1) % n
            if (d[a][b] is not None and d[a][b] <= KAPPA
                    and d[b][a] is not None and d[b][a] <= KAPPA):
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[ra] = rb
        blocks = {}
        for a in range(n):
            blocks.setdefault(find(a), []).append(a)
        parts[str(ft)] = sorted((sorted(m) for m in blocks.values()),
                                key=lambda m: m[0])
    return parts


def check_battery(bdir):
    cfg = json.load(open(os.path.join(bdir, "config.json")))
    n, t_ticks = cfg["n"], cfg["ticks"]
    family = cfg["family"]
    exp_steps = n * t_ticks + n * (t_ticks - FTICKS[0])
    exp_bits = 2 * n * t_ticks * MSG_BITS + 2 * n * (t_ticks - FTICKS[0]) * L2_BITS
    exp_records = 2 * n * t_ticks + 2 * n * (t_ticks - FTICKS[0])
    out = {"battery": cfg["battery"], "runs": {}, "failures": [],
           "append_cut_checks": 0, "append_cut_agree": 0,
           "restart_checks": 0, "restart_agree": 0,
           "pair_composition_checks": 0, "pair_composition_agree": 0}
    tags = sorted(fn[:-5] for fn in os.listdir(bdir)
                  if fn.endswith(".json") and fn not in
                  ("config.json", "summaries.json", "checks.json"))
    for tag in tags:
        summ = json.load(open(os.path.join(bdir, tag + ".json")))
        raw = open(os.path.join(bdir, summ["log_file"]), "rb").readlines()
        records = [json.loads(line) for line in raw]
        line_bytes = [len(line) for line in raw]
        run = {"steps_ok": summ["steps"] == exp_steps,
               "bits_ok": summ["bits_sent"] == exp_bits,
               "records_ok": len(records) == exp_records}
        if not (run["steps_ok"] and run["bits_ok"] and run["records_ok"]):
            out["failures"].append(f"{tag}: budget shape "
                                   f"steps={summ['steps']} bits={summ['bits_sent']} "
                                   f"records={len(records)}")
        t0 = time.time()
        reports, fsteps = fold(records, summ["seed"], n, family)
        run["replay_wall_s"] = round(time.time() - t0, 3)
        run["replay_steps"] = fsteps
        run["replay_ok"] = state_hash(reports, family) == summ["final_hash"]
        if not run["replay_ok"]:
            out["failures"].append(f"{tag}: replay hash mismatch")
        # DET vs TAL at registered cuts
        cuts = {len(records)}
        k = 4096
        while k < len(records):
            cuts.add(k)
            k += 4096
        seen = set()
        for idx, r in enumerate(records):
            if r["tick"] in FTICKS and r["tick"] not in seen:
                seen.add(r["tick"])
                cuts.add(idx)
        state = {"all": empty_tally(), "1": empty_tally(),
                 "2": empty_tally()}
        agree = 0
        for idx, r in enumerate(records, start=1):
            tally_step(state, r, n)
            if idx in cuts:
                out["append_cut_checks"] += 1
                det = tally_batch(records[:idx], n)
                if det == state:
                    agree += 1
                    out["append_cut_agree"] += 1
                else:
                    out["failures"].append(f"{tag}: DET!=TAL at cut {idx}")
        run["cut_agree"] = agree
        online = {"all": summ["tally"], "1": summ["tally1"],
                  "2": summ["tally2"]}
        run["tally_final_ok"] = state == online
        if not run["tally_final_ok"]:
            out["failures"].append(f"{tag}: final TAL != online tally")
        # pair composition (T3.6): combined = level1 + level2
        out["pair_composition_checks"] += 1
        composed = {f: state["1"][f] + state["2"][f] for f in state["all"]}
        if composed == state["all"]:
            out["pair_composition_agree"] += 1
        else:
            out["failures"].append(f"{tag}: tally pair composition")
        # restart exactness at formation cuts (joint arm + ablations)
        if summ["arm"] in ("joint", "joint-abl"):
            run["restarts"] = {}
            for cut in FTICKS:
                reps_c, steps_c = fold(records, summ["seed"], n, family,
                                       upto_tick=cut)
                ok = state_hash(reps_c, family) == summ["hashes"][str(cut)]
                nbytes = sum(b for line, b in zip(records, line_bytes)
                             if line["tick"] < cut)
                run["restarts"][str(cut)] = {"ok": ok,
                                             "prefix_bytes": nbytes,
                                             "fold_steps": steps_c}
                out["restart_checks"] += 1
                if ok:
                    out["restart_agree"] += 1
                else:
                    out["failures"].append(f"{tag}: restart mismatch cut {cut}")
        # formation agreement
        parts = partitions_from_log(records, n)
        want = summ["partitions"]
        run["formation_ok"] = all(parts[ft] == want[ft] for ft in want)
        if not run["formation_ok"]:
            out["failures"].append(f"{tag}: formation mismatch")
        out["runs"][tag] = run
        print(f"checked {tag}: replay_ok={run['replay_ok']} "
              f"cuts={agree} tally_ok={run['tally_final_ok']} "
              f"formation_ok={run['formation_ok']}", flush=True)
    with open(os.path.join(bdir, "checks.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"{cfg['battery']}: cuts {out['append_cut_agree']}/"
          f"{out['append_cut_checks']}, restarts {out['restart_agree']}/"
          f"{out['restart_checks']}, pair {out['pair_composition_agree']}/"
          f"{out['pair_composition_checks']}, failures={out['failures']}")
    return out


if __name__ == "__main__":
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    check_battery(os.path.join(base, sys.argv[1]))
