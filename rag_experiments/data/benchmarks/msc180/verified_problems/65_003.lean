import Mathlib

open Metric Set NNReal

theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
  have hbounded' : ∀ x ∈ Icc a b, ‖deriv f x‖₊ ≤ L := by
    intro x hx
    exact_mod_cast hbounded x hx
  simpa using (convex_Icc a b).lipschitzOnWith_of_nnnorm_deriv_le hderiv hbounded'

/-
Used theorem names explicitly mentioned in the proof above:
- convex_Icc
- Convex.lipschitzOnWith_of_nnnorm_deriv_le
-/

/- Statements of the listed theorems -/
-- theorem convex_Icc : {𝕜 : Type u_1} {β : Type u_4} [OrderedSemiring 𝕜] [OrderedAddCommMonoid β] [Module 𝕜 β]
--   [OrderedSMul 𝕜 β] (r s : β) : Convex 𝕜 (Set.Icc r s)

-- theorem Convex.lipschitzOnWith_of_nnnorm_deriv_le : {𝕜 : Type u_3} {G : Type u_4} [RCLike 𝕜] [NormedAddCommGroup G]
--   [NormedSpace 𝕜 G] {f : 𝕜 → G} {s : Set 𝕜} {C : NNReal} (hf : ∀ x ∈ s, DifferentiableAt 𝕜 f x)
--   (bound : ∀ x ∈ s, ‖deriv f x‖₊ ≤ C) (hs : Convex ℝ s) : LipschitzOnWith C f s

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `convex_Icc`
-- Source: .lake/packages/mathlib/Mathlib/Analysis/Convex/SpecificFunctions/Deriv.lean:161
example : StrictConcaveOn ℝ (Icc (-(Real.pi / 2)) (Real.pi / 2)) Real.cos := by
  apply strictConcaveOn_of_deriv2_neg (convex_Icc _ _) Real.continuousOn_cos fun x hx => ?_
  rw [interior_Icc] at hx
  simpa using Real.cos_pos_of_mem_Ioo hx

-- Uses `Convex.lipschitzOnWith_of_nnnorm_deriv_le`
-- Source: .lake/packages/mathlib/Mathlib/Analysis/Calculus/MeanValue.lean:660
example {𝕜 G : Type*} [RCLike 𝕜] [NormedAddCommGroup G] [NormedSpace 𝕜 G] [CompleteSpace G]
    {f : 𝕜 → G} {C : ℝ≥0} (hf : Differentiable 𝕜 f) (bound : ∀ x, ‖deriv f x‖₊ ≤ C) :
    LipschitzWith C f := by
  exact lipschitzOnWith_univ.1 <|
    Convex.lipschitzOnWith_of_nnnorm_deriv_le
      (hf := fun x _ => hf x)
      (bound := fun x _ => bound x)
      convex_univ

-- The mean value theorem set in dimension 1: if the derivative of a function is bounded by `C`,
-- then the function is `C`-Lipschitz. Version with `deriv` and `LipschitzWith`.
