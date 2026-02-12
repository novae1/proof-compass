import Mathlib

open Set Function
open scoped NNReal

-- MSC-180/65_001
theorem unique_root_of_nonzero_deriv {a b : ℝ} (_hab : a < b) (f : ℝ → ℝ)
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

-- MSC-180/65_003
theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (_hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
  have hbounded' : ∀ x ∈ Icc a b, ‖deriv f x‖₊ ≤ L := by
    intro x hx
    exact_mod_cast hbounded x hx
  simpa using (convex_Icc a b).lipschitzOnWith_of_nnnorm_deriv_le hderiv hbounded'

-- MSC-180/14_001
theorem kernel_subgroup_and_isomorphism {G H : Type*} [AddCommGroup G] [AddCommGroup H]
    (φ : G →+ H) :
    φ.ker = {g | φ g = 0} ∧ (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H)) := by
  constructor
  · ext g
    rfl
  · intro hsurj
    exact ⟨QuotientAddGroup.quotientKerEquivOfSurjective φ hsurj⟩

-- MSC-180/08_003
theorem exists_element_with_maximal_order {G : Type*} [CommGroup G] [Fintype G] :
    ∃ g : G, ∀ x : G, orderOf x ∣ orderOf g := by
  obtain ⟨g, hg⟩ :=
    Monoid.exists_orderOf_eq_exponent (G := G) (Monoid.ExponentExists.of_finite (G := G))
  refine ⟨g, ?_⟩
  intro x
  rw [hg]
  exact Monoid.order_dvd_exponent x

-- MSC-180/14_003 (corrected with `P ≠ 0`; the original formal benchmark statement is false)
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

-- Counterexample showing the original benchmark formalization for 14_003 is not provable as-is.
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
