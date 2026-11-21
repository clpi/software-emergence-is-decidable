# Emergence premise audit — the derivation-graph audit (2026-11-21)

Program: **Derive and test useful emergence from actor interactions**
(the emergence goal). Spec: the emergence ladder spec
(~/workspace/research/emergence-ladder-spec-2026-11-21.md). Repo:
clpi/software-emergence-is-decidable at
cddf398adceac41c4c171b8b012d9dc07af7e7f5 at the audit's opening.

## What this audit is

Rung 6 closed with four carried premises — T3.8, T4.5, T5.6, and
T5.4 — and named their discharge route: the derivation-graph
audit of the spec's endgame section. This record is that audit,
executed. For each premise the audit traces the premise's
derivation graph — the statements, definitions, and records the
premise rests on, in order — and then attempts the discharge at
the end of the chain.

The discharge rule, stated before any attempt: a premise is
discharged only by a kernel-checked proof (Lean 4.19.0,
core-only, cold build clean, no sorry, axioms within
{propext, Quot.sound}). Evidence, execution, and argument can
verify a premise's content and can name exactly what a proof
still needs; they do not discharge it.

Scope boundary, absolute: no battery outcome is reinterpreted
anywhere in this record. Every registered capability claim in
rungs 2–6 was falsified as registered and stays falsified. This
audit is only about the four premises' proof status.

## Result in one paragraph

One premise is discharged: **T5.6**, proved in Lean for the
concrete measure (section 3). Three stay premises, each with
its derivation graph traced to the exact link that does not
exist and a named statement of what would discharge it:
**T3.8** and **T4.5** both hang from rung 6's soundness theorem
T6.1, whose threshold derivation failed at rung 6 because the
rung 2–5 records do not separate (section 4); **T5.4**'s audit
was executed in full and its content verified on the persisted
artifacts, but the claim quantifies over any lawful rung-5
implementation's derivation graph, and the spec's own route
discharges it through this audit only when the endgame's
derivation machinery has landed — it has not (section 5).
Premise debt after this audit: three of the original four.

## 1. Method

For each premise: (a) the statement, quoted from the spec;
(b) the premise as it stands in its rung's Lean file (in each
case a definition stating the premise, proved by nothing,
depended on by nothing); (c) the discharge route the spec and
the rung records name; (d) the derivation graph — every node
the discharge would have to pass through, with each node's
state (proved, measured, failed, absent); (e) the attempt and
its outcome.

Toolchain for every proof below: Lean 4.19.0 at the pinned
local toolchain, core only (no Mathlib), single-file cold
compiles, axiom audits printed from the same files that carry
the proofs.

## 2. The four derivation graphs, traced

**T5.6** (rung 5, mu monotonicity under accumulation) rests on:
the definition of mu as a sum of positive weights over engaged
edges (F1) → monotonicity of such a sum under family inclusion
→ the antecedent (no edge removed, live set grows) as a
measured per-pair fact. Every node exists: F1's machinery is
proved, the sum monotonicity is elementary, and the antecedent
was measured at rung 5 (it held at exactly 1 of 56 checkpoint
pairs). The only missing node was the implication itself,
stated in the rung-5 Lean file over an abstract mu function —
a form no proof can discharge, since an arbitrary function
satisfies no monotonicity. Discharging the premise therefore
means proving the implication for the concrete measure.
Attempted in section 3: **discharged**.

**T3.8** (rung 3, no free capability) rests on: the spec's own
label — discharged, if ever, only by rung 6's T6.1 in general
form → T6.1 (soundness: a view satisfying conditions C1–C5
exhibits emergence at margin m in its full battery) → C1's
threshold, derived from the rung 2–5 battery records by the
registered rule → those records separating (some battery
recording emergence at margin m). The last node **failed**:
rung 6 derived the thresholds from the records and the records
do not separate — the emergence side of the derivation is
empty, the threshold does not exist, and DECIDE issued
NOT-CERTIFIED for all 25 registered view instances. The chain
is broken at its first link, two levels below T3.8. Attempted
in section 4: **stays a premise**.

**T4.5** (rung 4, transfer bound) rests on the same chain, one
edge shorter: its antecedent is literally "the source view
satisfies rung 6's certificate conditions with margin m" —
the conditions whose threshold does not exist. Attempted in
section 4: **stays a premise**.

