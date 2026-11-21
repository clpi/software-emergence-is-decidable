# Emergence rung 6 — registration (written before any DECIDE run)

Date: 2026-11-21. Spec: ~/workspace/research/
emergence-ladder-spec-2026-11-21.md §1, §5, §6. This
registration governs every rung-6 evaluation below. Amendments,
if any, are appended here before the runs they affect, with the
measured reason, in the rung 2–5 pattern.

## 1. What is decided, and the governing order of operations

Rung 6 first executes §5.5's precondition, exactly as specced:
the rung 2–5 records separate iff C1's rule (§5.2) yields a
positive M1 AND C5's rule yields a strict bound. The threshold
computations of §2 are executed on the persisted battery
records before DECIDE is run on any instance. If the
precondition fails, §5.7(c) applies: the claim that dies is
"emergence is decidable from this interaction matrix", stated
in those words, and DECIDE's lawful output on every instance
is NOT-CERTIFIED (C1 cannot hold when its threshold does not
exist). DECIDE, its independent checker, and the T6.4
agreement battery are still built and run — detector
correctness (T6.4) is a claim about the procedure, separable
from the precondition, and the prior rungs' falsification
pattern requires the instrument to be verified even when the
claim it serves is dead.

## 2. The threshold computations (exactly §5.2, no other rule)

Inputs: the persisted records of rungs 2–5 (research records
plus scratch artifacts, named in §3). A battery **recorded
emergence** iff its registered decision, under its own
registered rule, was a win. The registered decisions on
record, transcribed with provenance into the outcome table
(§3), are: rung 2 — NO WIN in MAIN v1, MAIN2 v2, MAIN3 v3,
PROBE v3 (SMALL batteries carry no §1.9 decision: two arms
only, registered as such); rung 3 — NO WIN in field3 and
region3; rung 4 — falsified in pair 0 and pair 1; rung 5 —
falsified jointly (field fails the horizon conjunct; region
unattributable with vacuous monotonicity scope). No other
reading of "recorded" is used for the governing computation.

- **M1** = (least total engaged weight mu over the views of
  batteries that recorded emergence) − (greatest total
  engaged weight mu over the views of batteries that recorded
  no emergence). If the emergence set is empty, the least is
  undefined and M1 does not exist. If the no-emergence set is
  empty, likewise. M1 exists as a certificate threshold only
  if it is defined and positive (§5.2, §5.5).
- **C5 bound** = the greatest rho, lexicographic, over the
  views of batteries that recorded no emergence. The bound is
  computable whenever the no-emergence view set is non-empty;
  separation in the §5.5 sense additionally requires an
  emergence-side view whose rho the bound separates from —
  with no emergence view, no candidate can be certified
  against the bound as an emergence witness, and the
  precondition's two-sided separation fails. Both facts are
  printed, neither rounded into the other.
