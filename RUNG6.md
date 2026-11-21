# Emergence rung 6 — the certificate: DECIDE over the rung 2–5 records

Executed 2026-11-21, after rung 5 landed (repo head
c289b55f2c029a311f80912a6ec56ee4f345f637). Spec:
~/workspace/research/emergence-ladder-spec-2026-11-21.md,
section 5 (rung 6) and section 6 (endgame). Registration:
~/workspace/emergence-rung6-scratch/registration.md, written
before DECIDE ran against any record, with no amendments.
Scratch: ~/workspace/emergence-rung6-scratch/ (decider
decide.py, independent checker check6.py, Lean
lean/EmergenceRung6.lean, results in results/ and
fixtures/).

## 1. Headline

**The section 5.5 precondition FAILS: the rung 2–5 records
do not separate.** Under the governing outcome reading
(registration section 2 — a battery recorded emergence
exactly when its registered decision was a win), no battery
in rungs 2–5 recorded emergence: rung 2 NO WIN in all four
decision batteries, rung 3 NO WIN in both families, rung 4
falsified in both pairs, rung 5 NO COMPOUNDING in both
families. The emergence side of the threshold derivation is
therefore empty, M1 does not exist, and by spec section
5.7(c) the claim that dies is "emergence is decidable from
this interaction matrix" — at the thresholds these records
induce, there is nothing to decide: DECIDE issues
NOT-CERTIFIED for all 25 registered view instances, in
agreement with every battery outcome, and no certificate of
emergence exists over this ladder's records. DECIDE itself
— the procedure, its certificates, its independent checker,
and its Lean kernel model — is verified at every point the
fixtures and the checker reach (sections 5–7). The failure
is in the records, not in the procedure, and it is total:
section 4 shows the non-separation survives even the most
generous non-governing re-reading of the rung-2 evidence.

## 2. Registration (summary; the registered text governs)

- Governing threshold computation: the emergence set is the
  persisted views of batteries whose registered decision was
  a win; M1 = (least emergence mu) − (greatest no-emergence
  mu), existing only if that set is nonempty and M1 > 0.
  The spec 5.1 sensitivity analysis is computed and printed
  but does not govern: no margin was ever registered for
  section 5.1, and choosing one now would be a hand-chosen
  threshold.
- Instances: 11 batteries (rung 2: MAIN v1, MAIN2 v2, MAIN3
  v3, PROBE v3, SMALL3 v3 partial; rung 3: field3, region3;
  rung 4: pair 0, pair 1; rung 5: field, region) and 25
  views (V1 rung-2 small3; V2–V7 rung-3 joint views; V8–V9
  rung-4 carried views; V10–V25 rung-5 live rep1 cut views),
  plus constructed fixtures F1–F7 for detector correctness
  only, at stated test thresholds that are inputs to the
  procedure, never thresholds over records.
- C2 and C4, whose bars are M1/2, are NOT EVALUABLE when M1
  does not exist — never silently holds, never silently
  fails; their computable content (per-axis dead scans,
  per-cut mus) is printed in every certificate. C1 without
  M1 is FAIL with the threshold's absence as the reason.
  C3 is read at the producing lane's persisted scan unit
  (the exact counterfactual scan, tick unit) and labeled.
  C5's bound is computable from the no-emergence side alone.
- Certificate: the section 5.4 JSON tuple, issued for every
  view instance including NOT-CERTIFIED ones, carrying the
  threshold derivation, per-condition states and witnesses,
  the premise list, and the engaged-edge hash. The checker
  is a separate program importing nothing from the decider.
- Band for T6.7: per-edge weights moved to any w' with
  w/2 ≤ w' ≤ 2w, edge sets unchanged; test maps ×2 and
  ceil(w/2), registered before any run.
- Premise debt: the section 6.3 derivation-graph audit is
  NOT executed in this lane; the extension-stable edge
  definition is NOT adopted — DECIDE runs on the records as
  persisted and carries the near-empty scope of the rung-5
  compounding premise as a named retest candidate. Both
  dispositions were registered in advance.

## 3. Threshold computations, with inputs

Outcome table (from the four rung records' decision lines
and the persisted decision files; the checker rebuilt it
independently — section 6):

| battery | registered decision | emergence recorded |
|---|---|---|
| rung2 MAIN v1 | NO WIN | no |
| rung2 MAIN2 v2 | NO WIN | no |
| rung2 MAIN3 v3 | NO WIN | no |
| rung2 PROBE v3 | NO WIN | no |
| rung2 SMALL3 v3 | partial (scale point, live vs isolated only) | no |
| rung3 field3 | NO WIN | no |
| rung3 region3 | NO WIN | no |
| rung4 pair 0 | falsified (no transfer) | no |
| rung4 pair 1 | falsified (no transfer) | no |
| rung5 field | NO COMPOUNDING | no |
| rung5 region | NO COMPOUNDING | no |

