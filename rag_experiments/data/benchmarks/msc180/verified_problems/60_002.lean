import Mathlib

open scoped BigOperators

theorem weierstrass_approximation (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
    (ε : ℝ) (hε : ε > 0) :
    ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε := by
  obtain ⟨B, hB⟩ := exists_polynomial_near_of_continuousOn 0 1 f hf ε hε
  refine ⟨B, ?_⟩
  intro x hx
  exact (hB x hx).le

/-
Used theorem names explicitly mentioned in the proof above:
- exists_polynomial_near_of_continuousOn
-/

/- Statements of the listed theorems -/
-- theorem exists_polynomial_near_of_continuousOn : (a b : ℝ) (f : ℝ → ℝ) (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
--   ∃ p, ∀ x ∈ Set.Icc a b, |Polynomial.eval x p - f x| < ε

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `exists_polynomial_near_of_continuousOn`
-- Source: .lake/packages/mathlib/Mathlib/Topology/ContinuousMap/Weierstrass.lean:107
example (a b : ℝ) (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (hε : 0 < ε) :
    ∃ p : Polynomial ℝ, ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  exact exists_polynomial_near_of_continuousOn a b f hf ε hε
