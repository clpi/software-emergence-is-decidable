# Rung 3 registration — composition (written before any rung-3 run)

Ladder spec: ~/workspace/research/emergence-ladder-spec-2026-11-21.md
(sections 1 and 2), also clpi/software-emergence-is-decidable at
192df382, SPEC.md. Rung-2 record:
~/workspace/research/emergence-rung2-2026-11-21.md; rung-2
registration (DET/TAL interfaces, spec gap G1 closed there):
~/workspace/emergence-rung2-scratch/registration.md. This
registration is append-only. No rung-3 battery run precedes it.

## What is under test

Spec section 2.2, verbatim in substance: Cap12 > max(Cap1, Cap2,
Cap(every section 2.4 control arm)) + delta, all at one equal total
budget, delta decided below. Cap12 is the joint system (level-1 and
level-2 interaction on one append-only log), Cap1 is level-1 alone
(the flat arm), Cap2 is the frozen-partition system (partition formed
at the first formation tick, never updated, level-1 interaction
disabled after formation, only block-level messages flow).

## The member protocol (inherited, not re-decided)

Protocol v3 of rung 2 is the member protocol at both levels:
origin authority (an actor's own-site estimate is its raw
observation; a receiver ignores components about its own site) and
the evidence gate (a non-origin value is relayed only when the
sender holds at least 3 reports for that site). Bundle format,
offsets, message size (336 bits), noise rates, scoring, and the
seed split are rung 2's, unchanged, for family A. Family B adapts
the same protocol to labels (below).

## Task families (two, per section 2.7)

Family A ("field3"): rung 2's distributed field reconstruction,
unchanged. Hidden field = sum of 3 sinusoids (amplitudes 60/35/20,
seed-derived phases); actor i observes field(i) + uniform noise in
{-25..25}; tasks predict the field at distances 1..6 in both
directions; score max(0, 1 - |pred - truth|/120); split by seed
2026112199 (sha256 rule of rung 2), split-blind. N = 256 actors on
a ring, horizon T = 32 ticks.

Family B ("region3"): region classification. The ring of N = 256
sites is partitioned into 6 contiguous segments; segment lengths
are N//6 jittered by seed-derived draws in {-4..4}, adjusted to sum
to N, minimum length 12 (draw procedure in the harness, a
deterministic function of the run seed). The label of segment s is
s mod 3 (3 classes). Actor i observes label(i) correctly with
probability 0.7, else one of the other two classes with probability
0.15 each (seed-derived draws). An actor's estimate for a site is
the mode of its reports for that site (ties break to the smallest
label; no reports = no estimate). Bundles carry label estimates in
rung 2's 8-component offset structure; NULL marks no estimate.
Protocol v3 adapted: own-site estimate is the raw observation;
receivers ignore own-site components; a non-origin label is relayed
only with at least 3 reports for the site. Corruption (below)
replaces a label by a label different from the site's true label:
(truth + 1) mod 3 or (truth + 2) mod 3, chosen by the noise stream.
Tasks: predict the label at distances 1..6 in both directions;
score 1 if the prediction equals the true label, else 0; a site
with no reports is predicted as class 0. Split by seed 2026112299
under the same sha256 rule with family B's seed. N = 256, T = 32.

Both families satisfy section 2.7's minimums (>= 64 actors, >= 3
formation ticks, k = 8 replicates per arm).

## Group formation rule G (declared alternative, section 2.1)

The canonical rule (connected components of the dependence-
confirmed mutual-reach graph) is NOT used, for a stated reason:
under this protocol adjacent actors are mutually reachable within
the first ticks with probability near 1 (a delivered bundle's
offset-0 component is the sender's origin value, so one delivered
record each way establishes mutual reach; the per-tick delivered
probability is 0.75), and connected components are transitive, so
the canonical rule returns a single block of all N actors at the
first formation tick and the rung tests nothing. Section 2.1
permits a battery to declare another deterministic rule. The
declared rule:

- Reach: actor b is reached by actor a within a cut iff, folding
  the cut's level-1 records, b's report table holds at least one
  report about site a. Provenance reach is exact for this protocol
  by construction: a value about site s is created only by s's own
  observation and is copied verbatim by relays (corruption changes
  a value in transit but the corrupted component still describes,
  and traces to, its site); so origin sets read off the fold are
  the dependence reach, not an estimate. No scan is sampled
  anywhere in this rung (see G2 handling below).
