# Rung 4 registration — transfer (written before any rung-4 run)

Ladder spec: ~/workspace/research/emergence-ladder-spec-2026-11-21.md
(sections 1 and 3), also clpi/software-emergence-is-decidable at
ee3086521932c19f4ed0a054d4362cf21d525972, SPEC.md. Rung-3 record:
~/workspace/research/emergence-rung3-2026-11-21.md — its "Rung 4
inherits" list is binding on this registration (the margin and
pairing decision in item 2 is made here; item 7, transfer sign is
family-dependent, is answered by registering two pairs in opposite
directions). Rung-2 record:
~/workspace/research/emergence-rung2-2026-11-21.md. Rung-3
registration and harness: ~/workspace/emergence-rung3-scratch/.
This registration is append-only. No rung-4 battery run precedes
it. A code-validation smoke run at reduced scale (N = 64, one
seed, no artifact, no decision) may precede the batteries, as
rung 3's debugging run preceded its amendment; it is not a
battery run and no number from it enters any decision.

## What is under test

Spec section 3, verbatim in substance: interaction structure
derived in one task family, carried as weights into a different
held-out family, improves held-out capability there beyond what
the same total information in unstructured form achieves.
Transfer advantage (spec 3.3):

  DT = Cap(target with A*) - max(Cap(target with U),
       Cap(target with R*), Cap(target with nothing))

with A*, U, R* as defined below, each Cap the mean over k = 8
replicates at equal budgets, and the null and decision rule of
the Margin section below. Spec 3.5 falsification, honored as
written: the claim is dead if DT <= delta in the registered
battery, or if any null replicate's DT >= the observed DT.

## The systems (source and target are the same system shape)

Both source and target systems are the single-level member
system of rungs 2-3: protocol v3 (origin authority + evidence
gate >= 3 reports) on a ring of N = 256 actors, horizon T = 32
ticks, bundle of 8 components (336 bits), noise per sent message
drop 0.15 / corrupt 0.15 / misdeliver 0.10 drawn from one
seed-derived stream per run with every outcome written into the
log record (the live arm of spec 1.7). This is rung 3's level-1
system run for the full horizon (rung 3's flat arm minus its
filler level-2 records). Member protocol, bundle format,
offsets, scoring, and splits are rung 2's and rung 3's,
unchanged:

- Family "field": hidden field = sum of 3 sinusoids (amplitudes
  60/35/20, seed-derived phases); observation = field + uniform
  noise in {-25..25}; tasks predict the field at distances 1..6
  in both directions; score max(0, 1 - |pred - truth|/120);
  estimate = upper median of reports; split seed 2026112199.
- Family "region": 6 seed-drawn segments, labels = segment index
  mod 3; observation correct with probability 0.7; estimate =
  mode of reports (ties to the smallest label); score 1 if the
  prediction equals the true label else 0; a site with no reports
  is predicted as class 0; split seed 2026112299.

Run seeds 2026112101..2026112108, k = 8 replicates, for every
gossip run in this rung (source and target alike). Actor names:
source actors and target actors live in disjoint namespaces by
family (no actor name is shared between the two families of a
pair); operationally, no source log record, source task, source
field/label draw, or source actor state is an input to any
target run — the only object that crosses is the artifact A*
(and the control artifacts derived from it), per spec 3.1.

## Pairs (spec 3.5: at least two pairs, at least one sharing no
task generator)

- Pair 0: source field -> target region.
- Pair 1: source region -> target field.

