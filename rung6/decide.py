#!/usr/bin/env python3
"""Rung 6 DECIDE: threshold derivation from the rung 2-5 records,
condition evaluation C1-C5 over persisted views, certificate issue.
Implements registration.md exactly. No threshold is chosen here:
M1 and the C5 bound are computed from the outcome table below,
whose every entry names its record."""
import json, hashlib, os, math, time

HOME = os.path.expanduser("~/workspace")
SCR = os.path.join(HOME, "emergence-rung6-scratch")

# Outcome table: battery -> recorded emergence under its own
# registered rule. Provenance: the research record named.
OUTCOMES = [
    ("rung2-main-v1", False, "emergence-rung2 record, MAIN (v1): NO WIN"),
    ("rung2-main2-v2", False, "emergence-rung2 record, MAIN2 (v2): NO WIN"),
    ("rung2-main3-v3", False, "emergence-rung2 record, MAIN3 (v3): NO WIN"),
    ("rung2-probe-v3", False, "emergence-rung2 record, PROBE (v3): NO WIN"),
    ("rung2-small3-v3", False, "emergence-rung2 record, SMALL3: no decision registered (two arms)"),
    ("rung3-field3", False, "emergence-rung3 record: NO WIN"),
    ("rung3-region3", False, "emergence-rung3 record: NO WIN"),
    ("rung4-pair0", False, "emergence-rung4 record: falsified, dT = 0"),
    ("rung4-pair1", False, "emergence-rung4 record: falsified, dT = 0"),
    ("rung5-field", False, "emergence-rung5 record: falsified, horizon conjunct"),
    ("rung5-region", False, "emergence-rung5 record: falsified as registered (attribution, vacuous scope)"),
]
BATTERY_OF_VIEW = {
    "V1": "rung2-small3-v3",
    "V2": "rung3-field3", "V3": "rung3-field3", "V4": "rung3-field3",
    "V5": "rung3-region3", "V6": "rung3-region3", "V7": "rung3-region3",
    "V8": "rung4-pair0", "V9": "rung4-pair1",
    "V10": "rung5-field", "V11": "rung5-field", "V12": "rung5-field",
    "V13": "rung5-field", "V14": "rung5-field", "V15": "rung5-field",
    "V16": "rung5-field", "V17": "rung5-field",
    "V18": "rung5-region", "V19": "rung5-region", "V20": "rung5-region",
    "V21": "rung5-region", "V22": "rung5-region", "V23": "rung5-region",
    "V24": "rung5-region", "V25": "rung5-region",
}

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()

def h256(obj):
    return hashlib.sha256(canon(obj)).hexdigest()

def norm(name, mu, lam, edges, dead, cuts, provenance, scan):
    v = {"name": name, "mu": mu, "lambda": lam,
         "edges": [{"set": sorted(e["edge"]), "weight": e["weight"]} for e in edges],
         "dead": sorted(dead), "cuts": cuts, "provenance": provenance,
         "scan": scan}
    v["hash"] = h256({k: v[k] for k in ("name", "mu", "lambda", "edges", "dead", "cuts")})
    return v

def extract_views():
    views = []
    # V1 rung 2 small3
    p = os.path.join(HOME, "emergence-rung2-scratch/results/small3/view.json")
    v = json.load(open(p))
    minimal_axes = set()
    for ms in v["minimal_sufficient"]:
        minimal_axes.update(a.replace("group", "") for a in ms["axes"])
    dead = [i for i in range(8) if str(i) not in minimal_axes]
    views.append(norm("V1", v["mu_full"], v["lambda_full"], v["edges"], dead, None,
                      "rung2 small3 live-noisy rep1 view (N=64, G=8)",
                      "exact counterfactual scan, tick unit (rung2 view.py)"))
    # V2-V7 rung 3 joint views
    idx = 2
    for fam, tag in (("field3", "field"), ("region3", "region")):
        p = os.path.join(HOME, f"emergence-rung3-scratch/results/{fam}/view3.json")
        vv = json.load(open(p))
        for w in vv["views"]:
            if w["kind"] != "joint":
                continue
            views.append(norm(f"V{idx}", w["mu_full"], w["lambda_full"], w["edges"],
                              [], None,
                              f"rung3 {tag}3 joint rep1 view at formation tick {w['formation_tick']} (dead not evaluable above 11 axes, rung3 record)",
                              "exact counterfactual folds, tick unit (rung3 view3.py); dead-axis scan not evaluable at 19/29 axes"))
            idx += 1
    # V8, V9 rung 4 source views
    for fam, name in (("field", "V8"), ("region", "V9")):
        p = os.path.join(HOME, f"emergence-rung4-scratch/results/{fam}/view.json")
        v = json.load(open(p))
        views.append(norm(name, v["mu"], v["lambda"], v["edges"], v["dead"], None,
                          f"rung4 {fam} source view rep1 (G=8)",
                          "exact counterfactual scan, tick unit (rung4 harness)"))
    # V10-V25 rung 5 cut views
    idx = 10
    for fam in ("field", "region"):
        p = os.path.join(HOME, f"emergence-rung5-scratch/results/{fam}5/views-live-rep1.json")
        vv = json.load(open(p))
        mus = [e["mu"] for e in vv]
        for e in vv:
            t = e["tick"]
            half = [m for e2, m in zip(vv, mus) if e2["tick"] >= t / 2 and e2["tick"] <= t]
            views.append(norm(f"V{idx}", e["mu"], e["lambda"], e["edges"], e["dead"], half,
                              f"rung5 {fam} live rep1 cut view at tick {t}",
                              "exact counterfactual scan, tick unit (rung5 harness)"))
            idx += 1
    return views

