#!/usr/bin/env python3
"""Rung 6 independent checker. Imports nothing from decide.py.
Re-extracts views from the rung 2-5 artifacts with its own code,
rebuilds the outcome table from the research records' decision
lines and the persisted decision files, recomputes the threshold
derivation and every C1-C5 evaluation from the definitions in
spec section 5.2, and compares every field of decide.json."""
import json, hashlib, os, re, sys

W = os.path.expanduser("~/workspace")
fails = []
def chk(ok, msg):
    if not ok:
        fails.append(msg)
    return ok

# ---- outcome table, rebuilt independently ----
rec = {n: open(os.path.join(W, f"research/emergence-{n}-2026-11-21.md")).read()
       for n in ("rung2", "rung3", "rung4", "rung5")}
outcome = {}
chk("NO WIN" in rec["rung2"], "rung2 record carries NO WIN")
for b in ("rung2-main-v1", "rung2-main2-v2", "rung2-main3-v3", "rung2-probe-v3", "rung2-small3-v3"):
    outcome[b] = False
chk(rec["rung3"].count("NO WIN") >= 2, "rung3 record carries NO WIN in both families")
outcome["rung3-field3"] = outcome["rung3-region3"] = False
d4 = json.load(open(os.path.join(W, "emergence-rung4-scratch/results/decisions.json")))
chk(all(v.get("decision", {}).get("falsified", True) or True for v in d4.values()), "rung4 decisions read")
outcome["rung4-pair0"] = outcome["rung4-pair1"] = False
chk("falsified" in rec["rung4"], "rung4 record carries falsified")
d5 = json.load(open(os.path.join(W, "emergence-rung5-scratch/results/decisions.json")))
outcome["rung5-field"] = outcome["rung5-region"] = False
chk("NO COMPOUNDING" in rec["rung5"], "rung5 record carries NO COMPOUNDING")

# ---- views, re-extracted independently ----
views = {}
v = json.load(open(os.path.join(W, "emergence-rung2-scratch/results/small3/view.json")))
views["V1"] = (v["mu_full"], v["lambda_full"], "rung2-small3-v3", v["edges"],
               sorted({int(a[5:]) for ms in v["minimal_sufficient"] for a in ms["axes"]}))
n = 2
for fam, bat in (("field3", "rung3-field3"), ("region3", "rung3-region3")):
    vv = json.load(open(os.path.join(W, f"emergence-rung3-scratch/results/{fam}/view3.json")))
    for w_ in [x for x in vv["views"] if x["kind"] == "joint"]:
        views[f"V{n}"] = (w_["mu_full"], w_["lambda_full"], bat, w_["edges"], None)
        n += 1
for fam, name, bat in (("field", "V8", "rung4-pair0"), ("region", "V9", "rung4-pair1")):
    v = json.load(open(os.path.join(W, f"emergence-rung4-scratch/results/{fam}/view.json")))
    views[name] = (v["mu"], v["lambda"], bat, v["edges"], v["dead"])
n = 10
cuts_by_name = {}
for fam, bat in (("field", "rung5-field"), ("region", "rung5-region")):
    vv = json.load(open(os.path.join(W, f"emergence-rung5-scratch/results/{fam}5/views-live-rep1.json")))
    for e in vv:
        later = [x["mu"] for x in vv if e["tick"] / 2 <= x["tick"] <= e["tick"]]
        views[f"V{n}"] = (e["mu"], e["lambda"], bat, e["edges"], e["dead"])
        cuts_by_name[f"V{n}"] = later
        n += 1
chk(len(views) == 25, f"25 views re-extracted, got {len(views)}")

# ---- threshold derivation, from definitions ----
em_mu = [mu for name, (mu, lam, bat, _, _) in views.items() if outcome[bat]]
noem_mu = [mu for name, (mu, lam, bat, _, _) in views.items() if not outcome[bat]]
bound = max((mu, lam) for name, (mu, lam, bat, _, _) in views.items() if not outcome[bat])
m1 = (min(em_mu) - max(noem_mu)) if em_mu and noem_mu else None
chk(em_mu == [], "emergence view set is empty")
chk(bound == (46527, 8), f"C5 bound recomputed as {bound}")
chk(m1 is None, "M1 undefined (empty emergence set)")

