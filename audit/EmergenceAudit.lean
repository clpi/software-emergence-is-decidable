/-
Emergence premise audit (spec section 6.3 route) — the T5.6
discharge.

Lean 4.19.0, core only, no sorry. This file proves T5.6 (mu
monotonicity under accumulation, ladder spec section 4.4) in
the form the rung-5 registration states it, for the concrete
measure: mu of a cut is the total weight of the cut's engaged
edges — the edges lying entirely inside the cut's live set
(F1's definition, as the rung-3 file's muOf). The premise
definition in EmergenceRung5.lean quantified over an abstract
mu, which no proof can discharge; here mu is the measure
itself, the antecedent is the premise's own (no edge of the
earlier cut is absent from the later cut, and the live set
only grows), and one standing hypothesis is named, not
hidden: a cut's edge family is duplicate-free. In the rung-5
instrument that is constructional — one edge per tick, ticks
distinct — and the battery's scope table is stated over edge
sets, which is the same fact.

The remaining three premises of the ladder family (T3.8,
T4.5, T5.4) are not stated here: the audit record
(~/workspace/research/emergence-premise-audit-2026-11-21.md)
gives their derivation graphs and the named reason each one
stays a premise. Nothing in this file is depended on by any
battery verdict.
-/

namespace Audit

/-- The measure of an edge family: the total weight of its
edges, weights carried by the family itself. -/
def mu (w : List Nat → Nat) (E : List (List Nat)) : Nat :=
  (E.map w).sum

/-- The engaged part of an edge family at a live set: the
edges lying entirely inside the live set (F1 section 3). -/
def engaged (live : List Nat) (E : List (List Nat)) :
    List (List Nat) :=
  E.filter (fun e => e.all (fun a => live.contains a))

/-- The sum of a joined list of weights is the sum of the
parts (proved here; core states it only for folds). -/
theorem join (l₁ l₂ : List Nat) :
    (l₁ ++ l₂).sum = l₁.sum + l₂.sum := by
  induction l₁ with
  | nil => simp
  | cons a t ih => simp [List.sum_cons, ih]; omega

/-- A member of a list splits the list around it. -/
theorem split {e : List Nat} :
    ∀ (l : List (List Nat)), e ∈ l →
      ∃ L R, l = L ++ e :: R := by
  intro l
  induction l with
  | nil => intro h; simp at h
  | cons a t ih =>
    intro h
    have hmem := List.mem_cons.mp h
    cases hmem with
    | inl hh =>
      exact ⟨[], t, by simp [hh]⟩

    | inr hh =>
      obtain ⟨L, R, hR⟩ := ih hh
      exact ⟨a :: L, R, by rw [hR]; rfl⟩

/-- The sum lemma in the premise's own form: over a
duplicate-free family, membership inclusion of families
gives the weight inequality. -/
theorem carry (w : List Nat → Nat) :
    ∀ (E₁ E₂ : List (List Nat)), E₁.Nodup →
      (∀ e ∈ E₁, e ∈ E₂) → mu w E₁ ≤ mu w E₂ := by
  intro E₁
  induction E₁ with
  | nil => intro E₂ _ _; exact Nat.zero_le _
  | cons e t ih =>
    intro E₂ hnd hsub
    have hne : e ∉ t := (List.nodup_cons.mp hnd).1
    have htnd : t.Nodup := (List.nodup_cons.mp hnd).2
    have he : e ∈ E₂ :=
      hsub e (List.mem_cons_self : e ∈ e :: t)
    obtain ⟨L, R, hE₂⟩ := split E₂ he
    have ht : ∀ x ∈ t, x ∈ L ++ R := by
      intro x hx
      have hx₂ : x ∈ E₂ := hsub x (List.mem_cons_of_mem e hx)
      rw [hE₂] at hx₂
      have hmem := List.mem_append.mp hx₂
      cases hmem with
      | inl h => exact List.mem_append_left R h
      | inr h =>
        have hmem₂ := List.mem_cons.mp h
        cases hmem₂ with
        | inl h =>
          exact absurd h.symm (fun hh => hne (hh ▸ hx))
        | inr h => exact List.mem_append_right L h
    have hle := ih (L ++ R) htnd ht
    have hLR : mu w (L ++ R) = mu w L + mu w R := by
      simp only [mu, List.map_append, join]
    have hsum : mu w E₂ = mu w L + w e + mu w R := by
      rw [hE₂]
      simp only [mu, List.map_append, List.map_cons, join,
        List.sum_cons]
      omega
    have hcons : mu w (e :: t) = w e + mu w t := by
      simp only [mu, List.map_cons, List.sum_cons]
    rw [hcons, hsum]
    omega

/-- Engaged monotonicity: if no edge of the earlier family
is absent from the later family and the live set only
grows, the earlier engaged family is a membership
subfamily of the later one, duplicate-free by construction,
so its measure is at most the later measure. -/
theorem bound (w : List Nat → Nat) (live₁ live₂ : List Nat)
    (E₁ E₂ : List (List Nat)) (hnd : E₁.Nodup)
    (hedges : ∀ e ∈ E₁, e ∈ E₂)
    (hlive : ∀ a ∈ live₁, a ∈ live₂) :
    mu w (engaged live₁ E₁) ≤ mu w (engaged live₂ E₂) := by
  apply carry w _ _ (hnd.filter _)
  intro e he
  have hmem := List.mem_filter.mp he
  have hall : ∀ a ∈ e, a ∈ live₂ := by
    intro a ha
    have h1 : (fun x => live₁.contains x) a = true :=
      (List.all_eq_true.mp hmem.2) a ha
    have h2 : a ∈ live₁ := List.contains_iff_mem.mp h1
    exact hlive a h2
  exact List.mem_filter.mpr ⟨hedges e hmem.1,
    List.all_eq_true.mpr (fun a ha =>
      List.contains_iff_mem.mpr (hall a ha))⟩

/-- T5.6 (monotonicity under accumulation), discharged for
the concrete measure: with mu at a cut defined as the total
engaged weight of the cut's view, the premise's implication
is a theorem. The antecedent is the premise's own — between
any two cuts, the appended records remove no hyperedge and
the live set only grows — and the duplicate-free hypothesis
is the instrument's one-edge-per-tick construction, named
in the file header. The battery measures the antecedent per
checkpoint pair; this theorem is the implication itself. -/
theorem t56 (w : List Nat → Nat) (live : Nat → List Nat)
    (edges : Nat → List (List Nat))
    (hnd : ∀ i, (edges i).Nodup)
    (hant : ∀ i j, i ≤ j →
      (∀ e ∈ edges i, e ∈ edges j) ∧
      (∀ a ∈ live i, a ∈ live j)) :
    ∀ i j, i ≤ j →
      mu w (engaged (live i) (edges i)) ≤
        mu w (engaged (live j) (edges j)) := by
  intro i j hij
  exact bound w (live i) (live j) (edges i) (edges j)
    (hnd i) (hant i j hij).1 (hant i j hij).2

end Audit

#print axioms Audit.join
#print axioms Audit.split
#print axioms Audit.carry
#print axioms Audit.bound
#print axioms Audit.t56
