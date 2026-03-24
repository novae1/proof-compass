import Mathlib

theorem homomorphism_agreement {R A B : Type*} [CommSemiring R] [Semiring A] [Semiring B]
    [Algebra R A] [Algebra R B] {X : Set A} (hgen : Algebra.adjoin R X = ⊤)
    {α β : A →ₐ[R] B} (h_agree : ∀ x ∈ X, α x = β x) :
    α = β := by
  have hX : X ⊆ AlgHom.equalizer α β := by
    intro x hx
    exact (AlgHom.mem_equalizer α β x).2 (h_agree x hx)
  have hadjoin : Algebra.adjoin R X ≤ AlgHom.equalizer α β := Algebra.adjoin_le hX
  have htop : (⊤ : Subalgebra R A) ≤ AlgHom.equalizer α β := by
    simpa [hgen] using hadjoin
  exact (AlgHom.equalizer_eq_top (φ := α) (ψ := β)).1 (top_unique htop)

/-
Used theorem names explicitly mentioned in the proof above:
- AlgHom.mem_equalizer
- Algebra.adjoin_le
- AlgHom.equalizer_eq_top
- top_unique
-/

/- Statements of the listed theorems -/
-- theorem AlgHom.mem_equalizer : {R : Type u_1} {A : Type u_2} {B : Type u_3} [CommSemiring R] [Semiring A]
--   [Algebra R A] [Semiring B] [Algebra R B] {F : Type u_4} [FunLike F A B] [AlgHomClass F R A B] (φ ψ : F) (x : A) :
--   x ∈ AlgHom.equalizer φ ψ ↔ φ x = ψ x

-- theorem Algebra.adjoin_le : {R : Type uR} {A : Type uA} [CommSemiring R] [Semiring A] [Algebra R A] {s : Set A}
--   {S : Subalgebra R A} (H : s ⊆ ↑S) : Algebra.adjoin R s ≤ S

-- theorem AlgHom.equalizer_eq_top : {R : Type u_1} {A : Type u_2} {B : Type u_3} [CommSemiring R] [Semiring A]
--   [Algebra R A] [Semiring B] [Algebra R B] {F : Type u_4} [FunLike F A B] [AlgHomClass F R A B] {φ ψ : F} :
--   AlgHom.equalizer φ ψ = ⊤ ↔ φ = ψ

-- theorem top_unique : {α : Type u} [PartialOrder α] [OrderTop α] {a : α} (h : ⊤ ≤ a) : a = ⊤

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `AlgHom.mem_equalizer`
-- Source: .lake/packages/mathlib/Mathlib/FieldTheory/PolynomialGaloisGroup.lean:74
example {R A B : Type*} [CommSemiring R] [Semiring A] [Semiring B]
    [Algebra R A] [Algebra R B] (α β : A →ₐ[R] B) (x : A) :
    x ∈ AlgHom.equalizer α β ↔ α x = β x := by
  simpa using (AlgHom.mem_equalizer α β x)

-- Uses `Algebra.adjoin_le`
-- Source: .lake/packages/mathlib/Mathlib/FieldTheory/Adjoin.lean:525
example {F E : Type*} [Field F] [Field E] [Algebra F E] (S : Set E) :
    Algebra.adjoin F S ≤ (IntermediateField.adjoin F S).toSubalgebra := by
  exact Algebra.adjoin_le (IntermediateField.subset_adjoin F S)

-- Uses `AlgHom.equalizer_eq_top`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/Algebra/Subalgebra/Basic.lean:1203
example {R A B F : Type*} [CommSemiring R] [Semiring A] [Semiring B]
    [Algebra R A] [Algebra R B] [FunLike F A B] [AlgHomClass F R A B] (φ : F) :
    AlgHom.equalizer φ φ = ⊤ := by
  exact AlgHom.equalizer_eq_top.2 rfl

-- Uses `top_unique`
-- Source: .lake/packages/mathlib/Mathlib/Topology/MetricSpace/HausdorffDimension.lean:146
example {α : Type*} [PartialOrder α] [OrderTop α] {a : α} (h : ⊤ ≤ a) : a = ⊤ := by
  exact top_unique h
