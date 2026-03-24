import Mathlib

theorem root_multiplicity_factorization_nonzero {α : Type*} [Field α] {P : Polynomial α}
    {a : α} {k : ℕ} (hP : P ≠ 0) (h : multiplicity (Polynomial.X - Polynomial.C a) P = k) :
    ∃ g : Polynomial α,
      P = (Polynomial.X - Polynomial.C a) ^ k * g ∧ Polynomial.eval a g ≠ 0 := by
  classical
  have hk : P.rootMultiplicity a = k := by
    rw [Polynomial.rootMultiplicity_eq_multiplicity (p := P) (a := a), if_neg hP]
    exact h
  obtain ⟨g, hgfac, hgndvd⟩ :=
    Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd (p := P) hP a
  refine ⟨g, ?_, ?_⟩
  · simpa [hk] using hgfac
  · intro hge
    apply hgndvd
    exact (Polynomial.dvd_iff_isRoot).2 ((Polynomial.IsRoot.def).2 hge)

example :
    ¬ (∃ g : Polynomial ℚ,
      (0 : Polynomial ℚ) = (Polynomial.X - Polynomial.C (0 : ℚ)) ^ (1 : ℕ) * g ∧
      Polynomial.eval (0 : ℚ) g ≠ 0) := by
  rintro ⟨g, hg, hge⟩
  have hg' : (Polynomial.X - Polynomial.C (0 : ℚ)) ^ (1 : ℕ) * g = 0 := hg.symm
  have hX : (Polynomial.X - Polynomial.C (0 : ℚ)) ^ (1 : ℕ) ≠ 0 := by
    exact pow_ne_zero _ (Polynomial.X_sub_C_ne_zero (0 : ℚ))
  have hg0 : g = 0 := by
    rcases mul_eq_zero.mp hg' with hleft | hright
    · exact (hX hleft).elim
    · exact hright
  exact hge (by simp [hg0])

/-
Used theorem names explicitly mentioned in the proof above (reduced to most relevant):
- Polynomial.rootMultiplicity_eq_multiplicity
- Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd
- Polynomial.dvd_iff_isRoot
- Polynomial.IsRoot.def
-/

/- Statements of the listed theorems -/
-- theorem Polynomial.rootMultiplicity_eq_multiplicity : {R : Type u} [Ring R] [DecidableEq R] (p : Polynomial R) (a : R) :
--   Polynomial.rootMultiplicity a p = if p = 0 then 0 else multiplicity (Polynomial.X - Polynomial.C a) p

-- theorem Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd : {R : Type u} [Ring R] (p : Polynomial R) (hp : p ≠ 0)
--   (a : R) :
--   ∃ q, p = (Polynomial.X - Polynomial.C a) ^ Polynomial.rootMultiplicity a p * q ∧ ¬Polynomial.X - Polynomial.C a ∣ q

-- theorem Polynomial.dvd_iff_isRoot : {R : Type u} {a : R} [CommRing R] {p : Polynomial R} :
--   Polynomial.X - Polynomial.C a ∣ p ↔ p.IsRoot a

-- theorem Polynomial.IsRoot.def : {R : Type u} {a : R} [Semiring R] {p : Polynomial R} : p.IsRoot a ↔ Polynomial.eval a p = 0

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `Polynomial.rootMultiplicity_eq_multiplicity`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/Polynomial/Div.lean:627
example {R : Type*} [CommRing R] {p : Polynomial R} {x : R} :
    Polynomial.rootMultiplicity x p = 0 ↔ Polynomial.IsRoot p x → p = (0 : Polynomial R) := by
  classical
  simp only [Polynomial.rootMultiplicity_eq_multiplicity, ite_eq_left_iff,
    Nat.cast_zero, multiplicity_eq_zero, Polynomial.dvd_iff_isRoot, not_imp_not]

-- Uses `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/Polynomial/Expand.lean:283
example {α : Type*} [Field α] (P : Polynomial α) (hP : P ≠ 0) (a : α) :
    ∃ g : Polynomial α,
      P = (Polynomial.X - Polynomial.C a) ^ P.rootMultiplicity a * g ∧
        ¬ (Polynomial.X - Polynomial.C a) ∣ g := by
  obtain ⟨g, hg, hndvd⟩ :=
    Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd (p := P) hP a
  exact ⟨g, hg, hndvd⟩

-- Uses `Polynomial.dvd_iff_isRoot`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/Polynomial/Div.lean:610
example {R : Type*} [CommRing R] (a : R) (p : Polynomial R) :
    Polynomial.X - Polynomial.C a ∣ p - Polynomial.C (p.eval a) := by
  rw [Polynomial.dvd_iff_isRoot, Polynomial.IsRoot.def, Polynomial.eval_sub,
    Polynomial.eval_C, sub_self]

-- TODO: generalize this to Ring. In general, 0 can be replaced by any element in the center of R.

-- Uses `Polynomial.IsRoot.def`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/Polynomial/Roots.lean:156
example {R : Type*} [CommRing R] [IsDomain R] {p : Polynomial R} {a x : R} :
    x ∈ (p - Polynomial.C a).roots ↔ p ≠ Polynomial.C a ∧ p.eval x = a := by
  rw [Polynomial.mem_roots', Polynomial.IsRoot.def, sub_ne_zero, Polynomial.eval_sub, sub_eq_zero,
    Polynomial.eval_C]
