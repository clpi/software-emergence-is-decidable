# Emergence rung 5 — compounding over time: NO COMPOUNDING, the claim is falsified as registered

Executed 2026-11-21 under the ladder spec
(~/workspace/research/emergence-ladder-spec-2026-11-21.md, §1
and §4), building on the rung-2/3/4 machinery. Registration
written before any battery run, no amendments:
~/workspace/emergence-rung5-scratch/registration.md (landed in
the repo as rung5/registration.md).

**Headline: capability does not compound over time in the
registered sense. The claim is falsified as registered.**

- **Field fails the horizon conjunct under both decision
  rules.** The live arm's mean horizon gain is 0.135138,
  against the registered margin δ = 0.333693 and the
  rung-2-style global margin δ_g = 0.384999. Both margins are
  set by the frozen control: its per-replicate gains run from
  −0.220750 to +0.112943 (spread 0.333693) and its
  final-checkpoint capabilities spread 0.384999. The live
  gain is real but smaller than the control's own variability,
  so the strict-gain conjunct fails.
- **Region passes the gain conjunct under both rules** (live
  mean gain 0.246762 against δ = 0.082254 and δ_g = 0.083549),
  **but its monotonicity conjunct is vacuous and its gain is
  not attributable to live accumulation.** The T5.6 antecedent
  fails at all 28 region checkpoint pairs (every pair has at
  least one removed hyperedge), so no pair is in scope and the
  non-decreasing conjunct quantifies over the empty set. And
  the frozen control satisfies both conjuncts in region — its
  mean gain is 0.253562, above δ and above the live arm's own
  gain — so under §4.3 the region gain cannot be credited to
  the live history: a foreign, clean, replayed history
  compounds there just as much.
- The claim was registered for both families; field's failure
  alone kills it. **NO COMPOUNDING, under the registered rule
  and under the global rule alike.**

Below the headline, labeled as the narrower facts they are:
the raw mean curves rise steeply to tick 64 in both families
and dip at the final checkpoint (field −0.004644, region
−0.004048 on the means; all 8 field replicates dip). Those
pairs are out of scope, so the dip is not the falsifier — the
margin is. Had the scope been all pairs, monotonicity would
also have failed in both families (the dips exceed ε by four
orders of magnitude). The monotonicity conjunct as registered
was tested on exactly one in-scope pair across both families
(field (1, 2), which rises); everywhere else the antecedent
failed first. That near-empty scope is itself a measured
result, and it is rung 6's largest inheritance (below).

## Status at a glance

