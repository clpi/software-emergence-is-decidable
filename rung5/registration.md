# Rung 5 registration — compounding over time

Registered 2026-11-21, before any rung-5 battery run. Spec: the ladder
spec's shared section 1 and rung-5 section 4 (compounding over time).
This registration fixes every quantity the decision reads. The decision
rule below is fixed here and is not revised after results are seen;
amendments, if any, are appended to this file before the battery they
affect, with the measured reason, following the rung-2/3/4 pattern.

## 1. The claim under test

From spec section 4.3: on ONE append-only interaction log, the
capability curve over the registered checkpoints is non-decreasing
within the registered tolerance at every in-scope checkpoint pair, and
strictly gains over the full horizon by more than the registered
margin. Restart and replay are exact by construction; one record
mismatch fails the run. The claim is registered per family and the
rung's headline requires both families (the rung-3/4 precedent): a
split result is printed as a split and the claim is dead as
registered.

Falsified by (spec 4.5): any in-scope checkpoint pair with a drop
greater than the registered tolerance; a failed strict horizon gain;
or any restart or replay mismatch (a checker failure is a run
failure — the constructional half of the claim dies with it).

## 2. System, families, seeds

Unchanged from rungs 2–4 wherever the rung does not say otherwise:

- Actors: N = 256 on a ring. Working set: 12 tasks per actor (sites at
  offsets −6..−1 and +1..+6), 3,072 tasks per run.
- Families: field (real-valued sites, truth in [0, 900), split seed
  2026112199) and region (labels in {0, 1, 2, 3}, split seed
  2026112299). The splits fix which tasks are held out; the working
  set is fixed across the whole horizon (spec 4.3). Held-out tasks per
  replicate, computed exactly from the registered split rule: field
  1,551 of 3,072; region 1,544 of 3,072.
- Member protocol: v3, the evidence gate (a non-origin value enters an
  outgoing estimate only with at least 3 reports; a site's own value
  is always its observation). Unchanged; the gate constant 3 is the
  only constant ever measured (rungs 2, 3, 4 all inherit this), and no
  rung-5 quantity depends on re-measuring it.
- Bundles: 8 components per send (offsets −1, 0, +1 plus 5 rotating
  relay offsets reaching distance 9), 336 bits per message, 2 sends
  per actor per tick (one per direction).
- Noise (live arm): drop 0.15, corrupt 0.15, misdeliver 0.10.
- Replicates: k = 8 seeds, 2026112101..2026112108, per spec 1.9.
  No p-values anywhere.
- Random streams: one stream per run, seeded from the pair (seed,
  arm), following the rung-3/4 construction. The generator runs of
  section 4 use no stream (clean generation draws nothing).

## 3. Horizon and checkpoints

- Horizon: T = 128 ticks of live interaction on one append-only log
  per replicate. Checkpoints are cuts of that one log, never separate
  runs with separate logs.
- Checkpoint ticks: 1, 2, 4, 8, 16, 32, 64, 128 (m = 8 cuts, spec
  requires at least 6). Log lengths at the cuts: 512, 1,024, 2,048,
  4,096, 8,192, 16,384, 32,768, 65,536 records. Span from first to
  last cut: a factor of 128 in log length, about 2.11 orders of
  magnitude (spec 4.1 asks for at least two where the host allows;
  recorded here as the actual span).
- At every checkpoint the harness records, per run: the held-out
  capability of the derived state at the cut, the working-set score,
  the held-out coverage, the state hash of the cut, and the online
  tally snapshot at the cut.

## 4. Arms

The four section-1.7 arms, in their rung-2 single-level form (rung 5
is a single-level rung like rung 2; rung 3's two-level forms and its
noisy-generator deviation served its formation rule and do not
apply):

- live: the run's own sends under the registered noise.
- isolated: every send becomes a filler record (same send, nothing
  delivered). Reports never change; the curve is the flat baseline.
- frozen: the run's own sends are formed and discarded; the delivered
  records are a replay, tick by tick, of a generator run's records.
  The generator is a live-clean run (no noise) at seed + 777000 on the
  same family and horizon — the rung-2 frozen semantics. Generator
  runs are persisted and verified like battery runs.