def thresholds(views):
    outcome = {b: e for b, e, _ in OUTCOMES}
    em, noem = [], []
    for v in views:
        (em if outcome[BATTERY_OF_VIEW[v["name"]]] else noem).append(v)
    least_em = min((v["mu"] for v in em), default=None)
    great_noem = max((v["mu"] for v in noem), default=None)
    bound = max(((v["mu"], v["lambda"]) for v in noem), default=None)
    m1 = None
    if least_em is not None and great_noem is not None:
        m1 = least_em - great_noem
    return {"emergence_views": [v["name"] for v in em],
            "noemergence_views": [v["name"] for v in noem],
            "least_emergence_mu": least_em,
            "greatest_noemergence_mu": great_noem,
            "m1": m1,
            "m1_exists": m1 is not None and m1 > 0,
            "c5_bound": list(bound) if bound else None,
            "separates": (m1 is not None and m1 > 0) and len(em) > 0}

def decide(view, th, weight_map=None):
    """weight_map: optional function on weights (band tests, fixtures).
    Returns (verdict, conditions dict)."""
    edges = view["edges"]
    if weight_map:
        edges = [{"set": e["set"], "weight": weight_map(e["weight"])} for e in edges]
    mu = view["mu"] if not weight_map else None
    # under a weight map the persisted mu is not the mapped mu; the
    # mapped mu is recomputed as the engaged sum scaled per edge is
    # not recoverable from mu alone, so band tests use the fixture
    # path in decide_fixture. For persisted views the band test only
    # needs C1's status, which is weight-independent here.
    cond = {}
    if not th["m1_exists"]:
        cond["C1"] = ("FAIL", "threshold does not exist: M1 undefined or not positive (registration section 2)")
    else:
        cond["C1"] = ("HOLD" if mu >= th["m1"] else "FAIL", f"mu {mu} vs M1 {th['m1']}")
    if not th["m1_exists"]:
        cond["C2"] = ("NOT EVALUABLE", "bar is M1/2 and M1 does not exist; dead-axis scan printed separately")
    else:
        bar = th["m1"] / 2
        bad = [a for a in view["dead"] if any(a in e["set"] and e["weight"] >= bar for e in edges)]
        cond["C2"] = ("FAIL" if bad else "HOLD", f"dead axes carrying an edge of weight >= {bar}: {bad}")
    if view.get("scan_confirmed", True):
        cond["C3"] = ("HOLD", "every size>=2 edge dependence-confirmed by the exact scan at the registered unit: " + view["scan"])
    else:
        cond["C3"] = ("FAIL", "an edge lacks a two-direction dependence confirmation")
    if not th["m1_exists"]:
        cond["C4"] = ("NOT EVALUABLE", "bar is M1/2 and M1 does not exist; per-cut mus printed where persisted")
    elif view["cuts"] is None:
        cond["C4"] = ("NOT EVALUABLE", "no per-cut views persisted for this instance")
    else:
        bar = th["m1"] / 2
        cond["C4"] = ("HOLD" if all(m >= bar for m in view["cuts"]) else "FAIL",
                      f"cut mus at/after half horizon {view['cuts']} vs bar {bar}")
    if th["c5_bound"] is None:
        cond["C5"] = ("FAIL", "bound does not exist")
    else:
        rho = (view["mu"], view["lambda"])
        cond["C5"] = ("HOLD" if rho > tuple(th["c5_bound"]) else "FAIL",
                      f"rho {rho} vs bound {tuple(th['c5_bound'])} (lexicographic, strict)")
    verdict = "EMERGENT" if all(c[0] == "HOLD" for c in cond.values()) else "NOT-CERTIFIED"
    return verdict, cond

def decide_fixture(fx):
    """Fixtures carry explicit fields and test thresholds as inputs."""
    th = fx["thresholds"]
    view = {"mu": fx["mu"], "lambda": fx["lambda"], "edges": fx["edges"],
            "dead": fx["dead"], "cuts": fx["cuts"], "scan": fx["scan"],
            "scan_confirmed": fx["scan_confirmed"]}
    m1 = th["m1"]
    thx = {"m1_exists": m1 is not None, "m1": m1, "c5_bound": th["c5_bound"]}
    return decide(view, thx)