| piece | state |
|---|---|
| claim (both families, registered rule) | FALSIFIED — field horizon conjunct fails |
| claim under the global rule | FALSIFIED — same conjunct, larger margin |
| field monotonicity (in scope) | holds on the single in-scope pair (1, 2) |
| region monotonicity (in scope) | vacuous — zero in-scope pairs |
| attribution (§4.3) | region gain matched by the frozen control |
| restart / replay / DET = TAL | verified 512 / 80 / 640, zero failures |
| T5.1, T5.2, T5.3, T5.5 | PROVED in Lean |
| T5.4 | PREMISE by construction review (spec §4.4's route) |
| T5.6 | PREMISE — antecedent and consequent measured per pair |

## Registration (summary; the full text governs)

One append-only log per replicate: N = 256 actors on a ring,
protocol v3 (the evidence gate at ≥ 3 reports), the rung-2/3/4
families and splits (field split 2026112199, region split
2026112299), noise (0.15 drop, 0.15 corrupt, 0.10 misdeliver),
8 seeds 2026112101..2026112108. Horizon T = 128 ticks;
checkpoints at ticks 1, 2, 4, 8, 16, 32, 64, 128 — cuts of the
one log (512 to 65,536 records, a factor of 128, about 2.11
orders of magnitude). Arms: live, isolated, frozen (replay of
a live-clean generator at seed + 777000, the rung-2 form),
shuffled. Capability at a cut is the held-out mean score of
that replicate's derived state at the cut, scored with no
further interaction; the curve is the mean over the 8 seeds.

Tolerance from the scorer's granularity: ε_field = 1/1488960
≈ 6.716097e-07, ε_region = 1/12352 ≈ 8.095855e-05. Registered
margin: δ = the maximum over the control arms of the spread of
per-replicate horizon gains (final minus first checkpoint);
the rung-2-style global margin δ_g (control spreads of the
final-checkpoint capability) is printed alongside and does not
govern. Scope: a pair (i, j) is in scope iff, on replicate 1's
live cut views, the appended records remove no hyperedge
(identity = (tick, component set)) and the live-component set
only grows. Grain G = 8 as in rungs 2–4, with the rung-4
saturation finding registered against it. G2 stays OPEN; no
sampled quantity is used anywhere.

## The curves (raw replicates; checkpoints 1, 2, 4, 8, 16, 32, 64, 128)

### Field

live, per replicate:
- rep1: 0.65689, 0.66547, 0.67246, 0.70710, 0.73167, 0.75089, 0.78726, 0.78264
- rep2: 0.64181, 0.64783, 0.66406, 0.68476, 0.72247, 0.76849, 0.80313, 0.80177
- rep3: 0.65308, 0.65802, 0.67043, 0.70607, 0.73499, 0.77011, 0.79124, 0.78788
- rep4: 0.64329, 0.65141, 0.65890, 0.69558, 0.72096, 0.75664, 0.77827, 0.77046
- rep5: 0.63851, 0.63967, 0.65001, 0.68957, 0.71290, 0.75577, 0.80333, 0.79842
- rep6: 0.67121, 0.67942, 0.69271, 0.71985, 0.74831, 0.77426, 0.80815, 0.80437
- rep7: 0.63958, 0.64636, 0.65701, 0.68820, 0.70610, 0.74149, 0.78322, 0.78017
- rep8: 0.66220, 0.66932, 0.68400, 0.70564, 0.72742, 0.75510, 0.77023, 0.76196

live mean curve: 0.650822, 0.657188, 0.668696, 0.699594,
0.725603, 0.759093, 0.790604, 0.785960. Per-checkpoint spreads:
0.032699, 0.039743, 0.042704, 0.035085, 0.042215, 0.032769,
0.037922, 0.042408. Live gains per replicate: 0.125752,
0.159967, 0.134806, 0.127165, 0.159908, 0.133156, 0.140592,
0.099758 (mean 0.135138).

frozen mean curve: 0.6205, 0.6205, 0.6040, 0.6040, 0.5770,
0.5508, 0.5324, 0.5324 (the mean falls over the horizon).
Frozen gains per replicate: −0.220750, +0.112943, −0.149210,
−0.140700, +0.056775, −0.192220, −0.137621, −0.033994 (mean
−0.088097, spread 0.333693). Isolated is flat per replicate
(0.62020..0.66172 by seed, gain exactly 0). Shuffled mean
curve rises slightly, 0.6228 → 0.6399; gains 0.002138..
0.026010 (mean 0.017045).

### Region

live, per replicate:
- rep1: 0.37889, 0.38277, 0.40674, 0.43329, 0.47733, 0.53756, 0.58808, 0.58031
- rep2: 0.36982, 0.37565, 0.39573, 0.42940, 0.47733, 0.56671, 0.63018, 0.63018
- rep3: 0.37241, 0.37953, 0.39637, 0.43847, 0.47085, 0.54469, 0.60492, 0.60039
- rep4: 0.38018, 0.38925, 0.41062, 0.43847, 0.49093, 0.55894, 0.62435, 0.61917
- rep5: 0.38212, 0.39896, 0.42811, 0.46956, 0.51490, 0.60363, 0.67358, 0.66516
- rep6: 0.38666, 0.40091, 0.41969, 0.45661, 0.49352, 0.55829, 0.61658, 0.61399
- rep7: 0.35104, 0.35816, 0.38083, 0.42681, 0.48640, 0.57060, 0.65868, 0.65674
- rep8: 0.38860, 0.40285, 0.42228, 0.46308, 0.50518, 0.57124, 0.61982, 0.61788

live mean curve: 0.376214, 0.386010, 0.407545, 0.444462,
0.489556, 0.563957, 0.627024, 0.622976. Per-checkpoint spreads:
0.037565, 0.044689, 0.047280, 0.042746, 0.044041, 0.066062,
0.085492, 0.084845. Live gains per replicate: 0.201425,
0.260363, 0.227979, 0.238990, 0.283031, 0.227332, 0.305699,
0.229275 (mean 0.246762).

frozen mean curve: 0.3954, 0.3954, 0.4431, 0.4431, 0.5172,
0.5951, 0.6490, 0.6490 — at or above the live curve at every
checkpoint. Frozen gains per replicate: 0.226684, 0.261658,
0.264896, 0.270078, 0.281088, 0.231218, 0.287565, 0.205311
(mean 0.253562, spread 0.082254). Isolated is flat per
replicate (0.30764..0.36269 by seed, gain exactly 0).
Shuffled is flat to slightly falling (mean gain −0.002024).

A shape fact, checker-verified in the logs: the frozen curves
are exactly constant on the checkpoint pairs (1, 2), (4, 8),
and (64, 128) in every replicate of both families, and the
generator runs show the same plateaus. Mechanism for the
early plateaus, measured in the generator logs: bundles at
ticks 0, 1, 2 carry exactly one non-null component (the
sender's own site; the mean over bundles is 1.0), because the
v3 gate relays a non-own value only at ≥ 3 reports and no
site reaches 3 reports before tick 3 (at tick 3 the mean is
3.0). The first two ticks therefore append duplicates of the
tick-0 values, leaving every median and mode — and the state
hash — unchanged; the generator's and the frozen fold's
hashes are equal at cuts (1, 2) and (4, 8). At (64, 128) the
capabilities are equal while the hashes differ. In a clean
run every value in flight about a site is that site's own
observation or a median/mode of such values, so a clean state
changes only through first arrivals, which the gate and the
rotating relay offsets deliver in waves.

## Budgets and costs

Componentwise-equal per run, all 80 runs (64 battery + 16
generator), checker-verified: steps 32,768; bits sent
22,020,096; records 65,536 (512 per tick). Bits delivered
(8 replicates, per family): field — live 149,772,000, frozen
176,160,768, shuffled 176,160,768, isolated 0; region — live
149,727,984, frozen 176,160,768, shuffled 176,160,768,
isolated 0. Log store per run 15.4–16.7 MB. Counted
separately: checkpoint view construction (16 views; walls
1.3–16.0 s by cut, the t = 128 field view the most expensive
at 16.0 s) and the checker's folds.

## Scope and the T5.6 measurements

Live-component inclusion held at all 28 pairs in both
families: the live set is all 8 components at every cut
(λ = 8 throughout), so the antecedent's second half never
binds. The first half — no hyperedge removed — failed almost
everywhere. Removed-edge counts (rows: earlier cut; entries:
removed count to each later cut):

Field (in scope: (1, 2) only):
- from 1: 0, 1, 1, 1, 1, 1, 1 (to 2, 4, 8, 16, 32, 64, 128)
- from 2: 1, 2, 2, 2, 2, 2
- from 4: 4, 4, 4, 4, 4
- from 8: 8, 8, 8, 8
- from 16: 16, 16, 16
- from 32: 31, 27
- from 64: 63

Region (in scope: none):
- from 1: 1, 1, 1, 1, 1, 1, 1
- from 2: 2, 2, 2, 2, 2, 2
- from 4: 4, 4, 4, 4, 4
- from 8: 8, 8, 8, 8
- from 16: 10, 10, 10
- from 32: 21, 17
- from 64: 46

Why edges are removed (measured structure, stated as the
mechanism it is): a tick's hyperedge is a counterfactual
against the whole cut fold — the component scores with that
tick's values removed from the fold of the entire prefix.
Appending records changes the fold, so an earlier tick's
counterfactual edge changes identity or vanishes. The counts
grow with the earlier cut's tick count, as that mechanism
predicts. The view is a function of the cut (§4.1's own
warning), and at this grain its per-tick edges are not stable
under extension.

The measure mu at the cuts (replicate 1, live): field 428,
862, 1737, 3482, 6943, 9942, 22122, 46527 — non-decreasing at
every pair (the consequent holds on all 28 field pairs,
in-scope or not). Region: 428, 874, 1764, 2668, 3467, 6055,
14381, 2616 — the consequent fails on the four pairs into
t = 128 from t = 8, 16, 32, 64; all four are out of scope
(their antecedents fail), so T5.6 is not refuted on an
in-scope pair; its antecedent simply almost never holds in
this instrument. Non-empty edges per view grow over the
horizon (field 1, 2, 4, 8, 16, 26, 61, 117 of 128 ticks;
region 1, 2, 4, 8, 10, 17, 46, 55). Dead groups: all 8 at
every field cut; in region, all 8 from t = 2 on (at t = 1,
groups 1 and 2 are not dead). The rung-4 grain saturation
persists: the sensitivity structure is saturated at every
cut, and only mu moves.

## The decision

Registered rule, per family:

- Field: monotonicity over the in-scope pairs holds (the one
  in-scope pair (1, 2) rises; worst in-scope drop −0.006366).
  Horizon: gain 0.135138 against δ = 0.333693 (frozen gain
  spread; shuffled 0.023872, isolated 0) — FAILS. Under the
  global rule: δ_g = 0.384999 (frozen final-cap spread;
  isolated 0.041522, shuffled 0.040023) — FAILS.
- Region: monotonicity vacuous (no in-scope pairs). Horizon:
  gain 0.246762 against δ = 0.082254 (frozen gain spread;
  shuffled 0.023316, isolated 0) — passes; under the global
  rule δ_g = 0.083549 (frozen final-cap spread; isolated and
  shuffled 0.055052) — passes.
- Attribution (§4.3): in region the frozen arm satisfies both
  conjuncts (gain 0.253562 > δ, monotonicity over the same
  empty scope), so region's gain is not attributable to live
  accumulation. In field no control satisfies both (frozen
  mean gain −0.088097; shuffled 0.017045; isolated 0).

Rung decision: **NO COMPOUNDING in both families' joint
reading — the claim is dead as registered, under the
registered rule and under the global rule.**

Mechanism readings (labeled as readings, each consistent with
the printed vectors): in field, a foreign stream's values are
seed-random phases against the run's own field, so frozen
accumulation poisons some seeds and helps others — its gain
variance, not any live effect, sets the margin the live gain
had to beat. In region, layouts across seeds share the
segment process (six segments, labels cycling 0, 1, 2), so a
foreign layout's values are predictive of the run's own
layout; the frozen control there does not isolate "history"
from "the family's shared structure", and it compounds
exactly as much as live interaction does. The controls
isolate what they isolate; the claim as registered is dead
under either reading.

## Verification (independent checker, separate code path)

check5.py imports nothing from any harness and recomputes
from the persisted artifacts. Zero failures:

- replay of every persisted log reproduces the recorded
  final hash and capability: 80/80 runs;
- checkpoint cut folds reproduce the recorded cut hash and
  capability at every cut: 640/640;
- append-cut equality (DET = TAL): a from-scratch batch tally
  of each prefix equals the harness's online tally snapshot
  at that cut: 640/640;
- restarts: folding a cut's prefix and continuing with the
  suffix reproduces the final hash, at every checkpoint of
  every battery run: 512/512;
- budget shapes (steps, bits sent, 512 records per tick):
  80/80;
- replicate 1's live cut views recomputed from the persisted
  prefixes agree (mu, live set, edges, components, dead):
  16/16;
- evaluation in reverse checkpoint order reproduces
  replicate 1's live cut capabilities: 16/16;
- each frozen log is its generator's log, record for record:
  16/16;
- the decision record (curves, spreads, gains, both margins,
  pair scope, both decisions) recomputed independently:
  2/2 families agree.

## Theorem obligations (Lean 4.19.0, core only)

EmergenceRung5.lean, cold compile clean, no sorry; every
proved theorem's axioms are within {propext, Quot.sound}:

- T5.1 restart exactness — PROVED (restart_exact).
- T5.2 replay exactness — PROVED (the trace of the
  uninterrupted run is exactly the set of prefix folds:
  trace_in, trace_covers, replay_exact).
- T5.3 tally at every cut — PROVED (tally_acc, tally_cut:
  the incremental tally equals the from-scratch batch tally
  on every prefix).
- T5.4 no forgetting — PREMISE by construction review, the
  route §4.4 names before the endgame. Review, labeled as
  review and not proof: every derived state in the rung-5
  harness is the fold of the full cut (the functionality
  content proved inside T5.1/T5.2), and the harness contains
  no reweight records and no other influence-reduction route
  — influence is never reduced at all in this system. Stated
  in Lean as a premise definition depended on by nothing.
- T5.5 curve well-definedness — PROVED (read_assign,
  eval_order_free: an evaluation pass assigns each visited
  checkpoint the evaluation at that checkpoint, in any
  visit order). Empirical half: the checker's reverse-order
  evaluations, 16/16.
- T5.6 monotonicity under accumulation — PREMISE until rung
  6, not claimed. Stated in Lean as a premise definition
  depended on by nothing. The battery measured its
  antecedent (near-vacuous here, above) and its consequent
  per pair (holds on all field pairs; fails on four region
  pairs, all out of scope).

## Verified vs claimed

Verified: the constructional core, a fourth time — restart,
replay, append-cut tally equality, and budget equality at
the 128-tick horizon, all against an independent checker;
four of the six theorem obligations proved; the exact
capability curves of all four arms in both families; the
T5.6 antecedent and consequent measured per pair.

Claimed and falsified: compounding over time, as registered
— dead on field's horizon margin under both rules, and in
region unattributable to live accumulation with a vacuous
monotonicity scope.

Not claimed: that capability fails to grow — it grows, in
both families, steeply to tick 64. The registered claim was
stronger (monotone in scope and a strict horizon gain beyond
the controls' own spread, attributable to the live history),
and the stronger claim is what died.

## Rung 6 inherits

1. The falsified compounding claim with its exact vectors
   (above). It stands until a same-contract re-measure at a
   current pin says otherwise.
2. T5.6's antecedent is near-vacuous in this instrument:
   hyperedge removal at 55 of 56 checkpoint pairs across
   both families (field 27 of 28, region 28 of 28); the only
   in-scope pair in the rung is field (1, 2). Root cause,
   measured: per-tick hyperedges are counterfactuals against
   the whole cut fold, so appending rewrites them. The
   certificate must either adopt an extension-stable edge
   definition (edges fixed at the tick that creates them,
   computed against that tick's own prefix) or carry the
   near-empty scope honestly. Under an extension-stable
   definition, region's four mu-dropping pairs into t = 128
   are the consequent's first retest.
3. The attribution counterexample: in region, any same-family
   history compounds as much as the live one (frozen gain
   0.253562 ≥ live 0.246762; frozen final mean 0.6490 above
   live 0.6230). A rung-6 statement about accumulation must
   say what the history is of, not merely that it
   accumulated; the frozen arm is the standing counterexample
   to the stronger reading.
4. The margin warning: in field, δ measured the frozen
   control's gain variance (−0.2208..+0.1129), not a live
   effect scale. Decision quantities in rung 6 inherit this:
   a spread-based margin over a control whose treatment is
   seed-luck can exceed any honest live gain.
5. Premise debt, updated: T3.8 and T4.5 (from rungs 3 and 4),
   T5.6 (this rung), and T5.4 by construction review — its
   discharge route is the §6.3 derivation-graph audit at the
   endgame. Four premise obligations now stand in rung 6's
   debt.
6. The compounding infrastructure, verified a fourth time:
   80/80 replay, 640/640 cut folds, 640/640 DET = TAL,
   512/512 restarts, at a horizon 4× rung 4's log length.
7. Grain saturation persists at G = 8: the live set is all
   8 components at every cut in both families, the dead set
   is all groups (region t = 1 excepted for two groups), and
   the sensitivity structure never moves; only mu moves. A
   certificate that needs sensitivity structure must change
   grain or component definition by registration, as rung 4
   already inherited and rung 5 confirms.
8. The final-checkpoint dip: the live mean curves dip at
   t = 128 in both families (all 8 field replicates dip),
   out of scope as registered. A retest that puts the last
   pair in scope — under the repaired edge definition of
   item 2, or at a longer horizon — is a named candidate,
   not a silent hope.
9. G2 (the dependence-scan cost gap) is still OPEN, owned
   onward; rung 5 used no sampled quantity. The v3 gate
   constant (≥ 3 reports) is inherited a fourth time as the
   only measured constant; its sensitivity is still
   unmeasured.

## Premise audit addendum (2026-11-21)

The derivation-graph audit named at rung 6 has been executed;
its record is ~/workspace/research/emergence-premise-audit-2026-11-21.md.
Outcomes for this rung's premise list:

- **T5.6 is DISCHARGED — PROVED in conditional form for the
  concrete measure.** The audit's Lean proof (landed in the
  repo under the audit directory) instantiates the premise's
  abstract measure to the view's actual engaged-weight sum
  and proves the premise's own implication; cold compile
  clean under Lean 4.19.0, core only, no sorry, axioms within
  {propext, Quot.sound}. One hypothesis is named in the
  proof: duplicate-free edge families, constructional here
  (one edge per tick). The antecedent's per-pair truth is
  unchanged — it held at exactly one of 56 pairs — and the
  falsified compounding claim above stands as recorded.
- **T5.4 stays PREMISE.** The audit executed its full
  derivation-graph examination — the graph enumerated from
  the code, a static scan finding no influence-reduction
  route, and a dynamic re-run over the persisted logs
  (prefix folds and restarts 8 of 8 in each family, influence
  probe 24 of 24 in each family) — and verified the premise's
  content for this implementation. It stays a premise because
  the claim quantifies over any lawful implementation's
  derivation graph and the spec's discharge route for it is
  this audit over the endgame's derivation machinery, which
  has not landed. The audit's section 5.4 names exactly what
  would discharge it.
