/-
Emergence rung 6 — the certificate: theorem obligations
T6.1–T6.7.

Lean 4.19.0, core only, no sorry. States as in the rung-6
record (~/workspace/research/emergence-rung6-2026-11-21.md)
and the registration (registration.md section 8):

- T6.1 soundness: PREMISE. The rung's central theorem; not
  proved here, stated as a definition (T61Premise) depended
  on by nothing. No EMERGENT verdict issues in this rung —
  the threshold derivation over the rung 2–5 records yields
  no M1 — so no verdict rests on this premise.
- T6.2 completeness on the registered class: PREMISE, per
  the spec; stated as a definition (T62Premise) over an
  abstract class predicate, depended on by nothing, never
  claimed generally.
- T6.3 decidability: PROVED (verdict_congr, eval_cases) —
  the evaluation is a total computable function of the view
  and the thresholds alone, and each condition's evaluation
  lands in exactly one of its three states.
- T6.4 detector correctness: PROVED in its Lean half
  (controls: kernel decide evaluations of concrete views,
  one passing view and one failure per condition, plus the
  no-threshold control). The empirical half is the agreement
  battery against the independent checker (check6.py), in
  the record.
- T6.5 margin monotonicity: PROVED (mu_mono, c1_mono,
  c4_mono, c5_mono) — increasing any hyperedge weight (and
  no other change) preserves C1, C4, C5 at fixed thresholds.
- T6.6 certificate checkability: PROVED (check_sound,
  check_complete) — the check accepts exactly the
  certificates whose every presented field recomputes: the
  soundness direction is proved, and the honest certificate
  is accepted.
- T6.7 reweighting stability: PROVED in scoped form
  (no_threshold_stable) — when the C1 threshold does not
  exist, no reweighting of the view changes the verdict
  from NOT-CERTIFIED, because C1's evaluation does not read
  the view's weights in that case. The general band
  statement beyond this scope stands with T6.1's family and
  is not claimed.
-/

namespace Rung6

/-- A hyperedge: a natural weight and the list of component
indices it joins. -/
structure Edge where
  weight : Nat
  comps : List Nat
deriving DecidableEq, Repr

