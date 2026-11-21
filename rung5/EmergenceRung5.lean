/-
Emergence rung 5 — compounding over time: theorem obligations
T5.1–T5.6.

Lean 4.19.0, core only, no sorry. States as in the rung-5
record (~/workspace/research/emergence-rung5-2026-11-21.md)
and the registration (registration.md section 12):

- T5.1 restart exactness: PROVED (restart_exact) — restarting
  from the state derived from a prefix, and folding the suffix,
  is folding the whole log.
- T5.2 replay exactness: PROVED (trace_in, trace_covers,
  replay_exact) — the states the uninterrupted run passes
  through are exactly the folds of the log's prefixes:
  replaying a cut from the initial state reproduces the
  checkpoint state, at every cut.
- T5.3 tally at every cut: PROVED (tally_acc, tally_cut) — the
  incremental tally, folded record by record, equals the
  from-scratch batch tally on every prefix.
- T5.4 no forgetting: PREMISE by construction review, the
  route spec 4.4 names before the endgame. Stated as a
  definition (T54Premise), not proved, not an axiom, depended
  on by nothing. The review is recorded in the rung-5 record:
  the derived state is the fold of the full cut (the
  functionality content proved inside T5.1/T5.2), and the
  rung-5 harness has no reweight records and no other
  influence-reduction route. Labeled review, not proof.
- T5.5 curve well-definedness: PROVED (read_assign,
  eval_order_free) — the value an evaluation pass assigns to a
  checkpoint is the evaluation function at that checkpoint,
  whatever order the pass visits the checkpoints in.
- T5.6 monotonicity under accumulation: PREMISE until rung 6,
  never claimed. Stated as a definition (T56Premise), not
  proved, not an axiom, depended on by nothing. The battery
  measures its antecedent and its consequent per checkpoint
  pair; it does not claim the theorem.
-/

namespace Rung5

variable {W R : Type}

/-- A run's state is the fold of its log (spec section 1.2),
generic over the state type, the record type, and the step
function, as in rungs 2–4. -/
def run (step : W → R → W) (w : W) (L : List R) : W :=
  L.foldl step w

theorem run_append (step : W → R → W) (w : W) (L₁ L₂ : List R) :
    run step w (L₁ ++ L₂) = run step (run step w L₁) L₂ := by
  simp [run, List.foldl_append]

/-- T5.1 (restart exactness): restart from the checkpoint cut —
fold the prefix, then continue with the suffix — reproduces
the uninterrupted run exactly. -/
theorem restart_exact (step : W → R → W) (w : W)
    (L₁ L₂ : List R) :
    run step (run step w L₁) L₂ = run step w (L₁ ++ L₂) :=
  (run_append step w L₁ L₂).symm

/- ---------------- T5.2: replay exactness ---------------- -/

/-- The recorded trace of a run: the state at every cut, in
order, starting from the initial state. -/
def trace (step : W → R → W) (w : W) : List R → List W
  | [] => [w]
  | r :: L => w :: trace step (step w r) L

/-- Every state in the trace is the fold of a prefix of the
log: replaying that prefix from the initial state reproduces
the state. -/
theorem trace_in (step : W → R → W) (w : W) :
    ∀ (L : List R) (s : W), s ∈ trace step w L →
      ∃ P L₂, L = P ++ L₂ ∧ s = run step w P := by
  intro L
  induction L generalizing w with
  | nil =>
    intro s hs
    simp only [trace, List.mem_singleton] at hs
    exact ⟨[], [], rfl, by rw [hs]; rfl⟩
  | cons r L ih =>
    intro s hs
    simp only [trace, List.mem_cons] at hs
    cases hs with
    | inl h =>
      exact ⟨[], r :: L, rfl, by rw [h]; rfl⟩
    | inr h =>
      obtain ⟨P, L₂, hL, hsP⟩ := ih (w := step w r) s h
      refine ⟨r :: P, L₂, by subst hL; rfl, ?_⟩
      rw [hsP]
      rfl

/-- The initial state heads every trace. -/
theorem trace_head (step : W → R → W) (w : W) :
    ∀ (L : List R), w ∈ trace step w L := by
  intro L
  cases L with
  | nil => simp [trace]
  | cons r L => simp only [trace]; exact List.mem_cons_self

/-- Every prefix fold is a state in the trace: the run passes
through the fold of every prefix, so a checkpoint state
exists for every cut. -/
theorem trace_covers (step : W → R → W) (w : W) :
    ∀ (P L₂ : List R), run step w P ∈ trace step w (P ++ L₂) := by
  intro P
  induction P generalizing w with
  | nil =>
    intro L₂
    exact trace_head step w L₂
  | cons r P ih =>
    intro L₂
    show run step w (r :: P) ∈ trace step w ((r :: P) ++ L₂)
    simp only [List.cons_append, trace, List.mem_cons]
    exact Or.inr (ih (w := step w r) L₂)

/-- T5.2 (replay exactness), the two directions together: the
trace of the uninterrupted run over a log is exactly the set
of folds of its prefixes — replay of any cut from the initial
state reproduces the checkpoint state at that cut, and every
checkpoint state arises this way. -/
theorem replay_exact (step : W → R → W) (w : W) (L : List R)
    (s : W) :
    s ∈ trace step w L ↔
      ∃ P L₂, L = P ++ L₂ ∧ s = run step w P := by
  refine ⟨trace_in step w L s, ?_⟩
  rintro ⟨P, L₂, hL, hs⟩
  rw [hs, hL]
  exact trace_covers step w P L₂

/- ---------------- T5.3: tally at every cut ---------------- -/