- A battery's **views** for these computations: every view
  persisted by that battery's lane with a recorded (mu,
  lambda): rung 2 — the small3 live-noisy rep-1 view (the only
  full view that lane computed); rung 3 — the joint rep-1
  views at formation ticks 8/16/24 in both families (level
  views printed in the sensitivity analysis, not the governing
  set, because §5.2 speaks of the battery's view and the joint
  view is the battery's system view); rung 4 — the two source
  views (field, region, rep 1); rung 5 — the live rep-1 cut
  views at all 8 checkpoints in both families (16 views).
  Views are taken as persisted; no view is recomputed to a
  different grain for this rung.

## 3. Instance set

**Battery instances (outcome side)** — each with its recorded
outcome, from the named record:
B1 rung2 MAIN v1 (NO WIN; record §MAIN), B2 rung2 MAIN2 v2
(NO WIN), B3 rung2 MAIN3 v3 (NO WIN), B4 rung2 PROBE v3
(NO WIN), B5 rung2 SMALL3 v3 (no decision registered;
§5.1-evaluable against its single persisted control, labeled
partial), B6 rung3 field3 (NO WIN), B7 rung3 region3
(NO WIN), B8 rung4 pair0 (falsified), B9 rung4 pair1
(falsified), B10 rung5 field (falsified — horizon conjunct),
B11 rung5 region (falsified as registered — attribution and
vacuous scope; its gain conjunct passed, printed as such).

**View instances (structure side)** — every view in §2's
governing sets: V1 rung2 small3 (mu 1961, lambda 8);
V2–V7 rung3 joint rep-1 at t8/t16/t24, field3 (6940, 6933,
6983; lambda 19) and region3 (6942, 6988, 6930; lambda 29);
V8 rung4 field source (11708, 8); V9 rung4 region source
(7018, 8); V10–V25 rung5 live rep-1 cuts, field (428, 862,
1737, 3482, 6943, 9942, 22122, 46527; lambda 8) and region
(428, 874, 1764, 2668, 3467, 6055, 14381, 2616; lambda 8).
(The mu values in this paragraph are the registration's
transcription of the records; the decider and checker both
re-extract them from the persisted artifacts, and any
transcription error is a checker finding, not a silent fix.)

**Constructed fixtures (detector correctness only)** — small
hand-built views with known condition values, evaluated under
*hypothetical test thresholds supplied as procedure inputs*
(they are inputs to a function test, not certificate
thresholds; no certificate issues against them): F1 a view
passing all five conditions under its test thresholds;
F2–F6 views failing exactly one of C1, C2, C3, C4, C5 each;
F7 a view with M1 absent (threshold input = none) that would
pass every structural condition — expected NOT-CERTIFIED,
proving the procedure cannot issue EMERGENT without a
threshold. Fixtures are generated by a script in this scratch
and persisted as JSON; their expected verdicts are computed
by hand in this registration's fixture table (in the record)
before the decider runs.

## 4. DECIDE, as implemented here

DECIDE(view, thresholds) where thresholds = (M1 or absent,
C5 bound or absent), executing §5.3 steps 2–4 on an already
persisted probe view (step 1, running the probe, is the
battery lanes' work; every view instance above is a persisted
probe view in the §5.2 sense — the live arm's log's view):

- C1: M1 exists and mu(view) >= M1. If M1 is absent, C1 fails
  with reason "threshold does not exist".
- C2: no emergent-dead axis of the view carries a hyperedge
  of weight >= M1/2. If M1 is absent, C2 is NOT EVALUABLE
  (its bar is M1/2) — reported in those words; the dead-axis
  scan itself is still computed and printed.
- C3: every hyperedge of size >= 2 in the view is
  dependence-confirmed in both directions by the exact scan.
  On persisted views, edges exist only where the producing
  lane's exact counterfactual scan (tick unit, the registered
  scan unit of rungs 2–5) changed a component; the decider
  reads the persisted edge set and the scan provenance and
  reports C3 at that unit, labeled. (Per-message scan cost is
  G2, still OPEN; nothing here upgrades the unit.)
