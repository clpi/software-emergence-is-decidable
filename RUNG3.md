# Rung 3 — composition: groups as actors (2026-11-21)

Spec: ~/workspace/research/emergence-ladder-spec-2026-11-21.md
(sections 1-2), also clpi/software-emergence-is-decidable at
192df382, SPEC.md. Registration (written before any battery run,
with amendment v2 appended before any battery run):
~/workspace/emergence-rung3-scratch/registration.md. Code:
~/workspace/emergence-rung3-scratch/{harness3.py, check3.py,
view3.py}; results: ~/workspace/emergence-rung3-scratch/results/.
Rung-2 record: ~/workspace/research/emergence-rung2-2026-11-21.md
— its "Rung 3 inherits" list was binding on this rung: protocol
v3 is the member protocol, the DET/TAL interfaces are reused,
and the section 1.9 margin question was decided in this rung's
registration, below.

## Headline: NO WIN in both families — the rung-3 claim is falsified as registered

Under the registered decision rule (per-arm margin, below), the
joint system fails to beat at least one control arm by that
arm's spread in each family, so spec section 2.7's falsification
condition is met in both batteries and the claim is dead as
registered. The narrower facts, which are also the result: the
joint system has the highest mean capability of all eight arms
in both families; it beats the frozen-partition system (Cap2),
the isolated arm, and the shuffled arm by more than those arms'
spreads in both families; it does not beat level-1 alone (flat)
by flat's spread in either family (+0.0163 against a 0.0306 bar
in field3; +0.0336 against a 0.0583 bar in region3). Second-order
interaction at this scale and horizon adds a small positive
amount over level-1 alone — less than replicate variability.

## Registration (summary; the scratch registration governs)

- Families: field3 = rung 2's field reconstruction, unchanged
  (N = 256 ring, T = 32, split seed 2026112199); region3 = region
  classification (6 seed-drawn segments, labels = segment index
  mod 3, observations correct with probability 0.7, mode
  estimates, accuracy scoring, split seed 2026112299). Both
  satisfy section 2.7's minimums (>= 64 actors, >= 3 formation
  ticks, k = 8).
- Member protocol: rung 2's v3 (origin authority + evidence gate
  >= 3 reports) at both levels; level-2 messages are the 336-bit
  bundle plus a 16-bit tag, counted in full.
- Formation: declared alternative rule (spec 2.1 permits):
  provenance reach read off the level-1 fold (exact by
  construction for this protocol — a value about a site
  originates only at that site and is copied verbatim); ring
  neighbours are linked iff both directions of first reach are
  established by tick kappa; blocks are the connected components
  of the linked ring adjacencies. Formation ticks 8, 16, 24.
  Because first-reach ticks are prefix facts, the partition is
  the same at all three ticks in every run (checked, not
  assumed: the checker recomputes all three and they agree).
