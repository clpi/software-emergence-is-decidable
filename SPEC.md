# Emergence Ladder — Specification for Rungs 3–6 and the Endgame

Program: **Derive and test useful emergence from actor interactions**
(goal goal_d8666507a5fa). Directive: Chris, 2026-11-21 07:40 PST —
"go way more ambitious, where no man has gone before." Goal record:
~/workspace/goals/breakthrough-randomness-model-weighted-compressed-emergent-with-machine-checked-proof-of-emergence/GOAL.md

This document is the spec for rungs 3, 4, 5, 6 and the endgame. Rung 1
(detector + tally) and rung 2 (noisy gossip at scale) are specified and
owned elsewhere; this spec consumes their outputs through the shared
definitions of §1 and does not restate them. Status of this document:
**proposed semantics throughout** — a spec, written spec-first under the
standing law (SPEC-FIRST, AGENT-PROOF). Nothing in this document is a
capability claim. A rung's claim exists only when its battery has run
and its theorems have landed, per §8.

## 0. States, foundations, and what is built on

Four states are used in this spec and never blurred: **settled intent**
(Chris's directives, quoted in the goal record), **proposed** (this
spec's definitions and claims, not yet implemented), **implemented**
(code exists), **verified** (executed proof at a named pin).

Foundations this spec builds on, with their states:

- **F1 — the highest-minimal-axis emergence measure. Verified.**
  clpi/software-has-a-highest-minimal-axis at
  63d9d3fdce1f81c81cd5cda2bd9850b0c1494646, 58 theorems (42 core + 16
  controls), cold gate PASS, axioms a subset of {propext,
  Classical.choice, Quot.sound}. Spec of record:
  ~/workspace/hma-scratch/SPEC.md. The definitions consumed here are
  exactly its §1–§4: instance (A, V, C, B, W, F, H, w); Live(S);
  engaged(S); mu(S) = sum of w(e) over e in engaged(S); lambda(S) =
  |Live(S)|; rho(S) = (mu(S), lambda(S)) lexicographic; sufficient,
  minimal, highestMinimal as there defined. No definition in this spec
  modifies F1; where a rung needs a quantity F1 does not define, the
  quantity is defined in §1 or the gap is named in §9.
- **F2 — rung 1 detector and incremental tally. Verified at its stated
  scope.** Five Lean theorems and 96 append-cut checks; XOR scores 4/4
  live against 2/4 for the best isolated or frozen control. Scope, in
  Chris's own framing: this verifies the detector and the incremental
  tally — NOT emergent intelligence. This spec refers to that artifact
  as DET1 (detector) and TAL1 (tally); their exact interfaces are a
  rung-2 deliverable to publish (spec gap G1, §9). Until G1 closes,
  every reference to DET1/TAL1 below is a reference to the verified
  rung-1 behavior, not to a published signature.
- **F3 — the governing invariant. Settled intent.** Intelligence is
  incremental and compounding (Chris, 2026-11-20 01:29 PST). Rung 5 is
  this invariant made measurable; it is a claim under test there, not
  an assumption available to any rung's proof.
- **F4 — the one hypergraph. Settled intent.** The canonical hypergraph
  is the singular total equivalence terms graph, symbol-bound at
  minimum resolution, append-only, drift excluded by construction
  (Chris, 2026-11-19 15:43 PST). Every structure in this spec is a view
  of it or a finite quotient of a view of it; nothing here introduces a
  second store.

## 1. Shared definitions (all rungs)

Every rung is stated over these definitions. An implementer implements
§1 once and each rung against it.

### 1.1 Actor system

An **actor system** is a tuple S = (N, M, P, R, seed):

- N: a finite set of actor names. Finiteness is by qualification
  (named actors, named criteria), never an imposed bound.
- M: a finite message alphabet (a finite value type).
- P: the actor program — for each actor n in N, a function from
  (local state, inbox multiset over M) to (new local state, outbox
  multiset of (destination, M)). P is a single function for the whole
  system (actors differ by name and state, not by code), unless a
  rung's battery explicitly declares a heterogeneous variant.
- R: the delivery rule — a function from the global outbox and the
  channel state to per-actor inboxes, including the noise model where
  a rung declares one. R is part of the system, stated in full in any
  battery that runs the system.
- seed: the sole source of randomness. Every stochastic choice in P
  or R is a deterministic function of (seed, log position). A run with
  no seed named is not a lawful run.

### 1.2 The interaction log and the append-only history

A **run** of S for T ticks produces the **interaction log** L: the
append-only sequence of records, one per delivered message, each
record = (tick, source, destination, message, channel annotation).
L is a prefix-closed object: L_t is the prefix through tick t. The
log is the state (rung 5 makes this load-bearing): an actor's local
state at tick t is a derived view, recomputed from L_t by P, never an
independent store. Appending is the only mutation. A **cut** is a
prefix L_t; the append-cut checks of rung 1 are checks over cuts.

### 1.3 The interaction matrix as a hypergraph view

The **interaction view** of a log L is the HMA instance (F1 §1) built
as follows, deterministically from L:

- Axes A: one axis per actor n in N (the axis value is n's local-state
  projection, §1.4) plus one axis per channel parameter of R that the
  battery varies. The battery's axis list is part of its registration.
- Contract C: the set of configurations reachable by re-running S from
  seed under the battery's declared variations of the axes in A, all
  other inputs held at their logged values.
- Components B: the battery's declared behavior components — named,
  finitely many, each a function of a full run's observable output
  (per-task scores, per-actor final projections, or aggregates of
  them, as the battery declares).
- F: the behavior function, F(x)(b) = component b's value in the run
  at configuration x.
- Hypergraph H: hyperedges are the delivery sets of L — for each tick,
  the set of components whose values the tick's delivered messages can
  reach under F's dependence structure, computed by the dependence
  scan of §1.5. An edge of size < 2 carries no interdependence and is
  excluded from engaged(S) by F1's definition, as there.
- Weights w: positive naturals, one per hyperedge, assigned by the
  battery's declared weighting rule. **Weights change selection, not
  evidence** (settled intent): w may choose which configurations a
  search visits first; w never enters a score, a tally, or a verdict.

The **interaction matrix** of the goal record is this view read as a
matrix: rows and columns indexed by B, entry (b, b') = total weight of
hyperedges containing both b and b', diagonal (b, b) = total weight of
hyperedges containing b. The matrix is a presentation of the view, not
a second object; any quantity defined on the view is read off the
matrix and conversely.

### 1.4 Projections

A **projection** is a named finite function from an actor's local
state to a finite value type. Batteries declare their projections.
The default projection, used unless a battery overrides it, is the
actor's full local state quotiented by the equivalence the task's
scorer cannot distinguish (two states are equivalent when every
continuation under P and the task's remaining inputs scores
identically). An implementer who cannot compute the default uses the
full local state and records the substitution in the battery record;
the substitution is sound (finer) and may only be flagged as a cost
note, never silently.

### 1.5 Dependence scan

The dependence of component b on a delivered message m is decided by
counterfactual replay: re-run the suffix of the run from m's tick
with m removed (all else, including seed-derived choices, identical);
b depends on m iff its final value differs. The scan is exact, finite,
and exponential in nothing: one suffix replay per message. Batteries
with logs too long for per-message replay declare a sampling rule in
their registration, and every quantity computed from a sampled scan is
labeled SAMPLED wherever it is reported; a SAMPLED quantity supports
no theorem in §3–§6 and no certificate in rung 6.

### 1.6 Capability

A **task family** is a finite set of tasks with a scorer: each task
maps a run's observable output to a rational score in [0, 1]. A
battery splits its family, by seed, into a **working set** (visible to
the system during the run) and a **held-out set** (scored only, never
an input to P, R, or any selection). The split seed is part of the
registration and differs from the run seed.

**Capability** Cap(run) = the mean held-out score of the run. Every
capability claim in this spec is an inequality between Cap values of
runs that differ only in their control arm (§1.7), at equal budgets
(§1.8), over the battery's registered replicates (§1.9).

### 1.7 Control arms

Every rung's battery runs, at minimum, these arms of the same system:

- **live**: P and R as defined; messages delivered as sent.
- **isolated**: R delivers nothing; each actor runs on its own inputs
  only, for the same ticks, with the same total budget (§1.8) — the
  budget the channel would have consumed is spent by the arm's
  declared filler (extra local ticks), named in the registration.
- **frozen**: messages are delivered, but from a fixed replay of a
  previously recorded log's message stream (same counts per tick per
  destination), not generated by the current run's actors.
- **shuffled**: messages are generated live but R permutes
  destinations within each tick by a seed-derived permutation, so
  per-tick message multisets are preserved and addressing is destroyed.

Rungs add level-specific arms (rung 3) or information-matched arms
(rung 4) on top of these four; no rung removes one.

### 1.8 Budgets

A **budget vector** is B = (bits, steps, store, ticks): total message
bits delivered, total actor-program steps executed (counted by the
instrumented interpreter's step counter, the same counter for every
arm), total bytes written to the log, and ticks. Arms are **budget
equal** when their budget vectors are componentwise equal, except
store, which may differ only by the arm's declared filler records and
is reported, never hidden. A comparison at unequal budgets is not a
result; it is a battery defect, recorded as such, and the run is
discarded. Costs are counted separately per resource (settled intent):
no rung collapses B into a scalar.

### 1.9 Replicates, margin, and the decision rule template

A battery registers, before any run: the task family and split seed;
the axis list; the projections; the weighting rule; the arms; the
budget vector; the replicate count k (k >= 8 per arm); the run seeds;
and the margin δ.

For an arm X, Cap(X) is the mean of Cap over its k replicates, and
spread(X) is the max minus min over the same replicates. The battery's
margin is δ = max over the control arms of spread(control), computed
from the control replicates only, after they run. **Decision rule:**
the live arm **wins** the battery iff Cap(live) > Cap(control) + δ
for **every** control arm. Any other outcome is **no win**, reported
as the exact vector of differences. There is no significance test and
no p-value anywhere in this spec: the rule is a deterministic
inequality over registered replicates with the margin derived from
the controls' own spread. A battery whose δ is 0 and whose
differences are 0 is a tie, reported as a tie — ties short of the bar
are open work, per the standing zero-loss law, never rounded up.

### 1.10 The detector and the tally

DET (the detector) is the rung-1/rung-2 artifact that, given a log L
and its interaction view, computes for every cut L_t: Live, engaged,
mu, lambda, rho over the view's axes, and the per-arm capability
tallies. TAL (the tally) is its incremental form: the value at cut
t+1 is derived from the value at cut t and the appended records only.
Rung 1 verified DET/TAL agreement on 96 append cuts for the XOR
instance; rung 2 owns extending that verification to the noisy case.
Every rung below consumes DET/TAL outputs; no rung recomputes them by
a second route except as a stated control (the independent-route
agreement checks of rung 5).


## 2. Rung 3 — Composition: emergent groups as actors

**Claim under test (proposed).** Second-order interaction — interaction
between groups that exist only because of first-order interaction —
produces capability that neither level produces alone, at equal total
budgets.

### 2.1 Group formation, exactly

Fix a level-1 system S1 = (N, M, P, R, seed) and its log L. A **group
formation rule** is a deterministic function G from a cut L_t to a
partition of N. The rule is part of the battery registration; the
canonical rule, used unless a battery declares another, is: two actors
are in the same block iff they are joined by a hyperedge of size >= 2
in the interaction view of L_t whose dependence scan (§1.5) confirms
both directions of reach within the cut; blocks are the connected
components of that graph, singletons included. G is recomputed at
registered **formation ticks** t1 < t2 < ... < tm (part of the
registration); between formation ticks the partition is fixed.

A **group actor** for block g is the actor whose local state is the
tuple of its members' projections (§1.4) at the formation tick, whose
program P2 is P lifted memberwise (a group actor's step is one step of
each member, in name order), and whose messages are pairs (member
name, M) tagged with the group name. The **level-2 system** S2 has
actor set = the blocks of the current partition, message alphabet
M2 = N x M, program P2, and delivery rule R2 = R lifted to blocks
(a message to any member is a message to its block, delivered to the
named member). The **joint system** S12 runs S1 until the first
formation tick, then runs S1 and S2 concurrently on the same log:
level-1 deliveries and level-2 deliveries are both records in L,
distinguished by a level field. Group actors exist only from their
formation tick; there is no group actor for a block before it forms.

### 2.2 The capability question, as an inequality

Let Cap12 = Cap of the joint system, Cap1 = Cap of S1 alone continued
for the full horizon, Cap2 = Cap of the frozen-partition system:
S2 over the partition formed at the first formation tick, with that
partition never updated and level-1 interaction disabled after
formation (members run isolated inside their blocks; only block-level
messages flow). All at the joint budget B12 (§2.3). **Rung 3's claim:**
Cap12 > max(Cap1, Cap2, Cap(control arms of §2.4)) + δ, with δ by §1.9.
The claim is about the composition, not about either level: Cap1 and
Cap2 are themselves arms of the battery, not background facts.

### 2.3 Budget equality

B12 is fixed in the registration. Cap1's arm spends B12 by running S1
for the full horizon with its unused level-2 budget converted to extra
ticks at the registered exchange (1 level-2 step = |block| level-1
steps, by the definition of P2's step). Cap2's arm spends B12 by
running its members' isolated steps as filler at the same exchange.
Store differs only by declared filler records (§1.8). Bits: level-2
messages count their full tagged length against the same bits total.

### 2.4 Control arms

The four arms of §1.7 applied to the joint system, plus three
level-specific arms:

- **freeze-1**: level-1 interaction frozen at the first formation
  tick (level-1 messages after that tick are replayed frozen, §1.7);
  level-2 live. Isolates what level-2 adds over a dead level-1.
- **freeze-2**: the partition forms once and level-2 interaction is
  shuffled (§1.7) thereafter; level-1 live. Isolates what live
  level-2 addressing adds.
- **flat**: no groups ever form; the joint budget is spent by S1
  alone with filler ticks — this is Cap1's arm, named separately so
  the report cannot conflate "level-1 alone" with "level-1 plus
  bookkeeping".

### 2.5 Metrics reported

Per battery: the full Cap vector over all arms with per-arm spread;
mu and rho of the level-1 view, the level-2 view (axes = group
actors), and the joint view, at each formation tick; the partition
sequence; the count of group actors that are emergent-dead at level 2
(F1 §4 definition applied to the level-2 view); and B per arm per
resource. A group actor is **load-bearing** iff removing it (isolating
its block for the remainder) drops Cap12 by more than δ in a
registered ablation replicate set; the load-bearing count is reported.

### 2.6 Theorem obligations (8)

Each statement is over the definitions of §1–§2. Labels: PROVED means
proved at a named pin when the rung closes; PREMISE means assumed,
named, and discharged only by a later rung or a stated control; OPEN
means not yet proved and not assumed — the rung does not close until
every OPEN is PROVED or re-labeled PREMISE with Chris's adoption.

- **T3.1 (formation is a function of the cut).** For the canonical G,
  G(L_t) is determined by L_t alone: two runs with equal cuts have
  equal partitions. Label: OPEN (proof route: G is defined from the
  view of L_t, and the view is a function of the log, F1 machinery).
- **T3.2 (group replay exactness).** Re-running S12 from seed over the
  recorded log reproduces every group actor's state at every formation
  tick exactly. Label: OPEN.
- **T3.3 (freeze soundness).** The freeze-1 arm's log equals the joint
  log with every level-1 record after the formation tick replaced by
  its frozen source, and no other record changed; freeze-2 likewise
  for level-2 addressing. Label: OPEN (constructional; expected to
  close by the arm implementations' definitions).
- **T3.4 (budget conservation under lifting).** One P2 step executes
  exactly |block| P steps, so the §2.3 exchange is exact, not
  approximate. Label: OPEN.
- **T3.5 (joint engaged structure).** engaged of the joint view
  contains the images of engaged of the level-1 view and of the
  level-2 view under the member/block inclusions; hence mu(joint) >=
  max(mu(level 1), mu(level 2)) when weights are carried by the
  inclusions. Label: OPEN (route: F1 L1 monotonicity applied to the
  inclusion maps).
- **T3.6 (second-order tally).** TAL over the joint log equals the
  pair (TAL over level-1 records, TAL over level-2 records) composed
  by the joint-view construction, at every cut. Label: OPEN.
- **T3.7 (shuffle preserves marginals).** The shuffled arm's per-tick
  message multiset equals the live arm's, tick by tick. Label: OPEN
  (constructional from §1.7).
- **T3.8 (no free capability).** If every group actor is emergent-dead
  at level 2 at every formation tick, then Cap12 <= Cap(flat) + δ for
  the battery's δ. Label: PREMISE — this is the rung's bridge from
  structure to capability; it is tested by the battery (§2.7) and is
  discharged as a theorem only if rung 6's certificate proves its
  general form (T6.1). Until then it is named wherever rung 3's claim
  is stated.

### 2.7 Falsification, printed in advance

**Rung 3's claim is dead if**, in the registered battery (k >= 8
replicates per arm, at least two distinct task families, at least one
with >= 64 actors and >= 3 formation ticks): Cap12 <= max over all
§2.4 arms of Cap(arm) + δ — i.e. the decision rule of §1.9 fails
against any single control — **or** T3.8's premise is refuted by an
ablation in which a provably emergent-dead group actor is load-bearing
(structure says inert, capability says otherwise: the measure, not
the rung, is then the defect, and the rung reopens at §1).

## 3. Rung 4 — Transfer: interaction structure into a held-out family

**Claim under test (proposed).** Interaction structure derived in one
task family, carried as weights over the hypergraph view into a
different held-out family, improves held-out capability there beyond
what the same total information in unstructured form achieves.

### 3.1 Source, extraction, target

- **Source family** Fs and **target family** Ft: two task families
  (§1.6) with disjoint task sets and disjoint actor-name sets. Ft is
  held out in the strong sense: no run on Ft, and no statistic of Ft
  beyond its registered size and scorer range, is available during
  extraction.
- **Extraction.** Run the source battery's live arm on Fs. From its
  log's interaction view, extract the **structure artifact** A*: the
  interaction matrix (§1.3) quotiented by actor names — entries are
  reindexed by the rank order of each component's diagonal weight, so
  A* carries pattern (which components interact, with what relative
  weights) and no names. A* is a finite matrix of naturals; its size
  in bits, |A*|, is computed by the canonical encoding (row-major,
  each entry in the minimal bytes for the matrix maximum, plus the
  dimension header) and recorded.
- **Carriage.** On Ft, A* is installed as the initial weighting w0 of
  the target system's interaction view and as the selection order for
  the target run's configuration search (weights change selection,
  §1.3). Nothing else crosses: no source log records, no source task
  data, no source actor states.

### 3.2 The information-matched control

The control arm receives, in place of A*, an **unstructured artifact**
U with |U| = |A*| bits exactly: the multiset of A*'s entries,
flattened and permuted by a seed-derived permutation, with the header
intact — same total information by the bit count, no pattern (rows
and columns destroyed). A second control receives a **random
artifact** R* of the same bit size drawn from the seed. A third
control receives nothing (w0 = uniform). If |U| = |A*| cannot be met
exactly by the canonical encoding, the battery is defective and does
not run; padding to equality is by trailing zero entries in the
header's declared pad field, counted in |U|.

### 3.3 The transfer metric and its null

**Transfer advantage** ΔT = Cap(target with A*) − max(Cap(target with
U), Cap(target with R*), Cap(target with nothing)), each Cap by §1.9
over k >= 8 replicates at equal budgets (the carriage and control
installations all count against the same bits budget; the artifact
bits are charged to every arm identically, including the nothing arm,
which receives a zero artifact of the same size as filler). **Null:**
the distribution of ΔT under destination-shuffled carriage — A*
installed with its rows and columns permuted by seed-derived
permutations (pattern destroyed, marginals kept), over >= 32
permutation replicates. **Decision rule:** transfer is established
iff ΔT > δ (δ from the target controls' spread, §1.9) **and** ΔT
exceeds every one of the >= 32 null replicates' ΔT values. Both
conjuncts are required; either failing is no transfer.

### 3.4 Theorem obligations (6)

- **T4.1 (extraction determinism).** A* is a function of the source
  log alone: equal logs give equal artifacts, bit for bit. Label: OPEN.
- **T4.2 (information equality).** |U| = |A*| under the canonical
  encoding, by construction of U. Label: OPEN (constructional).
- **T4.3 (selection-only carriage).** Installing A* as w0 changes the
  target run's selection order and no score, tally, or scorer input:
  for any fixed configuration sequence, the target run's Cap is
  identical with A*, U, R*, or no artifact installed. Label: OPEN
  (route: §1.3's weights discipline, made a theorem about the target
  harness).
- **T4.4 (null exactness).** Under the null's permutations, the
  permuted artifacts' entry multisets equal A*'s; hence the null
  distribution is over artifacts of identical information content.
  Label: OPEN (constructional).
- **T4.5 (transfer bound).** If the source view satisfies rung 6's
  certificate conditions (T6.1) with margin m, and the target family's
  view admits an embedding of A*'s pattern with distortion at most d
  (both terms defined in rung 6's spec, §5), then ΔT >= m − d in the
  battery's units. Label: PREMISE until rung 6 closes; rung 4's
  empirical claim does not depend on it, and it is never cited as
  evidence for ΔT.
- **T4.6 (carriage replay).** The target run with A* installed is
  exactly replayable from (Ft registration, A*, seed): replay
  reproduces the run's log bit for bit. Label: OPEN.

### 3.5 Falsification, printed in advance

**Rung 4's claim is dead if**, in the registered battery (at least two
(source, target) family pairs, at least one pair sharing no task
generator): ΔT <= δ, **or** any null replicate's ΔT >= the observed
ΔT — pattern-free carriage doing as well as the pattern kills the
claim that structure, rather than information volume, transferred.

## 4. Rung 5 — Compounding over time

**Claim under test (proposed).** Capability is a non-decreasing
function of append-only interaction history length, up to a registered
tolerance, with restart and replay exact by construction — the
governing invariant (F3) as a falsifiable statement.

### 4.1 The capability curve

Fix a system S, a task family, and a checkpoint schedule
t_1 < t_2 < ... < t_m (ticks, registered; m >= 6, spanning at least
two orders of magnitude in log length where the host allows, the
actual span recorded). **Cap(t_i)** is the capability (§1.6) of the
system whose actors' states are derived from the cut L_{t_i} and
which is then scored on the held-out set with **no further
interaction** (evaluation runs are isolated-arm runs seeded from the
cut's derived states). The **capability curve** is the sequence
Cap(t_1), ..., Cap(t_m) with, per checkpoint, the mu and rho of the
cut's interaction view.

### 4.2 Constructional properties (not measurements)

- **Restart exactness.** Killing the run at any tick and restarting
  it from the log alone (no other state) reproduces the uninterrupted
  run's log exactly, record for record, from the restart tick on.
- **Replay exactness.** Replaying L from the empty state reproduces
  every actor's derived state at every checkpoint exactly.
- **No forgetting.** Every actor state at every tick is a function of
  the full cut L_t. The only operation that reduces the influence of
  a past record is an **explicit reweighting**: a registered change to
  w (§1.3), itself appended to the log as a reweight record naming the
  rule and the records it reweights. There is no other deletion,
  decay, or summarization route in a lawful rung-5 run; a run whose
  implementation has one is not a rung-5 run.

These are properties of the construction, verified by the checks of
§4.4 on every battery run, not sampled statistics: a single mismatch
at any record is a failure of the run and of the implementation, and
is reported as such, never averaged.

### 4.3 The monotone compounding claim and its protocol

**Claim.** There exists a registered tolerance ε >= 0 (registered
before the run; ε = 0 is the strong form and is the default unless a
battery argues a positive ε from its scorer's granularity) such that
for all i < j: Cap(t_j) >= Cap(t_i) − ε, **and** Cap(t_m) >
Cap(t_1) + δ (δ by §1.9 from the checkpoint evaluation replicates'
spread) — non-decreasing within tolerance, and strictly compounding
over the full horizon. **Protocol:** each checkpoint's Cap is the
mean of >= 8 isolated evaluation replicates from the cut's derived
states, on the same held-out set for every checkpoint; the working
set is fixed across the horizon (new tasks enter only as appended
log records through the system's own interaction, never by the
battery reaching in); the interaction during the horizon is the live
arm; the three control arms of §1.7 run the same horizon in parallel
registrations, and the claim is stated for the live arm's curve
against each control arm's curve by the same rule (a control whose
curve also satisfies the claim weakens the attribution to
interaction, and the battery report must say so in its headline, not
its footnotes).

### 4.4 Theorem obligations (6)

- **T5.1 (restart exactness).** For every tick, restart-from-log
  reproduces the uninterrupted log suffix exactly. Label: OPEN
  (constructional from §1.2: state is derived, seed is recorded).
- **T5.2 (replay exactness).** Replay reproduces every checkpoint's
  derived states exactly. Label: OPEN (constructional, same route).
- **T5.3 (tally at every cut).** TAL's value at every cut of a rung-5
  log equals DET's from-scratch value at that cut. Label: OPEN — this
  is rung 1's 96 append-cut checks promoted to a theorem over the
  rung-5 log class; rung 2's noisy extension is its sibling, and
  whichever closes second cites the first's proof route.
- **T5.4 (no forgetting).** In a lawful rung-5 implementation, every
  derived state is a function of the full cut, and every influence
  reduction factors through an appended reweight record. Label: OPEN
  — stated over the implementation's derivation graph: the claim is
  that the graph has no edge from a state to anything but the log and
  prior states. Verified by the derivation-graph audit of §6.3 when
  the endgame lands; before that, by construction review recorded in
  the battery record (labeled as review, not proof).
- **T5.5 (curve well-definedness).** Cap(t_i) is independent of the
  evaluation order of checkpoints and of the evaluation replicates'
  interleaving with the horizon run. Label: OPEN (route: evaluation
  runs are isolated and seeded from cuts; cuts are prefixes).
- **T5.6 (mu monotonicity under append).** For cuts t < t' of one log,
  with the battery's fixed axes and contract construction, mu at t'
  is >= mu at t whenever the appended records add hyperedges and
  remove none and Live at t is a subset of Live at t'. Label:
  PREMISE — the antecedent's Live inclusion is the load-bearing
  assumption; the battery measures whether it holds (it is printed
  per checkpoint pair), and any checkpoint pair violating it is
  excluded from the claim's scope by name, never silently.

### 4.5 Falsification, printed in advance

**Rung 5's claim is dead if** any checkpoint pair (i, j), i < j, in
scope for T5.6 shows Cap(t_j) < Cap(t_i) − ε — monotone compounding
fails at that pair and the pair is the counterexample of record —
**or** the strict horizon inequality fails (Cap(t_m) <= Cap(t_1) + δ:
no compounding over the full run), **or** any restart or replay check
mismatches at any record (the constructional claim dies immediately,
independently of the curve).


## 5. Rung 6 — The certificate: emergence decided from structure

**Claim under test (proposed).** There are derived, checkable
conditions on the interaction matrix under which emergence is
guaranteed, and a decision procedure that, given any actor system in
the model, decides whether its interaction yields emergence and by
how much, with a machine-checked certificate.

### 5.1 The emergence predicate, fixed

A system S with log L and interaction view V **exhibits emergence at
margin m** (m a positive rational, registered) iff, in the battery
that produced L: Cap(live) > Cap(control) + m for every control arm
of §1.7, at equal budgets, with the live arm's replicates all above
every control replicate's maximum (the strong form: separation of
replicate sets, not only of means). This predicate is the rung's
ground truth. It is expensive (it is the battery) — the certificate
exists to decide it from structure without running the battery.

### 5.2 The derived conditions

The conditions are stated over the interaction matrix (§1.3) of the
candidate system's **registered probe log**: a log produced by running
S for a registered probe horizon (shorter than a battery horizon,
registered per system class) under the live arm only. Let A = the
probe view's axis set, mu and rho as in F1, and let the probe view's
hyperedges carry their logged weights. The conditions:

- **C1 (engaged weight).** mu(A) >= M1, where M1 is the least total
  engaged weight at which any battery in rungs 2–5 has recorded
  emergence at margin m, minus the greatest total engaged weight at
  which any such battery has recorded no emergence at margin m, must
  be positive — i.e. M1 exists iff the recorded batteries separate.
  M1 is computed from the rung 2–5 battery records by this rule and
  no other; if the records do not separate, C1 is undefined and rung
  6 does not start (named precondition, §5.5).
- **C2 (no dead load).** No axis carrying a hyperedge of weight >=
  M1/2 is emergent-dead in the probe view (F1 §4 definition).
- **C3 (two-sided reach).** Every hyperedge of size >= 2 in the probe
  view is dependence-confirmed in both directions by the exact scan
  (§1.5) — sampled scans certify nothing (§1.5).
- **C4 (cut stability).** For every cut of the probe log at or after
  half the probe horizon, mu over the cut's view is >= M1/2: the
  engaged structure is a property of the system's interaction, not of
  one moment.
- **C5 (margin in rho).** rho(A) exceeds, lexicographically, the
  greatest rho recorded for any no-emergence battery's view in rungs
  2–5 — the refinement coordinate must also separate, so the
  certificate states by how much in both coordinates.

Conditions C1–C5 are **derived** in the only sense this spec allows:
each threshold is computed from the recorded batteries by the stated
rule, and the derivation (the battery records, the arithmetic) is
part of the certificate (§5.4). A threshold chosen by hand voids the
certificate.

### 5.3 The detector as a decision procedure

DECIDE(S, registration) executes exactly:

1. Run the probe (live arm, probe horizon, registered seed) → L.
2. Build the interaction view by §1.3 (exact dependence scan).
3. Evaluate C1–C5 by their definitions (all finite scans over a
   finite view; F1 §3's computability applies).
4. Output EMERGENT(m, rho(A)) if all five hold, NOT-CERTIFIED with
   the list of failed conditions otherwise. NOT-CERTIFIED is not a
   claim of no emergence; it is the absence of a certificate, and is
   reported in those words.

DECIDE terminates on every input: the probe is finite, the view is
finite, every check is a finite scan. Its cost is bounded by the
probe cost plus one dependence scan per probe message plus the view
scans; the bound is printed with each verdict.

### 5.4 The certificate

A certificate for EMERGENT(m, rho) is the tuple (probe log hash,
view, the C1–C5 evaluations with their witnesses — the engaged
hyperedge list, the dead-axis scan, the dependence confirmations,
the per-cut mu values, the rho comparison — and the threshold
derivation: the rung 2–5 battery record identifiers and the
arithmetic producing M1 and the C5 bound). A certificate is checked
by re-running DECIDE steps 2–4 on the hashed probe log and comparing
every field; checking never re-runs the probe and never trusts the
presented view. The Lean form of the certificate is the rung's proof
artifact: the theorems of §5.6 in the program's proof repo, with the
certificate's witnesses as the decidable instances (kernel `decide`
controls, on the F1 precedent).

### 5.5 Precondition

Rung 6 starts only when the rung 2–5 records separate (C1's rule
yields a positive M1 and C5's rule yields a strict bound). If they do
not separate, that is a result about the measure, printed as such:
the interaction matrix, as defined in §1.3, does not determine
emergence at margin m, and the program returns to §1 with the
non-separating batteries as the evidence. This is a designed outcome,
not a failure of nerve: it is the falsification route of §5.7 applied
early.

### 5.6 Theorem obligations (7)

- **T6.1 (soundness).** Any system whose probe view satisfies C1–C5
  exhibits emergence at margin m (§5.1) in its full battery. Label:
  OPEN — the rung's central theorem. Its proof, when it exists, also
  discharges rung 3's T3.8 premise in general form. Until it is
  PROVED, every EMERGENT verdict is labeled with this theorem's state.
- **T6.2 (completeness on the registered class).** Any system in the
  registered system class whose full battery exhibits emergence at
  margin m has a probe view satisfying C1–C5. Label: PREMISE —
  completeness is claimed only over system classes registered in
  advance, and a class registration is itself a battery record. A
  system outside every registered class receives NOT-CERTIFIED or
  EMERGENT by soundness alone, never a completeness-backed reading.
- **T6.3 (decidability).** DECIDE terminates on every lawful input
  and its verdict is a function of (S, registration) alone. Label:
  OPEN (route: §5.3's finiteness, on F1's computability).
- **T6.4 (detector correctness).** DECIDE's C1–C5 evaluations equal
  the from-definitions values on every probe view — the implemented
  detector decides the stated conditions, not approximations of them.
  Label: OPEN (route: agreement battery against an independent
  implementation from this spec alone, on the HMA solver/checker
  precedent, plus the Lean controls of §5.4).
- **T6.5 (margin monotonicity).** If a probe view satisfies C1–C5 at
  margin m, the same view with any hyperedge weight increased (and no
  other change) satisfies C1, C4, C5 at margin m. Label: OPEN (route:
  F1 L1-style monotonicity of mu and rho in engaged weight).
- **T6.6 (certificate checkability).** Certificate checking (§5.4)
  runs in time polynomial in the probe log's size and the view's
  size, and accepts exactly the certificates whose every field
  recomputes. Label: OPEN.
- **T6.7 (reweighting stability).** A selection-only reweighting
  (§1.3: weights change selection, not evidence) of the probe run
  changes no C1–C5 evaluation of the resulting view except through
  the weights the conditions themselves read (C1, C4, C5), and never
  changes a NOT-CERTIFIED verdict into EMERGENT by reweighting alone
  when the underlying dependence structure (C3) and dead-axis
  structure (C2) are unchanged and the weight change is within the
  registered selection band. Label: OPEN — this is the theorem that
  keeps the certificate honest against gaming the weights; its band
  term is defined in the rung-6 battery registration.

### 5.7 Falsification, printed in advance

**Rung 6's claim is dead if** any one of: (a) a single system
satisfies C1–C5 on its probe view and its full battery fails §5.1's
predicate (soundness counterexample — one suffices, and it is
preserved as a standing control in the proof repo); (b) DECIDE's
verdict disagrees with the from-definitions evaluation on any probe
view in the T6.4 agreement battery (the detector, not the theorem,
dies first); (c) the §5.5 precondition fails — the rung 2–5 records
do not separate, so no derived threshold exists. In case (c) the
claim that dies is "emergence is decidable from this interaction
matrix", stated in those words in the program record.

## 6. Endgame — the emergence measure as a derived quantity

**Settled intent.** The emergence measure becomes a first-class
derived quantity in the one derivation machinery, over the same
append-only hypergraph as everything else in Idol, feeding the
parametric model line. This section specifies the interfaces. The
machinery itself (the one derivation machinery, the hypergraph of
F4) is not specified here; what is specified is exactly what the
emergence program publishes into it and consumes from it.

### 6.1 What is derived

For each registered system and each cut of its log, the derivation
machinery derives, as ordinary derived quantities over the
hypergraph view of the cut: Live, engaged, mu, lambda, rho (F1
definitions); the highest minimal axis vector of the cut's view (F1
§4, by the F1 solver's semantics); the load-bearing dispositions of
rung 3 (§2.5) where a rung-3 battery has registered them; the
capability-curve point of rung 5 (§4.1) where a rung-5 registration
covers the cut; and, where rung 6 has closed, the DECIDE verdict and
certificate reference for the system's probe view. Each derived value
carries its premise cone: the log prefix, the registration, and the
theorem pins it rests on. A value whose premises include an OPEN
theorem is derived and labeled with that theorem's state; derivation
does not launder premises.

### 6.2 Incremental derivation, as an interface property

Appending records to a log re-derives only the quantities whose
premise cones meet the appended records (the standing incremental
law: witnesses join, derivations re-derive over their premise cones,
no batch mode underneath). The emergence quantities satisfy this by
TAL's incrementality (T5.3) for mu/rho over cuts, and by the
append-cut structure of F1's scans for the rest; any emergence
quantity whose implementation recomputes from the empty log on an
append is a defect against this interface, recorded as such, however
correct its values.

### 6.3 What the parametric model line consumes

The parametric model line (PDLM; weights as first-class program
values) consumes exactly three interfaces from this program, and no
others:

- **I1 (selection weights).** The derived rho and highest-minimal
  vector of a system's current view, as a weight vector over the
  view's axes, usable as selection weights in the model's derivation
  — selection only (§1.3): the model may order its search by them;
  they enter no score the model reports as evidence.
- **I2 (certificate query).** A query by system identity returning
  the rung-6 verdict (EMERGENT(m, rho) with its certificate
  reference, or NOT-CERTIFIED with failed conditions), checked per
  §5.4 at query time against the current pins. The model may gate a
  composition (rung 3) on a positive verdict; the gate's decision and
  the verdict it read are appended to the consuming run's log.
- **I3 (compounding signal).** The rung-5 capability curve of a
  system, as derived points with premise cones, readable as the
  model's evidence about whether further interaction with that system
  is predicted to compound. A prediction drawn from I3 is labeled
  with the curve's registration and tolerance wherever it is used;
  I3 carries measurements, not the invariant (F3) itself.

No interface in this section lets the consuming side write into the
emergence program's records: consumption is by derivation over the
same hypergraph, and any feedback from the model into a system's
interaction is an ordinary appended record in that system's log,
under that system's registration.

### 6.4 Endgame falsification, printed in advance

**The endgame integration claim is dead if** any derived emergence
quantity (§6.1) differs, on any shared instance, from the standalone
computation of the same quantity (the F1 solver for mu/rho/highest
minimal, DET for the tallies, DECIDE for verdicts) — derivation and
the standalone route must agree exactly, and one disagreement is a
defect in the integration, preserved as a standing control — **or**
any consuming use through I1–I3 is found to let a selection weight
enter a reported score (the §1.3 discipline breached at the
interface).

## 7. Cross-rung discipline (all rungs, restated once)

- Controls: live vs isolated / frozen / shuffled at equal information
  and compute budgets (§1.7, §1.8), plus each rung's added arms.
  Weights change selection, not evidence (§1.3).
- Costs: bandwidth (bits), storage (store), restart, and replay are
  counted separately (§1.8); restart and replay in rung 5 are exact
  or the run fails (§4.2).
- Claims sit at their evidence level: a rung's claim is **proposed**
  in this spec, **implemented** when its battery harness exists,
  **verified** only when its battery has run under its registration
  and its OPEN theorems are PROVED or adopted as PREMISEs by name.
- Falsification conditions are printed in advance per rung (§2.7,
  §3.5, §4.5, §5.7, §6.4) and are not revisable after a battery
  registers; a falsified claim is recorded as falsified, with its
  counterexample preserved, never edited into a weaker claim that
  would have passed.
- Registrations are append-only records in the program's goal
  workspace, written before the battery they govern runs.

## 8. Theorem obligation summary

27 obligations: rung 3 — 8 (T3.1–T3.8; T3.8 PREMISE, the rest OPEN);
rung 4 — 6 (T4.1–T4.6; T4.5 PREMISE until rung 6 closes, the rest
OPEN); rung 5 — 6 (T5.1–T5.6; T5.6 PREMISE, the rest OPEN); rung 6 —
7 (T6.1–T6.7; T6.2 PREMISE, the rest OPEN). No obligation is PROVED
at the writing of this spec; F1's 58 theorems and rung 1's 5 are the
proved base these obligations build on and are not counted here.

## 9. Spec gaps (named, with owners)

- **G1 — DET1/TAL1 published interfaces.** §1.10 consumes the rung-1
  detector and tally through their verified behavior; their exact
  signatures are not yet published as a spec. Owner: the rung-2 lane
  (its noisy extension must fix the signatures it extends). Blocks:
  nothing in this spec's statement; blocks any implementation of
  rungs 3–6 that would otherwise guess the signatures.
- **G2 — dependence scan cost at rung-2 scale.** §1.5's exact scan is
  one suffix replay per message; at hundreds-to-thousands of actors
  over long horizons this may be the battery's dominant cost. The
  spec's answer is the SAMPLED label and its consequences (§1.5),
  which keep sampled quantities out of every theorem and
  certificate. A sublinear exact scan, if one exists, is an open
  problem owned by the rung-2 lane; this spec does not assume it.
- **G3 — system classes for T6.2.** Completeness is over registered
  classes; the registration format for a system class (what makes
  two systems members of one class) is not defined here. Owner: the
  rung-6 lane, before any completeness claim is stated for a class.
- **G4 — the derivation machinery's own interface surface.** §6
  specifies what this program publishes and what the model line
  consumes, in the machinery's standing terms (derived quantity,
  premise cone); the machinery's general publication format is owned
  by the derivation-machinery program, and §6 is written to be
  re-pointed at it when it is named. Owner: parent agent, on the
  machinery program's next record.

## 10. Provenance

Written 2026-11-21 under Chris's 07:40 PST expansion directive.
Builds on F1 (verified, pin above), F2 (verified at its scope), F3
and F4 (settled intent). Everything else in this document is proposed
semantics at spec-first, agent-proof resolution: exact enough that
an implementer implements it or cannot help but implement it, with
its falsification conditions printed before any battery runs.

## 11. Addendum (2026-11-21) — the emergence vector is parametric, solvable, and optimizable

Chris's requirement (2026-11-21 07:46 PST, recorded in the goal
record): the emergence vector is **parametric on any other vector**
— defined over any system's axis/configuration vector, in any
domain; it is a **solvable quantity** — the rung-6 decision
procedure decides it; it is an **optimizable quantity** — a solver
searches for vectors that achieve or maximize it, the
highest-minimal-axis solver being the seed form. This section
states all three at the resolution the rest of this spec holds.
States: §11.1 is **proposed semantics** resting on F1's verified
definitions without modifying them; §11.2 separates what is
decidable on the verified base today from what rung 6 adds;
§11.3's problem is proposed, with its seed instance verified (F1's
solver, at the F1 pin); §11.5 and §11.6 are **registrations** —
proposed domain instantiations under §11.4's form. No battery has
run in either domain, and nothing in this section is a result.

