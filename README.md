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

**Proposed.** Everything else in SPEC.md: rung 2 (noisy gossip
at scale — its execution is a separate lane), rungs 3–6
(composition, transfer, compounding over time, the certificate),
the endgame interfaces, the optimization problem beyond its
seed instance, and both domain registrations. The spec carries
27 theorem obligations for rungs 3–6; none is proved at this
repo's founding, and the spec says so.

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