- Amendment v2 (appended before any battery run, following
  rung 2's amendment pattern): kappa 2 -> 1. Evidence: a
  debugging run at the registered scale and seed measured the
  adjacency first-reach distribution — at kappa = 2 exactly one
  adjacency is cut, one cut does not split a ring, and the joint
  arm would have been mechanically identical to flat (a vacuous
  battery). At kappa = 1 the same distribution gives 19 cuts.
  The amendment also specified the view subfamily for views
  with more than 11 axes (below). Nothing else changed.
- Arms (8): joint, flat (Cap1), frozen-partition (Cap2),
  isolated, frozen, shuffled, freeze-1, freeze-2 — spec 2.4 and
  1.7 as registered. The frozen stream's generator is a
  live-noisy joint run at seed + 777000 (registered deviation
  from rung 2's clean generator: under this formation rule a
  clean run forms a single block, so a clean generator's
  level-2 stream would be all filler).
- Budgets: one invocation schedule for every arm — steps =
  14336 and bits sent = 9830400 for every run of both families
  (checker-verified per run); ticks = 32; bits delivered and
  store reported per arm (table below). The section 2.3
  exchange is realized as filler steps at the same ticks (the
  rung-2 reading), not as a horizon extension for flat;
  registered with its reason.
- Margin decision (registered, applied uniformly): PER-ARM —
  joint wins iff Cap(joint) > Cap(X) + spread(X) for every
  control arm X. Reason, from rung-2 evidence: the global
  delta imported the frozen arm's cross-seed field-difficulty
  spread into every comparison (in rung 2 it put the isolated
  bar above the score ceiling). Per-arm keeps each comparison's
  margin derived from that arm's own variability and does not
  lower the binding bar (the frozen arm's own threshold is
  unchanged). The section 1.9 global-delta decision is printed
  alongside; it agrees here (NO WIN under both rules, both
  families).

## Results — field3 (raw replicates; Cap = mean held-out score)

| arm | replicates | mean | spread |
|---|---|---|---|
| joint | 0.7681 0.7723 0.7737 0.7874 0.7690 0.7947 0.7952 0.7778 | 0.7798 | 0.0271 |
| flat | 0.7804 0.7510 0.7613 0.7686 0.7498 0.7661 0.7560 0.7749 | 0.7635 | 0.0306 |
| frozen-partition | 0.7133 0.7106 0.7132 0.7081 0.7025 0.7119 0.7130 0.7105 | 0.7104 | 0.0109 |
| freeze-2 | 0.7336 0.7237 0.7411 0.7263 0.7240 0.7665 0.7431 0.7469 | 0.7381 | 0.0427 |
| isolated | 0.6421 0.6230 0.6440 0.6369 0.6202 0.6617 0.6260 0.6487 | 0.6378 | 0.0415 |
| shuffled | 0.6396 0.6350 0.6492 0.6258 0.6225 0.6636 0.6345 0.6488 | 0.6399 | 0.0411 |
| freeze-1 | 0.4310 0.6953 0.4872 0.4993 0.6321 0.4484 0.4898 0.5639 | 0.5309 | 0.2642 |
| frozen | 0.3959 0.6766 0.4689 0.4637 0.6216 0.4373 0.4611 0.5668 | 0.5115 | 0.2808 |

Decision vector (registered per-arm rule; bar = the arm's own
spread): vs flat +0.0163 vs 0.0306 FAILS; vs freeze-1 +0.2489
vs 0.2642 FAILS; vs freeze-2 +0.0416 vs 0.0427 FAILS (by
0.0011); vs frozen +0.2683 vs 0.2808 FAILS; vs frozen-partition
+0.0694 vs 0.0109 beats; vs isolated +0.1420 vs 0.0415 beats;
vs shuffled +0.1399 vs 0.0411 beats. Global delta (section
1.9) = 0.2808; decision under it: NO WIN. Registered decision:
**NO WIN.**

## Results — region3 (raw replicates)

| arm | replicates | mean | spread |
|---|---|---|---|
| joint | 0.5687 0.5576 0.5797 0.5913 0.6451 0.6166 0.6289 0.6133 | 0.6001 | 0.0874 |
| flat | 0.5343 0.5667 0.5427 0.5732 0.5926 0.5699 0.5680 0.5848 | 0.5665 | 0.0583 |
| freeze-1 | 0.5609 0.5440 0.5764 0.5855 0.6095 0.5408 0.5829 0.5544 | 0.5693 | 0.0687 |
| frozen | 0.5531 0.5376 0.5751 0.5758 0.5972 0.5246 0.5758 0.5473 | 0.5608 | 0.0725 |
| freeze-2 | 0.4547 0.4799 0.5123 0.5006 0.5589 0.5149 0.5356 0.5363 | 0.5117 | 0.1043 |
| frozen-partition | 0.4747 0.5000 0.4767 0.4339 0.4929 0.4521 0.4780 0.5052 | 0.4767 | 0.0712 |
| isolated | 0.3446 0.3258 0.3407 0.3478 0.3497 0.3601 0.3076 0.3627 | 0.3424 | 0.0551 |
| shuffled | 0.3400 0.3297 0.3387 0.3472 0.3478 0.3633 0.3044 0.3627 | 0.3417 | 0.0589 |

Decision vector: vs flat +0.0336 vs 0.0583 FAILS; vs freeze-1
+0.0308 vs 0.0687 FAILS; vs freeze-2 +0.0885 vs 0.1043 FAILS;
vs frozen +0.0393 vs 0.0725 FAILS; vs frozen-partition +0.1235
vs 0.0712 beats; vs isolated +0.2578 vs 0.0551 beats; vs
shuffled +0.2584 vs 0.0589 beats. Global delta = 0.1043;
decision under it: NO WIN. Registered decision: **NO WIN.**

## Budgets per arm (B, reported per section 2.5)

Steps and bits sent are identical for every run (14336;
9830400) — see Registration. Bits delivered (min..max over
replicates) and store = log bytes (min..max):

field3: joint 8347360..8397760, 7838051..8028287; flat
4661328..4697952, 7413990..7441828; frozen-partition
4813376..4867184, 7336945..7489451; isolated 0, 6959584..6964176;
frozen 8326208..8381632, 7810986..7985546; shuffled 9830400,
7425203..7927948; freeze-1 8330640..8403152, 7791419..7962020;
freeze-2 8985696..9023664, 7728557..8057958.
region3: joint 8337296..8390064, 7445498..7700138; flat
4655952..4701312, 7187643..7197239; frozen-partition
4814992..4869488, 7163163..7312952; isolated 0, 6922176;
frozen 8305552..8371424, 7337352..7732479; shuffled 9830400,
7222043..7692296; freeze-1 8306784..8377312, 7370813..7658533;
freeze-2 8988048..9031728, 7396365..7750410.

## Views (joint replicate 1 of each family; spec 2.5 metrics)

Views of joint replicate 1 per family (view3.py over the
persisted log; components = per-block held-out means scored
from folds of the included records; hyperedges = per-tick
counterfactuals; weight = the tick's delivered count at the
view's level). Both runs' partitions have more than 11 blocks
(field3 19, region3 29), so every view is computed over the
registered subfamily (amendment v2): sensitivity and Live are
LOWER BOUNDS, labeled as such; rho below is (mu, lambda) at the
full axis set under that computation; emergent-dead is not
declared for any block (dead = not evaluable, see Ablation).
The level-1 view's window is the prefix through the next
formation tick, so its mu grows with window size as well as
with structure; the level-2 and joint views are over the
interval [t_j, t_{j+1}).

field3 (19 blocks, sizes 2..41):
| view | t8 mu / lambda | t16 mu / lambda | t24 mu / lambda |
|---|---|---|---|
| level-1 | 6523 / 19 | 9107 / 19 | 10412 / 19 |
| level-2 | 3053 / 16 | 3452 / 16 | 3509 / 14 |
| joint | 6940 / 19 | 6933 / 19 | 6983 / 19 |

region3 (29 blocks, sizes 1..42):
| view | t8 mu / lambda | t16 mu / lambda | t24 mu / lambda |
|---|---|---|---|
| level-1 | 5194 / 29 | 7407 / 29 | 9569 / 29 |
| level-2 | 3493 / 28 | 1735 / 20 | 1715 / 14 |
| joint | 6942 / 29 | 6988 / 29 | 6930 / 29 |

Full view objects (hyperedges, sensitivity, interaction
matrices, full components) are in results/field3/view3.json
and results/region3/view3.json. Machinery cross-check: the
view builder's entry fold over the full log reproduces joint
replicate 1's recorded cap with |diff| = 0.00 in both families
(bit-exact); a task-by-task comparison against the independent
checker's fold on field3 found zero differing held-out tasks.
Detector outputs only; they carry no capability claim. Two
readings, stated as observations on lower bounds: the joint
view's mu is roughly flat across formation ticks in both
families while the level-1 view's grows (window effect
included), and region3's level-2 mu falls after t8 (3493 ->
1715) — the later intervals' level-2 deliveries engage fewer
components there, consistent with freeze-2's poor region3
showing.