Threshold derivation over the 25 views:

- Emergence views: none. Least emergence mu: does not exist.
- No-emergence views: all 25. Greatest no-emergence mu:
  46,527 (V17, rung-5 field, tick 128).
- **M1: does not exist** (empty emergence set). The section
  5.2 precondition — M1 exists and is positive — fails.
- **C5 bound: rho (46527, 8)** — the greatest no-emergence
  rho on record, from the same view. No recorded view's rho
  exceeds it (V17 equals it; strict excess fails).
- C2/C4 bar M1/2: does not exist; both conditions NOT
  EVALUABLE on all 25 instances.

Per-instance verdicts (all NOT-CERTIFIED; C1 FAIL ×25 —
threshold absent; C2 NOT EVALUABLE ×25; C3 HOLD ×25 at the
registered scan unit; C4 NOT EVALUABLE ×25; C5 FAIL ×25):

| view | battery | mu | lambda | dead axes |
|---|---|---|---|---|
| V1 | rung2-small3 | 1,961 | 8 | {3} |
| V2 | rung3-field3 | 6,940 | 19 | not evaluable (>11 axes) |
| V3 | rung3-field3 | 6,933 | 19 | not evaluable |
| V4 | rung3-field3 | 6,983 | 19 | not evaluable |
| V5 | rung3-region3 | 6,942 | 29 | not evaluable |
| V6 | rung3-region3 | 6,988 | 29 | not evaluable |
| V7 | rung3-region3 | 6,930 | 29 | not evaluable |
| V8 | rung4-pair0 | 11,708 | 8 | all 8 |
| V9 | rung4-pair1 | 7,018 | 8 | all 8 |
| V10–V17 | rung5-field t1…t128 | 428, 862, 1737, 3482, 6943, 9942, 22122, 46527 | 8 | all 8 |
| V18–V25 | rung5-region t1…t128 | 428, 874, 1764, 2668, 3467, 6055, 14381, 2616 | 8 | all 8 (V18: {0,3,4,5,6,7}) |

Agreement: DECIDE's verdict agrees with the from-definitions
battery outcome on all 25 instances and all 11 batteries —
every battery decided falsified, every view NOT-CERTIFIED.
This is agreement in the degenerate direction the records
force; it is not evidence the procedure can certify a
positive, which is what the fixtures and the Lean controls
carry (sections 5, 7).

## 4. The generous reading also fails (non-governing)

The spec 5.1 predicate, re-evaluated from the persisted
rung-2 replicate files by both the decider and the checker
(identical results): MAIN v1 and MAIN2 v2 fail replicate
separation outright — no margin makes them emergence under
5.1. MAIN3 v3 separates, and its live mean exceeds every
control mean by at least 0.147161 (the frozen arm binds), so
it satisfies 5.1 for any margin below 0.147161; PROBE v3
likewise below 0.122004. The small battery separates against
its only control (isolated): live replicates 0.7263–0.7831
against isolated 0.6215–0.6685, mean difference +0.120099.

None of this rescues separation, for two independent
reasons. First, no margin was registered for 5.1, so no
battery's 5.1 status at any particular margin is a recorded
outcome. Second, even granting the strongest reading —
small3 emergence-positive against its only control — its
view's mu is 1,961, and the candidate M1 would be
1,961 − 46,527 = **−44,566**: not positive. MAIN3 and PROBE
persisted no views at all, so they contribute no mu to any
side. Under every reading of the persisted records, the
records do not separate.

## 5. Fixtures and band (detector correctness)

Fixtures F1–F7, evaluated by the decider and independently
by the checker, 7/7 agreement with the registered
expectations: F1 (mu 1,700, thresholds M1 1,000, bound
(1500, 3)) is EMERGENT — the procedure can certify a
positive when its conditions hold. F2–F6 each fail exactly
one condition (C1, C2, C3, C4, C5 respectively) and are
NOT-CERTIFIED. F7 — F1's view under the records' actual
threshold state (M1 absent) — is NOT-CERTIFIED: even a
fixture-shaped view cannot be certified over these records.

Band (T6.7, empirical half): both registered weight maps
(×2, ceil(w/2)) applied to all 25 views — 50 reweightings,
zero verdict flips, as the scoped Lean theorem predicts
(C1's failure does not read the view's weights when the
threshold is absent). The general band statement — stability
of an EMERGENT verdict inside a factor-2 band at thresholds
that exist — is not tested by any instance here, because no
EMERGENT verdict exists; it stands unclaimed with T6.1's
family.