/-- A probe view in the procedure's finite form: its edges,
its emergent-dead axes, the mus of its log's cuts at or
after half the probe horizon, its live-component count
(the refinement coordinate's second component), and the
dependence-scan confirmation flag the producing lane's
exact scan supplies (C3's input). -/
structure View where
  edges : List Edge
  dead : List Nat
  cuts : List Nat
  lambda : Nat
  confirmed : Bool
deriving DecidableEq, Repr

/-- The derived thresholds: M1 (absent when the records do
not separate) and the C5 bound. -/
structure Thr where
  m1 : Option Nat
  bound : Option (Nat × Nat)
deriving DecidableEq, Repr

/-- The contribution of one edge to mu: its weight when it
joins at least two components, else nothing (edges of size
below 2 carry no interdependence, spec section 1.3). -/
def contrib (e : Edge) : Nat :=
  if 2 ≤ e.comps.length then e.weight else 0

/-- mu of a view: the total engaged weight. -/
def mu (v : View) : Nat :=
  (v.edges.map contrib).sum

/-- The three states of a condition evaluation. A condition
whose bar does not exist is not evaluable; it is never
silently a hold. -/
inductive St where
  | hold
  | fail
  | na
deriving DecidableEq, Repr

/-- C1 (engaged weight): mu reaches M1. Without M1 there is
nothing to reach: fail, with the threshold's absence as the
reason (registration section 4). -/
def evalC1 (v : View) (t : Thr) : St :=
  match t.m1 with
  | none => St.fail
  | some m => if m ≤ mu v then St.hold else St.fail

/-- Whether a dead axis carries a hyperedge at or above the
bar: some edge containing it has weight at least the bar. -/
def deadLoad (v : View) (bar : Nat) : Bool :=
  v.dead.any (fun a => v.edges.any (fun e => a ∈ e.comps && bar ≤ e.weight))

/-- C2 (no dead load). Its bar is M1/2, so without M1 it is
not evaluable. -/
def evalC2 (v : View) (t : Thr) : St :=
  match t.m1 with
  | none => St.na
  | some m => if deadLoad v (m / 2) then St.fail else St.hold

/-- C3 (two-sided reach): the producing scan's confirmation
is the condition's input; an unconfirmed edge set fails. -/
def evalC3 (v : View) (_t : Thr) : St :=
  if v.confirmed then St.hold else St.fail

/-- C4 (cut stability): every cut mu at or after half the
horizon reaches M1/2. Not evaluable without M1, and not
evaluable on a view carrying no cuts. -/
def evalC4 (v : View) (t : Thr) : St :=
  match t.m1 with
  | none => St.na
  | some m =>
    if v.cuts.isEmpty then St.na
    else if v.cuts.all (fun c => m / 2 ≤ c) then St.hold else St.fail

/-- Lexicographic strict excess of rho over the bound. -/
def rhoAbove (mu lam : Nat) (b : Nat × Nat) : Bool :=
  b.1 < mu || (b.1 == mu && b.2 < lam)

/-- C5 (margin in rho): rho strictly exceeds the greatest
no-emergence rho on record. -/
def evalC5 (v : View) (t : Thr) : St :=
  match t.bound with
  | none => St.fail
  | some b => if rhoAbove (mu v) v.lambda b then St.hold else St.fail

/-- The verdict: EMERGENT (true) exactly when all five
conditions hold. A not-evaluable condition is not a hold. -/
def verdict (v : View) (t : Thr) : Bool :=
  (evalC1 v t == St.hold) && (evalC2 v t == St.hold) &&
  (evalC3 v t == St.hold) && (evalC4 v t == St.hold) &&
  (evalC5 v t == St.hold)

/- ---------------- T6.3: decidability ---------------- -/

/-- The verdict is a function of the view and the thresholds
alone: equal inputs, equal verdict. -/
theorem verdict_congr {v v' : View} {t t' : Thr}
    (hv : v = v') (ht : t = t') : verdict v t = verdict v' t' := by
  rw [hv, ht]

/-- Every condition evaluation lands in one of its three
states — the evaluation is total, by construction, and this
records the case split the procedure's finiteness rests on
for C1 (the others are identical in form). -/
theorem evalC1_cases (v : View) (t : Thr) :
    evalC1 v t = St.hold ∨ evalC1 v t = St.fail ∨ evalC1 v t = St.na := by
  obtain ⟨m1o, bnd⟩ := t
  cases m1o with
  | none => exact Or.inr (Or.inl rfl)
  | some m =>
    by_cases h : m ≤ mu v
    · have : evalC1 v { m1 := some m, bound := bnd } = St.hold := if_pos h
      exact Or.inl this
    · have : evalC1 v { m1 := some m, bound := bnd } = St.fail := if_neg h
      exact Or.inr (Or.inl this)

/- ---------------- T6.5: margin monotonicity ---------------- -/

/-- Reweighting a view by a weight function: edges and cut
mus are mapped, nothing else changes. -/
def reweight (f : Nat → Nat) (v : View) : View :=
  { v with edges := v.edges.map (fun e => { e with weight := f e.weight }),
           cuts := v.cuts.map f }

theorem sum_edges_le {f : Nat → Nat} (hf : ∀ w, w ≤ f w) :
    ∀ (l : List Edge), (l.map contrib).sum ≤
      ((l.map (fun e => { e with weight := f e.weight })).map contrib).sum := by
  intro l
  induction l with
  | nil => simp
  | cons e l ih =>
    have h1 : contrib e ≤ contrib { e with weight := f e.weight } := by
      unfold contrib
      by_cases h : 2 ≤ e.comps.length
      · rw [if_pos h, if_pos h]; exact hf e.weight
      · rw [if_neg h, if_neg h]; exact Nat.zero_le 0
    simp only [List.map_cons, List.sum_cons]
    exact Nat.add_le_add h1 ih

/-- mu is monotone under a pointwise weight increase that
changes nothing else. -/
theorem mu_mono {f : Nat → Nat} (hf : ∀ w, w ≤ f w) (v : View) :
    mu v ≤ mu (reweight f v) :=
  sum_edges_le hf v.edges

/-- C1, once holding, keeps holding under a weight increase
at fixed thresholds. -/
theorem c1_mono {f : Nat → Nat} (hf : ∀ w, w ≤ f w)
    (v : View) (t : Thr) (h : evalC1 v t = St.hold) :
    evalC1 (reweight f v) t = St.hold := by
  obtain ⟨m1o, bnd⟩ := t
  cases m1o with
  | none => simp [evalC1] at h
  | some m =>
    have hh : m ≤ mu v := by
      by_cases hle : m ≤ mu v
      · exact hle
      · exfalso
        have h2 : evalC1 v { m1 := some m, bound := bnd } = St.fail := if_neg hle
        rw [h] at h2
        exact St.noConfusion h2
    exact if_pos (Nat.le_trans hh (mu_mono hf v))

/-- C4, once holding, keeps holding: the cut mus only grow. -/
theorem c4_mono {f : Nat → Nat} (hf : ∀ w, w ≤ f w)
    (v : View) (t : Thr) (h : evalC4 v t = St.hold) :
    evalC4 (reweight f v) t = St.hold := by
  obtain ⟨m1o, bnd⟩ := t
  cases m1o with
  | none => simp [evalC4] at h
  | some m =>
    have hne : v.cuts.isEmpty = false := by
      by_cases he : v.cuts.isEmpty
      · exfalso
        have h2 : evalC4 v { m1 := some m, bound := bnd } = St.na := by
          simp [evalC4, he]
        rw [h] at h2; exact St.noConfusion h2
      · simpa using he
    have hall : v.cuts.all (fun c => m / 2 ≤ c) = true := by
      by_cases ha : v.cuts.all (fun c => m / 2 ≤ c)
      · simpa using ha
      · exfalso
        have h2 : evalC4 v { m1 := some m, bound := bnd } = St.fail := by
          simp [evalC4, hne, ha]
        rw [h] at h2; exact St.noConfusion h2
    have hne2 : (reweight f v).cuts.isEmpty = false := by
      cases hc : v.cuts with
      | nil => simp [hc] at hne
      | cons a l => simp [reweight, hc]
    have hall2 : (reweight f v).cuts.all (fun c => m / 2 ≤ c) = true := by
      apply List.all_eq_true.mpr
      intro x hx
      have hxc : x ∈ v.cuts.map f := hx
      obtain ⟨c, hc, rfl⟩ := List.mem_map.mp hxc
      have hmc : m / 2 ≤ c := by
        have := List.all_eq_true.mp hall c hc
        exact of_decide_eq_true this
      exact decide_eq_true (Nat.le_trans hmc (hf c))
    simp [evalC4, hne2, hall2]

/-- C5, once holding, keeps holding: rho's first coordinate
only grows and its second is unchanged. -/
theorem c5_mono {f : Nat → Nat} (hf : ∀ w, w ≤ f w)
    (v : View) (t : Thr) (h : evalC5 v t = St.hold) :
    evalC5 (reweight f v) t = St.hold := by
  obtain ⟨m1o, bnd⟩ := t
  cases bnd with
  | none => simp [evalC5] at h
  | some b =>
    have hh : rhoAbove (mu v) v.lambda b = true := by
      by_cases ha : rhoAbove (mu v) v.lambda b
      · simpa using ha
      · exfalso
        have h2 : evalC5 v { m1 := m1o, bound := some b } = St.fail := by
          simp [evalC5, ha]
        rw [h] at h2; exact St.noConfusion h2
    have hm : mu v ≤ mu (reweight f v) := mu_mono hf v
    have hgoal : rhoAbove (mu (reweight f v)) (reweight f v).lambda b = true := by
      have hl : (reweight f v).lambda = v.lambda := rfl
      rw [hl]
      unfold rhoAbove at hh ⊢
      cases hb : decide (b.1 < mu v) with
      | true =>
        have hlt : b.1 < mu v := of_decide_eq_true hb
        simp [Nat.lt_of_lt_of_le hlt hm]
      | false =>
        have h2 : (b.1 == mu v && b.2 < v.lambda) = true := by
          rw [hb] at hh; simpa using hh
        have hbe : b.1 = mu v := beq_iff_eq.mp ((Bool.and_eq_true _ _).mp h2).1
        have hlt2 : b.2 < v.lambda :=
          of_decide_eq_true ((Bool.and_eq_true _ _).mp h2).2
        by_cases he : b.1 = mu (reweight f v)
        · have e1 : (b.1 == mu (reweight f v)) = true := by simp [he]
          have e2 : decide (b.2 < v.lambda) = true := decide_eq_true hlt2
          simp [e1, e2]
        · have hle : b.1 ≤ mu (reweight f v) := hbe ▸ hm
          have e1 : decide (b.1 < mu (reweight f v)) = true :=
            decide_eq_true (Nat.lt_of_le_of_ne hle he)
          simp [e1]
    exact if_pos hgoal

/- ---------------- T6.7: reweighting stability, scoped ---------------- -/

/-- When the C1 threshold does not exist, the verdict is
NOT-CERTIFIED for every view and stays so under every
reweighting: C1's evaluation reads only the threshold's
absence, never the view's weights. This is the scoped form
of T6.7 that this rung's records support; the general band
statement is not claimed. -/
theorem no_threshold_stable (v : View) (t : Thr) (h : t.m1 = none) :
    verdict v t = false ∧
    ∀ (f : Nat → Nat), verdict (reweight f v) t = false := by
  have hc : ∀ (w : View), evalC1 w t = St.fail := by
    intro w
    unfold evalC1
    rw [h]
  constructor
  · unfold verdict
    rw [hc v]
    simp
  · intro f
    unfold verdict
    rw [hc (reweight f v)]
    simp

/- ---------------- T6.6: certificate checkability ---------------- -/

/-- A certificate's presented fields: the mu, the lambda,
and the verdict it claims. (The full certificate carries
witnesses beyond these; the check's contract is over the
recomputed fields.) -/
structure Cert where
  muF : Nat
  lamF : Nat
  verdictF : Bool
deriving DecidableEq, Repr

/-- The check: accept exactly when every presented field
equals the recomputed field. -/
def check (c : Cert) (v : View) (t : Thr) : Bool :=
  (c.muF == mu v) && (c.lamF == v.lambda) && (c.verdictF == verdict v t)

/-- Soundness: an accepted certificate's fields are the
recomputed fields. -/
theorem check_sound {c : Cert} {v : View} {t : Thr}
    (h : check c v t = true) :
    c.muF = mu v ∧ c.lamF = v.lambda ∧ c.verdictF = verdict v t := by
  unfold check at h
  have h1 := (Bool.and_eq_true _ _).mp h
  have h2 := (Bool.and_eq_true _ _).mp h1.1
  exact ⟨beq_iff_eq.mp h2.1, beq_iff_eq.mp h2.2,
    beq_iff_eq.mp h1.2⟩

/-- Completeness: the honest certificate — every field the
recomputed value — is accepted. -/
theorem check_complete (v : View) (t : Thr) :
    check ⟨mu v, v.lambda, verdict v t⟩ v t = true := by
  unfold check
  simp

/- ---------------- T6.4: kernel controls ---------------- -/

/-- The passing fixture F1 in Lean form. -/
def viewPass : View :=
  { edges := [{ weight := 900, comps := [0, 1] }, { weight := 800, comps := [1, 2] }],
    dead := [3], cuts := [900, 1700], lambda := 3, confirmed := true }

def thrPass : Thr := { m1 := some 1000, bound := some (1500, 3) }

theorem control_pass : verdict viewPass thrPass = true := by decide

/-- One failure per condition, mirroring the fixture
battery F2–F6, and the no-threshold control F7. -/
def viewC1 : View := { viewPass with edges :=
  [{ weight := 500, comps := [0, 1] }, { weight := 400, comps := [1, 2] }] }
theorem control_c1 : verdict viewC1 { m1 := some 1000, bound := some (500, 3) } = false := by decide

def viewC2 : View := { viewPass with dead := [1] }
theorem control_c2 : verdict viewC2 thrPass = false := by decide

def viewC3 : View := { viewPass with confirmed := false }
theorem control_c3 : verdict viewC3 thrPass = false := by decide

def viewC4 : View := { viewPass with cuts := [900, 400] }
theorem control_c4 : verdict viewC4 thrPass = false := by decide

def viewC5 : View := { viewPass with edges :=
  [{ weight := 800, comps := [0, 1] }, { weight := 600, comps := [1, 2] }] }
theorem control_c5 : verdict viewC5 thrPass = false := by decide

theorem control_no_threshold :
    verdict viewPass { m1 := none, bound := some (1500, 3) } = false := by decide

/- ---------------- T6.1, T6.2: premises ---------------- -/

/-- T6.1 (soundness), as a premise: for an abstract
emergence predicate E over views, every view the procedure
certifies exhibits E. Stated, not proved, depended on by
nothing in this file. Its proof would also discharge rung
3's T3.8 in general form; that discharge has not happened. -/
def T61Premise (E : View → Prop) : Prop :=
  ∀ (v : View) (t : Thr), verdict v t = true → E v

/-- T6.2 (completeness on a registered class), as a premise:
over an abstract registered class, every view whose system
exhibits E is certified. Scoped to the class by the
statement's own form; never claimed for views outside it. -/
def T62Premise (E : View → Prop) (registered : View → Prop) : Prop :=
  ∀ (v : View) (t : Thr), registered v → E v → verdict v t = true

end Rung6