## Ablation (spec 2.5 load-bearing; spec 2.7's T3.8 test)

Ablation set: the blocks of the final partition of joint
replicate 1 (19 blocks in field3, sizes 2..41; 29 blocks in
region3, sizes 1..42), each isolated from tick 24 in 4 replicate
runs at seeds 2026112101..2026112104 whose noise streams match
the joint runs' exactly (the ablation logs are identical to the
joint logs before tick 24). Load-bearing bar: the family's
global delta (field3 0.2808; region3 0.1043), as registered.

Result: **zero load-bearing blocks in either family.** The
largest mean Cap drop is +0.0047 (field3 block 15, 41 members)
and +0.0045 (region3 block 24, 42 members); several blocks have
negative mean drops (isolating them slightly raises Cap). By
the final formation tick the blocks' knowledge is already
distributed across the ring, so no single block's last-8-tick
traffic carries the capability. Per-block drops are in the
ablation summaries (results/field3-abl, results/region3-abl).

T3.8 disposition: the section 2.7 refutation needs a group
actor that is provably emergent-dead AND load-bearing. No
block is load-bearing, so the refutation does not trigger on
the capability side. On the structure side, the level-2 views
of replicate 1 have 19 (field3) and 29 (region3) axes — above
the registered exactness cap of 11 — so emergent-dead is not
provable for any block under the registered rule (deadness is
never declared from a restricted configuration family;
amendment v2 stated this consequence in advance). The
antecedent is therefore reported as NOT EVALUABLE at these
block counts, T3.8 is neither refuted nor confirmed, and it
stands as PREMISE (below). The evaluability gap is a G2-class
cost fact, handed to rung 4.