**T5.4** (rung 5, no forgetting) rests on: the rung-5 harness's
derivation graph — the claim is that the graph has no edge
from a derived state to anything but the log and prior states,
and that every influence reduction factors through an appended
reweight record → the audit of that graph (this record,
section 5) → and, for a discharge rather than a verification,
either the endgame's derivation machinery carrying the graph
with premise cones (the spec's stated route: the audit
discharges T5.4 "when the endgame lands") or a formal model of
the graph inside Lean. The audit node is executed here in
full; the machinery node is **absent** (rung 6: the certificate
query exists as a standalone artifact only; the endgame's
derived-quantity claim remains proposed). Attempted in
section 5: **stays a premise**, with its content verified.

## 3. T5.6 — DISCHARGED

The proof, in the audit Lean file (landing in section 6):

- The measure is defined concretely: mu of an edge family is
  the sum of the family's weights; the engaged part of a
  family at a live set is the subfamily of edges lying
  entirely inside the live set. This is F1's definition, the
  same form the rung-3 file proved its conditional T3.5 over.
- The workhorse lemma: over a duplicate-free family,
  membership inclusion of families gives the weight
  inequality. (A member splits its list; the rest of the
  smaller family lands in the two remaining parts; the sums
  compare term by term. No positivity assumption is needed —
  weights are naturals.)
- Engaged monotonicity follows: an edge engaged at the
  earlier cut is a member of the later family and lies inside
  the later live set, so the earlier engaged family is a
  membership subfamily of the later one.
- The closing theorem is the premise's own implication with
  mu instantiated to the concrete measure: for any two cuts
  i ≤ j, if every edge of cut i is a member of cut j's family
  and every live component of cut i is live at cut j, then
  mu at i ≤ mu at j.

