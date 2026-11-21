# Emergence rung 4 — transfer: NO TRANSFER, the claim is falsified as registered in both pairs

Executed 2026-11-21 under the ladder spec
(~/workspace/research/emergence-ladder-spec-2026-11-21.md, §3),
building on the rung-3 machinery. Registration written before
any battery run (append-only, one pre-battery amendment):
~/workspace/emergence-rung4-scratch/registration.md.

**Headline: the transferred interaction structure did not
improve held-out capability at all. In both (source, target)
pairs the A\* arm's capability is bit-identical to every
control's on every replicate: ΔT = 0.000000 exactly, against
δ = 0.049870 (pair 0) and δ = 0.021497 (pair 1). The claim is
falsified under §3.5's first condition (ΔT ≤ δ) in both pairs —
and independently under its second condition, because in both
pairs all 32 permutation-null replicates have ΔT_null ≥ ΔT
(pair 0: 25 nulls at exactly 0, 7 at +0.000729; pair 1: all 32
at exactly 0).** The per-arm decision (the alternative rule,
printed for comparability) is also NO in both pairs, and the
paired per-seed difference vector is identically zero. This is
a printed loss, not a near-win: the transfer effect measured
is exactly zero, not small.

Why it is zero (measured, below): on every one of the 16
target logs, the working-score landscape over configurations
has its maximum at the full configuration or at a
lightest-removal leave-one/leave-two-out neighbor, and every
arm's order — under the registered sum priority, every order
opens with exactly those subsets — evaluates the winner within
budget. All four arms and the unbounded-search diagnostic
select the same subset on every seed. The battery cannot
distinguish "the transferred pattern carries nothing usable"
from "the search-order carriage channel is saturated because
the optimum is order-independent on this system"; both
readings are consistent with the data, and the registered
claim is dead under either.

## Status at a glance

| piece | state |
|---|---|
| pair 0 (field → region) | ΔT = 0.000000, δ = 0.049870 — falsified (both §3.5 conditions) |
| pair 1 (region → field) | ΔT = 0.000000, δ = 0.021497 — falsified (both §3.5 conditions) |
| nulls | 32 per pair; every null ΔT ≥ ΔT in both pairs |
| verification | independent checker: zero failures (counts below) |
| T4.1 extraction determinism | PROVED |
| T4.2 information equality | PROVED |
| T4.3 selection-only carriage | PROVED |
| T4.4 null exactness | PROVED |
| T4.5 transfer bound | PREMISE (stated, not proved — rung 6 only) |
| T4.6 carriage replay | PROVED |
| G2 (dependence-scan cost) | still OPEN, handed to rung 5; nothing sampled used |

## Registration (summary; full text in the scratch registration, landed as rung4/registration.md)

System: the rung-3 level-1 system alone (protocol v3 evidence
gate, N = 256 ring, T = 32, noise drop 0.15 / corrupt 0.15 /
misdeliver 0.10), seeds 2026112101..2026112108, k = 8. Families
unchanged from rungs 2–3: **field** (sinusoid reconstruction)
and **region** (segment classification). Pairs: pair 0 =
field → region, pair 1 = region → field; both pairs share no
task generator; the claim required transfer in both.

View grain: G = 8 contiguous groups of 32. A configuration is a
subset S of groups; the fold admits only records whose true
source group lies in S (a run's own observation is initial
state, present in every fold — the level-1 analog of rung 3's
own-block admission). Components: per-group held-out mean
scores of the fold. Hyperedges: per-tick counterfactual
component sets, tick = scan unit (exact at that unit), weight
= the tick's delivered count. Sensitivity, Live, mu, lambda,
rho computed exactly over all 256 configurations.

Extraction: A\* from the source family's **replicate-1** live
log's interaction view matrix, quotiented by actor names —
entries reindexed by rank order of the diagonal (descending,
ties by ascending index). Canonical encoding: 4 header bytes
(dimension, width, two pad bytes, always zero) + 64 entries at
w bytes each; w = 2 in both pairs, so every artifact is 1,056
bits. Controls: U = A\*'s entries flattened and permuted
(Fisher–Yates, seed 2026112501 + pair); R\* = i.i.d. uniform
entries on {0..max(A\*)} (seed 2026112601 + pair); nothing =
uniform priority, charged a zero artifact of the same size.
Nulls j = 1..32: A\* conjugated by permutation p_j (seed
2026112701 + 1000·pair + j).