## Lean (EmergenceRung3.lean, Lean 4.19.0, core-only, no sorry)

Cold compile clean; axiom audit: every theorem depends only on
propext and/or Quot.sound (both inside the standard set);
no sorryAx anywhere. Dispositions of the eight obligations:

- T3.1 PROVED: G is defined from the level-1 projection of the
  cut (g_reads_l1_only), is deterministic in the cut (g_det),
  and first-reach facts are stable under appends
  (firstReach_append) — the registered partition cannot be
  changed by later records.
- T3.2 PROVED: fold append composition and restart exactness
  (restart_exact), and the state at a formation tick is a
  function of the log prefix alone (state_of_prefix). The
  empirical half is the checker's 48/48 restart agreement per
  battery (below).
- T3.3 PROVED: the freeze transformation preserves length
  (freeze_length), leaves a log unchanged when no record is in
  the frozen class (freeze_id_on), and maps a log pointwise to
  its frozen sources when every record is in the class
  (freeze_replaces) — together with the pointwise definition,
  exactly the records in the class change.
- T3.4 PROVED: over a partition of the actor list, the summed
  member-step count of one group step over all blocks is
  exactly N (t34_steps, via List.length_flatten) — the section
  2.3 exchange is exact.
- T3.5 PROVED IN CONDITIONAL FORM: if the joint view's engaged
  family contains a level view's engaged family as a sublist
  with weights carried, then that level's mu <= mu(joint)
  (t35_mu_mono, via sum_le_of_sublist); applied to both levels
  this gives mu(joint) >= max(mu(level 1), mu(level 2)) under
  the antecedent. The engaged-inclusion antecedent is
  discharged by the view construction, not in Lean; the
  monotonicity core is proved.
- T3.6 PROVED: the joint tally is the componentwise sum of the
  two filtered tallies for any record predicate, in particular
  level (tally_filter_pair) — at every cut, since every prefix
  is a list. Empirical half: the checker's pair-composition
  agreement on every run (below).
- T3.7 PROVED: counts of any predicate are preserved under a
  permutation of a tick's records (countP_perm) and under a
  readdressing that preserves the predicate
  (countP_map_readdress); composed in t37_shuffle_marginals.
- T3.8 PREMISE (unchanged): stated in the file as a definition
  (T38Premise), not proved, not an axiom, depended on by no
  theorem. Tested by the battery's ablation as far as the
  registered instruments reach (above); discharged, if ever,
  only by rung 6's T6.1.

## Verification (independent checker, check3.py)

Per battery, the checker re-implements generation, the fold,
the tally, and formation from the registration and verifies:
replay to the recorded final hash; restart exactness from each
formation-tick prefix (joint and ablation runs); DET = TAL at
every registered append cut for the combined tally and each
level's tally; the tally pair composition (combined = level-1
+ level-2 componentwise — T3.6's empirical half); budget shape
(steps, bits sent, record count identical for every arm); and
formation agreement (partitions recomputed from each log's
level-1 prefixes equal the recorded partitions).

- field3 (72 runs: 64 battery + 8 generator): append cuts
  504/504 agree, restarts 48/48, pair compositions 72/72,
  failures: none.
- region3 (72 runs): append cuts 504/504, restarts 48/48,
  pair compositions 72/72, failures: none.
- field3-abl (76 runs): append cuts 532/532, restarts 228/228,
  pair compositions 76/76, failures: none.
- region3-abl (116 runs): append cuts 812/812, restarts
  348/348, pair compositions 116/116, failures: none.

Totals: 336 runs, every one replay-exact; 2352/2352 append-cut
agreements; 672/672 restart agreements; 336/336 pair
compositions; formation agreement and budget shape on every
run. Full per-run results in each battery's checks.json.

## Spec gap G2 — state after rung 3

