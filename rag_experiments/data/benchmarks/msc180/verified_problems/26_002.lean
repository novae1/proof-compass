import Mathlib

theorem exists_sup_of_bddAbove {A : Set ℝ} (hne : A.Nonempty) (hbd : BddAbove A) :
    ∃ s : ℝ, IsLUB A s := by
  exact Real.exists_isLUB hne hbd

/-
Used theorem names explicitly mentioned in the proof above:
- Real.exists_isLUB
-/

/- Statements of the listed theorems -/
-- theorem Real.exists_isLUB : {s : Set ℝ} (hne : s.Nonempty) (hbdd : BddAbove s) : ∃ x, IsLUB s x

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `Real.exists_isLUB`
-- Source: .lake/packages/mathlib/Mathlib/Topology/Instances/NNReal.lean:275
example {f : ℕ → ℝ} (h_bdd : BddAbove (Set.range f))
    (h_mon : Monotone f) : ∃ r : ℝ, Filter.Tendsto f Filter.atTop (nhds r) := by
  obtain ⟨B, hB⟩ := Real.exists_isLUB (Set.range_nonempty f) h_bdd
  exact ⟨B, tendsto_atTop_isLUB h_mon hB⟩

-- An antitone, bounded below sequence `f : ℕ → ℝ` has a finite limit.