## 6. Certificate format and checker results

Certificate: one JSON object per view instance with the
fields spec 5.4 names — instance, battery, view hash
(sha-256 of the canonical view JSON), the threshold
derivation (emergence and no-emergence view lists, least
and greatest mus, M1 and its existence, the C5 bound, the
separation flag), per-condition evaluations (state and
witness for C1–C5, including the dead-axis scan and the cut
mus where the condition itself is not evaluable), the
premise list (section 8), and the verdict. All 25
certificates are in results/decide.json in the scratch;
their compact content is the table in section 3.

Independent checker (check6.py; imports nothing from the
decider): rebuilt the outcome table from the four records'
decision lines and the persisted rung-4/rung-5 decision
files; re-extracted all 25 views from the rung artifacts
with its own code; recomputed the threshold derivation
(M1 absent, C5 bound (46527, 8), greatest no-emergence mu
46,527); compared every certificate field — mu, lambda,
battery, all five condition states, verdict, engaged-edge
hash recomputed from the raw artifacts, cut mus — and
re-evaluated all 7 fixtures and the sensitivity analysis
from the raw replicate files. **Result: 0 failures.** One
disagreement would have killed T6.4; there were none.

## 7. Theorems (Lean 4.19.0, core only, no sorry)

File: lean/EmergenceRung6.lean in the scratch, landed as
rung6/EmergenceRung6.lean. Cold compile clean; axiom audit:
every proved item depends only on propext and Quot.sound
(several on propext alone or none).

- T6.1 soundness: PREMISE — stated as a definition depended
  on by nothing. Not proved; no EMERGENT verdict issues in
  this rung, so no verdict rests on it.
- T6.2 completeness on the registered class: PREMISE —
  stated as a definition over an abstract class predicate,
  depended on by nothing, never claimed generally.
- T6.3 decidability: PROVED — the verdict is a function of
  the view and the thresholds alone (congruence theorem),
  and each condition's evaluation is total over its three
  states (case theorem for C1, the others identical in
  form). Finiteness is by the definitions: finite edge
  lists, finite cut lists, natural arithmetic.
- T6.4 detector correctness: PROVED in its Lean half — seven
  kernel-decide controls mirroring the fixtures (one passing
  view, one failure per condition, the no-threshold
  control). The empirical half is the checker agreement of
  section 6: 25/25 certificates, 7/7 fixtures, 0 failures.
- T6.5 margin monotonicity: PROVED — mu is monotone under a
  pointwise weight increase changing nothing else, and C1,
  C4, C5 holdings are each preserved under such an increase
  at fixed thresholds.
- T6.6 certificate checkability: PROVED — soundness (an
  accepted certificate's presented mu, lambda, and verdict
  equal the recomputed fields) and completeness (the honest
  certificate is accepted).
- T6.7 reweighting stability: PROVED in scoped form — when
  the C1 threshold does not exist, every view's verdict is
  NOT-CERTIFIED and stays so under every reweighting,
  because C1's evaluation reads only the threshold's
  absence. The general band statement is not claimed
  (section 5).

## 8. Premise debt disposition

The debt at this rung's opening was four. **None of the four
is discharged by this rung**, and the reason is the one
registered in advance: the discharge route the spec names
for the family — the derivation-graph audit of spec 6.3 —
was not executed in this lane, and this rung's results do
not substitute for it. All four are carried by name inside
every certificate's premise list:

1. Rung-3 deadness (T3.8): discharged only by T6.1 in
   general form; T6.1 stands as premise. Carried.
2. Rung-4 transfer bound (T4.5): same route, same state.
   Carried.
3. Rung-5 compounding (T5.6): carried, with its measured
   scope: the antecedent failed at 55 of 56 checkpoint
   pairs at rung 5 because a tick's hyperedge is a
   counterfactual against the whole cut fold. The
   extension-stable edge definition (edges fixed at the
   tick that creates them) is the named repair and a retest
   candidate for any future battery; it was not adopted
   here, by registration.
4. Rung-5 view determination (T5.4): premise by construction
   review at rung 5; the audit that would discharge it was
   not executed. Carried.

Nothing in this rung's verdicts rests on any of the four:
every NOT-CERTIFIED verdict follows from C1 and C5, whose
inputs are persisted mus and the outcome table alone. The
attribution counterexample from rung 5 stands unaddressed
by any positive claim here — there is no positive claim —
and any future certificate over a compounding battery must
state what the certified history is OF, per rung 5's
inheritance item (3). Inherited open items unchanged: the
dependence-scan cost gap (G2) is still OPEN; the
evidence-gate constant (≥3 reports) remains the only
measured constant, its sensitivity unmeasured after four
inheritances; grain saturation at G=8 persists in every
record this rung consumed.

