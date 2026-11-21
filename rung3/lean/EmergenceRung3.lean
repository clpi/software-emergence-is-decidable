/-
Emergence rung 3 — composition: theorem obligations T3.1–T3.8.

Lean 4.19.0, core only, no sorry. Each theorem is proved in the
form stated in the rung-3 record (~/workspace/research/
emergence-rung3-2026-11-21.md):

- T3.1: formation G is defined from the level-1 projection of the
  cut alone; first-reach facts are stable under appends (so a
  partition formed at a cut cannot be changed by later records).
- T3.2: replay/restart exactness of the fold, and the state at a
  formation tick is a function of the log prefix alone.
- T3.3: the freeze transformation changes exactly the records it
  is defined to change (level-1 records at or after the formation
  tick for freeze-1; level-2 likewise), and no others; length is
  preserved.
- T3.4: over a partition of the actor list, the member-step count
  of one group step summed over all blocks is exactly N — the
  section 2.3 exchange is exact.
- T3.5: conditional form — if the joint view's engaged family
  contains the level views' engaged families as sublists with
  weights carried, mu(joint) >= max(mu(level 1), mu(level 2)).
  The engaged-inclusion antecedent is discharged by the view
  construction, not in this file; the monotonicity core is proved.
- T3.6: the joint tally is the componentwise sum of the level-1
  and level-2 tallies, at every cut.
- T3.7: a per-tick permutation of records, and readdressing that
  preserves content predicates, preserve every content count —
  the shuffled arm's marginals equal the live arm's.
- T3.8: stated as a named premise (a Prop definition). NOT proved,
  NOT an axiom. It is discharged, if ever, by rung 6 (T6.1).
-/

namespace Rung3

/-- Channel annotation of a record (ladder spec section 1.2). -/
inductive Ann where
  | delivered | dropped | misdelivered | frozen | shuffled | filler
  deriving DecidableEq, Repr

