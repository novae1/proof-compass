import Mathlib

open Function

theorem kernel_subgroup_and_isomorphism {G H : Type*} [AddCommGroup G] [AddCommGroup H]
    (φ : G →+ H) :
    φ.ker = {g | φ g = 0} ∧ (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H)) := by
  constructor
  · ext g
    rfl
  · intro hsurj
    exact ⟨QuotientAddGroup.quotientKerEquivOfSurjective φ hsurj⟩

/-
Used theorem names explicitly mentioned in the proof above:
- QuotientAddGroup.quotientKerEquivOfSurjective
-/

/- Statements of the listed theorems -/
-- theorem QuotientAddGroup.quotientKerEquivOfSurjective : {G : Type u} [AddGroup G] {H : Type v} [AddGroup H] (φ : G →+ H)
--   (hφ : Function.Surjective ⇑φ) : G ⧸ φ.ker ≃+ H

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `QuotientAddGroup.quotientKerEquivOfSurjective`
-- Source: .lake/packages/mathlib/Mathlib/GroupTheory/Index.lean:228
example {G H : Type*} [AddCommGroup G] [AddCommGroup H]
    (φ : G →+ H) (hφ : Surjective φ) :
    Nonempty (G ⧸ φ.ker ≃+ H) := by
  exact ⟨QuotientAddGroup.quotientKerEquivOfSurjective φ hφ⟩
