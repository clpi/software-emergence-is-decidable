# software-emergence-is-decidable

Emergence from actor interactions, made a quantity: for any
qualified system — named axes, a contract of allowed
configurations, behavior components, and a hypergraph joining
the components — the emergence vector is defined parametrically
over the system's own axis vector, in any domain. It is solvable:
the vector is computed exactly by finite scans, and a decision
procedure with machine-checked certificates decides emergence
from structure. It is optimizable: a solver searches a system's
parameter space for vectors that achieve or maximize emergence,
with the highest-minimal-axis solver as the verified seed form.

Program of record in Idol Frontier: **Derive and test useful
emergence from actor interactions** (goal goal_d8666507a5fa).

## Contents

- SPEC.md — the ladder spec at agent-proof resolution: the
  shared definitions (actor system, append-only interaction log,
  the interaction matrix as a hypergraph view, capability,
  control arms, budgets, the decision rule), rungs 3–6 each with
  its theorem obligations and its falsification condition
  printed in advance, the endgame interfaces, the spec gaps
  G1–G4, and the §11 addendum: the emergence vector parametric
  over any system, its solvability at two levels, the emergence
  optimization problem stated exactly, and the first two domain
  registrations — fuzzing and video game NPCs — with their gaps
  G5 and G6.
- PROGRAM.md — the program record: Chris's directives in his
  words, the ladder, the discipline, and the state of each rung.
- RUNG3.md — rung 3 (composition) executed: the registration,
  both batteries' raw replicates, the decision, the ablation,
  the Lean dispositions, and what rung 4 inherits. The code,
  registration, proof file, and result artifacts are under
  rung3/.
- RUNG4.md — rung 4 (transfer) executed: the registration, both
  pairs' raw replicates, the decision, the selection-identity
  mechanism, the Lean dispositions, and what rung 5 inherits.
  The code, registration, proof file, and result artifacts are
  under rung4/.

## State, plainly

**Verified.**

- Rung 1 — the detector and the incremental tally over the
  interaction matrix as a reweightable view of the append-only
  hypergraph: five Lean theorems and 96 append-cut checks; the
  XOR instance scores 4/4 live against 2/4 for the best isolated
  or frozen control. Scope, in Chris's own framing: this
  verifies the detector and the tally — NOT emergent
  intelligence.
- The base measure — the emergence measure, liveness, the
  refinement vector, and the highest minimal vector, with 58
  theorems — is proved at its own home,
  clpi/software-has-a-highest-minimal-axis at
  63d9d3fdce1f81c81cd5cda2bd9850b0c1494646, cold gate PASS. This
  repo builds on it and does not restate or re-prove it.
- Rung 3 — composition, executed (RUNG3.md): the verification
  stack under the rung is verified — 336 runs replay-exact
  against an independent checker, 2352/2352 append-cut DET=TAL
  agreements, 672/672 restart agreements, the second-order
  tally composition on every run, budgets componentwise equal
  on every run — and 7 of the rung's 8 Lean obligations are
  proved (T3.5 in conditional form; T3.8 stands as a named
  premise, unproved). The rung's capability claim itself is
  NOT in this list: it is falsified, next section.
- Rung 4 — transfer, executed (RUNG4.md): the verification
  stack under the rung is verified — 16 gossip runs
  replay-exact against an independent checker, 96/96 append-cut
  DET=TAL agreements, 48/48 restart agreements, extraction and
  artifact facts (bit sizes, entry multisets, canonical
  hashes) verified on the persisted artifacts, 592 searches
  recomputed exactly with max difference 0.0 — and 5 of the
  rung's 6 Lean obligations are proved (T4.5 stands as a named
  premise for rung 6, unproved). The rung's transfer claim
  itself is NOT in this list: it is falsified, next section.

**Falsified.** Rung 3's claim (SPEC.md section 2.2): in both
registered families the joint system failed to beat at least
one control arm by the registered margin — NO WIN in field3
and NO WIN in region3, under the registered per-arm rule and
under section 1.9's global delta alike. The joint system has
the highest mean capability of all eight arms in both families
and beats the frozen-partition, isolated, and shuffled arms
beyond their spreads; it does not beat level-1 alone beyond
flat's spread. The loss is printed in RUNG3.md with the exact
decision vectors, and it stands until a same-contract
re-measure at a current pin says otherwise.

Rung 4's claim (SPEC.md section 3.2): the transferred
interaction structure improved held-out capability by exactly
zero. In both registered pairs (field → region and
region → field) the A* arm's capability is bit-identical to
every control's on every replicate — ΔT = 0.000000 against
δ = 0.049870 (pair 0) and δ = 0.021497 (pair 1) — and all 32
permutation-null replicates in each pair have ΔT_null ≥ ΔT, so
the claim is falsified under both of section 3.5's conditions,
in both pairs, under the registered global-δ rule and the
per-arm rule alike. Every arm and the unbounded-search
diagnostic select the same configuration on every seed: on
this system the configuration landscape's optimum is the full
configuration or a lightest-removal neighbor, and the
search-order carriage channel cannot register any pattern.
The loss is printed in RUNG4.md with the exact vectors, and it
stands until a same-contract re-measure at a current pin says
otherwise.

**Proposed.** Everything else in SPEC.md: rung 2 (noisy gossip
at scale — its execution is a separate lane), rungs 5–6
(compounding over time, the certificate),
the endgame interfaces, the optimization problem beyond its
seed instance, and both domain registrations. The spec carries
27 theorem obligations for rungs 3–6; rung 3's eight and rung
4's six are dispositioned above and in RUNG3.md / RUNG4.md, and
the rest are unproved, as the spec says.

**Not claimed.** Emergent intelligence, at any rung so far. Any
result in fuzzing or in NPC gameplay — no battery has run in
either domain. Any optimality result beyond the seed instance.
A claim in this program sits at its machine-checked evidence
level, and the falsification condition of every claim is printed
before its battery runs.

## The discipline

Live interaction is compared against isolated actors, frozen
replay, and shuffled messages, at equal information and compute
budgets. Weights change selection, not evidence. Bandwidth,
storage, restart, and replay costs are counted separately.
Four states in prose — settled intent, proposed, implemented,
verified — never blurred.