### 11.1 The emergence vector of any instance

Let I = (A, V, C, B, W, F, H, w) be any F1 instance (§0, F1 §1) —
any qualified system in any domain: A its axis set, C the contract
of allowed configurations over the axis vectors, B its behavior
components, F its behavior function, H its hypergraph, w its
weights. No part of what follows mentions actors, messages, or any
domain.

The **emergence profile** of I is the function from the subsets of
A to refinement values: profile(S) = rho(S) = (mu(S), lambda(S))
by F1 §3, for every S a subset of A. The profile is finite — A is
finite by qualification, never by an imposed bound — and
computable from I alone by F1 §3's finite scans.

The **emergence vector** of I, E(I), is the tuple:

- mu(A) and lambda(A): the total emergence and total liveness of
  the full axis set;
- rho-star: the rho of I's highest minimal vector (unique by F1
  T3), and S-star: the highest minimal vector itself, as fixed by
  the deterministic solver rule of F1 §7 — so E(I) is a function
  of I, never an unnamed member of a tied set;
- dead(I): the emergent-dead axes of I (F1 §4), reported
  separately from S-star, per F1's correction;
- the profile itself, carried as a derived object: any entry
  readable on demand, under §6's derivation discipline.

A system's axis/configuration vector in any domain instantiates
(A, C): the axes are the system's named parameters, the contract
the set of its allowed configurations. E is therefore parametric
in exactly the required sense: change the system and its vector,
and E is defined by the same construction, with no domain-specific
case anywhere in this section. An implementation that special-
cases a domain in computing E is a defect against §11.1.