## 9. Verified vs claimed

Verified by execution in this rung: the threshold derivation
and its failure (two independent implementations agreeing);
25/25 certificate fields under independent recheck; 7/7
fixtures under two implementations; 50/50 band
reweightings without a flip; the sensitivity figures of
section 4 under two implementations; the Lean file's cold
compile and axiom audit.

Claimed, not verified: nothing beyond the above. In
particular not claimed: that DECIDE would certify a real
positive instance (fixtures are constructed); that the
section 5.1 predicate at any specific margin describes any
battery (no margin was registered); the general T6.7 band
statement; T6.1 and T6.2 in any form.

Falsified in this rung, exactly as spec 5.7(c) names it:
the rung 2–5 records separate under DECIDE's conditions —
they do not, under the governing reading or under the most
generous non-governing one (section 4). The claim "emergence
is decidable from this interaction matrix," as a claim about
these records, is falsified with it: the matrix's records
contain no emergence for a decision procedure to find.

## 10. The ladder's final state, and the endgame

Per-rung disposition:

- Rung 1 (detector): verified at stated scope — exact
  detector and incremental tally, five theorems, XOR probe
  separation on a toy. Not emergent intelligence; never
  claimed as such.
- Rung 2 (noisy gossip): claim FALSIFIED as registered —
  NO WIN at the registered margin in every decision
  battery; the narrower fact stands that the v3 code's live
  arm beats every control mean and replicate at both scales.
- Rung 3 (composition): claim FALSIFIED as registered —
  NO WIN in both families under both margin rules; joint
  views carry the highest means and zero load-bearing
  blocks. T3.1–T3.7 proved, T3.8 premise.
- Rung 4 (transfer): claim FALSIFIED as registered — the
  transfer effect is exactly zero in both pairs; the
  carriage channel is closed by the target task's
  order-independent optimum. T4.1–T4.4, T4.6 proved, T4.5
  premise.
- Rung 5 (compounding): claim FALSIFIED as registered —
  NO COMPOUNDING under both margin rules; the one family
  passing the margins is unattributable (its frozen control
  compounds as much). Infrastructure verified a fourth
  time. T5.1–T5.3, T5.5 proved; T5.4, T5.6 premises.
- Rung 6 (the certificate): the decision procedure is built
  and verified (checker, fixtures, Lean), and its governing
  precondition over the ladder's records FAILS — the
  records do not separate, so the certificate's positive
  form is never instantiated. T6.3–T6.6 proved, T6.7 proved
  in scoped form, T6.1–T6.2 premises.

What the ladder establishes, in total: a complete,
machine-checked measurement stack for interaction emergence
— detector, tally, views, margins, transfer and compounding
batteries, and now an exact decision procedure with
recheckable certificates — and, measured with that stack,
**no emergence in any system the ladder tested**: every
capability claim the ladder registered was falsified by its
own battery, and the final rung confirms there is no
threshold derivation under which the accumulated records
say otherwise. The four premises and the open items of
section 8 are the ladder's remaining debt, each with a
named discharge route (the derivation-graph audit) or a
named retest candidate (extension-stable edges; a battery
whose live arm separates at a pre-registered margin and
persists its views).

The endgame interfaces, concretely, as of this rung:

- I2 (certificate query): EXISTS as a standalone artifact —
  DECIDE plus its independent checker plus the Lean kernel
  model, answering "does this view exhibit emergence, and
  under what certificate" for any view in the persisted
  form, with premises carried in the answer. It is NOT
  integrated into any derivation machinery: no hypergraph
  query route reaches it, and spec 6.2's claim — the
  emergence measure as a derived quantity in the one
  derivation machinery — remains PROPOSED, not established.
- I1 (selection weights): untouched by this rung; the
  rung-2–5 arms' selection behavior stands as measured
  there. Weights changed selection in those batteries and
  evidence nowhere.
- I3 (compounding signal): exists as rung 5's measured
  curve data and its falsified claim; as an interface
  feeding a derivation machinery, PROPOSED only.
- Spec 6.4's falsification condition (the same system
  certified and refuted from the same records) is not
  triggered: no system is certified, and the refutations
  are the batteries' own.

The ladder is complete: six rungs executed, every claim
dispositioned on executed evidence, the final rung's
procedure verified and its precondition printed as failed.
Any continuation is a new battery under a new registration
— pre-registered margin, persisted views, extension-stable
edges — not a reinterpretation of these records.