Carriage: per target seed, ONE live gossip run; the artifact
never touches the run — arms are paired per seed by
construction (the same log serves every arm). Search: all 256
subsets ordered by priority, first E = 32 evaluated on the
working rows, best working score selected (ties to the
earliest evaluated); capability = the selected fold's
held-out score. Diagnostic (not an arm): unbounded search,
E = 256.

Margin decision (registered, governs): PRIMARY is the spec's
§1.9/§3.3 global δ = max over the three controls of
spread(control). Reason, from the rung-2/3 evidence: no rung-4
control is a replay arm — the rung-2/3 pathology (a control's
spread being cross-draw seed luck from a foreign stream) does
not arise; every arm is a search order over the same per-seed
target logs, so a control's spread measures search-outcome
variability across target draws, the noise the margin exists
to dominate. Printed alongside, neither governing: the per-arm
decision (rung 3's registered rule) and the paired per-seed
difference vector. Pairing decided (rung-3 inherits item 2):
arms ARE paired per seed; task draws are NOT held fixed across
seeds.

Amendment v2 (appended before any battery run, rung-2/3
pattern): the search priority is the **total** submatrix sum
over S×S, not the mean. Measured reason, from the permitted
code-validation smoke at N = 64 (a debugging measurement, not
a battery result): under the mean, every artifact order's head
was the eight singletons (a singleton's priority is its
diagonal, 530..1617 in the smoke field view, against a
full-set mean 2–4× smaller), so all 32 evaluations of every
artifact arm would have been spent on subsets of size 1–3
while the nothing arm evaluates the full configuration first —
the battery would have measured subset-size bias, not pattern.
With the total (entries are naturals, the sum is monotone in
S), every arm's order opens full set → leave-one-outs →
leave-two-outs of least removed mass; only the pattern chooses
within each size class. Everything else unchanged.

G2: remains OPEN. Rung 4 uses no sampled quantity anywhere
(tick-unit scan; G = 8, so sensitivity and deadness are
exact); nothing labeled SAMPLED enters any theorem or
decision, because nothing sampled exists in this rung.

Budgets: per gossip run, steps = 8,192, bits sent =
5,505,024, ticks = 32, records = 16,384 — identical for source
and target runs of both families. E = 32 evaluations per arm
and per null per seed. 1,056 artifact bits charged identically
to every arm (the nothing arm carries a zero filler artifact
of the same size). Costs counted separately (below).

## Source views and artifacts

Field view (replicate 1, the pair-0 source): mu = 11,708,
lambda = 8; components [0.8220, 0.8138, 0.8166, 0.7650, 0.7009,
0.7256, 0.6597, 0.7466]; diagonal [6060, 8250, 5680, 8703,
6975, 9984, 11315, 6512]. Region view (replicate 1, the pair-1
source): mu = 7,018, lambda = 8; components [0.7259, 0.5179,
0.3895, 0.4410, 0.6479, 0.5676, 0.5285, 0.4897]; diagonal
[2639, 3976, 3948, 3944, 3489, 3926, 4813, 3538].

Detector output, both views: **every group is emergent-dead**
— Live of the full set is all 8 components, and removing any
single group changes nothing, because every component is
sensitive to every group somewhere; the minimal sufficient
sets are the 8 singletons and the highest minimal vector is
any singleton at rho (mu, 8). The sensitivity content of the
view is fully redundant at this grain; A\* nevertheless has
rich weight structure (it is a weight matrix, not the
sensitivity relation), and the search below genuinely used
four different matrices per pair — the orders differed; the
selections did not.

Pair 0 A\* (field view, rank order [6, 5, 3, 1, 4, 7, 0, 2];
canonical SHA-256
7e97c5c8fc1681b746cd90ffa17c41b52c8f2e26ac4b2a57445bb8ed62debd20):

    [11315, 8286, 7432, 6552, 5705, 5667, 4790, 4837]
    [8286, 9984, 8266, 7400, 6545, 6092, 5210, 5243]
    [7432, 8266, 8703, 6546, 5679, 4799, 4356, 4377]
    [6552, 7400, 6546, 8250, 6536, 5644, 6060, 4804]
    [5705, 6545, 5679, 6536, 6975, 4797, 5213, 4816]
    [5667, 6092, 4799, 5644, 4797, 6512, 5205, 3925]
    [4790, 5210, 4356, 6060, 5213, 5205, 6060, 3911]
    [4837, 5243, 4377, 4804, 4816, 3925, 3911, 5680]

Pair 1 A\* (region view, rank order [6, 1, 2, 3, 5, 7, 4, 0];
canonical SHA-256
58ab6643e10af0374bca6642c3f0f28e58c7996eb88ec7d72b8f0ed2da3db31f):

    [4813, 2668, 3068, 2636, 1754, 1760, 2179, 1325]
    [2668, 3976, 1776, 3085, 1324, 1330, 1327, 1761]
    [3068, 1776, 3948, 2196, 1760, 2206, 2199, 885]
    [2636, 3085, 2196, 3944, 1757, 1763, 2186, 1322]
    [1754, 1324, 1760, 1757, 3926, 2643, 1758, 1754]
    [1760, 1330, 2206, 1763, 2643, 3538, 1773, 1329]
    [2179, 1327, 2199, 2186, 1758, 1773, 3489, 877]
    [1325, 1761, 885, 1322, 1754, 1329, 877, 2639]

Artifact sizes: |A\*| = |U| = |R\*| = |zero| = 1,056 bits in
both pairs (checker-verified on the persisted encodings; U's
and every null's entry multiset equals A\*'s, also
checker-verified).

## Results

Raw capabilities (identical for star, unstructured, random,
and nothing, on every seed — that identity IS the result):

Pair 0 (field → region), caps by seed 2026112101..108:
[0.542098, 0.571244, 0.553109, 0.586788, 0.591969, 0.556347,
0.568005, 0.576425]. Mean (every arm) 0.568248. Spreads:
unstructured 0.049870, random 0.049870, nothing 0.049870 (the
controls' spreads coincide because their caps coincide).
**ΔT = 0.000000, δ = 0.049870 → ΔT ≤ δ: falsified.** Nulls:
25 of 32 at ΔT_null = 0.000000, 7 at +0.000729, max +0.000729 —
all 32 ≥ ΔT → **falsified under the null condition too.**
Per-arm decision: NO. Paired differences: [0, 0, 0, 0, 0, 0,
0, 0].

Pair 1 (region → field), caps by seed: [0.756254, 0.758699,
0.754621, 0.769192, 0.766876, 0.775854, 0.754357, 0.772878].
Mean (every arm) 0.763591. Spreads: 0.021497 for all three
controls. **ΔT = 0.000000, δ = 0.021497 → falsified.** Nulls:
all 32 at ΔT_null = 0.000000 — all 32 ≥ ΔT → **falsified under
the null condition too.** Per-arm decision: NO. Paired
differences: all zero.

Selected subsets. Pair 1: every arm, every null, and the
ceiling select the full configuration (mask 255) on all 8
seeds — the full fold is the strict working-score argmax on
every field target log. Pair 0: every arm and the ceiling
select [255, 255, 254, 254, 255, 255, 239, 238] across the 8
seeds (254 = drop group 0; 239 = drop group 4; 238 = drop
groups 0 and 4 — on those seeds a lightest-removal neighbor
edges the full fold's working score by 0.002–0.031). The only
deviations anywhere in the battery: 7 of pair 0's 32 nulls
select 239 instead of 238 on seed 2026112108 (their
conjugation pushed the {drop 0, 4} subset past position 32
while {drop 4} stayed inside), each worth +0.000729 of mean
ΔT_null — the null distribution's entire positive mass, and
it sits above the observed ΔT of 0.

## The mechanism (measured)

The search did real work — in pair 0 it improved on the raw
full-fold run on 4 of 8 seeds (e.g. seed 2026112104: run cap
0.5803 → selected 0.5868) — but it did the *same* work under
every artifact. The configuration landscape of this system,
at this grain, is dominated by the top of the sum-priority
order: more admitted reports help almost everywhere, so the
working-score argmax over all 256 configurations is the full
set or a lightest-removal neighbor on all 16 target logs, and
amendment v2's order — deliberately built so that only the
pattern chooses *within* a size class — evaluates that winner
within the first 32 under every artifact, including the
pattern-destroyed and random ones. The unbounded diagnostic
(E = 256, nothing order) selects identically on all 16 seeds,
so the zero is not an E = 32 budget artifact within this
configuration family: no search budget distinguishes the arms
here, because the thing the orders disagree about (which
interior subsets to try first) never decides the winner.

Two honest readings, both consistent with everything above:
(a) the source interaction pattern, quotiented to an 8×8
weight matrix, carries no information that improves
configuration selection in a disjoint family; (b) the
carriage channel itself — selection order over group subsets
— has no bandwidth on a system whose optimum is the full
configuration, so no pattern, however informative, could have
registered. The registered claim required ΔT > δ and ΔT above
every null; it received ΔT = 0 and nulls at or above it. The
claim is dead as registered under either reading. A future
transfer test that wants to separate (a) from (b) needs a
configuration family whose optimum is interior, or a
different lawful carriage channel — registered in advance,
not improvised here.

## Verification (independent checker, separate code path)

~/workspace/emergence-rung4-scratch/check4.py imports nothing
from the harness and recomputes from the persisted artifacts
only. Zero failures:

- 16/16 gossip runs: budget shape (steps 8,192; bits sent
  5,505,024; records 16,384), replay to the recorded final
  hash, and final DET = TAL agreement with the harness's
  online tally.
- DET = TAL at 96/96 registered append cuts (6 per run: every
  4,096 records, the first three tick boundaries, the final).
- Restart exactness 48/48 (cuts at ticks 8/16/24, both
  families).
- Views recomputed from the replicate-1 logs agree with the
  harness's persisted views on matrix, components, mu, lambda,
  and the dead set, in both families.
- Per pair: extraction agreement (A\* recomputed from the
  checker's own source matrix equals the persisted artifact),
  canonical-encoding hash agreement, artifact size equality,
  entry-multiset equality for U and all 32 nulls.
- Search agreement: 296 searches per pair (4 arms + 32 nulls
  + ceiling, × 8 seeds) recomputed from the persisted target
  logs and artifacts — order prefixes, evaluated working
  scores, selected subsets, and capabilities all exact; max
  absolute difference 0.0. The per-subset working score table
  of each target seed is one artifact-free table, recomputed
  once and checked against every arm's recorded evaluations
  (the selection-only spot property).

Costs (counted separately, never in a decision): bits
delivered per run 4,644,528–4,707,696 (field) and
4,663,680–4,698,624 (region); persisted log 4,727,411–
4,743,656 bytes (field) and 4,566,658–4,575,652 bytes
(region); view construction 4.92 s (field) and 3.70 s
(region); restart prefixes at ticks 8/16/24 run 1.24–1.27 /
2.38–2.46 / 3.49–3.61 MB with fold costs 9,491–9,661 /
22,637–23,098 / 37,614–38,172 steps across both families.

## Theorems

Lean 4.19.0, core only, cold compile clean
(~/workspace/emergence-rung4-scratch/lean/EmergenceRung4.lean
at the landed revision). The word "sorry" occurs once in the
file, in the header comment; no theorem depends on sorryAx,
and every printed axiom set is inside {propext, Quot.sound}.

- **T4.1 extraction determinism — PROVED.** The matrix is
  additive over edge-list concatenation (entry append lemma);
  the rank order is a defined function of the diagonal and a
  permutation of the index list (rank permutation lemma); the
  artifact is a composition of those functions, so equal
  views give equal artifacts (extraction determinism).
  Axioms ⊆ {propext, Quot.sound}.
- **T4.2 information equality — PROVED.** The canonical bit
  size factors through the entry count and the maximum entry;
  a permutation of the entries preserves both (length and
  fold-max permutation lemmas), so U has exactly A\*'s bit
  size for any width function. Axioms {propext}.
- **T4.3 selection-only carriage — PROVED.** Capability
  factors through the evaluated configuration sequence and
  the artifact-free score table: artifacts inducing the same
  evaluated sequence give the same capability, and the
  selected configuration is always an evaluated one attaining
  the sequence's best score (selection specification lemma).
  Axioms ⊆ {propext, Quot.sound}.
- **T4.4 null exactness — PROVED.** Every entry count is
  preserved under a permutation of the entries; the nulls'
  entries are a permutation of A\*'s by construction
  (checker-verified on the persisted artifacts), so their
  entry multisets equal A\*'s. Axioms {propext}.
- **T4.5 transfer bound — PREMISE.** Stated as a definition
  only; not proved, not an axiom, depended on by nothing.
  Discharged, if ever, only by rung 6. Never cited as evidence
  for the measured transfer (there is none to cite it for).
- **T4.6 carriage replay — PROVED.** A run's state is the
  fold of its log; folding a concatenated log is folding the
  prefix and continuing (restart form), so the target run
  with A\* installed is exactly replayable from
  (registration, A\*, seed). Axioms ⊆ {propext, Quot.sound}.

## Verified vs claimed

Verified by execution in this lane: the two falsified
decisions and every number above them (battery + independent
checker, zero failures); the selection-identity mechanism
(picks and the ceiling diagnostic read off the persisted
search records, themselves checker-recomputed); the six
theorem dispositions (cold compile + printed axioms).
Claimed by nothing: no transfer effect (measured zero); no
reading of the zero is promoted over the other; T4.5 stays a
premise; G2 stays open. The detector outputs (mu, lambda,
dead sets) are reported as computed — at this grain they say
the sensitivity structure is fully redundant, which is a fact
about the view, not a claim about the system.

## Rung 5 inherits

1. The falsified rung-4 claim with its exact vectors: ΔT = 0
   in both pairs, δ = 0.049870 / 0.021497, nulls at or above
   ΔT everywhere (25/7 split in pair 0; 32 at exactly 0 in
   pair 1). Any future transfer claim starts from a printed
   zero, not from an unmeasured hope.
2. The channel-saturation finding: on this system the
   configuration landscape's optimum is the full configuration
   or a lightest-removal neighbor on every measured log, so a
   search-order carriage channel cannot register *any*
   pattern. A retest needs a configuration family with an
   interior optimum, or a different lawful channel — decided
   and registered in advance.
3. Grain saturation of the measure: at G = 8 over N = 256,
   every group is emergent-dead in both families' views (Live
   is everything under every leave-one-out; every singleton
   is minimal sufficient). Rung 5's checkpoint views must be
   grained knowing the measure saturates here — the mu curve
   over checkpoints will be flat at this grain unless the
   grain or the component definition changes, and that choice
   is a registration decision, not a discovery to make
   mid-battery.
4. The compounding infrastructure, verified a third time:
   restart exactness is constructional (48/48 here), DET =
   TAL at every registered cut (96/96), replay exact on every
   run (16/16). Rung 5's restart/replay obligations start from
   machinery that has now passed three independent checkers.
5. Gate-constant sensitivity, inherited a third time: the
   v3 evidence gate's constant (≥3) is still the only one ever
   measured; rung 4 inherited the protocol unchanged and its
   systems' behavior at other constants is unmeasured.
6. G2 (exact dependence-scan cost at scale) still OPEN;
   rung 4 used no sampled quantity. Rung 5 owns the next
   statement of it.
7. T4.5 remains PREMISE, joining T3.8 and (ahead) T5.6 in
   rung 6's debt; the endgame interfaces stand as specced —
   I1 selection weights (selection only, never evidence) now
   carries a measured zero as its first transfer datum.

## Files

- Registration (with amendment v2):
  ~/workspace/emergence-rung4-scratch/registration.md —
  landed as rung4/registration.md in the repo.
- Harness: ~/workspace/emergence-rung4-scratch/harness4.py —
  landed as rung4/harness4.py.
- Checker: ~/workspace/emergence-rung4-scratch/check4.py —
  landed as rung4/check4.py.
- Lean: ~/workspace/emergence-rung4-scratch/lean/
  EmergenceRung4.lean — landed as rung4/EmergenceRung4.lean.
- Results (full logs stay in scratch, regenerable from the
  landed harness at the registered seeds):
  ~/workspace/emergence-rung4-scratch/results/ — compact
  summaries landed under rung4/results/.
- This record: ~/workspace/research/
  emergence-rung4-2026-11-21.md — landed as RUNG4.md.

## Premise audit addendum (2026-11-21)

The derivation-graph audit named at rung 6 has been executed;
its record is ~/workspace/research/emergence-premise-audit-2026-11-21.md.
Outcome for this rung's premise list: **T4.5 stays PREMISE.**
Its antecedent is rung 6's certificate conditions, whose
threshold does not exist because the rung 2–5 records do not
separate; the audit's section 4 names exactly what would
discharge it (the soundness theorem proved, the embedding
terms formalized, a separating record set). No other line of
this record changes, and the falsified claim above stands as
recorded.