- shuffled: the run's own sends, clean, with destinations permuted
  within each tick (per-destination counts preserved) and each
  delivered value attributed to a neighboring site.

The controls isolate history from budget and from final-state luck:
isolated has the budget and no history; frozen has a full-length
history that is not the run's own live interaction; shuffled has the
run's own values with the history's addressing destroyed. Costs are
counted separately (section 8); the claim's comparison is of curves,
not of costs.

## 5. Evaluation

Capability at a checkpoint (spec 4.1, 4.3): Cap_r(t) is the held-out
mean score of replicate r's derived state at cut t, scored with no
further interaction — the isolated evaluation of that cut. In this
system the derived state is the full reports table and scoring is a
pure function of it, so the evaluation is the fold of the cut plus
the score; the 8 evaluation replicates of section 4.3 are the 8
registered seeds, the ladder's replicate structure throughout. The
curve Cap(t) is the mean over the 8 replicates; the per-checkpoint
spread (max − min over replicates) is printed with the curve.

Evaluation-order independence (the empirical half of T5.5): the
checker evaluates replicate 1's checkpoints in reverse order and
requires the same values.

## 6. Tolerance

The tolerance is the scorer's own granularity — the smallest change
one minimal score change in one task of one replicate can make in
the curve mean:

- field: one unit of prediction error in one task of one replicate
  moves the mean by 1 / (120 · 8 · 1551); epsilon_field =
  1/1488960 ≈ 6.716097e-07.
- region: one task changing class in one replicate moves the mean
  by 1 / (8 · 1544); epsilon_region = 1/12352 ≈ 8.095855e-05.

Monotonicity conjunct, per family: for every in-scope pair i < j,
Cap(t_j) ≥ Cap(t_i) − epsilon. The full pair table (all 28 pairs per
family) is printed with in-scope flags, the antecedent measurements,
the worst drop overall, and the worst in-scope drop.

## 7. Margin and decision rule

Per-replicate horizon gain of an arm: g(arm, r) = Cap_r(t_128) −
Cap_r(t_1).

Registered margin (governing): delta = the maximum, over the three
control arms, of the spread of the per-replicate gains (max over
replicates minus min over replicates, per arm, then the maximum over
arms). Reason: section 1.9 fixes the margin as the control arms' own
spread in the quantity under claim; the quantity under claim in the
horizon conjunct is a gain, so the controls' gain spread is the
margin. It is computed per family from that family's control arms.

Horizon conjunct, per family: the live arm's mean gain exceeds
delta.

Printed alongside, not governing: the rung-2-style global rule —
delta_g = the maximum over the control arms of the spread of the
final-checkpoint capability Cap_r(t_128) — and the horizon decision
under it (live mean gain against delta_g), for comparability with
rungs 2–4. If the two rules disagree, the disagreement is printed
plainly; the registered rule governs.

Attribution (spec 4.3): each control arm is checked against the same
two conjuncts — its mean curve non-decreasing within the same epsilon
over the live claim's in-scope pairs, and its mean gain against the
same delta. A control arm satisfying both is named in the headline:
the claim's attribution to live accumulation is weakened and must be
said.

## 8. Budgets

Componentwise-equal per run, every arm and every generator run:
steps 32,768 (256 actors × 128 ticks); bits sent 22,020,096
(256 × 128 × 2 × 336); records 65,536. Bits delivered and log store
differ by arm and are reported per run, not equalized (the section
1.8 practice of rungs 2–4). Counted separately, never in the budget:
checkpoint view construction, the checker's folds, restart prefix
sizes.

## 9. Checkpoint views and scope (T5.6)

Grain: G = 8 groups of 32 actors, components are the rung-2/3/4
group components (per-group held-out score of the fold), scan unit =
tick — unchanged, for cross-rung comparability. The rung-4 saturation
finding is registered as a fact about this instrument: at grain 8
over 256 actors, rung 4 found every group emergent-dead in the
removal sense and every singleton minimal sufficient in both views.
What the views can show at this grain: the engaged weight (mu) and
the edge set accumulated over cuts, and the live-component sets —
the T5.6 antecedent and consequent are about those. What they
cannot show: sensitivity-structure change (the removal structure is
saturated at this grain). If the antecedent holds trivially at this
grain, that is printed as a fact about the instrument, not hidden.

