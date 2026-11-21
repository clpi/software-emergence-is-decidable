/-
Emergence rung 4 — transfer: theorem obligations T4.1–T4.6.

Lean 4.19.0, core only, no sorry. Each theorem is proved in the
form stated in the rung-4 record (~/workspace/research/
emergence-rung4-2026-11-21.md):

- T4.1: extraction is a function of the source view alone: the
  interaction matrix is additive over edge-list concatenation
  (entry_append), the rank order is a defined function of the
  diagonal and a permutation of the index list (rank_perm), and
  the artifact is a composition of those functions, so equal
  views give equal artifacts (extract_det).
- T4.2: the canonical encoding's bit size factors through the
  entry count and the maximum entry; a permutation of the
  entries preserves both (length and fold-max), so the
  unstructured control, built by permuting A*'s entries, has
  exactly A*'s bit size for any width function.
- T4.3: selection-only carriage. The capability of a target run
  factors through the evaluated configuration sequence and the
  (artifact-free) score table: two artifacts inducing the same
  evaluated sequence give the same capability, and the selected
  configuration is always one of the evaluated ones, attaining
  the sequence's best score (pick_spec).
- T4.4: any entry count is preserved under a permutation of the
  entries; the null artifacts' entries are a permutation of
  A*'s by construction (checker-verified on the persisted
  artifacts), so their entry multisets equal A*'s.
- T4.5: PREMISE (stated as a definition, not proved, not an
  axiom, depended on by nothing). Discharged, if ever, only by
  rung 6. Never cited as evidence for the measured transfer.
- T4.6: carriage replay: a run's state is the fold of its log;
  folding a concatenated log is folding the prefix and
  continuing (restart form), so the target run and its search
  are exactly replayable from (registration, artifact, seed).
-/

namespace Rung4

/- ---------------- the interaction matrix and extraction ---------------- -/

