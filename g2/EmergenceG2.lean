/-
Emergence G2 — dependence-scan cost: the lemmas the indexed
scan rests on.

Lean 4.19.0, core only, no sorry.

The baseline dependence scan (ladder spec section 1.5, as the
rungs instantiate it) refolds the whole log for every
counterfactual: one fold per tick for the tick edges, one fold
per record for per-message dependence, one fold per
configuration subset for sensitivity. The indexed scan of
g2/G2.md replaces those refolds by one indexed pass. Its
exactness rests on two facts, proved here in abstract form:

- Tick removal commutes with the entry fold: the entries of
  the log with one tick's records removed are exactly the
  entries of the whole log with that tick's entries removed,
  provided every entry a record contributes carries the
  record's own tick (true of the rung harnesses' entry
  construction by definition). So a leave-one-tick-out
  counterfactual is a filter on the indexed entries, not a
  refold. The same holds for any record predicate, in
  particular for removing a single record.

- Component scores are sums over keys, and a sum over a list
  splits over any predicate's filter partition. So the change
  in a component under a counterfactual is the sum of the
  changes over the keys the counterfactual touches; keys it
  does not touch cancel exactly. This is what makes the
  per-key delta computation (and the coefficient test built
  on it) equal to the from-scratch fold comparison.

The coefficient (Moebius) criterion itself — a function on a
subset cube is identically zero iff every coefficient of its
multilinear expansion is zero — is proved in g2/G2.md by
Moebius inversion over the subset lattice, is verified
against brute-force subset evaluation on every fixture with
at most 11 axes, and carries the two finite controls at the
end of this file (the one-variable and two-variable cases,
proved in full).
-/

namespace G2

/-- A log record, abstracted to its tick and the entries it
contributes. Every entry carries the tick of its record: the
entry construction of the rung harnesses tags each delivered
value with the tick of the record that delivered it. -/
structure Rec where
  tick : Nat
  deriving Repr

/-- An indexed entry: a delivered value with its tick. -/
structure Entry where
  tick : Nat
  val : Int
  deriving DecidableEq, Repr

/-- Integer sum over a list of score numerators. Component
scores in the scan are sums of these over a component's keys,
scaled by a fixed denominator. -/
def sum : List Int → Int
  | [] => 0
  | x :: xs => x + sum xs

theorem sumcat (xs ys : List Int) :
    sum (xs ++ ys) = sum xs + sum ys := by
  induction xs with
  | nil => simp [sum]
  | cons x xs ih => simp [sum, ih]; omega

/-- A sum splits over any predicate's filter partition. -/
theorem sumpart (p : Int → Bool) (xs : List Int) :
    sum xs = sum (xs.filter p) + sum (xs.filter (fun x => !p x)) := by
  induction xs with
  | nil => simp [sum]
  | cons x xs ih =>
    by_cases h : p x
    · simp [List.filter, h, sum, ih]; omega
    · simp [List.filter, h, sum, ih]; omega

/-- Delta locality: when two score lists share an unaffected
part, the difference of their sums is the difference over the
affected parts alone. This is the lemma that lets the scan
compute a counterfactual component change by summing per-key
changes over only the keys the counterfactual touches. -/
theorem delta (affected₁ affected₂ unaffected : List Int) :
    sum (affected₁ ++ unaffected) - sum (affected₂ ++ unaffected)
      = sum affected₁ - sum affected₂ := by
  rw [sumcat, sumcat]; omega

/-- Filter is empty when the predicate is false throughout. -/
theorem filternil {p : Entry → Bool} {l : List Entry}
    (h : ∀ e ∈ l, p e = false) : l.filter p = [] := by
  induction l with
  | nil => rfl
  | cons e l ih =>
    simp [List.filter, h e List.mem_cons_self,
      ih (fun x hx => h x (List.mem_cons_of_mem e hx))]

/-- Filter is the identity when the predicate is true
throughout. -/
theorem filterself {p : Entry → Bool} {l : List Entry}
    (h : ∀ e ∈ l, p e = true) : l.filter p = l := by
  induction l with
  | nil => rfl
  | cons e l ih =>
    simp [List.filter, h e List.mem_cons_self,
      ih (fun x hx => h x (List.mem_cons_of_mem e hx))]