Views are computed on replicate 1 of the live arm at every
checkpoint (the ladder's practice: views are replicate-1 objects),
from the persisted log prefixes, by both the harness and the
checker.

Scope rule (registered before any run): a checkpoint pair (i, j),
i < j, is in scope iff, on replicate 1's live cut views:
(a) the appended records between the cuts remove no hyperedge —
hyperedge identity is (tick, component set); removed = edges present
in view i and absent in view j; in scope requires removed = 0; and
(b) the live-component set of view i is a subset of that of view j.
Out-of-scope pairs are named in the record with the violated part
and the measured counts. The mu value is printed at every
checkpoint, and the T5.6 consequent (mu_j ≥ mu_i) is measured and
printed per pair. T5.6 itself stays PREMISE until rung 6 (spec 4.4);
the battery measures its antecedent and consequent, it does not
claim the theorem.

## 10. Verification (independent checker, separate code path)

The checker imports nothing from any harness and recomputes from
the persisted artifacts:

- Replay: the fold of each persisted log (80 runs: 64 battery + 16
  generator) reproduces the recorded final state hash and final
  capability.
- Checkpoint cuts: the fold of each log's prefix at each checkpoint
  reproduces the recorded checkpoint state hash and capability —
  8 cuts per run, 640 cuts.
- Append-cut equality (DET = TAL): at every checkpoint cut, a
  from-scratch batch tally of the prefix equals the harness's online
  tally snapshot at that cut — 640 cuts.
- Restart: at every checkpoint of every battery run, folding the
  prefix and then continuing with the suffix reproduces the recorded
  final hash — 8 restarts per run, 512 restarts.
- Budget shapes: per run, steps, bits sent, and record counts
  (512 records per tick) match section 8.
- Views: replicate 1's live cut views recomputed from the persisted
  prefixes agree with the harness's views (mu, the live set, the
  edge multiset) at all 16 views (8 checkpoints × 2 families).
- Decisions: the curves, spreads, gains, margins, pair tables, and
  both decision rules recomputed from the persisted summaries agree
  with the harness's decision record.

## 11. Dependence scan (G2)

G2 (the scan-cost gap) stays OPEN, owned onward, unchanged handling:
no sampled quantity is used anywhere in rung 5; the scan unit is
the tick; sensitivity at every checkpoint view is exact over all
256 configurations at grain 8. No theorem or certificate in rung 5
rests on a sampled quantity.

## 12. Theorem obligations

Attempted in Lean 4.19.0, core only, cold compile clean, no sorry,
axioms within {propext, Classical.choice, Quot.sound}:

- T5.1 restart exactness — attempted PROVED (the fold append lemma
  in restart form).
- T5.2 replay exactness — attempted PROVED (the recorded trace's
  state at every position equals the fold of the prefix: replaying
  a cut from the initial state reproduces the state the
  uninterrupted run has at that cut, at every cut).
- T5.3 tally at every cut — attempted PROVED (the incremental tally
  equals the from-scratch batch tally on every prefix).
- T5.4 no forgetting — PREMISE by construction review, the route
  spec 4.4 itself names before the endgame: the record carries the
  review (the derived state is the fold of the full cut — the
  functionality content proved inside T5.1/T5.2 — and the rung-5
  harness has no reweight records and no other influence-reduction
  route), labeled review, not proof. Stated in Lean as a premise
  definition depended on by nothing.
- T5.5 curve well-definedness — attempted PROVED (the value
  assigned to a checkpoint by an evaluation pass is the evaluation
  function at that checkpoint, whatever order the pass visits the
  checkpoints in).
- T5.6 monotonicity under accumulation — PREMISE until rung 6,
  never claimed. Stated in Lean as a premise definition depended on
  by nothing; the battery measures its antecedent (section 9) and
  its consequent per pair.

## 13. Smoke

A code-validation smoke run at reduced scale (fewer actors, the
registered horizon and checkpoint shape) may precede the batteries
to validate mechanics; it decides nothing and its numbers enter no
decision. Any amendment it motivates is appended below before the
battery it affects, with the measured reason.