- First-reach tick d(a->b): the earliest tick whose deliveries
  leave b holding a report about site a, read off the tick-by-tick
  fold of the cut.
- Adjacency: ring neighbours a, a+1 (mod N) are linked iff
  d(a->a+1) <= kappa and d(a+1->a) <= kappa, with kappa = 2
  (reach established during ticks 0, 1, or 2). Per-direction
  failure probability is about 0.25^3 = 0.016 (no direct delivered
  record in three ticks; relay paths only make reach earlier), so
  the expected number of cut adjacencies at N = 256 is about 8 and
  the expected block count about 9, mean block size about 28.
- Blocks: connected components of the linked-adjacency graph
  (a subgraph of the ring, so blocks are arcs), singletons
  included. G reads only the level-1 records of the cut; it is a
  deterministic function of the cut alone (T3.1's content).
- Formation ticks: t1 = 8, t2 = 16, t3 = 24. At the start of a
  formation tick, G is applied to the cut of level-1 records with
  tick < t_j; the resulting partition is in force for ticks
  [t_j, t_{j+1}) (t_4 := T = 32). Level-2 interaction is active
  for ticks >= t1. Note, stated in advance: first-reach ticks are
  prefix facts, so the linked-adjacency set can only shrink as
  cuts grow (an adjacency unlinked at t1 stays unlinked; one
  linked at t1 was linked on ticks <= 2 and stays linked). The
  partition is therefore the same at t1, t2, t3 in every run.
  Recomputation at t2 and t3 is still performed and the equality
  is checked, not assumed. The joint-vs-Cap2 contrast does not
  depend on partition change: Cap2 disables level-1 after t1,
  the joint system does not.

## The level-2 system

Blocks are ordered by smallest member name (the block ring).
Member rank = position in the block's name-sorted member list.
A group actor's step (spec 2.1: one step of each member, in name
order) is executed as: each member forms its bundle from its
current state (the same bundle function as level 1) and sends it
to the member of the same rank in each adjacent block (left and
right in the block ring; if the target block is smaller, the
highest-rank member receives; if there is only one block, there
is no adjacent block and the sends are generated and discarded
as filler). With two blocks, left and right neighbours are the
same block and both sends go to it. A level-2 record's source is
the sending member, its destination the receiving member, its
interpreted source (for offset interpretation) the sending member
in the live arm. Messages are the 336-bit bundle plus a 16-bit
tag (block id + member rank), 352 bits, counted in full (spec
2.3). Level-2 deliveries append reports by the same rule as
level 1 (protocol v3, offsets interpreted relative to the
interpreted source member).

Noise at level 2: the same channel as level 1 — per message,
drop 0.15, corrupt 0.15, misdeliver 0.10, drawn from the run's
single seed-derived stream in record-generation order.
Misdelivery at level 2: destination = a uniform other member of
the ring (not the intended member), interpreted source = the
member of the same rank in a block adjacent (ring order, random
sign) to the actual destination's block.

## Arms (8 per family)

All arms run the same invocation schedule: every tick, every
actor is invoked at level 1 (1 step, 2 sends of 336 bits); every
tick >= t1, every actor is additionally invoked as a member of
its block's group actor (the group step; across all blocks this
is exactly N member steps per tick, the section 2.3 exchange:
1 group step = |block| member steps). Arms differ only in what
happens to the generated sends. Steps and bits sent are therefore
identical across arms by construction and are verified by the
checker; ticks are identical (T = 32); store (log bytes) differs
only by annotation content and is reported per run.

- joint (Cap12): level-1 live-noisy; level-2 live-noisy from t1
  under the current partition.
- flat (Cap1): level-1 live-noisy for the full horizon; level-2
  slot sends are formed per actor each tick >= t1 (bundle from
  own state, addressed to ring neighbours) and discarded as
  filler. This is the section 2.3 conversion realized as filler
  steps at the same ticks (the rung-2 arms' established reading
  of sections 1.7/1.8: budget is steps and bits sent, spent by
  generation; Cap2's own filler in section 2.3 is likewise
  isolated steps, not extra ticks). The horizon is NOT extended:
  section 1.8 makes ticks a budget component, and extending
  flat's horizon would compare the joint system against
  level-1-with-more-time, a different system, not level-1 alone
  at the budget.