/-- An edge family: pairs of a component set and its weight
(the view's hyperedges, ladder spec section 1.3). -/
abbrev Edges := List (List Nat × Nat)

/-- The interaction matrix entry: total weight of edges
containing both components. -/
def entry (E : Edges) (b c : Nat) : Nat :=
  ((E.filter (fun e => e.1.contains b && e.1.contains c)).map
    Prod.snd).sum

theorem sumapp (l₁ l₂ : List Nat) :
    (l₁ ++ l₂).sum = l₁.sum + l₂.sum := by
  induction l₁ with
  | nil => simp
  | cons a t ih => simp [List.sum_cons, ih]; omega

/-- T4.1 (additivity): the matrix of a concatenated edge family
is the entrywise sum of the matrices — extraction from parts
determines extraction from the whole. -/
theorem entry_append (E₁ E₂ : Edges) (b c : Nat) :
    entry (E₁ ++ E₂) b c = entry E₁ b c + entry E₂ b c := by
  simp [entry, List.filter_append, List.map_append, sumapp]

/-- The diagonal of the matrix, the rank key. -/
def diag (E : Edges) (b : Nat) : Nat := entry E b b

/-- One insertion step of the rank sort: a comes before b when
its diagonal is larger, or equal with a smaller index
(registration: descending diagonal, ties by ascending index). -/
def before (d : Nat → Nat) (a b : Nat) : Bool :=
  (d b < d a) || ((d a == d b) && (a < b))

def ins (d : Nat → Nat) (a : Nat) : List Nat → List Nat
  | [] => [a]
  | b :: t => if before d a b then a :: b :: t else b :: ins d a t

theorem ins_perm (d : Nat → Nat) (a : Nat) (l : List Nat) :
    (ins d a l).Perm (a :: l) := by
  induction l with
  | nil => simp [ins]
  | cons b t ih =>
    by_cases h : before d a b = true
    · simp [ins, h]
    · have h' : before d a b = false := by
        cases hb : before d a b with
        | true => exact absurd hb h
        | false => rfl
      simp only [ins, h', if_false]
      exact (List.Perm.cons b ih).trans (List.Perm.swap a b t)

/-- The rank order of an index list under a diagonal. -/
def rank (d : Nat → Nat) (l : List Nat) : List Nat :=
  l.foldr (ins d) []

theorem rank_perm (d : Nat → Nat) (l : List Nat) :
    (rank d l).Perm l := by
  induction l with
  | nil => rfl
  | cons a t ih =>
    show (ins d a (rank d t)).Perm (a :: t)
    exact (ins_perm d a (rank d t)).trans
      (List.Perm.cons a ih)

/-- The artifact: the matrix reindexed by the rank order of its
diagonal over the index list (registration: extraction). -/
def extract (E : Edges) (idx : List Nat) : List (List Nat) :=
  let r := rank (diag E) idx
  r.map (fun i => r.map (fun j => entry E i j))

/-- T4.1 (extraction determinism): A* is a function of the
source view alone — equal views (and equal index lists) give
equal artifacts, bit for bit under any encoding of the matrix. -/
theorem extract_det (E₁ E₂ : Edges) (idx : List Nat)
    (h : E₁ = E₂) : extract E₁ idx = extract E₂ idx := by
  rw [h]

/- ---------------- T4.2: information equality ---------------- -/

/-- The maximum of an entry list (0 for the empty list). -/
def top (l : List Nat) : Nat := l.foldr max 0

theorem top_perm {l₁ l₂ : List Nat} (h : l₁.Perm l₂) :
    top l₁ = top l₂ := by
  induction h with
  | nil => rfl
  | cons a _ ih =>
    show max a (top _) = max a (top _)
    rw [ih]
  | swap a b l =>
    show max b (max a (top l)) = max a (max b (top l))
    rw [← Nat.max_assoc, Nat.max_comm b a, Nat.max_assoc]
  | trans _ _ ih1 ih2 => rw [ih1, ih2]

/-- The canonical bit size of an entry list at width function
w: a fixed header plus one w(max)-byte word per entry. Any
encoding whose size factors through the entry count and the
maximum entry has this form. -/
def bits (w : Nat → Nat) (l : List Nat) : Nat :=
  8 * (4 + l.length * w (top l))

/-- T4.2 (information equality): a permutation of A*'s entries
— the unstructured control's construction — has exactly A*'s
bit size, for every width function. -/
theorem bits_perm (w : Nat → Nat) {l₁ l₂ : List Nat}
    (h : l₁.Perm l₂) : bits w l₁ = bits w l₂ := by
  rw [bits, bits, h.length_eq, top_perm h]

/- ---------------- T4.3: selection-only carriage ---------------- -/

/-- The search's selection step: fold a nonempty-start list
keeping the best-scoring element seen (ties keep the earlier
element). Scores are naturals (the harness's rationals scaled);
the score table is a parameter — no artifact appears in it. -/
def pick (score : Nat → Nat) (best : Nat) (l : List Nat) : Nat :=
  l.foldl (fun b m => if score m > score b then m else b) best

theorem pick_spec (score : Nat → Nat) (b : Nat) (l : List Nat) :
    (∀ m ∈ l, score m ≤ score (pick score b l))
    ∧ score b ≤ score (pick score b l)
    ∧ (pick score b l = b ∨ pick score b l ∈ l) := by
  induction l generalizing b with
  | nil =>
    exact ⟨fun m hm => by simp at hm, Nat.le_refl _, Or.inl rfl⟩
  | cons m t ih =>
    have step : pick score b (m :: t)
        = pick score (if score m > score b then m else b) t := rfl
    rw [step]
    have ih' := ih (b := if score m > score b then m else b)
    obtain ⟨h1, h2, h3⟩ := ih'
    by_cases hm : score m > score b
    · have e : (if score m > score b then m else b) = m := if_pos hm
      rw [e] at h1 h2 h3
      rw [e]
      refine ⟨?_, ?_, ?_⟩
      · intro x hx
        cases List.mem_cons.mp hx with
        | inl hx => rw [hx]; exact h2
        | inr hx => exact h1 x hx
      · omega
      · cases h3 with
        | inl h => refine Or.inr ?_; rw [h]; exact List.mem_cons_self
        | inr h => exact Or.inr (List.mem_cons_of_mem m h)
    · have e : (if score m > score b then m else b) = b := if_neg hm
      rw [e] at h1 h2 h3
      rw [e]
      refine ⟨?_, h2, ?_⟩
      · intro x hx
        cases List.mem_cons.mp hx with
        | inl hx => rw [hx]; omega
        | inr hx => exact h1 x hx
      · cases h3 with
        | inl h => exact Or.inl h
        | inr h => exact Or.inr (List.mem_cons_of_mem m h)

/-- Capability of a target run under an artifact, in the model:
the score table is fixed and artifact-free; the artifact enters
only through the evaluated sequence (its search order's
registered prefix). -/
def cap (score : Nat → Nat) (seq : List Nat) : Nat :=
  match seq with
  | [] => 0
  | m :: t => score (pick score m t)

/-- T4.3 (selection-only carriage): for any fixed evaluated
configuration sequence, the capability is identical whatever
artifact induced it — capability factors through the sequence
and the score table alone. -/
theorem cap_seq (score : Nat → Nat) (seq₁ seq₂ : List Nat)
    (h : seq₁ = seq₂) : cap score seq₁ = cap score seq₂ := by
  rw [h]

/-- T4.3 (the selected configuration is an evaluated one, and
attains the best score on the sequence): the content of the
selection step, from pick_spec. -/
theorem cap_attains (score : Nat → Nat) (m : Nat) (t : List Nat) :
    (∀ x ∈ m :: t, score x ≤ cap score (m :: t))
    ∧ (cap score (m :: t) = score m
       ∨ ∃ x ∈ m :: t, cap score (m :: t) = score x) := by
  have h := pick_spec score m t
  obtain ⟨h1, h2, h3⟩ := h
  refine ⟨?_, ?_⟩
  · intro x hx
    cases List.mem_cons.mp hx with
    | inl hx => rw [hx]; exact h2
    | inr hx => exact h1 x hx
  · cases h3 with
    | inl h => refine Or.inl ?_; show score (pick score m t) = score m
               rw [h]
    | inr h => exact Or.inr ⟨pick score m t,
        List.mem_cons_of_mem m h, rfl⟩

/- ---------------- T4.4: null exactness ---------------- -/

/-- Any count of a predicate is preserved under a permutation
of the list (rung 3's T3.7 core, restated for entries). -/
theorem count_perm {l₁ l₂ : List Nat} (h : l₁.Perm l₂)
    (p : Nat → Bool) : l₁.countP p = l₂.countP p := by
  induction h with
  | nil => rfl
  | cons a _ ih => simp only [List.countP_cons, ih]
  | swap a b l =>
    by_cases ha : p a <;> by_cases hb : p b <;>
      simp [List.countP_cons, ha, hb] <;> omega
  | trans _ _ ih1 ih2 => rw [ih1, ih2]

/-- T4.4 (null exactness): if a null artifact's flattened
entries are a permutation of A*'s (the registered conjugation
construction; verified on the persisted artifacts by the
checker), then every entry value occurs the same number of
times in both — the entry multisets are equal, so the null
distribution is over artifacts of identical information
content. -/
theorem null_counts {l₁ l₂ : List Nat} (h : l₁.Perm l₂) (v : Nat) :
    l₁.countP (fun x => x == v) = l₂.countP (fun x => x == v) :=
  count_perm h _

/- ---------------- T4.6: carriage replay ---------------- -/

/-- A run's state is the fold of its log (spec section 1.2),
generic over the state type and step function, as in rungs
2-3. -/
def run (step : W → Nat → W) (w : W) (L : List Nat) : W :=
  L.foldl step w

theorem run_append (step : W → Nat → W) (w : W)
    (L₁ L₂ : List Nat) :
    run step w (L₁ ++ L₂) = run step (run step w L₁) L₂ := by
  simp [run, List.foldl_append]

/-- T4.6 (carriage replay): restarting from any prefix of the
log alone reproduces the run — the whole run is the prefix
fold continued with the suffix — and the run is a function of
(step, initial state, log) alone, so the target run with A*
installed is exactly replayable from (registration, A*, seed),
the triple that determines those three inputs. -/
theorem replay (step : W → Nat → W) (w : W)
    (L₁ L₂ : List Nat) :
    run step w (L₁ ++ L₂) = run step (run step w L₁) L₂ :=
  run_append step w L₁ L₂

/- ---------------- T4.5: PREMISE (stated, not proved) ---------------- -/

/-- T4.5 (transfer bound) — PREMISE. This definition states the
premise; it is not proved in this file, it is not an axiom, and
no theorem here depends on it. It is discharged, if ever, only
by rung 6's certificate (T6.1). The battery's caps are
rationals in [0, 1]; they are carried here as naturals scaled
by a fixed positive factor, which preserves the inequality:
if the source view is certified at margin m and the target
view embeds the pattern with distortion at most d, then the
transfer advantage dt satisfies m <= dt + d (the natural form
of dt >= m - d). Rung 4's empirical claim does not depend on
this premise and it is never cited as evidence for dt. -/
def T45Premise (m d dt : Nat) (certified embedded : Prop) : Prop :=
  certified → embedded → m ≤ dt + d

end Rung4

#print axioms Rung4.entry_append
#print axioms Rung4.rank_perm
#print axioms Rung4.extract_det
#print axioms Rung4.top_perm
#print axioms Rung4.bits_perm
#print axioms Rung4.pick_spec
#print axioms Rung4.cap_seq
#print axioms Rung4.cap_attains
#print axioms Rung4.count_perm
#print axioms Rung4.null_counts
#print axioms Rung4.run_append
#print axioms Rung4.replay