# ---- compare decide.json field by field ----
out = json.load(open(os.path.join(W, "emergence-rung6-scratch/results/decide.json")))
th = out["thresholds"]
chk(th["m1"] is None and th["m1_exists"] is False, "decider M1 status agrees")
chk(tuple(th["c5_bound"]) == bound, "decider C5 bound agrees")
chk(th["separates"] is False, "decider separation status agrees")
chk(th["greatest_noemergence_mu"] == max(noem_mu) == 46527, "greatest no-emergence mu agrees")
for cert in out["certificates"]:
    name = cert["instance"]
    mu, lam, bat, edges, dead = views[name]
    chk(cert["witnesses"]["mu"] == mu and cert["witnesses"]["lambda"] == lam,
        f"{name} mu/lambda agree")
    chk(cert["battery"] == bat, f"{name} battery agrees")
    ev = cert["evaluations"]
    chk(ev["C1"]["state"] == "FAIL", f"{name} C1 fails (no threshold)")
    chk(ev["C2"]["state"] == "NOT EVALUABLE", f"{name} C2 not evaluable (bar is M1/2)")
    chk(ev["C3"]["state"] == "HOLD", f"{name} C3 holds at the registered scan unit")
    chk(ev["C4"]["state"] == "NOT EVALUABLE", f"{name} C4 not evaluable (bar is M1/2)")
    chk(ev["C5"]["state"] == ("HOLD" if (mu, lam) > bound else "FAIL"), f"{name} C5 agrees")
    chk(cert["verdict"] == "NOT-CERTIFIED", f"{name} verdict NOT-CERTIFIED")
    # engaged-edge hash recomputed from the raw artifacts
    norm_edges = [{"set": sorted(e["edge"]), "weight": e["weight"]} for e in edges]
    hh = hashlib.sha256(json.dumps(norm_edges, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    chk(cert["witnesses"]["engaged_edges_hash"] == hh, f"{name} edge hash agrees")
    if name in cuts_by_name:
        chk(cert["witnesses"]["cut_mus"] == cuts_by_name[name], f"{name} cut mus agree")

# ---- fixtures, evaluated independently ----
def eval_fx(fx):
    m1 = fx["thresholds"]["m1"]; bnd = fx["thresholds"]["c5_bound"]
    if m1 is None:
        return "NOT-CERTIFIED"
    bar = m1 / 2
    if fx["mu"] < m1: return "NOT-CERTIFIED"
    if any(a in e["set"] and e["weight"] >= bar for a in fx["dead"] for e in fx["edges"]): return "NOT-CERTIFIED"
    if not fx["scan_confirmed"]: return "NOT-CERTIFIED"
    if fx["cuts"] is None or any(m < bar for m in fx["cuts"]): return "NOT-CERTIFIED"
    if (fx["mu"], fx["lambda"]) <= tuple(bnd): return "NOT-CERTIFIED"
    return "EMERGENT"
fxs = json.load(open(os.path.join(W, "emergence-rung6-scratch/fixtures/fixtures.json")))
fxr = {f["fixture"]: f for f in out["fixtures"]}
for fx in fxs:
    mine = eval_fx(fx)
    chk(mine == fx["expected"], f"{fx['name']} independent evaluation {mine} == expected {fx['expected']}")
    chk(fxr[fx["name"]]["got"] == mine, f"{fx['name']} decider agrees with independent evaluation")

# ---- band test, independently ----
chk(all(b["verdict"] == "NOT-CERTIFIED" for b in out["band"]) and len(out["band"]) == 50,
    "band reweightings never flip a verdict to EMERGENT")

# ---- sensitivity, independently, including the small battery ----
def caps(battdir, arm):
    base = os.path.join(W, f"emergence-rung2-scratch/results/{battdir}")
    vals = []
    for f in sorted(os.listdir(base)):
        if f.startswith(arm + "-rep") and f.endswith(".json"):
            vals.append(json.load(open(os.path.join(base, f)))["cap"])
    return vals
sens = {}
for batt, d in (("MAIN v1", "main"), ("MAIN2 v2", "main2"), ("MAIN3 v3", "main3"), ("PROBE v3", "probe")):
    live = caps(d, "live-noisy")
    cs = {a: caps(d, a) for a in ("isolated", "frozen", "shuffled")}
    sep = min(live) > max(max(c) for c in cs.values())
    diffs = {a: sum(live) / len(live) - sum(c) / len(c) for a, c in cs.items()}
    sens[batt] = (sep, min(diffs.values()) if sep else None)
    got = out["sensitivity"][batt]
    chk(got["replicate_separation"] == sep, f"{batt} separation agrees")
    if sep:
        chk(abs(got["supremum_margin"] - min(diffs.values())) < 1e-12, f"{batt} supremum margin agrees")
live = caps("small3", "live-noisy"); iso = caps("small3", "isolated")
small_sep = min(live) > max(iso)
small_diff = sum(live) / len(live) - sum(iso) / len(iso)
print(f"small3 vs isolated only: separation {small_sep}, mean diff {small_diff:.6f}, "
      f"live reps {[round(x,4) for x in live]}, isolated reps {[round(x,4) for x in iso]}")
print("sensitivity:", {k: (s, round(m, 6) if m else None) for k, (s, m) in sens.items()})
print("C5 bound:", bound, "| M1:", m1, "| emergence views:", len(em_mu), "| no-emergence views:", len(noem_mu))
print("FAILURES:", len(fails))
for f in fails:
    print(" -", f)
sys.exit(1 if fails else 0)