G2 remains OPEN. Rung 3 introduced no sampled quantity:
formation uses provenance reach (exact by construction, not a
scan), and view hyperedges use tick-unit counterfactual folds
(exact at the tick unit, rung 2's declared unit). Sensitivity
and Live in views with more than 11 axes are computed over the
registered subfamily and are labeled lower bounds wherever
reported; they support no theorem and no deadness declaration.
The open remainder is the same as rung 2 left: per-message
dependence scans at scale, a sublinear exact scan, and — new
in this rung — exact sensitivity/deadness at block counts
above the subset-enumeration cap. Owner: rung 4 inherits;
rung 6's certificate work will need it closed or bounded.

## Verified vs claimed

Verified (executed, at the pins and paths named above):
- Both batteries ran exactly as registered (registration +
  amendment v2, both written before the runs they governed);
  budgets componentwise equal on the registered budget of
  record for all 128 battery runs and 16 generator runs (64
  and 8 per family).
- The decision: NO WIN in both families under the registered
  per-arm rule and under section 1.9's global delta. The rung-3
  claim (spec 2.2) is falsified as registered.
- The independent checker results listed above.
- Zero load-bearing blocks in both families' ablations.
- The Lean dispositions listed above, at a cold compile with
  the stated axiom audit.

Claimed (measured means, not decision-grade beyond the
registered rule):
- Joint's mean exceeds every other arm's mean in both
  families, and exceeds Cap2/isolated/shuffled by more than
  those arms' spreads. The composition's advantage over
  level-1 alone is positive in mean (+0.016 field, +0.034
  region) and smaller than replicate spread — a measured
  tendency, not a win under any rule registered or printed.
- Freeze-2's near-tie with joint in field3 (+0.0416 vs bar
  0.0427) says live level-2 addressing added little there;
  in region3 shuffled level-2 is actively harmful (freeze-2
  mean 0.5117 vs flat 0.5665). Both are single-battery facts.

Not claimed: any emergent intelligence; any capability win;
T3.8 in either direction; exact deadness at these block
counts; anything about the fuzzing or NPC domains (no battery
has run in either).

## Rung 4 inherits

1. The falsified claim and its exact decision vectors. Rung 4's
   transfer question starts from a composition whose measured
   advantage over level-1 alone is small and not
   decision-grade; transfer claims must not assume a composition
   gain that rung 3 did not establish.
2. The margin problem, again: per-arm delta fixed the
   cross-arm import rung 2 suffered, but the replay arms
   (frozen, freeze-1) still carry spreads of 0.26-0.28 in
   field3, dominated by generator/field luck across seeds, and
   those bars alone decided four comparisons. Whether
   replicates should hold the task draw fixed across seeds, or
   pair arms per seed, is a registration decision for the next
   rung that registers a battery — it must be made there, in
   advance, not retrofitted here.
3. Formation: the kappa = 1 rule and the amendment pattern;
   block counts per run 18-35; partitions provably stable after
   t1 under this rule (first-reach is a prefix fact). If rung 4
   wants partitions that evolve, it needs a rule whose inputs
   are not prefix-monotone — a design decision, registered.
4. T3.8's evaluability: exact deadness needs views with at
   most 11 axes or a cheaper exact sensitivity method (G2).
   Until then the premise can be neither refuted nor confirmed
   by this instrument at realistic block counts.
5. The ablation shape: single blocks are not load-bearing late
   (knowledge already distributed). Load-bearing structure, if
   rung 4 looks for it, is earlier in the run or collective
   (sets of blocks), not single late blocks.
6. From rung 2, still open and now inherited twice: the v3
   evidence gate's constant (3) has never had a sensitivity
   measurement; corruption remains the binding noise class.
7. The level-2 addressing fact: in region3, shuffled level-2
   addressing is worse than no level-2 (freeze-2 below flat);
   in field3 it is nearly free. Any transfer of interaction
   structure (rung 4's object) is family-dependent in sign —
   measure per family.

## Premise audit addendum (2026-11-21)

The derivation-graph audit named at rung 6 has been executed;
its record is ~/workspace/research/emergence-premise-audit-2026-11-21.md.
Outcome for this rung's premise list: **T3.8 stays PREMISE.**
Its discharge route runs through rung 6's soundness theorem,
whose threshold derivation failed because the rung 2–5 records
do not separate, and its antecedent remains NOT EVALUABLE at
this rung's block counts. The audit's section 4 names exactly
what would discharge it. No other line of this record changes,
and the falsified claim above stands as recorded.
