import Mathlib

open Matrix

theorem column_row_factorization {m n : ℕ} (A : Matrix (Fin m) (Fin n) ℂ) (hc : A.rank ≥ 1) :
    ∃ (c : ℕ) (h : c = A.rank) (C : Matrix (Fin m) (Fin c) ℂ)
      (R : Matrix (Fin c) (Fin n) ℂ), A = C * R := by
  have _ : A.rank ≥ 1 := hc
  classical
  let c : ℕ := A.rank
  let hcr : Module.finrank ℂ (LinearMap.range A.mulVecLin) = c := by
    simp [c, Matrix.rank]
  let b : Basis (Fin c) ℂ (LinearMap.range A.mulVecLin) :=
    Module.finBasisOfFinrankEq ℂ (LinearMap.range A.mulVecLin) hcr
  let e : (Fin c →₀ ℂ) ≃ₗ[ℂ] (Fin c → ℂ) := Finsupp.linearEquivFunOnFinite ℂ ℂ (Fin c)
  let beq : (LinearMap.range A.mulVecLin) ≃ₗ[ℂ] (Fin c → ℂ) := b.repr.trans e
  let incl : (Fin c → ℂ) →ₗ[ℂ] (Fin m → ℂ) :=
    (LinearMap.range A.mulVecLin).subtype.comp beq.symm.toLinearMap
  let rr : (Fin n → ℂ) →ₗ[ℂ] LinearMap.range A.mulVecLin :=
    LinearMap.rangeRestrict (R := ℂ) A.mulVecLin
  let coord : (Fin n → ℂ) →ₗ[ℂ] (Fin c → ℂ) := beq.toLinearMap.comp rr
  let C : Matrix (Fin m) (Fin c) ℂ := Matrix.toLin'.symm incl
  let R : Matrix (Fin c) (Fin n) ℂ := Matrix.toLin'.symm coord
  have hcomp : A.mulVecLin = incl.comp coord := by
    ext v i
    simp [incl, coord, rr, beq, e, LinearMap.rangeRestrict]
  refine ⟨c, rfl, C, R, ?_⟩
  apply Matrix.toLin'.injective
  have hC : Matrix.toLin' C = incl := by simp [C]
  have hR : Matrix.toLin' R = coord := by simp [R]
  calc
    Matrix.toLin' A = A.mulVecLin := rfl
    _ = incl.comp coord := hcomp
    _ = (Matrix.toLin' C).comp (Matrix.toLin' R) := by simpa [hC, hR]
    _ = Matrix.toLin' (C * R) := by simpa [Matrix.toLin'_mul]

/-
Used theorem names explicitly mentioned in the proof above (reduced to most relevant):
- Module.finBasisOfFinrankEq
- Finsupp.linearEquivFunOnFinite
- LinearMap.rangeRestrict
-/

/- Statements of the listed theorems -/
-- theorem Module.finBasisOfFinrankEq : (R : Type u) (M : Type v) [Ring R] [StrongRankCondition R] [AddCommGroup M]
--   [Module R M] [Module.Free R M] [Module.Finite R M] {n : ℕ} (hn : Module.finrank R M = n) : Basis (Fin n) R M

-- theorem Finsupp.linearEquivFunOnFinite : (R : Type u_7) (M : Type u_9) (α : Type u_10) [Finite α]
--   [AddCommMonoid M] [Semiring R] [Module R M] : (α →₀ M) ≃ₗ[R] α → M

-- theorem LinearMap.rangeRestrict : {R : Type u_1} {R₂ : Type u_2} {M : Type u_5} {M₂ : Type u_6} [Semiring R]
--   [Semiring R₂] [AddCommMonoid M] [AddCommMonoid M₂] [Module R M] [Module R₂ M₂] {τ₁₂ : R →+* R₂}
--   [RingHomSurjective τ₁₂] (f : M →ₛₗ[τ₁₂] M₂) : M →ₛₗ[τ₁₂] ↥(LinearMap.range f)

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `Module.finBasisOfFinrankEq`
-- Source: .lake/packages/mathlib/Mathlib/MeasureTheory/Measure/Lebesgue/EqHaar.lean:560
noncomputable example {R M : Type*} [Ring R] [StrongRankCondition R] [AddCommGroup M] [Module R M]
    [Module.Free R M] [Module.Finite R M] {n : ℕ} (hn : Module.finrank R M = n) :
    Basis (Fin n) R M := by
  exact Module.finBasisOfFinrankEq R M hn

-- Uses `Finsupp.linearEquivFunOnFinite`
-- Source: .lake/packages/mathlib/Mathlib/LinearAlgebra/Finsupp/Pi.lean:93
example {R : Type*} [Semiring R] {ι : Type*} [Finite ι] :
    Function.Injective (Finsupp.linearEquivFunOnFinite R R ι).symm := by
  exact (Finsupp.linearEquivFunOnFinite R R ι).symm.injective

-- Uses `LinearMap.rangeRestrict`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/Module/Submodule/Range.lean:403
example {R M M₂ : Type*} [Semiring R] [AddCommMonoid M] [AddCommMonoid M₂]
    [Module R M] [Module R M₂] (f : M →ₗ[R] M₂) : LinearMap.range f.rangeRestrict = ⊤ := by
  simpa [LinearMap.rangeRestrict] using (f.range_codRestrict (LinearMap.range f))