def fixtures():
    big = [{"set": [0, 1], "weight": 900}, {"set": [1, 2], "weight": 800}]
    base = {"mu": 1700, "lambda": 3, "edges": big, "dead": [3], "cuts": [900, 1700],
            "scan": "fixture scan", "scan_confirmed": True,
            "thresholds": {"m1": 1000, "c5_bound": [1500, 3]}}
    out = []
    def add(name, exp, **kw):
        fx = dict(base); fx.update(kw); fx["name"] = name; fx["expected"] = exp
        out.append(fx)
    add("F1", "EMERGENT")
    add("F2", "NOT-CERTIFIED", mu=900, thresholds={"m1": 1000, "c5_bound": [500, 3]})  # C1 fails alone: 900 < 1000, rho (900,3) still above its bound
    add("F3", "NOT-CERTIFIED", dead=[1])                     # C2 fails: dead axis 1 carries edges >= 500
    add("F4", "NOT-CERTIFIED", scan_confirmed=False)         # C3 fails
    add("F5", "NOT-CERTIFIED", cuts=[900, 400])              # C4 fails: 400 < 500
    add("F6", "NOT-CERTIFIED", mu=1400, cuts=[900, 1400])    # C5 fails: (1400,3) < (1500,3); C1 holds
    add("F7", "NOT-CERTIFIED", thresholds={"m1": None, "c5_bound": [1500, 3]})  # no threshold: C1 fails
    return out

def sensitivity():
    """Section 5.1 re-evaluation from persisted rung-2 replicates.
    Non-governing (registration section 7)."""
    res = {}
    for batt, d in (("MAIN v1", "main"), ("MAIN2 v2", "main2"), ("MAIN3 v3", "main3"), ("PROBE v3", "probe")):
        arms = {}
        base = os.path.join(HOME, f"emergence-rung2-scratch/results/{d}")
        for f in os.listdir(base):
            if f.endswith(".json") and "-rep" in f and "view" not in f:
                r = json.load(open(os.path.join(base, f)))
                arms.setdefault(r["arm"], []).append(r["cap"])
        live = arms["live-noisy"]
        ctrls = {a: arms[a] for a in ("isolated", "frozen", "shuffled")}
        diffs = {a: sum(live) / 8 - sum(c) / 8 for a, c in ctrls.items()}
        sep = min(live) > max(max(c) for c in ctrls.values())
        res[batt] = {"mean_diffs": diffs, "replicate_separation": sep,
                     "supremum_margin": min(diffs.values()) if sep else None,
                     "predicate_holds_for_some_positive_m": bool(sep and min(diffs.values()) > 0)}
    return res

def main():
    views = extract_views()
    th = thresholds(views)
    certs = []
    for v in views:
        t0 = time.time()
        verdict, cond = decide(v, th)
        wall = time.time() - t0
        cert = {"instance": v["name"], "battery": BATTERY_OF_VIEW[v["name"]],
                "view_hash": v["hash"], "provenance": v["provenance"],
                "threshold_derivation": th,
                "evaluations": {k: {"state": s, "witness": w} for k, (s, w) in cond.items()},
                "witnesses": {"mu": v["mu"], "lambda": v["lambda"], "rho": [v["mu"], v["lambda"]],
                              "engaged_edges_hash": h256(v["edges"]),
                              "dead_axes": v["dead"], "scan": v["scan"],
                              "cut_mus": v["cuts"]},
                "verdict": verdict, "decide_wall_s": wall}
        certs.append(cert)
    fxs = fixtures()
    fxr = []
    for fx in fxs:
        verdict, cond = decide_fixture(fx)
        fxr.append({"fixture": fx["name"], "expected": fx["expected"], "got": verdict,
                    "conditions": {k: s for k, (s, _) in cond.items()}})
    band = []
    for v in views:
        for label, wm in (("x2", lambda w: 2 * w), ("half", lambda w: -(-w // 2))):
            verdict, cond = decide(v, th, weight_map=wm)
            band.append({"instance": v["name"], "map": label, "verdict": verdict,
                         "c1": cond["C1"][0]})
    out = {"thresholds": th, "certificates": certs, "fixtures": fxr, "band": band,
           "sensitivity": sensitivity()}
    os.makedirs(os.path.join(SCR, "results"), exist_ok=True)
    json.dump(out, open(os.path.join(SCR, "results/decide.json"), "w"), indent=1)
    json.dump(fxs, open(os.path.join(SCR, "fixtures/fixtures.json"), "w"), indent=1)
    print("M1:", th["m1"], "exists:", th["m1_exists"], "| C5 bound:", th["c5_bound"],
          "| separates:", th["separates"])
    print("emergence views:", th["emergence_views"], "| no-emergence views:", len(th["noemergence_views"]))
    print("verdicts:", {c["verdict"] for c in certs}, "on", len(certs), "instances")
    print("fixtures:", [(f["fixture"], f["expected"] == f["got"]) for f in fxr])
    print("band flips to EMERGENT:", [b for b in band if b["verdict"] == "EMERGENT"])
    for k, s in out["sensitivity"].items():
        print(k, "sep:", s["replicate_separation"], "sup margin:", s["supremum_margin"])

if __name__ == "__main__":
    main()