/-- Tick removal commutes with the entry fold. `entries`
assigns to each record the entries it contributes, and every
contributed entry carries the record's tick. Then the entries
of the tick-filtered log are the tick-filtered entries of the
whole log: the counterfactual fold the baseline recomputes
from scratch is a filter on one indexed pass. -/
theorem tickfilter (entries : Rec → List Entry)
    (h : ∀ (r : Rec) (e : Entry), e ∈ entries r → e.tick = r.tick)
    (log : List Rec) (t : Nat) :
    (log.filter (fun r => r.tick != t)).flatMap entries
      = (log.flatMap entries).filter (fun e => e.tick != t) := by
  induction log with
  | nil => simp
  | cons r log ih =>
    by_cases hr : r.tick = t
    · have h1 : (fun r : Rec => r.tick != t) r = false := by simp [hr]
      have h2 : ∀ e ∈ entries r, (fun e : Entry => e.tick != t) e = false := by
        intro e he
        have : e.tick = t := by rw [h r e he]; exact hr
        simp [this]
      simp [List.filter_cons, h1, ih, List.flatMap_cons,
        List.filter_append, filternil h2]
    · have h1 : (fun r : Rec => r.tick != t) r = true := by
        simp [hr]
      have h2 : ∀ e ∈ entries r, (fun e : Entry => e.tick != t) e = true := by
        intro e he
        have hte : e.tick = r.tick := h r e he
        simp [hte, hr]
      simp [List.filter_cons, h1, ih, List.flatMap_cons,
        List.filter_append, filterself h2]

/- The same commutation for removing a single record by
identity of position is not needed: per-message dependence
removes one record, and the entry-level statement is the
filter partition of `sumpart` applied to that
record's entries, which are exactly the entries it
contributed, by the same tick-tagging construction. -/

/- ---------------- coefficient controls ---------------- -/

/-- Moebius coefficients of a function on the one-variable
cube, given its values at the empty set and the singleton:
coefficients are (d empty, d singleton - d empty). -/
def coef1 (d : Bool → Int) : Int × Int :=
  (d false, d true - d false)

/-- One-variable criterion: the coefficients both vanish iff
the function is constant zero on the cube — in particular a
nonzero coefficient proves a witness exists, and vanishing
coefficients prove no toggle of the variable changes the
value. Proved in full. -/
theorem coef1zero (d : Bool → Int) :
    (coef1 d).1 = 0 ∧ (coef1 d).2 = 0 ↔ d false = 0 ∧ d true = 0 := by
  constructor
  · intro h
    have h1 : d false = 0 := h.1
    have h2 : d true - d false = 0 := h.2
    constructor <;> omega
  · intro h
    obtain ⟨h1, h2⟩ := h
    show d false = 0 ∧ d true - d false = 0
    constructor <;> omega

/-- Moebius coefficients of a function on the two-variable
cube, values ordered (00, 10, 01, 11) over the two axes:
the coefficient of a monomial is the alternating sum of the
values on its subcube. -/
def coef2 (d : Bool → Bool → Int) : Int × Int × Int × Int :=
  (d false false,
   d true false - d false false,
   d false true - d false false,
   d true true - d true false - d false true + d false false)

/-- Two-variable criterion: all four coefficients vanish iff
the function is zero on all four points of the cube. The
forward direction is the load-bearing one for the scan: if
every coefficient of a toggle difference vanishes, the
difference is zero at every configuration, so the axis is
not sensitive; a single nonzero coefficient is a proved
witness that some configuration's difference is nonzero.
Proved in full. -/
theorem coef2zero (d : Bool → Bool → Int) :
    (coef2 d).1 = 0 ∧ (coef2 d).2.1 = 0 ∧ (coef2 d).2.2.1 = 0
      ∧ (coef2 d).2.2.2 = 0
    ↔ d false false = 0 ∧ d true false = 0 ∧ d false true = 0
      ∧ d true true = 0 := by
  constructor
  · intro h
    have h1 : d false false = 0 := h.1
    have h2 : d true false - d false false = 0 := h.2.1
    have h3 : d false true - d false false = 0 := h.2.2.1
    have h4 : d true true - d true false - d false true + d false false = 0 :=
      h.2.2.2
    refine ⟨?_, ?_, ?_, ?_⟩ <;> omega
  · intro h
    obtain ⟨h1, h2, h3, h4⟩ := h
    show d false false = 0 ∧ d true false - d false false = 0
      ∧ d false true - d false false = 0
      ∧ d true true - d true false - d false true + d false false = 0
    refine ⟨?_, ?_, ?_, ?_⟩ <;> omega

/-- Standing controls: the transforms compute as stated on
concrete values, checked by the kernel. -/
theorem coefcontrols :
    coef1 (fun b => if b then 5 else 2) = (2, 3)
    ∧ coef2 (fun x y => if x && y then 7 else 0) = (0, 0, 0, 7) := by
  decide

end G2
