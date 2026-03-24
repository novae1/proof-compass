import Mathlib

open Equiv

def excedances {n : ℕ} (π : Perm (Fin n)) : Finset (Fin n) :=
  Finset.univ.filter (fun i => π i > i)

def eulerianNumber (n k : ℕ) : ℕ :=
  Fintype.card {π : Perm (Fin n) | (excedances π).card = k}

def coexcedances {n : ℕ} (π : Perm (Fin n)) : Finset (Fin n) :=
  Finset.univ.filter (fun i => π i < i)

theorem excedance_coexcedance_dual {n : ℕ} (π : Perm (Fin n)) :
    (excedances π).card = (coexcedances π⁻¹).card := by
  classical
  have himage : coexcedances π⁻¹ = (excedances π).image π := by
    ext j
    constructor
    · intro hj
      refine Finset.mem_image.2 ?_
      refine ⟨π⁻¹ j, ?_, by simp⟩
      simpa [coexcedances, excedances] using hj
    · intro hj
      rcases Finset.mem_image.1 hj with ⟨i, hi, rfl⟩
      have hi' : π i > i := by simpa [excedances] using hi
      simpa [coexcedances] using hi'
  calc
    (excedances π).card = ((excedances π).image π).card := by
      exact (Finset.card_image_of_injective (s := excedances π) (f := π) π.injective).symm
    _ = (coexcedances π⁻¹).card := by simp [himage]

/-
Used theorem names explicitly mentioned in the proof above:
- Finset.mem_image
- Finset.card_image_of_injective
-/

/- Statements of the listed theorems -/
-- theorem Finset.mem_image : {α : Type u_1} {β : Type u_2} [DecidableEq β] {f : α → β} {s : Finset α} {b : β} :
--   b ∈ Finset.image f s ↔ ∃ a ∈ s, f a = b

-- theorem Finset.card_image_of_injective : {α : Type u_1} {β : Type u_2} {f : α → β} [DecidableEq β] (s : Finset α)
--   (H : Function.Injective f) : (Finset.image f s).card = s.card

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `Finset.mem_image`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/MonoidAlgebra/Support.lean:46
example {k G : Type*} [Semiring k] [DecidableEq G] [Mul G] (f : MonoidAlgebra k G) {r : k}
    (hr : ∀ y, r * y = 0 ↔ y = 0) {x y : G}
    (hy : y ∈ Finset.image (x * ·) f.support) :
    ∃ a : G, a ∈ f.support ∧ x * a = y := by
  simpa only [Finset.mem_image, exists_prop] using hy

-- Uses `Finset.card_image_of_injective`
-- Source: .lake/packages/mathlib/Mathlib/Data/Finset/NAry.lean:205
example {α β γ : Type*} [DecidableEq β] [DecidableEq γ] (f : α → β → γ) (a : α) (t : Finset β)
    (hf : Function.Injective (f a)) : (Finset.image₂ f {a} t).card = t.card := by
  simpa [Finset.image₂_singleton_left] using
    (Finset.card_image_of_injective (s := t) (f := f a) hf)