- C4: for every cut of the probe log at or after half the
  probe horizon, mu over the cut's view >= M1/2. Evaluable
  only where per-cut mus are persisted (rung 5's instances)
  and M1 exists; otherwise NOT EVALUABLE with the reason
  named (no per-cut views persisted, or M1 absent). The
  per-cut mu values are printed wherever they exist.
- C5: rho(view) strictly exceeds the C5 bound,
  lexicographically. If the bound is absent, C5 fails with
  reason "bound does not exist".
- Verdict: EMERGENT(m, rho) iff C1–C5 all hold (a NOT
  EVALUABLE condition is not a hold). Otherwise
  NOT-CERTIFIED with the list of failed and not-evaluable
  conditions. The margin m attached to an EMERGENT verdict is
  the margin input; in this rung no EMERGENT verdict can
  issue (C1 fails universally), so no m is asserted.

Cost bound printed per verdict (§5.3): the decider's scans
are linear in the view's edge count plus the subset scans the
persisted view already carries; the measured wall per
instance is printed.

## 5. The certificate and its checker

Certificate format (§5.4), JSON: (instance name, view hash —
SHA-256 of the canonical view JSON as persisted, the
threshold derivation: the outcome table's identifier, the
emergence and no-emergence view sets with their mus and
rhos, the arithmetic producing M1's status and the C5 bound,
the C1–C5 evaluations with witnesses: mu and the engaged
edge list's hash, the dead-axis list, the edge provenance,
the per-cut mus where they exist, the rho comparison — and
the verdict). A certificate is issued for every view
instance, including NOT-CERTIFIED ones (the certificate
certifies the evaluation, and for NOT-CERTIFIED the failed
conditions are its content).

The checker is a separate code path importing nothing from
the decider. It re-extracts every view from the persisted
rung artifacts, rebuilds the outcome table from the persisted
decision artifacts where they exist (rung 4 and rung 5
decisions files; rung 3 battery summaries; rung 2 battery
summaries) and the research records' decision lines
elsewhere, recomputes the threshold derivation, re-evaluates
C1–C5 from the definitions, and compares every certificate
field. Agreement criterion (T6.4): the decider's verdict and
every condition evaluation equal the checker's from-definitions
values on every registered instance (view instances,
constructed fixtures, and the band-reweighting tests of §6).
One disagreement kills the detector claim (T6.4), per §5.7(b).

## 6. The T6.7 band, defined here as the spec directs

A **selection-band reweighting** of a view: each hyperedge
weight w is replaced by w' with w/2 <= w' <= 2w (integer
rounding toward the nearer bound permitted), the edge's
component set unchanged, no edge added or removed. Test:
for every view instance, apply the two extreme band maps
(w -> 2w and w -> ceil(w/2)) and re-run DECIDE; the verdict
must not change from NOT-CERTIFIED to EMERGENT. (In this
rung the protection is structural — C1's failure is
threshold-absence, which no reweighting of a probe view can
repair — and the test is executed anyway, because T6.7 is a
claim about the procedure, not about this rung's luck.)

## 7. The §5.1 sensitivity analysis (non-governing, printed)

Separately from §2's governing computation, the checker
re-evaluates §5.1's predicate from the persisted replicates
of the rung-2 decision batteries: the predicate holds at
margin m iff every control's mean is beaten by more than m
AND the live replicates all exceed every control replicate's
maximum. For each battery the supremum margin (the least
mean difference, where replicate separation holds) is
printed. This analysis exists because §5.1 and the rungs'
registered δ-rules are different instruments; its results do
not enter M1, because no margin m was ever registered for
§5.1 by any rung 2–5 registration, and choosing one now
would be a hand-chosen threshold. What the analysis may
legitimately show: whether the non-separation is an artifact
of the δ-rules alone, or survives §5.1 as well — including
the mu side: whether any §5.1-positive battery persisted a
view whose mu could separate. Both readings are printed;
neither is promoted.

## 8. Theorem obligations, as they will be attempted

Lean 4.19.0, core only, toolchain at
~/workspace/tools/lean-dl/lean-4.19.0-linux. Model: a view
is a finite list of edges, each a natural weight and a list
of component indices; engaged = edges of size >= 2 (the
persisted views' mu is the F1 engaged sum; the Lean model
proves the procedure's properties over its own finite form,
on the rung 2–5 precedent — the empirical agreement battery
is T6.4's other half). Attempted: T6.3 (the evaluation is a
total function of view and thresholds alone — congruence and
decidability), T6.4 (kernel decide controls on concrete
views, mirroring the fixture battery), T6.5 (mu monotone
under pointwise weight increase on a fixed edge list, hence
C1/C4/C5 monotone in engaged weight at fixed thresholds),
T6.6 (the check function accepts exactly when every
presented field equals the recomputed field — soundness
direction proved, completeness by construction of the check
as a conjunction of decidable equalities), T6.7 scoped form
(threshold absent => verdict NOT-CERTIFIED under every
reweighting, since C1's evaluation does not read the view's
weights when its threshold does not exist). T6.1 and T6.2
are stated as premise definitions, depended on by nothing:
T6.1 is the rung's central theorem and is NOT proved here —
and because no EMERGENT verdict issues in this rung, no
verdict rests on it; T6.2 is PREMISE per the spec, scoped to
pre-registered system classes, never claimed generally.

Premise debt disposition, registered in advance: the
derivation-graph audit named as T5.4's discharge route is an
endgame (§6.3) instrument; this lane builds no derivation
machinery integration, so the audit is NOT executed here and
nothing is discharged by it. T3.8 (discharged only by T6.1
in general form — not proved), T4.5, T5.6, T5.4 therefore
stand as premises at this rung's close unless the Lean work
itself discharges one, which the record will state exactly.
The extension-stable edge definition named in rung 5's
inheritance item 2 is NOT adopted in this rung: the
precondition computation runs on the records as persisted,
and redefining edges would change the very records whose
separation is being tested. It is carried as a named retest
candidate in the closing section, not executed.

## 9. Falsification conditions (restated from §5.7)

The rung-6 claim is dead if: (a) a system satisfies C1–C5
and its full battery fails §5.1 (soundness counterexample —
none can arise here, since no instance satisfies C1);
(b) DECIDE disagrees with the from-definitions evaluation on
any instance in the §5 agreement battery (the detector dies);
(c) the §5.5 precondition fails — the records do not
separate, so no derived threshold exists, and the claim that
dies is "emergence is decidable from this interaction
matrix". The endgame (§6) is reported at its evidence level:
what this rung establishes concretely for I1/I2/I3, and what
remains proposed, with §6.4's falsification test (standalone
vs derived agreement on shared instances) applied to exactly
the instances where both sides exist.