The two families share no task generator (a sinusoid field with
median estimates against seed-drawn segments with mode
estimates), so both pairs satisfy the no-shared-generator
condition. The claim as registered requires transfer in BOTH
pairs (rung 3's both-families precedent): a split result is
reported as exactly that, and the claim is dead as registered.

## Groups, axes, components (the view grain)

G = 8 groups: contiguous ring arcs of 32 actors, group g =
actors 32g..32g+31 (rung 2's view grain). In any view of a log:

- Axes: the 8 groups. A configuration S (a subset of groups) is
  the fold of the log admitting only records whose true source
  lies in a group in S (rung 2/3 view semantics; the actor's own
  observation is initial state, not a record, and is present in
  every fold).
- Components: the 8 per-group held-out mean scores of that fold
  (component b = mean held-out score over the held-out tasks of
  group b's actors, the family's scoring rule).
- Hyperedges: per tick, the set of components whose value
  changes when that tick's delivered records are removed from
  the fold (the tick-unit counterfactual scan of rungs 2-3,
  exact at the tick unit); weight = the tick's delivered count.
- Interaction matrix M: M[b][b'] = total weight of hyperedges
  containing both b and b'; M[b][b] = total weight of hyperedges
  containing b (spec 1.3).

Sensitivity, Live, engaged, mu, lambda, rho for a view are
computed exactly over all 256 configurations (G = 8, rung 2's
view method), for the record; they are detector output and
carry no capability claim.

## Extraction (spec 3.1)

The source battery is the 8 live replicates of the source
family. Extraction reads replicate 1's log (seed 2026112101)
only (rung 2/3 precedent: views are computed on replicate 1):

1. Build the view of that log (above).
2. M = its interaction matrix.
3. Rank order: components sorted by descending diagonal M[b][b],
   ties by ascending component index. A*[i][j] = M[r_i][r_j]
   where r is that order. A* carries pattern and no names.

Canonical encoding of an 8x8 natural matrix X at width w:
4 header bytes (dimension 8, width w, pad count as 2 bytes,
big-endian) followed by the 64 entries row-major, each in w
bytes big-endian. The battery width w = the minimal byte count
for max(A*), at least 1, fixed by A* for the whole pair; every
artifact of the pair is encoded at that width. |X| = 8 * (4 +
64w + pad) bits, pad = 0 for every artifact of this rung
(equality below is exact, no padding is needed).

## The artifacts (per pair; spec 3.2)

- A*: as extracted.
- U (unstructured control): A*'s 64 entries flattened row-major
  and permuted by a Fisher-Yates shuffle drawn from
  random.Random(2026112501 + pair index), reshaped row-major.
  Same entry multiset as A*, hence same maximum, hence
  |U| = |A*| exactly (T4.2's content).
- R* (random control): 64 entries drawn i.i.d. uniform on
  {0..max(A*)} from random.Random(2026112601 + pair index),
  row-major; encoded at the battery width w, so |R*| = |A*|.
- Nothing: no artifact installed. The arm is charged a zero
  artifact of 64 zero entries at width w as filler (spec 3.3),
  |zero| = |A*|.
- Null artifacts (spec 3.3): for j = 1..32, a permutation p_j of
  {0..7} drawn by Fisher-Yates from
  random.Random(2026112701 + 1000 * pair index + j); the null
  artifact is A* conjugated by p_j: N_j[i][j'] = A*[p_j(i)]
  [p_j(j')] — rows and columns permuted by the same permutation:
  pattern kept as an abstract object, its placement on the
  target's component positions destroyed; entry multiset equal
  to A*'s (T4.4's content).

## Carriage: the target configuration search (spec 3.1, 3.3)

Per target seed, ONE live gossip run of the target family is
executed and its log persisted. The artifact is never an input
to the gossip run: for a fixed seed, every arm's log is the same
log (arms are paired per seed by construction). The artifact is
installed only as the selection order of the configuration
search over that log's view:

- Configurations: all 256 subsets S of the 8 groups. The
  behavior at S is the fold of the target log admitting only
  records whose source group is in S. The working score of S is
  that fold's mean working-set score; the held-out score of S
  is that fold's mean held-out score. Neither score reads the
  artifact (T4.3's content).
- Priority: for an installed artifact X and a nonempty S,
  prio_X(S) = (sum of X[i][j] over i, j in S) / |S|^2 — the mean
  artifact weight over S's component pairs. prio(empty) = -1.
  Search order: descending prio; ties by larger |S| first, then
  by smaller mask integer (bit g of the mask = group g).
- The nothing arm's order: prio identically 1 for every nonempty
  S under the same tie-breaks (the uniform weighting) — i.e.
  decreasing |S|, then mask ascending; empty last.
- Evaluation budget E = 32: the search evaluates the first 32
  subsets of its order on the working set and selects the best
  working score (ties to the earliest evaluated). Cap(arm,
  seed) = the held-out score of the selected subset's fold.
  Cap(arm) = the mean over the 8 seeds.
- Diagnostic (not an arm, never in any decision): the
  unbounded search (E = 256, the nothing order) per seed,
  reported as the search ceiling at this budget shape.

## Margin decision (registered before any run; rung 3 inherits
item 2 discharged here)

Primary rule, per spec 3.3's text: delta = max over the three
control arms (U, R*, nothing) of spread(control), spread = max
minus min of Cap over the arm's 8 seed replicates (spec 1.9).
Transfer is established in a pair iff DT > delta AND DT >
DT_j for every one of the 32 null replicates, where DT_j =
mean Cap(null_j) - max control mean (the same controls). Both
conjuncts are required; either failing is no transfer (spec
3.3). The rung-4 claim requires transfer in both pairs.

Reason for the global delta here, against rung 3's per-arm
choice: rung 3's pathology was a replay control (frozen,
freeze-1) whose spread is cross-draw seed luck from a foreign
stream, imported by the global rule into comparisons that arm
has no part in. No rung-4 control is a replay arm: U, R*, and
nothing are search orders over the same per-seed target logs as
the A* arm, so a control's spread measures how much that
control's search outcome varies across target draws — the
variability a transfer claim must beat, and the quantity spec
3.3 names. The pairing question rung 3 left open is decided as
follows: arms ARE paired per seed (one target log per seed,
shared by every arm — the artifact cannot affect the run), and
task draws are NOT held fixed across seeds (each seed is a
fresh draw; spec 1.9 replicates). Printed alongside the primary
decision, as facts and for comparability with rung 3: the
per-arm decision (Cap(A*) > Cap(X) + spread(X) for every
control X, with the same null conjunct), and the paired
per-seed difference vector Cap(A*, seed) - max over controls of
Cap(control, seed). Neither printout governs the claim; if the
per-arm decision disagrees with the primary decision, the
disagreement is reported plainly and the primary governs.

## Budgets (spec 1.8, 3.3)

Per gossip run (source or target): steps = N * T = 8192; bits
sent = N * T * 2 * 336 = 5505024; ticks = 32; records = 16384.
Bits delivered and store (log bytes) are reported per run, not
equalized (delivery is noise-dependent in every rung). Per
target seed: the search budget is E = 32 working-set
evaluations for every arm, null arms included, and the artifact
bits |A*| are charged identically to every arm (zero filler for
the nothing arm). Costs counted separately, never collapsed:
source battery cost, extraction cost (32 tick counterfactuals +
256 configuration folds on replicate 1), per-arm evaluation
counts, checker costs.

## DET / TAL and the checker (G1 interfaces, rungs 2-3)

TAL is the rung-2/3 tally vector, updated record by record;
DET is the same vector computed from scratch over any prefix.
Registered cuts: every 4096 records, the first three tick
boundaries, the final record; restart cuts at ticks 8, 16, 24.
An independent checker (separate code path, reads only
persisted logs, artifacts, and this registration; imports
nothing from the harness) verifies, per family: replay to the
recorded final hash of every persisted run; restart exactness
from each restart cut; DET = TAL at every registered cut and
agreement with the harness's online tally at the final record;
budget shape of every run; extraction agreement (the view and
A* recomputed from the source replicate-1 log by the checker's
own path, compared bit for bit against the persisted artifact's
canonical bytes); artifact facts (|U| = |R*| = |zero| = |A*| in
bits; U's and every null's entry multiset equal to A*'s);
search agreement (every arm's and null's order prefix,
evaluated working scores, selected subset, and Cap recomputed
from the persisted target logs and artifacts, compared exactly);
and the selection-only spot property (the per-subset working
score table of a seed is identical recomputed under any
installed artifact — the table is artifact-free by
construction, and the checker verifies the harness's recorded
table against its own).

## Spec gap G2 — state and handling

G2 remains OPEN, inherited from rung 3 unchanged in substance:
per-message dependence scans at scale and a sublinear exact
scan do not exist; exact sensitivity above the 11-axis subset
cap is not available in general. Rung 4's handling, registered:
no quantity in this rung is computed from a sampled scan, so
nothing carries the SAMPLED label and nothing sampled enters
any theorem or decision. The dependence scan unit is the tick
(exact at that unit, the rungs 2-3 declared unit). At G = 8
axes, sensitivity and deadness ARE exact (all 256
configurations folded), so the source and target views' dead
axes are reported as detector output — one place the G2-class
cap does not bind, stated as such. G2 itself is handed to
rung 5 still open.

## Theorem obligations (spec 3.4)

T4.1 extraction determinism, T4.2 information equality, T4.3
selection-only carriage, T4.4 null exactness, T4.6 carriage
replay: attempted in Lean 4.19.0 core-only, cold compile clean,
axioms within {propext, Classical.choice, Quot.sound}, no
sorry. T4.5 (transfer bound) is PREMISE until rung 6 closes:
stated in the Lean file as a named premise definition, not
proved, not an axiom, depended on by nothing, and never cited
as evidence for DT (spec 3.4).

## Falsification (spec 3.5, honored as written)

The rung-4 claim is dead if, in either pair, DT <= delta, or
any null replicate's DT >= the observed DT — printed as a loss
with the exact vectors, in both cases. A falsified claim is
recorded as falsified and stands until a same-contract
re-measure at a current pin says otherwise.

## Amendment v2 (appended before any battery run; supersedes the
priority rule only)

Evidence, from the code-validation smoke run the registration
permits (N = 64, seed 2026112101, one run per family — a
debugging measurement of the search instrument, not a battery
result; no rung-4 battery has run): under the registered
mean-weight priority, the head of every artifact arm's search
order is the eight singleton subsets (a singleton's priority is
its diagonal entry, 530..1617 in the smoke's field view, against
a full-set mean two to four times smaller), so all 32
evaluations of the A*, U, R*, and null arms are spent on
subsets of size 1-3, while the nothing arm's uniform order
evaluates the full configuration first. The comparison would
then measure the subset-size bias of the priority rule, not
the transferred pattern: spec 3.5's question — structure
rather than information volume — would not be what the battery
tests.

Change: prio_X(S) = the TOTAL artifact weight over S's
component pairs (the sum of X[i][j] over i, j in S), not the
mean. Entries are naturals, so the sum is monotone in S: every
arm's order now opens with the full configuration, the
leave-one-out subsets, and the leave-two-out subsets of least
removed artifact mass, and the artifact decides WHICH subsets
of each size are reached within E = 32 — the size profile of
the evaluated set is the same in shape for every arm, and only
the pattern chooses within it. prio(empty) = -1 and the
tie-breaks (larger |S| first, then smaller mask) are unchanged,
as are the nothing arm's uniform order, E, the artifacts, the
margin decision, and the falsification conditions.