/-- The batch tally (DET): a from-scratch recursion over the
whole list — the count of records satisfying p and the total
of the value function v. -/
def det (p : R → Bool) (v : R → Nat) : List R → Nat × Nat
  | [] => (0, 0)
  | r :: L => ((if p r then 1 else 0) + (det p v L).1,
               v r + (det p v L).2)

/-- One incremental tally step (TAL). -/
def tstep (p : R → Bool) (v : R → Nat) (acc : Nat × Nat)
    (r : R) : Nat × Nat :=
  (acc.1 + (if p r then 1 else 0), acc.2 + v r)

/-- The accumulator lemma: folding the tally step from any
accumulator adds exactly the batch tally of the list. -/
theorem tally_acc (p : R → Bool) (v : R → Nat) :
    ∀ (L : List R) (acc : Nat × Nat),
      L.foldl (tstep p v) acc
        = (acc.1 + (det p v L).1, acc.2 + (det p v L).2) := by
  intro L
  induction L with
  | nil => intro acc; rfl
  | cons r L ih =>
    intro acc
    show (L.foldl (tstep p v) (tstep p v acc r))
      = (acc.1 + (det p v (r :: L)).1,
         acc.2 + (det p v (r :: L)).2)
    rw [ih]
    simp only [det, tstep]
    exact Prod.ext (by omega) (by omega)

/-- T5.3 (tally at every cut): the incremental tally of any
prefix — in particular of the prefix ending at any checkpoint
of any log — equals the batch tally of that prefix computed
from scratch. -/
theorem tally_cut (p : R → Bool) (v : R → Nat) (L : List R) :
    L.foldl (tstep p v) (0, 0) = det p v L := by
  have h := tally_acc p v L (0, 0)
  simpa using h

/- ---------------- T5.5: curve well-definedness ---------------- -/

/-- An evaluation pass over a checkpoint order: each visited
checkpoint paired with the evaluation function at it. -/
def assign (f : Nat → Nat) (order : List Nat) : List (Nat × Nat) :=
  order.map (fun t => (t, f t))

/-- Reading a checkpoint's assigned value back from a pass. -/
def read (t : Nat) : List (Nat × Nat) → Option Nat
  | [] => none
  | (a, b) :: rest => if a = t then some b else read t rest

/-- The value a pass assigns to a visited checkpoint is the
evaluation function at that checkpoint. -/
theorem read_assign (f : Nat → Nat) :
    ∀ (order : List Nat) (t : Nat), t ∈ order →
      read t (assign f order) = some (f t) := by
  intro order
  induction order with
  | nil => intro t h; simp at h
  | cons a rest ih =>
    intro t h
    have hm : t = a ∨ t ∈ rest := List.mem_cons.mp h
    show read t ((a, f a) :: assign f rest) = some (f t)
    cases hm with
    | inl h =>
      subst h
      simp [read]
    | inr h =>
      by_cases hat : a = t
      · subst hat
        simp [read]
      · have hread : read t ((a, f a) :: assign f rest)
            = read t (assign f rest) := by simp [read, hat]
        rw [hread, ih t h]

/-- T5.5 (curve well-definedness): two evaluation passes over
orders that both visit a checkpoint assign it the same value —
the evaluation at that checkpoint — whatever order either
pass visits the checkpoints in, and however the passes
interleave with the horizon run (an evaluation reads only
its cut). -/
theorem eval_order_free (f : Nat → Nat) (o₁ o₂ : List Nat)
    (t : Nat) (h₁ : t ∈ o₁) (h₂ : t ∈ o₂) :
    read t (assign f o₁) = read t (assign f o₂) := by
  rw [read_assign f o₁ t h₁, read_assign f o₂ t h₂]

/- ---------------- T5.4: PREMISE (stated, not proved) ---------------- -/

/-- T5.4 (no forgetting) — PREMISE by construction review
(spec 4.4's pre-endgame route; the review is in the rung-5
record, labeled review, not proof). This definition states
the premise; it is not proved in this file, it is not an
axiom, and no theorem here depends on it. infl L r reads:
record r's presence influences the state derived from log L.
The premise: every record that influences any derived state
is a reweight record — influence is never reduced except
through an appended reweight record. -/
def T54Premise (infl : List R → R → Prop) (reweight : R → Prop) :
    Prop :=
  ∀ (L : List R) (r : R), infl L r → reweight r

/- ---------------- T5.6: PREMISE (stated, not proved) ---------------- -/

/-- T5.6 (monotonicity under accumulation) — PREMISE. This
definition states the premise; it is not proved in this file,
it is not an axiom, and no theorem here depends on it. It is
discharged, if ever, only by rung 6's certificate. mu is the
view's measure at a cut, live its live-component set, edges
its hyperedge set, cuts the checkpoint indices: if between
every two cuts the appended records remove no hyperedge and
the live set only grows, then mu is non-decreasing over the
cuts. The battery measures the antecedent and the consequent
per checkpoint pair; the rung-5 claim does not depend on this
premise and it is never cited as evidence. -/
def T56Premise (mu : Nat → Nat) (live : Nat → List Nat)
    (edges : Nat → List (Nat × List Nat)) (cuts : List Nat) :
    Prop :=
  (∀ i ∈ cuts, ∀ j ∈ cuts, i ≤ j →
    (∀ e ∈ edges i, e ∈ edges j) ∧ (∀ a ∈ live i, a ∈ live j))
  → ∀ i ∈ cuts, ∀ j ∈ cuts, i ≤ j → mu i ≤ mu j

end Rung5

#print axioms Rung5.restart_exact
#print axioms Rung5.trace_in
#print axioms Rung5.trace_head
#print axioms Rung5.trace_covers
#print axioms Rung5.replay_exact
#print axioms Rung5.tally_acc
#print axioms Rung5.tally_cut
#print axioms Rung5.read_assign
#print axioms Rung5.eval_order_free