Gate result: cold compile of the single file under Lean
4.19.0, core only — exit 0, no errors, no sorry (the one
occurrence of the word in the file is the header's "no
sorry"). Printed axioms: the split lemma depends on
{propext} alone; the sum lemma, the engaged bound, and the
closing theorem each depend on {propext, Quot.sound} — all
inside the allowed set.

One hypothesis is named in the proof, not hidden: the
duplicate-free edge family. In the rung-5 instrument it is
constructional — the view carries one edge per tick and ticks
are distinct — and the battery's own scope table is stated
over edge sets, which is the same fact. The premise's
antecedent is otherwise the premise's own, unchanged.

What the discharge does and does not say. The implication is
now a theorem: whenever the antecedent holds between two
cuts, mu does not decrease. The antecedent's truth per
checkpoint pair remains the battery's measurement, and it
held at exactly one of 56 pairs (field, ticks 1 to 2) — the
theorem's scope in this instrument is exactly as narrow as
rung 5 measured, and nothing about the falsified compounding
claim changes: the claim died on its horizon margin and its
attribution, not on this implication.

Disposition: T5.6 moves from PREMISE to PROVED (conditional
form, concrete measure) in the rung-5 record's premise list,
by addendum; the rung-6 debt list is amended by addendum from
four carried premises to three.

## 4. T3.8 and T4.5 — STAY PREMISES

The two premises share one root, so one graph serves both;
their distinct ends are stated separately.

The root: T6.1, rung 6's soundness theorem. The spec labels
T3.8 "discharged as a theorem only if rung 6's certificate
proves its general form (T6.1)", and T4.5 "PREMISE until rung
6 closes", with its antecedent defined by rung 6's conditions.
Rung 6 did not close T6.1: it stands in the rung-6 Lean file
as a premise, and the reason is structural, not a missing
proof attempt. C1's threshold is defined as a difference of
two quantities read off the rung 2–5 records; the records
contain no emergence at any margin (every battery's decision
was no win), so the least emergence-side quantity does not
exist, the threshold does not exist, and the conditions
C1–C5 cannot be satisfied by any view — DECIDE's 25 verdicts
were all NOT-CERTIFIED on exactly this ground, verified by an
independent checker at zero failures. A soundness theorem
about conditions that cannot be instantiated, over a
capability predicate that is an empirical quantity of a
battery harness, is not a statement the Lean model can prove:
the rung-6 file models the verdict and the conditions, and
the link from conditions to battery capability is precisely
the unproved bridge. No kernel-checked proof of T6.1 exists
to be had from the present records, and an argument is not a
discharge.

**T3.8's own end of the chain.** Even the premise's empirical
test could not evaluate its antecedent at rung 3: emergent
deadness of a group actor is provable under the registered
rule only for views of at most 11 axes, and the batteries'
level-2 views had 19 and 29 axes — the antecedent stands
recorded as NOT EVALUABLE, the premise neither refuted (no
block was load-bearing; the largest mean capability drop
under ablation was +0.0047 against bars of 0.2808 and 0.1043)
nor confirmed. What would discharge T3.8, exactly: a battery
whose records separate, so the threshold derivation yields a
positive threshold and C1–C5 become instantiable; then a
proof of T6.1 over a formal model that ties the conditions to
the capability predicate of a battery harness; T3.8 follows
as its group-actor case. A cheaper partial route exists and
is named for completeness: a rung-3-class battery whose
level-2 views stay within the exactness cap, making the
antecedent evaluable — that would let the battery test the
premise, but a test is evidence, not a discharge.

**T4.5's own end of the chain.** Its consequent is a lower
bound on a measured transfer advantage, and rung 4 measured
that advantage at exactly zero in both family pairs, with all
32 permutation nulls at or above it in each pair — the
mechanism is recorded: every arm and the unbounded-search
ceiling select the same configuration on every seed, so the
carriage channel the bound quantifies over carried nothing.
The bound's other antecedent term, the embedding distortion,
is a rung-6 term defined over the same failed derivation.
What would discharge T4.5, exactly: T6.1 proved (same route
as T3.8), the embedding and distortion terms formalized over
the target view, and a separating record set under which the
bound has a positive instance to bind to. None of the three
exists today.

Disposition: both stay PREMISE, carried by name, with this
section as the derivation-graph evidence. Neither is depended
on by any verdict: rung 3's and rung 4's decisions were
computed from their batteries alone, and rung 6's verdicts
rest on C1 and C5 only.

## 5. T5.4 — AUDIT EXECUTED; STAYS A PREMISE

### 5.1 The derivation graph, enumerated from the code

The rung-5 system (the rung-5 harness, over the rung-3 and
rung-4 harnesses it imports) derives state at exactly these
nodes, with these inputs and no others:

- Initial actor state: per-actor report lists seeded from the
  seed-derived observations (a function of seed and family
  only).
- The point estimate: a closure that reads the current report
  lists at bundle time — a derived view of the state fold,
  never a store.
- Sends: a function of the point estimate, the actor, and the
  tick.
- Records: the arm transform of the sends (live noise,
  isolated filler, frozen replay of a generator log, shuffled
  destinations), appended to one list per run — the run's log.
  The frozen arm's generator log is an input to the run,
  persisted beside its outputs.
- Actor state after a record: the delivery step appends the
  record's received values into the destination's report
  lists. This append is the only mutation of actor state in
  the three harness files.
- The tally: an incremental fold over the same records.
- Checkpoint snapshots: capability, coverage, and the state
  hash read off the current report lists at a checkpoint tick
  — reads, not mutations.
- The view of a cut: a pure function of the persisted record
  prefix and the family truth values, recomputed from the
  prefix alone (its per-tick edges are counterfactuals against
  the whole prefix fold — the fact rung 5 measured as the
  T5.6 antecedent's near-vacuity; a read-side recomputation,
  not a state route).
- The decision: a function of the run summaries and the
  replicate-1 views.

Edges into any derived state come only from: the seed-derived
initial observations, the records of the run's own log, and
prior states through the append fold. There is no edge from
any summary, window, decay, or sampling structure into a
state, because no such structure exists in the code (5.2).

One read-side threshold is noted for completeness: the point
estimate returns the null marker for a site with fewer than
three reports (the v3 evidence gate). It governs what an
actor sends, never what the state retains — the report lists
keep every appended value, and the fold below is over the
lists, not over the estimate.

### 5.2 Static audit (executed)

A word-boundary scan of the rung-3, rung-4, and rung-5 harness
files and the rung-5 checker for every influence-reduction
route name — reweight, decay, forget, truncate, expiry,
eviction, pruning — returns zero hits. (An earlier loose scan's
hits were all the word "summary", a reporting structure that
never feeds a state.) A mutation census of the same files:
the only write to actor state is the delivery step's append;
the log list only grows by append; checkpoint snapshots are
fresh dictionaries. The persisted record schema, read off the
first record of a persisted live log, has ten fields — tick,
level, source, intended destination, actual destination,
interpreted source, sent values, received values, annotation,
corruption flag — and no reweight field: the system has no
reweight record type, so the premise's "factors through an
appended reweight record" clause has no instance to check;
influence is never reduced at all in this system.

### 5.3 Dynamic audit (executed at audit time)

The audit script (landing in section 6) re-ran the
independent checker's fold — a code path that imports nothing
from the harness — over replicate 1's persisted live logs in
both families, at audit time:

- Append-only shape: both logs hold 65,536 records with
  non-decreasing tick order.
- Prefix folds: the state folded from each checkpoint prefix
  equals the checkpoint hash the harness recorded — 8 of 8
  checkpoints in field, 8 of 8 in region.
- Restart closure: continuing each checkpoint's folded state
  over the remaining records reproduces the final recorded
  hash — 8 of 8 in each family. No state is carried anywhere
  but in the fold of the log.
- Influence probe: for 24 sampled records per family that
  append at least one value, removing the record from the
  fold changes the folded report lists exactly — 24 of 24 in
  each family. Every appending record is a premise of the
  derived state, reached only through the fold. (The probe
  compares the report lists themselves, not the state hash:
  the hash quotients each list by its median or mode, and a
  single value's removal need not move a median. The first
  version of the probe compared hashes and failed 47 of 48
  samples on exactly that quotient; the corrected probe is
  the one reported here, and the failure is recorded rather
  than smoothed over.)

### 5.4 Why it stays a premise

The audit verifies the premise's content for the rung-5
implementation as built and run. The premise as stated,
though, quantifies over the derivation graph of any lawful
rung-5 implementation, and the spec's discharge route for it
is this audit "when the endgame lands" — the audit over the
one derivation machinery's graph, where derived quantities
carry premise cones. That machinery has not landed: rung 6
records the certificate query as a standalone artifact, not
integrated into any derivation machinery, and the endgame's
derived-quantity claim remains proposed. Under this audit's
own rule — a discharge is a kernel-checked proof or it stays
a premise — a code-level audit of one implementation, however
complete, is verification, not the discharge.

What would discharge T5.4, exactly, either of: (a) the
endgame derivation machinery lands, the rung-5 derivation is
re-expressed in it with premise cones, and this audit re-runs
over that graph — the spec's named route; or (b) a Lean
formalization of the harness derivation graph (state nodes,
their premise cones, the append fold as the only state edge)
with a kernel proof that every state node's cone is the full
cut plus any reweight records, the formal graph tied to the
code by the enumeration in 5.1. Until one exists, T5.4 stays
PREMISE by construction review — now a review backed by an
executed audit, labeled as what it is.

## 6. Landing and files

Landed in clpi/software-emergence-is-decidable under a new
audit directory, on top of cddf398a, through the GitHub API
route (the route the rung landings used), each blob read back
and hash-verified after the commit:

- The audit Lean file: the T5.6 proof of section 3 (five
  results — the joined-sum lemma, the split lemma, the sum
  lemma, the engaged bound, and the closing theorem — with
  their printed axiom audits in the file).
- The audit script: the dynamic half of section 5, rerunnable
  against the persisted rung-5 artifacts.
- This record, as the audit directory's record file.

Working copies and scratch: the audit scratch directory under
~/workspace (the Lean file, the audit script, and this
record's source). The rung records (rung 3, rung 4, rung 5,
rung 6) each gain a dated addendum stating this audit's
outcome for their premise lists; no original line of any rung
record is rewritten.

Naming gate: the outbound-text gate was run over this record
before delivery; its verdict and the created-name census are
reported with the delivery, not inside the record.

## 7. Premise debt, after the audit

- T3.8 — PREMISE. Route: separating records, then T6.1.
- T4.5 — PREMISE. Route: T6.1, formalized embedding terms,
  separating records.
- T5.4 — PREMISE (content verified by executed audit).
  Route: the endgame machinery audit, or a formal graph
  model with a kernel proof.
- T5.6 — PROVED (conditional form, concrete measure).
  Section 3.

No other state in the ladder changes. The falsified claims
stay falsified; the open items rung 6 carried (the
dependence-scan cost gap, the evidence-gate constant's
unmeasured sensitivity, grain saturation) are untouched by
this audit and remain open under their own names.
