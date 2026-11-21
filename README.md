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
- RUNG5.md — rung 5 (compounding over time) executed: the
  registration, both families' raw replicate curves, the
  decision under both rules, the scope collapse and the
  attribution counterexample, the Lean dispositions, and what
  rung 6 inherits. The code, registration, proof file, and
  result artifacts are under rung5/.
- RUNG6.md — rung 6 (the certificate) executed: the
  registration, the threshold derivation over the rung 2–5
  records and its failure, DECIDE's verdict on every
  registered instance, the certificate format and the
  independent checker's results, the Lean dispositions, the
  premise debt carried, and the ladder's final state. The
  decider, checker, registration, proof file, and result
  artifacts are under rung6/.

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
  premise, unproved — the premise audit of 2026-11-21, in
  the audit directory, traced its discharge route to rung
  6's soundness theorem and it stands as a premise still).
  The rung's capability claim itself is
  NOT in this list: it is falsified, next section.
- Rung 4 — transfer, executed (RUNG4.md): the verification
  stack under the rung is verified — 16 gossip runs
  replay-exact against an independent checker, 96/96 append-cut
  DET=TAL agreements, 48/48 restart agreements, extraction and
  artifact facts (bit sizes, entry multisets, canonical
  hashes) verified on the persisted artifacts, 592 searches
  recomputed exactly with max difference 0.0 — and 5 of the
  rung's 6 Lean obligations are proved (T4.5 stands as a named
  premise for rung 6, unproved — the 2026-11-21 premise audit
  traced its discharge route and it stands as a premise
  still). The rung's transfer claim
  itself is NOT in this list: it is falsified, next section.
- Rung 5 — compounding over time, executed (RUNG5.md): the
  verification stack under the rung is verified — 80 runs
  replay-exact against an independent checker, 640/640
  append-cut DET=TAL agreements at the checkpoints, 512/512
  restart agreements, 16/16 checkpoint views and 16/16
  reverse-order evaluations recomputed exactly — and 4 of
  the rung's 6 Lean obligations are proved (T5.4 stands as a
  premise by construction review, its content verified by
  the 2026-11-21 premise audit in the audit directory; T5.6
  was discharged by that audit — proved in conditional form
  for the concrete measure, in the audit directory's Lean
  file). The rung's compounding
  claim itself is NOT in this list: it is falsified, next
  section.
- Rung 6 — the certificate, executed (RUNG6.md): DECIDE, the
  exact decision procedure of SPEC.md section 5, is built and
  verified at every point its tests reach — an independent
  checker (no shared code with the decider) re-derived the
  threshold computation and compared every field of all 25
  certificates with 0 failures; the constructed fixture
  battery passes 7/7 under both implementations, including a
  positive instance the procedure certifies; 50 registered
  band reweightings flip no verdict; and the Lean kernel
  model proves T6.3 (decidability), T6.4's Lean half (seven
  kernel controls), T6.5 (margin monotonicity), T6.6
  (certificate checkability), and T6.7 in scoped form, with
  T6.1 and T6.2 standing as named premises depended on by
  nothing. The rung's precondition over the ladder's records
  is NOT in this list: it fails, next section.

**Falsified.** Rung 2's claim (noisy gossip at scale, executed
in its own lane; record in the program's research archive,
not in this repo): NO WIN at the registered margin in every
decision battery — MAIN v1, MAIN2 v2, MAIN3 v3, and PROBE v3
all decided against the live arm at the margin the frozen
control's spread set. The narrower fact stands that the v3
code's live arm beats every control mean and every control
replicate at both scales.

Rung 3's claim Rung 3's claim (SPEC.md section 2.2): in both
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

Rung 5's claim (SPEC.md section 4.3): capability does not
compound over time in the registered sense — NO COMPOUNDING.
In field, the live arm's mean horizon gain is 0.135138
against the registered margin δ = 0.333693 (and δ_g =
0.384999 under the global rule), both set by the frozen
control's spread, so the strict-gain conjunct fails under
both rules. In region the gain conjunct passes (0.246762
against δ = 0.082254), but the monotonicity conjunct is
vacuous — the T5.6 antecedent fails at all 28 checkpoint
pairs, so no pair is in scope — and the frozen control
satisfies both conjuncts (gain 0.253562), so the gain is not
attributable to live accumulation. The claim required both
families and is dead as registered. The loss is printed in
RUNG5.md with the exact curves, and it stands until a
same-contract re-measure at a current pin says otherwise.

Rung 6's precondition (SPEC.md sections 5.5 and 5.7(c)): the
rung 2–5 records do not separate under DECIDE's conditions.
No battery in rungs 2–5 recorded emergence under its
registered rule, so the emergence side of the threshold
derivation is empty and M1 does not exist; DECIDE issues
NOT-CERTIFIED for all 25 registered view instances, in
agreement with every battery outcome. The failure survives
the most generous re-reading of the rung-2 evidence: even
granting the small battery emergence against its only
control, the candidate M1 is 1,961 − 46,527 = −44,566, not
positive. The claim "emergence is decidable from this
interaction matrix," as a claim about these records, is
falsified with it. The full derivation is printed in
RUNG6.md, and it stands until a new battery — pre-registered
margin, persisted views — separates at a current pin.

**Proposed.** What remains of SPEC.md: the endgame
integration — the certificate query (interface I2) exists as
the standalone DECIDE artifact of rung 6 but is not a derived
quantity in any derivation machinery, and interfaces I1
(selection weights) and I3 (compounding signal) stand as
measured data and a falsified claim respectively, not as
interfaces; the optimization problem beyond its seed
instance; and both domain registrations. The spec carries 27
theorem obligations for rungs 3–6; rung 3's eight, rung 4's
six, rung 5's six, and rung 6's seven are dispositioned above
and in RUNG3.md / RUNG4.md / RUNG5.md / RUNG6.md. Three
premises remain open across the ladder — rung 3's deadness
obligation, rung 4's structure obligation, and rung 5's
view-determination obligation. The derivation-graph audit
of SPEC.md section 6.3 was executed on 2026-11-21 (the
audit directory and its record): it discharged rung 5's
compounding obligation and traced each remaining premise
to the exact link its discharge still needs.

**The ladder is complete.** Six rungs executed; every
registered capability claim falsified by its own battery;
the measurement and certification stack verified end to end;
no emergence found in any system the ladder tested. Any
continuation is a new battery under a new registration, not
a reinterpretation of these records.

**Not claimed.** Emergent intelligence, at any rung. That
DECIDE would certify a real positive instance — its positive
fixture is constructed. The general form of T6.7's band
stability at thresholds that exist. Any
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
