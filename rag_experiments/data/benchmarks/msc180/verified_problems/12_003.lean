import Mathlib

theorem maximal_ideal_iff_quotient_field {R : Type*} [CommRing R] [Nontrivial R]
    (M : Ideal R) :
    M.IsMaximal ↔ IsField (R ⧸ M) := by
  simpa using Ideal.Quotient.maximal_ideal_iff_isField_quotient M

/-
Used theorem names explicitly mentioned in the proof above:
- Ideal.Quotient.maximal_ideal_iff_isField_quotient
-/

/- Statements of the listed theorems -/
-- theorem Ideal.Quotient.maximal_ideal_iff_isField_quotient : {R : Type u} [CommRing R] (I : Ideal R) :
--   I.IsMaximal ↔ IsField (R ⧸ I)

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `Ideal.Quotient.maximal_ideal_iff_isField_quotient`
-- Source: .lake/packages/mathlib/Mathlib/RingTheory/Ideal/Over.lean:258
example {R S : Type*} [CommRing R] [CommRing S] [Algebra R S] [Algebra.IsIntegral R S]
    (I : Ideal S)
    [hI : I.IsMaximal] : (I.comap (algebraMap R S)).IsMaximal := by
  let J : Ideal R := I.comap (algebraMap R S)
  have hfield : IsField (R ⧸ J) := by
    exact (Ideal.Quotient.maximal_ideal_iff_isField_quotient (I := J)).1
      (Ideal.isMaximal_comap_of_isIntegral_of_isMaximal (R := R) (S := S) I)
  exact (Ideal.Quotient.maximal_ideal_iff_isField_quotient (I := J)).2 hfield