- frozen-partition (Cap2): level-1 live-noisy for ticks < t1;
  partition formed at t1 from its own cut and never updated;
  for ticks >= t1, level-1 sends are generated and discarded
  (members isolated at level 1) and level-2 is live-noisy over
  the frozen partition.
- isolated (section 1.7 on the joint system): all sends at both
  levels generated and discarded as filler, all ticks.
- frozen (section 1.7 on the joint system): all records at both
  levels are a verbatim replay, per tick, of a previously
  recorded joint run's log at the generator seed (run seed +
  777000). The generator run is live-NOISY, not live-clean:
  under the registered formation rule a clean run forms a
  single block (every adjacency is linked at tick 0), so a clean
  generator's level-2 stream is all filler and the frozen arm
  would test no level-2 content at all. This deviation from
  rung 2's clean generator is registered here, with its reason,
  before any run.
- shuffled (section 1.7 on the joint system): sends generated
  live at both levels; per tick and per level, destinations are
  permuted among the tick's sends by the run's stream; the
  interpreted source of a level-1 record is a ring neighbour
  (random sign) of the actual destination, of a level-2 record
  the same-rank member of a block adjacent to the actual
  destination's block. Per-tick message multisets are preserved
  (T3.7's content).
- freeze-1: level-1 live for ticks < t1, then the generator
  run's level-1 records replayed verbatim per tick; level-2
  live-noisy from t1 under partitions formed from this arm's
  own log.
- freeze-2: level-1 live-noisy; partitions form and update as
  in the joint arm; level-2 sends are shuffled (as in the
  shuffled arm) for ticks >= t1.

Partitions in every arm that uses them are formed from that
arm's own level-1 log by the registered G (frozen and isolated
arms form partitions for reporting; their level-2 sends are
replayed or discarded regardless).

## Budgets (verified equal, per section 1.8 as read above)

Per run, every arm: steps = N*T (level 1) + N*(T - t1) (level-2
member steps) = 256*32 + 256*24 = 14336. Bits sent =
2*N*T*336 + 2*N*(T - t1)*352 = 5505024 + 4325376 = 9830400.
Records per log = 2*N*T + 2*N*(T - t1) = 28672. Ticks = 32.
Bits delivered and store (log bytes) are reported per run, not
equalized (delivery is noise-dependent in every rung; store
differs only by annotation and destination content).

## Replicates, seeds, margin — the margin decision

k = 8 replicates per arm per family. Run seeds 2026112101..
2026112108 (rung 2's seeds; the field/label draws per seed are
therefore the same fields rung 2 measured, which is intended:
rung 3's arms are new systems over the same task draws). One
noise stream per (seed, arm), seeded by the pair, as in rung 2.

Margin decision (registered before any run, applied uniformly):
PER-ARM margin. The joint arm wins the battery iff for every
control arm X, Cap(joint) > Cap(X) + spread(X), where Cap is the
mean over the arm's 8 replicates and spread(X) is max minus min
over X's replicates (section 1.9's definitions). Reason, from
rung-2 evidence: section 1.9's global delta (max over control
spreads) was 0.3694 in MAIN3, set entirely by the frozen arm,
whose spread is dominated by cross-seed field difficulty (the
frozen stream replays a different field per replicate, so its
capability varies with the draw, not with anything the arm
does). Importing that spread into every comparison put the
isolated bar at 1.0066 — above the score ceiling — so the global
rule judged arms by a variance they do not have. The per-arm
rule keeps the decision a deterministic inequality over
registered replicates with the margin derived from the controls'
own variability (no significance test, no p-value), and it does
NOT lower the binding bar: the frozen arm's own threshold under
per-arm delta is exactly its section 1.9 threshold. The section
1.9 global-delta decision is also computed and printed alongside
in the record; the registered (per-arm) decision governs the
claim. Changing this rule after seeing results is not lawful
and will not be done.

## Views, deadness, ablation (sections 2.5, 2.7)