/-- A log record, abstracted to the fields the rung-3 theorems
quantify over. `sites` is the list of sites this record appends
reports about (the checker's append rule, abstracted); `sumAbs`
and `reports` are the record's tally contributions. -/
structure Rec where
  tick : Nat
  lvl : Nat
  dst : Nat
  ann : Ann
  corr : Bool
  delivered : Bool
  sumAbs : Nat
  reports : Nat
  sites : List Nat
  deriving Repr

/- ---------------- T3.6: the second-order tally ---------------- -/

/-- The rung-2 tally vector (registration.md, DET/TAL). -/
structure Tally where
  records : Nat
  deliveredClass : Nat
  annDelivered : Nat
  dropped : Nat
  corr : Nat
  misdelivered : Nat
  frozen : Nat
  shuffled : Nat
  filler : Nat
  reports : Nat
  sumAbsRecv : Nat
  deriving DecidableEq, Repr

namespace Tally

def zero : Tally :=
  ⟨0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0⟩

def add (a b : Tally) : Tally :=
  ⟨a.records + b.records, a.deliveredClass + b.deliveredClass,
   a.annDelivered + b.annDelivered, a.dropped + b.dropped,
   a.corr + b.corr, a.misdelivered + b.misdelivered,
   a.frozen + b.frozen, a.shuffled + b.shuffled,
   a.filler + b.filler, a.reports + b.reports,
   a.sumAbsRecv + b.sumAbsRecv⟩

theorem add_zero (a : Tally) : add a zero = a := by
  obtain ⟨a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11⟩ := a
  rfl

theorem zero_add (a : Tally) : add zero a = a := by
  obtain ⟨a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11⟩ := a
  simp only [add, zero]
  congr 1 <;> omega

theorem add_comm (a b : Tally) : add a b = add b a := by
  obtain ⟨a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11⟩ := a
  obtain ⟨b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11⟩ := b
  simp only [add]
  congr 1 <;> omega

theorem add_assoc (a b c : Tally) : add (add a b) c = add a (add b c) := by
  obtain ⟨a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11⟩ := a
  obtain ⟨b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11⟩ := b
  obtain ⟨c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11⟩ := c
  simp only [add]
  congr 1 <;> omega

/-- One record's tally contribution. -/
def contrib (r : Rec) : Tally :=
  ⟨1,
   if r.delivered then 1 else 0,
   if r.ann = Ann.delivered then 1 else 0,
   if r.ann = Ann.dropped then 1 else 0,
   if r.corr then 1 else 0,
   if r.ann = Ann.misdelivered then 1 else 0,
   if r.ann = Ann.frozen then 1 else 0,
   if r.ann = Ann.shuffled then 1 else 0,
   if r.ann = Ann.filler then 1 else 0,
   r.reports,
   if r.delivered then r.sumAbs else 0⟩

def step (t : Tally) (r : Rec) : Tally := add t (contrib r)

def tally (L : List Rec) : Tally := L.foldl step zero

theorem foldl_step_add (t u : Tally) (L : List Rec) :
    L.foldl step (add t u) = add t (L.foldl step u) := by
  induction L generalizing u with
  | nil => simp [add_zero]
  | cons r L ih =>
    show (L.foldl step (step (add t u) r)) = _
    rw [show step (add t u) r = add t (step u r) from add_assoc t u (contrib r)]
    exact ih (u := step u r)

theorem tally_cons (r : Rec) (L : List Rec) :
    tally (r :: L) = add (tally L) (contrib r) := by
  show L.foldl step (step zero r) = add (L.foldl step zero) (contrib r)
  have e1 : step zero r = add (contrib r) zero := by
    show add zero (contrib r) = add (contrib r) zero
    rw [zero_add, add_zero]
  rw [e1, foldl_step_add, add_comm]

/-- T3.6 (second-order tally): for any predicate p on records —
in particular "level = 1" versus "level = 2" — the tally of a
log is the componentwise sum of the tallies of its two filtered
parts. Applied with p = (lvl = 1): TAL over the joint log equals
the pair (TAL over level-1 records, TAL over level-2 records)
composed by Tally.add, at every cut (every prefix is a list, so
the theorem is already cut-general). -/
theorem tally_filter_pair (p : Rec → Bool) (L : List Rec) :
    tally L = add (tally (L.filter p)) (tally (L.filter (fun r => !p r))) := by
  induction L with
  | nil => rfl
  | cons r L ih =>
    by_cases hp : p r = true
    · have h1 : (r :: L).filter p = r :: L.filter p := by
        simp [List.filter_cons, hp]
      have h2 : (r :: L).filter (fun r => !p r) = L.filter (fun r => !p r) := by
        simp [List.filter_cons, hp]
      rw [tally_cons, ih, h1, h2, tally_cons,
          add_assoc, add_comm (tally (L.filter (fun r => !p r))) (contrib r),
          ← add_assoc]
    · have hp' : p r = false := by
        cases h : p r with
        | false => rfl
        | true => exact absurd h hp
      have h1 : (r :: L).filter p = L.filter p := by
        simp [List.filter_cons, hp']
      have h2 : (r :: L).filter (fun r => !p r)
          = r :: L.filter (fun r => !p r) := by
        simp [List.filter_cons, hp']
      rw [tally_cons, ih, h1, h2, tally_cons, ← add_assoc]

end Tally

/- ---------------- T3.2: replay and restart exactness ---------------- -/

/-- A run's state is the fold of its log (spec section 1.2: the
log is the state). Generic over the state type and step function,
as in rung 2. -/
def runFrom {W : Type} (apply : W → Rec → W) (w : W) (L : List Rec) : W :=
  L.foldl apply w

theorem runFrom_append {W : Type} (apply : W → Rec → W) (w : W)
    (L₁ L₂ : List Rec) :
    runFrom apply w (L₁ ++ L₂) = runFrom apply (runFrom apply w L₁) L₂ := by
  simp [runFrom, List.foldl_append]

/-- T3.2 (group replay exactness, fold form): restarting from a
prefix alone reproduces the state at that cut — the state after
the whole log is the state at the cut folded with the suffix. -/
theorem restart_exact {W : Type} (apply : W → Rec → W) (w : W)
    (L₁ L₂ : List Rec) :
    runFrom apply w (L₁ ++ L₂) = runFrom apply (runFrom apply w L₁) L₂ :=
  runFrom_append apply w L₁ L₂

/-- T3.2 (formation-tick form): an actor's (hence a group actor's)
state at a formation tick is a function of the log prefix through
that tick alone: two logs with equal prefixes have equal states
at the tick. -/
theorem state_of_prefix {W : Type} (apply : W → Rec → W) (w : W)
    (t : Nat) (L₁ L₂ : List Rec)
    (h : L₁.filter (fun r => r.tick < t) = L₂.filter (fun r => r.tick < t)) :
    runFrom apply w (L₁.filter (fun r => r.tick < t))
      = runFrom apply w (L₂.filter (fun r => r.tick < t)) := by
  rw [h]

/- ---------------- T3.1: formation is a function of the cut ---------------- -/

/-- First tick at which `holder` holds a report about `site`,
over the level-1 records of L (log order = tick order). -/
def firstReach (L : List Rec) (site holder : Nat) : Option Nat :=
  match L.filter (fun r => (r.lvl == 1) && (r.dst == holder)
      && r.sites.contains site) with
  | [] => none
  | r :: _ => some r.tick

/-- The registered rule's linkage: mutual first-reach by
kappa = 1 (registration amendment v2). -/
def linked (L : List Rec) (a b : Nat) : Bool :=
  match firstReach L a b, firstReach L b a with
  | some t1, some t2 => (t1 ≤ 1) && (t2 ≤ 1)
  | _, _ => false

/-- The formation graph (linked ring adjacencies) of a log's
level-1 projection. Blocks are the connected components of this
graph; the graph is the formation content of G. -/
def graphOf (L : List Rec) (n : Nat) : List (Nat × Nat) :=
  (List.range n).filterMap (fun a =>
    if linked L a ((a + 1) % n) then some (a, (a + 1) % n) else none)

/-- G, as registered: a function of the level-1 records alone. -/
def G (L : List Rec) (n : Nat) : List (Nat × Nat) :=
  graphOf (L.filter (fun r => r.lvl == 1)) n

/-- T3.1 (projection form): G reads only the level-1 projection
of the cut — applying G to a log or to its level-1 projection
gives the same formation. -/
theorem g_reads_l1_only (L : List Rec) (n : Nat) :
    G L n = G (L.filter (fun r => r.lvl == 1)) n := by
  simp [G, List.filter_filter]

/-- T3.1 (determinism): equal cuts have equal formations. -/
theorem g_det (L₁ L₂ : List Rec) (n : Nat) (h : L₁ = L₂) :
    G L₁ n = G L₂ n := by
  rw [h]

/-- T3.1 (prefix stability): a first-reach fact established at a
cut is unchanged by appending more records — so the registered
partition, a function of first-reach ticks bounded by kappa, is stable once
formed. -/
theorem firstReach_append (L L' : List Rec) (site holder t : Nat)
    (h : firstReach L site holder = some t) :
    firstReach (L ++ L') site holder = some t := by
  unfold firstReach at h ⊢
  rw [List.filter_append]
  cases hf : L.filter (fun r => (r.lvl == 1) && (r.dst == holder)
      && r.sites.contains site) with
  | nil =>
    rw [hf] at h
    simp at h
  | cons r rs =>
    rw [hf] at h
    exact h

/- ---------------- T3.3: freeze soundness ---------------- -/

/-- The freeze transformation: records at the frozen level at or
after the formation tick are replaced by their frozen source;
every other record is itself. (freeze-1: lvl = 1; freeze-2's
addressing shuffle is T3.7's map.) -/
def freeze (src : Rec → Rec) (lvl t1 : Nat) (L : List Rec) : List Rec :=
  L.map (fun r => if r.lvl = lvl ∧ t1 ≤ r.tick then src r else r)

/-- T3.3 (length): freezing changes no record count. -/
theorem freeze_length (src : Rec → Rec) (lvl t1 : Nat) (L : List Rec) :
    (freeze src lvl t1 L).length = L.length := by
  simp [freeze]

/-- T3.3 (no other record changed): a log with no frozen-level
record at or after the formation tick is unchanged by freezing —
combined with the pointwise definition of `freeze` (a map that
replaces exactly the records in the frozen class), this pins the
transformation's action record by record. -/
theorem freeze_id_on (src : Rec → Rec) (lvl t1 : Nat) :
    ∀ (L : List Rec), (∀ r ∈ L, ¬ (r.lvl = lvl ∧ t1 ≤ r.tick)) →
    freeze src lvl t1 L = L := by
  intro L
  induction L with
  | nil => intro _; rfl
  | cons r L ih =>
    intro hL
    have hr : ¬ (r.lvl = lvl ∧ t1 ≤ r.tick) := hL r (by simp)
    have hL' : ∀ r ∈ L, ¬ (r.lvl = lvl ∧ t1 ≤ r.tick) :=
      fun x hx => hL x (List.mem_cons_of_mem _ hx)
    show (if r.lvl = lvl ∧ t1 ≤ r.tick then src r else r)
        :: freeze src lvl t1 L = r :: L
    rw [if_neg hr, ih hL']

/-- T3.3 (the frozen class is replaced): a log whose records are
all frozen-level records at or after the formation tick is
mapped pointwise to its frozen sources. -/
theorem freeze_replaces (src : Rec → Rec) (lvl t1 : Nat) :
    ∀ (L : List Rec), (∀ r ∈ L, r.lvl = lvl ∧ t1 ≤ r.tick) →
    freeze src lvl t1 L = L.map src := by
  intro L
  induction L with
  | nil => intro _; rfl
  | cons r L ih =>
    intro hL
    have hr : r.lvl = lvl ∧ t1 ≤ r.tick := hL r (by simp)
    have hL' : ∀ r ∈ L, r.lvl = lvl ∧ t1 ≤ r.tick :=
      fun x hx => hL x (List.mem_cons_of_mem _ hx)
    show (if r.lvl = lvl ∧ t1 ≤ r.tick then src r else r)
        :: freeze src lvl t1 L = src r :: L.map src
    rw [if_pos hr, ih hL']

/- ---------------- T3.4: budget conservation under lifting ---------------- -/

/-- T3.4: if the blocks' concatenation is the actor list, one
group step over all blocks (one member step per member) executes
exactly as many member steps as there are actors. The section
2.3 exchange (1 group step = |block| member steps) is exact. -/
theorem t34_steps (blocks : List (List Nat)) (n : Nat)
    (h : blocks.flatten = List.range n) :
    (blocks.map List.length).sum = n := by
  rw [← List.length_flatten, h, List.length_range]

/- ---------------- T3.5: joint engaged structure (conditional) ---------------- -/

/-- The weight of an engaged family: sum of weights over its
edges. Weights are positive naturals (F1 section 1). -/
def muOf (w : List Nat → Nat) (E : List (List Nat)) : Nat :=
  (E.map w).sum

theorem sum_le_of_sublist (w : List Nat → Nat) {l₁ l₂ : List (List Nat)}
    (h : List.Sublist l₁ l₂) : (l₁.map w).sum ≤ (l₂.map w).sum := by
  induction h with
  | slnil => simp
  | cons a _ ih =>
    simp only [List.map_cons, List.sum_cons]
    exact Nat.le_trans ih (Nat.le_add_left _ _)
  | cons₂ a _ ih =>
    simp only [List.map_cons, List.sum_cons]
    exact Nat.add_le_add_left ih _

/-- T3.5 (monotonicity core): if the joint view's engaged family
contains a level view's engaged family as a sublist (the image
under the member/block inclusion, weights carried — the
antecedent discharged by the view construction), then the level
view's mu is at most the joint view's mu; applied to both levels,
mu(joint) >= max(mu(level 1), mu(level 2)). -/
theorem t35_mu_mono (w : List Nat → Nat)
    {e1 e2 ej : List (List Nat)}
    (h1 : List.Sublist e1 ej) (h2 : List.Sublist e2 ej) :
    muOf w e1 ≤ muOf w ej ∧ muOf w e2 ≤ muOf w ej :=
  ⟨sum_le_of_sublist w h1, sum_le_of_sublist w h2⟩

/- ---------------- T3.7: shuffle preserves marginals ---------------- -/

/-- Any count of a predicate is preserved under a permutation of
the list. -/
theorem countP_perm {L₁ L₂ : List Rec} (h : List.Perm L₁ L₂) (p : Rec → Bool) :
    L₁.countP p = L₂.countP p := by
  induction h with
  | nil => rfl
  | cons a _ ih => simp only [List.countP_cons, ih]
  | swap a b L =>
    by_cases ha : p a <;> by_cases hb : p b <;>
      simp [List.countP_cons, ha, hb] <;> omega
  | trans _ _ ih1 ih2 => rw [ih1, ih2]

/-- Readdressing (a map that changes only destination and
interpreted-source fields) preserves every count of a content
predicate — a predicate the readdressing does not change. -/
theorem countP_map_readdress (f : Rec → Rec) (p : Rec → Bool)
    (hf : ∀ r, p (f r) = p r) (L : List Rec) :
    (L.map f).countP p = L.countP p := by
  induction L with
  | nil => rfl
  | cons r L ih => simp [List.countP_cons, hf, ih]

/-- T3.7: the shuffled arm's per-tick message counts, for any
content predicate (annotation class, value content, level), equal
the live arm's: the shuffled tick is a permutation of the live
tick's sends composed with a readdressing. -/
theorem t37_shuffle_marginals (f : Rec → Rec) (p : Rec → Bool)
    (hf : ∀ r, p (f r) = p r) {L₁ L₂ : List Rec} (h : List.Perm L₁ L₂) :
    (L₁.map f).countP p = L₂.countP p := by
  rw [countP_map_readdress f p hf, countP_perm h]

/- ---------------- T3.8: PREMISE (stated, not proved) ---------------- -/

/-- T3.8 (no free capability) — PREMISE. This definition states
the premise; it is not proved in this file, it is not an axiom,
and no theorem here depends on it. It is tested by the rung-3
battery's ablation (spec section 2.7) and is discharged as a
theorem only if rung 6's certificate proves its general form
(T6.1). The battery's caps and delta are rationals in [0, 1];
they are carried here as naturals scaled by 10^6, which preserves
the inequality under any fixed positive scaling. -/
def T38Premise (capJoint capFlat δ : Nat) (everyGroupDead : Prop) : Prop :=
  everyGroupDead → capJoint ≤ capFlat + δ

end Rung3

#print axioms Rung3.Tally.tally_filter_pair
#print axioms Rung3.restart_exact
#print axioms Rung3.state_of_prefix
#print axioms Rung3.g_reads_l1_only
#print axioms Rung3.firstReach_append
#print axioms Rung3.freeze_length
#print axioms Rung3.freeze_id_on
#print axioms Rung3.freeze_replaces
#print axioms Rung3.t34_steps
#print axioms Rung3.t35_mu_mono
#print axioms Rung3.countP_perm
#print axioms Rung3.t37_shuffle_marginals
