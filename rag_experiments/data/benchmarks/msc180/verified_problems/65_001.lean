import Mathlib

open Set

theorem unique_root_of_nonzero_deriv {a b : ℝ} (hab : a < b) (f : ℝ → ℝ)
    (hf : ContinuousOn f (Icc a b))
    (hderiv : ∀ x ∈ Ioo a b, DifferentiableAt ℝ f x)
    (hnonzero : ∀ x ∈ Ioo a b, deriv f x ≠ 0) :
    ∀ (p q : ℝ), p ∈ Icc a b → q ∈ Icc a b → f p = 0 → f q = 0 → p = q := by
  intro p q hp hq hfp hfq
  by_contra hpq
  have hrolle : ∀ {u v : ℝ}, u < v →
      u ∈ Icc a b → v ∈ Icc a b → f u = 0 → f v = 0 → False := by
    intro u v huv hu hv hfu hfv
    have hcont_uv : ContinuousOn f (Icc u v) :=
      hf.mono (Icc_subset_Icc hu.1 hv.2)
    have hderiv_uv : ∀ x ∈ Ioo u v, DifferentiableAt ℝ f x := by
      intro x hx
      exact hderiv x ⟨lt_of_le_of_lt hu.1 hx.1, lt_of_lt_of_le hx.2 hv.2⟩
    obtain ⟨c, hc, hdc⟩ := exists_deriv_eq_zero huv hcont_uv (by simp [hfu, hfv])
    exact (hnonzero c ⟨lt_of_le_of_lt hu.1 hc.1, lt_of_lt_of_le hc.2 hv.2⟩) hdc
  rcases lt_or_gt_of_ne hpq with hpq' | hqp'
  · exact hrolle hpq' hp hq hfp hfq
  · exact hrolle hqp' hq hp hfq hfp

/-
Used theorem names explicitly mentioned in the proof above (reduced to most relevant):
- exists_deriv_eq_zero
- lt_or_gt_of_ne
-/

/- Statements of the listed theorems -/
-- theorem exists_deriv_eq_zero : {f : ℝ → ℝ} {a b : ℝ} (hab : a < b) (hfc : ContinuousOn f (Set.Icc a b)) (hfI : f a = f b) :
--   ∃ c ∈ Set.Ioo a b, deriv f c = 0

-- theorem lt_or_gt_of_ne : {α : Type u_1} [LinearOrder α] {a b : α} (h : a ≠ b) : a < b ∨ a > b

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `exists_deriv_eq_zero`
-- Source: .lake/packages/mathlib/Mathlib/Analysis/Calculus/LocalExtr/Polynomial.lean:35
example {a b : ℝ} {f : ℝ → ℝ} (hab : a < b) (hfc : ContinuousOn f (Set.Icc a b))
    (hEq : f a = f b) : ∃ c ∈ Set.Ioo a b, deriv f c = 0 := by
  exact exists_deriv_eq_zero hab hfc hEq

-- Uses `lt_or_gt_of_ne`
-- Source: .lake/packages/mathlib/Mathlib/Order/Basic.lean:373
example [LinearOrder α] {a b : α} (h : a ≠ b) : a < b ∨ b < a := by
  exact lt_or_gt_of_ne h