### 11.2 Solvability: the vector is decided, at two levels

**Level one — computing the vector (verified base).** For every
finite instance I, E(I) is computable exactly: Live by F1's pair
scans, engaged and mu by finite sums, S-star by F1's solver
semantics. Termination and exactness rest on F1, verified at its
pin, and are not re-claimed here. In this sense the emergence
vector is a solvable quantity for any system today: given the
instance, the vector is decided by computation, not estimated.

**Level two — deciding emergence from structure (rung 6,
proposed).** DECIDE (§5.3) is restated at this generality. Its
conditions C1–C5 (§5.2) are conditions on the interaction matrix;
for a general instance the matrix is read off (H, w) directly —
entry (b, b') = total weight of hyperedges containing both b and
b', diagonal (b, b) = total weight of hyperedges containing b —
and for actor systems §1.3's view is the instance, so the two
readings agree by construction. Where the system is an actor
system, DECIDE's steps 1–2 produce the instance from the probe
log, as §5.3 states. Where an instance is presented directly,
steps 1–2 are the presentation itself, and C3 reads the dependence
witnesses the presentation carries: an instance presented without
dependence witnesses receives NOT-CERTIFIED on C3, in those words.
Verdicts and certificates are exactly §5.3–§5.4's, unchanged.
What this addendum adds is only the statement that neither the
vector nor the decision is tied to the actor model: the actor
model is one way to present an instance, not a premise of the
definitions.

### 11.3 Optimizability: the emergence optimization problem

**Problem OPT-E.** Input:

- a finite parameter set Theta — finite by qualification: named
  parameters, named ranges;
- a family of instances, one per theta in Theta, given by a
  stated construction (the family's registration: how theta
  determines the instance, and the registration's fixed
  enumeration of Theta);
- a legality predicate K on Theta, decidable: theta is lawful
  iff K(theta) holds. The contract is part of the instance; K
  states any further restriction — budgets, design rules, safety
  bounds;
- a target: ACHIEVE(P), for a stated decidable predicate P on
  emergence vectors, or MAXIMIZE.

**Objective (MAXIMIZE form).** Maximize, over lawful theta, the
headline of E(I(theta)) in the lexicographic refinement order:
first mu of the instance's full axis set, then lambda of it. Ties
break by the registration's enumeration of Theta, earliest first,
mirroring F1 §7's deterministic choice — so the optimum is a
single named theta-star, a function of the input. A family whose
registration wants the highest-minimal headline instead (rho-star
in place of the full-set headline) declares it in its
registration; the two forms are different problems, and a report
names which one it solved. The ACHIEVE form's band predicates —
emergence at or above a floor, named components held dead, a
stated interval on mu — are instances of P, stated in the
registration, not new problems.

**The seed instance (verified semantics).** Take Theta = the
power set of one instance's axis set A; the instance at S is the
sub-instance on axes S (F1's restriction); K(S) = "S is
sufficient" (F1 §4); target MAXIMIZE over minimal sufficient
sets. OPT-E is then exactly the highest-minimal-axis problem,
and its solver is F1's solver at the F1 pin. The general problem
is this problem with the subset lattice replaced by any
registered family: the seed is an instance of OPT-E, not an
analogy for it.

**What a general solver must compute.** (1) E(I(theta)) exactly,
per §11.2 level one, for every theta it reports on — sampled or
estimated vectors support no optimality claim (the §1.5 SAMPLED
discipline, applied to optimization). (2) The argmax under the
stated order and tie-break. (3) A certificate of optimality:
either the full evaluation record over lawful Theta (finite,
hence checkable by re-evaluating any entry), or a pruned record
in which every pruned theta carries a bound argument whose
soundness is proved. The proved bounds available today are F1's
monotonicity (L1: mu and lambda are monotone in the axis set,
for the subset family) and the trivial bound mu(S) <= mu(A) for
S a subset of A. A pruning rule resting on anything else names
its theorem obligation in the family's registration, OPEN until
proved, and the solver's output is labeled with it: an optimality
claim whose certificate contains an unproved pruning is labeled
PREMISE with the obligation named, never verified.

**Falsification of an optimality claim, printed in advance.** A
solver's claim for a family is dead if any lawful theta is
exhibited whose headline is strictly greater in the lexicographic
order than the returned theta-star's, or equal in headline and
ordered strictly earlier by the registered tie-break. The
counterexample is preserved as a standing control beside the
family's registration. For ACHIEVE: the claim "no lawful theta
achieves P" is dead if one lawful theta achieving P is exhibited;
the claim "theta achieves P" is dead if E at theta, recomputed
from the definitions, fails P.

### 11.4 The domain registration form

A domain registers by fixing, in a registration record written
before any battery in the domain runs:

1. the axis set A and each axis's finite value set — the
   system's parametric vector;
2. the behavior components B, each defined as a function of a
   run's observable output;
3. the contract C's shape: which axis vectors are allowed
   configurations, as a decidable predicate or an enumeration
   rule;
4. the instance construction: how a configuration and a run
   determine F, H, and w — for actor domains, §1's construction;
   for others, the domain's stated route, including its
   dependence rule (the analogue of §1.5), stated exactly;
5. what E means in the domain, in the domain's own terms, as a
   reading of §11.1's tuple — a reading, not a redefinition;
6. the domain battery's arms and its falsification condition,
   printed in advance, on the pattern of §2.7, §3.5, §4.5, §5.7.

The vector, the decision procedure, and the optimization problem
do not change per domain (§11.1–§11.3). A domain that needs them
changed has found a spec gap: named in its registration, with an
owner, on §9's pattern.

### 11.5 Domain registration: fuzzing — emergence-guided generation

State: registered here, **proposed**. No battery has run.

- **Axes.** The generation vector of a fuzzing campaign over a
  named target program: seed-corpus selection weights per corpus
  class; the mutation operator mix (weights per operator class);
  mutation depth per generation round; the scheduling rule's
  parameters (energy per corpus entry, as a finite table over
  registered energy levels); grammar production weights where
  the target has a grammar; the splicing rule's parameters
  (donor selection weights; splice-point distribution class).
  Each axis's value set is the finite set in the campaign
  registration — registered discretizations of any continuous
  knob.
- **Components.** The target's behavior components: coverage
  elements (the instrumentation's edge set, quotiented by the
  registration's equivalence — the §1.4 projection choice, named
  in the registration); distinct crash classes (by the signature
  rule the registration states); distinct hang classes (by the
  timeout rule); and any per-input-class outcome classes the
  registration names. Each component is a function of a campaign
  run's observable output: the coverage record and the finding
  log.
- **Contract.** The axis vectors the campaign can actually
  realize within its registered budget vector (§1.8's form:
  input bits generated, target executions, stored corpus bytes,
  rounds), under the target's input validity rules. A
  configuration outside the budget is not in C.
- **Instance construction.** The corpus entries are the actors;
  a campaign round is a tick; the messages are (a) spliced
  fragments passed from donor entries to generated inputs and
  (b) the coverage feedback signal by which one entry's
  discovery changes the scheduling of others. The delivery rule
  is the campaign's scheduler, stated in full in the
  registration. The interaction log is the campaign record:
  round, source entries, generated input, coverage delta,
  findings. F, H, w by §1.3's construction over this log.
  Dependence by §1.5's counterfactual rule, read as: component b
  depends on corpus entry e iff removing e from the corpus and
  replaying the campaign from e's round — seed and all else
  identical — changes b's final value.
- **What E means here.** mu of the full axis set is the total
  weight of behavior components reachable only through
  interaction between corpus entries: coverage and findings
  whose dependence sets contain chains through other entries'
  discoveries — the part of the target's behavior that no
  isolated input's mutation neighborhood reaches. S-star is the
  smallest subset of the generation vector whose variation
  already produces that full jointly-reachable behavior: the
  load-bearing generation knobs and corpus classes.
  Emergence-guided generation is OPT-E over the generation
  vector: steer the campaign toward configurations maximizing
  mu, or achieving a registered target on E, in place of
  steering by coverage alone.
- **Falsification, printed in advance.** The domain claim —
  emergence-guided generation beats interaction-free generation
  at equal budgets — is dead if, in the registered battery (at
  least two target programs; at least 8 replicates per arm;
  budget vectors componentwise equal), the emergence-guided arm
  fails to beat, by the battery's margin (§1.9's rule: the
  controls' own replicate spread), any one of: coverage-guided
  generation with interaction disabled (no splicing, no
  cross-entry scheduling — each entry mutates alone);
  coverage-blind generation at the same budget; or
  shuffled-interaction generation (splicing with seed-permuted
  donors, §1.7's shuffle read on donors) — **or** an ablation
  shows a provably emergent-dead corpus class load-bearing for
  a behavior the battery credited to interaction.
- **Domain spec gap. G5 — rare-event component presence.**
  §11.1 treats each component as an exact function of a run; a
  crash class observed in one replicate and no other has no
  settled presence rule (present in that run's F, absent from
  the battery's component set, or present with a replicate
  count). Coverage components are unaffected. Until G5 closes,
  crash and hang classes are reported per replicate and excluded
  from mu in any fuzzing certificate. Owner: the fuzzing domain
  lane, at its founding. Blocks: fuzzing certificates over
  finding classes; nothing else.

### 11.6 Domain registration: video game NPCs — parametric emergent gameplay

State: registered here, **proposed**. No battery has run; no game
has been built to this registration.

- **Axes.** The parametric configuration vector of a game's NPC
  simulation: per-archetype behavior weights (goal priority
  weights over the registered goal set); perception radii per
  archetype (registered discrete levels); disposition values
  per faction pair (registered levels); communication range and
  rumor fidelity (the gossip channel's parameters — §1.1's
  delivery rule read on the engine); resource scarcity
  parameters (spawn rates and stock levels per resource class);
  population composition (counts per archetype, within the
  registration's totals); interaction rule variants per
  archetype pair (trade / ignore / flee / ally / deceive, as
  finite rule choices). The axis vector is the design vector:
  every entry is a knob a designer may lawfully turn.
- **Components.** Gameplay state variables, each a function of
  a simulated run's observable trace under the registration's
  event classifier: faction control per location (the
  controlling faction, or none); alliance structure class (the
  class of the alliance graph over factions, from the
  registration's finite class list); market state per good
  (price band, from the registration's bands); quest
  availability per quest line (locked / available / completed /
  failed, as trace-derived states); event classes (war
  declared, market crash, ambush occurred, migration occurred
  — each present or absent, by the classifier).
- **Contract.** The design space: the axis vectors the
  registration declares shippable — designer-imposed ranges and
  exclusions, stated as a decidable predicate over the vector.
  Configurations outside it, however emergent, are not in C and
  are not results.
- **Instance construction.** NPCs are actors under §1.1 without
  translation: the engine is the delivery rule (perception,
  rumor, trade, and threat messages delivered by the engine's
  stated rules), and the interaction log is the simulation
  event log. F, H, w by §1.3; dependence by §1.5's counterfactual
  replay of the simulation. Domain precondition: the engine is
  seed-deterministic (the sole source of randomness is the
  seed, §1.1). A nondeterministic engine makes component values
  not functions of the run, and voids the registration until
  fixed.
- **What E means here.** mu of the full axis set is the total
  weight of gameplay components live only through NPC–NPC
  interaction: event classes and state variables that no single
  NPC's or archetype's parameter variation produces — emergent
  gameplay, quantified rather than anecdotally reported.
  S-star is the smallest knob subset whose variation produces
  the full emergent structure: the design's load-bearing knobs,
  the ones a designer must not flatten. Parametric generation
  of emergent gameplay is OPT-E over the design vector with the
  target in its band form: ACHIEVE(P), where P states a
  registered band on E — emergence at or above a floor (a
  living world) with named components held dead (no war class,
  say, in a children's title). The optimizer searches the
  lawful design space for vectors in the band, and §11.3's
  certificate is what makes "this configuration is in the band"
  a checked claim rather than a hope.
- **Falsification, printed in advance.** The domain claim —
  optimizer-selected configurations exhibit more
  interaction-dependent gameplay than hand-tuned or random
  lawful configurations — is dead if, in the registered battery
  (at least two game scenarios; at least 8 simulation
  replicates per arm; equal simulation budgets), configurations
  the optimizer returns for high emergence fail to beat, by the
  battery's margin, the live-versus-control separation (§1.7's
  arms read on the engine: live NPCs against isolated NPCs,
  frozen event replay, and shuffled messages) of configurations
  drawn uniformly from the lawful design space — **or** a
  provably emergent-dead knob is shown load-bearing for an
  event class the battery credited to interaction.
- **Domain spec gap. G6 — the event classifier.** A component
  is a function of a trace only once the registration's event
  classifier is a stated, deterministic function of the trace.
  Where a class is today judged by human playtesting, it is not
  yet a component. Owner: the NPC domain lane, at its founding.
  Blocks: any NPC battery, until each component it scores names
  its classifier. The general machinery needs nothing further:
  §1.4's projection discipline is where the classifier plugs in.

### 11.7 What this addendum does not claim

No domain battery has run. No instance of the optimization
problem beyond the F1 seed has been solved. The decision
procedure at level two (§11.2) is rung 6's proposed procedure,
not an artifact. The addendum's claims are exactly: the vector
is defined for any instance (§11.1 — proposed semantics on a
verified base); computing it is decidable today (§11.2 level
one — verified base); the optimization problem is stated
exactly, with its seed instance verified (§11.3); and two
domains are registered at the resolution §11.4 demands (§11.5,
§11.6), each with the gap it found named — G5, G6 — rather than
smoothed over. Provenance: Chris's requirement, 2026-11-21
07:46 PST; written the same day, spec-first, before any
implementation in either domain.