Views are computed for joint replicate 1 (seed 2026112101) of
each family, by a view builder over the persisted log, following
rung 2's view method (counterfactual folds of the recorded log;
no re-running of the system):

- Components: for a partition P, one component per block = the
  block's mean held-out task score, scored by the family's rule
  from a fold of the included records.
- Level-1 view at formation tick t_j: included records = the
  cut's level-1 records with tick < t_{j+1}; axes = blocks of
  P_j (block grain — the registered quotient of the section 1.3
  actor axes; actor-grain subset tables over 256 axes are
  infeasible and the quotient is named wherever reported);
  configurations = folds including level-1 records whose source
  block (under P_j) is in the configuration set; hyperedges =
  per-tick counterfactual component sets within the included
  records, weight = the tick's delivered level-1 count.
- Level-2 view at t_j: included records = level-1 records with
  tick < t_{j+1} (substrate, always included) plus level-2
  records with tick in [t_j, t_{j+1}); axes = blocks of P_j;
  configurations vary only the level-2 records, by source block;
  hyperedges = per-tick counterfactuals over the interval's
  level-2 records, weight = the tick's delivered level-2 count.
- Joint view at t_j: included records = both levels with tick
  in [t_j, t_{j+1}); configurations vary both levels by source
  block (source block under the partition in force at the
  record's tick); hyperedges = per-tick counterfactuals over
  both levels' records of the tick, weight = the tick's total
  delivered count.
- Live, engaged, mu, lambda, rho per F1 (hma SPEC sections 2-4)
  from the configuration folds by the single-axis sensitivity
  path argument (rung 2's view): Live(S) = union of sens[a] for
  a in S, sens[a] = components changed by toggling axis a at
  some configuration. Exactness: if a view has at most 11 axes,
  all subset configurations are folded and sensitivity is exact.
  If a view has more than 11 axes, sensitivity is computed over
  the registered subfamily (the empty set, the full set, and all
  leave-one-out sets, toggling each axis from each), Live is a
  lower bound, and emergent-dead is reported as NOT PROVABLY
  DEAD for every axis of that view (deadness is never declared
  from a restricted configuration family).
- Emergent-dead at level 2 (F1 section 4): block g is dead in
  the level-2 view at t_j iff Live(A without g) = Live(A) in
  that view, computed exactly or not declared (above).
- Interaction matrix per section 1.3 from each view's
  hyperedges. mu and rho reported per view per formation tick;
  the partition sequence is in every run summary.

Ablation (section 2.5 load-bearing, section 2.7's T3.8 test):
the ablation set is the blocks of the final partition P3 of
joint replicate 1, per family. For each such block g, an
ablation replicate set of 4 runs at seeds 2026112101..2026112104:
the joint system with one modification — for ticks >= t3, every
member of g (the fixed actor set from replicate 1's P3) is
isolated: its sends at both levels are generated and discarded,
records addressed to it are not delivered (annotation filler),
and level-2 sends from other blocks that would target its
members are discarded. All other mechanics, including formation
from the run's own log, are the joint arm's. Cap drop for seed s
= Cap(joint, s) - Cap(ablation g, s); g is load-bearing iff the
mean drop over the 4 seeds exceeds delta_abl, where delta_abl =
the section 1.9 global delta of that family's battery (max over
control arms of spread) — the conservative choice, registered
here. Section 2.7's refutation triggers iff some block of the
ablation set is provably emergent-dead in the level-2 view at
t3 AND load-bearing under this rule; that outcome is printed as
a refutation of T3.8's premise (the measure is the defect; the
rung reopens at section 1), not as a rung-3 win or loss.

## DET / TAL and the checker (G1 interfaces, rung 2)

The rung-2 registration's DET/TAL interface publication is
reused unchanged in form: DET is the batch computation over a
whole prefix, TAL the incremental fold, and the checker verifies
DET = TAL at registered append cuts. Rung 3's tally vector adds
per-level record counts; the joint tally is the pair of the
level tallies (T3.6's content). Registered cuts: every 4096
records, the formation-tick boundaries, and the final record.
An independent checker (separate code path, reads only persisted
logs + config, re-implements field/label generation, the fold,
and formation from this registration) verifies per run: replay
to the recorded final hash; restart exactness from each
formation-tick prefix (fold of the prefix reproduces the online
hash at that cut, joint arm); DET = TAL at every registered cut,
combined and per level; budget shape (steps, bits sent, record
count as above); and formation agreement (partitions recomputed
from the log's level-1 prefixes equal the summary's recorded
partitions, every arm).

## Spec gap G2 — state and handling

G2 (dependence-scan cost at scale; the SAMPLED label) is OPEN
after rung 2: rung 2's scans were tick-unit counterfactual folds
on one small instance, and no per-message scan at scale or
sublinear exact scan exists. Rung 3's handling, registered:
formation uses provenance reach, which is exact by construction
for this protocol and is not a scan at all; view hyperedges use
tick-unit counterfactual folds, exact at the tick unit (the
scan unit is the tick, as in rung 2's view). No quantity in
rung 3 is computed from a sampled scan, so nothing carries the
SAMPLED label and nothing SAMPLED enters any theorem or the
ablation test. G2 remains OPEN and is handed to rung 4 in the
record; rung 3 does not claim to close it.

## Falsification (spec 2.7, honored as written)

The rung-3 claim is dead if, in either family's battery,
Cap(joint) <= Cap(X) + spread(X) for any single control arm X
under the registered per-arm rule — printed as a loss with the
exact difference vector — or if the ablation refutes T3.8's
premise as specified above (printed as a refutation; the rung
reopens at section 1). A win in one family and a loss in the
other is reported as exactly that; the claim as registered
requires both families.

## Projection and weights (sections 1.3, 1.4)

Projection: the full local state (the section 1.4 substitution,
as in rung 2 — finer than the default quotient; a group actor's
state is the tuple of its members' full states). Weighting rule:
a hyperedge's weight is the delivered-message count of its tick
at the view's level(s). Weights select nothing in this rung's
decision (capability only); they enter mu as in F1.

## Amendment v2 (appended before any battery run; supersedes kappa only)

Evidence, from debugging runs at the registered scale (N = 256,
seed 2026112101, joint arm — a debugging measurement of the
formation instrument, not a battery result; no battery in this
registration has run): the first-reach ticks of the 256 ring
adjacencies in that run's level-1 log are distributed as
(d(a->a+1), d(a+1->a)): (0,0) x159, (0,1) x39, (1,0) x30,
(1,1) x9, (0,2) x7, (2,0) x5, (2,1) x4, (2,2) x2, (3,1) x1.
Reach is faster than the registration's estimate because a
misdelivered bundle landing on an actor appends reports about
the interpreted source's sites, so an adjacency's reach is
established at tick 0 with probability about 0.82, not 0.75.
Consequences for the registered rule: at kappa = 2 exactly one
adjacency is cut, and one cut does not split a ring — the
partition is a single block, level-2 has no adjacent block to
address, and the joint arm is mechanically identical to flat.
The battery as registered would test nothing. At kappa = 0 the
same histogram gives 97 cut adjacencies (mean block size about
2.6 — level-2 would be a relabeling of level-1). At kappa = 1
it gives 19 cut adjacencies, about 19 blocks of mean size
about 13.

Change: kappa = 1 (reach established during ticks 0 or 1).
Everything else in this registration is unchanged, including
the formation rule's form, the formation ticks, the arms, the
budgets, the margin decision, and the falsification conditions.
Expected block counts under kappa = 1 are roughly 10-30 per
run (seed-dependent); a replicate whose partition has very few
blocks is data, handled by the decision rule as registered.

Consequence for the views, stated in advance: at kappa = 1 the
views will typically have more than 11 axes, so the registered
exactness fallback applies. The fallback's configuration
subfamily is hereby specified as: the empty set, the full set,
all singletons, all pairs, all leave-one-out sets, and all
leave-two-out sets (for B axes, at most 2 + 2B + B(B-1) folds).
Sensitivity and Live from that family are lower bounds and are
labeled as such wherever reported; emergent-dead is declared
only from an exact (all-subsets) computation, as registered.
If a view has at most 11 axes the exact computation applies
automatically. This means the section 2.7 T3.8-ablation route
is armed only for blocks in an exactly computed level-2 view;
where the view is restricted, the record reports the antecedent
as not evaluable rather than stretching the computation. That
limitation is a G2-class cost fact and is handed on in the
record.
