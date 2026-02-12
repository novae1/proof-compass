# Manual-Hint Pilot for 5 MSC-180 Problems

## Objective
Build a small, controlled benchmark for three settings on the same 5 problems:

1. **A: No hint**
2. **B: Theorem statement hint(s)**
3. **C: Theorem statement hint(s) + one usage example**

This document is the manual reference set (no retriever yet).

## Setup (to keep fixed across A/B/C)
- Lean: **4.15.0**
- Mathlib: **v4.15.x**
- Same model and decoding params across all conditions
- Same number of attempts per problem
- Same 5 problems

## Problem Registry

| Problem ID | Benchmark Name | Status | Baseline Theorem Name (in proof file) | Primary Mathlib Theorem |
|---|---|---|---|---|
| `65_001` | Uniqueness of Root for Differentiable Function with Non-Vanishing Derivative | original | `unique_root_of_nonzero_deriv` | `exists_deriv_eq_zero` |
| `65_003` | Lipschitz Condition from Bounded Derivative | original | `lipschitz_from_bounded_deriv` | `Convex.lipschitzOnWith_of_nnnorm_deriv_le` |
| `14_001` | Kernel of a Homomorphism and Quotient Group Isomorphism | original | `kernel_subgroup_and_isomorphism` | `QuotientAddGroup.quotientKerEquivOfSurjective` |
| `08_003` | Existence of a Common Multiple Order Element in a Finite Abelian Group | original | `exists_element_with_maximal_order` | `Monoid.exists_orderOf_eq_exponent` |
| `14_003` | Root Multiplicity and Polynomial Factorization | **corrected formalization** (`P ≠ 0`) | `root_multiplicity_factorization_nonzero` | `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd` |

Baseline proof file:
- `benchmarks/MSC-180/selected_undergrad_mathlib_proofs.lean`

---

## 1) MSC-180/65_001

### Formal target theorem
```lean
 theorem unique_root_of_nonzero_deriv {a b : ℝ} (_hab : a < b) (f : ℝ → ℝ)
    (hf : ContinuousOn f (Icc a b))
    (hderiv : ∀ x ∈ Ioo a b, DifferentiableAt ℝ f x)
    (hnonzero : ∀ x ∈ Ioo a b, deriv f x ≠ 0) :
    ∀ (p q : ℝ), p ∈ Icc a b → q ∈ Icc a b → f p = 0 → f q = 0 → p = q := by
```

### Baseline proof (Lean 4.15)
```lean
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
```

### Mathlib theorems used in this proof

`exists_deriv_eq_zero`
```lean
exists_deriv_eq_zero {f : ℝ → ℝ} {a b : ℝ}
  (hab : a < b) (hfc : ContinuousOn f (Set.Icc a b)) (hfI : f a = f b) :
  ∃ c ∈ Set.Ioo a b, deriv f c = 0
```

`ContinuousOn.mono`
```lean
ContinuousOn.mono {f : α → β} {s t : Set α}
  (hf : ContinuousOn f s) (h : t ⊆ s) : ContinuousOn f t
```

`Set.Icc_subset_Icc`
```lean
Set.Icc_subset_Icc {a₁ a₂ b₁ b₂ : α} (h₁ : a₂ ≤ a₁) (h₂ : b₁ ≤ b₂) :
  Set.Icc a₁ b₁ ⊆ Set.Icc a₂ b₂
```

`lt_or_gt_of_ne`
```lean
lt_or_gt_of_ne {a b : α} (h : a ≠ b) : a < b ∨ a > b
```

### Manual hint package
- **Condition B (statement-only):** include `exists_deriv_eq_zero`.
- **Condition C (statement + usage):** include `exists_deriv_eq_zero` + the usage line:
```lean
obtain ⟨c, hc, hdc⟩ := exists_deriv_eq_zero huv hcont_uv (by simp [hfu, hfv])
```

---

## 2) MSC-180/65_003

### Formal target theorem
```lean
theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (_hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
```

### Baseline proof (Lean 4.15)
```lean
theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (_hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
  have hbounded' : ∀ x ∈ Icc a b, ‖deriv f x‖₊ ≤ L := by
    intro x hx
    exact_mod_cast hbounded x hx
  simpa using (convex_Icc a b).lipschitzOnWith_of_nnnorm_deriv_le hderiv hbounded'
```

### Mathlib theorems used in this proof

`convex_Icc`
```lean
convex_Icc (r s : β) : Convex 𝕜 (Set.Icc r s)
```

`Convex.lipschitzOnWith_of_nnnorm_deriv_le`
```lean
Convex.lipschitzOnWith_of_nnnorm_deriv_le
  (hf : ∀ x ∈ s, DifferentiableAt 𝕜 f x)
  (bound : ∀ x ∈ s, ‖deriv f x‖₊ ≤ C)
  (hs : Convex ℝ s) : LipschitzOnWith C f s
```

### Manual hint package
- **Condition B:** include `Convex.lipschitzOnWith_of_nnnorm_deriv_le`.
- **Condition C:** include it + usage line:
```lean
simpa using (convex_Icc a b).lipschitzOnWith_of_nnnorm_deriv_le hderiv hbounded'
```

---

## 3) MSC-180/14_001

### Formal target theorem
```lean
theorem kernel_subgroup_and_isomorphism {G H : Type*} [AddCommGroup G] [AddCommGroup H]
    (φ : G →+ H) :
    φ.ker = {g | φ g = 0} ∧ (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H)) := by
```

### Baseline proof (Lean 4.15)
```lean
theorem kernel_subgroup_and_isomorphism {G H : Type*} [AddCommGroup G] [AddCommGroup H]
    (φ : G →+ H) :
    φ.ker = {g | φ g = 0} ∧ (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H)) := by
  constructor
  · ext g
    rfl
  · intro hsurj
    exact ⟨QuotientAddGroup.quotientKerEquivOfSurjective φ hsurj⟩
```

### Mathlib theorem used in this proof

`QuotientAddGroup.quotientKerEquivOfSurjective`
```lean
QuotientAddGroup.quotientKerEquivOfSurjective
  (φ : G →+ H) (hφ : Function.Surjective φ) :
  G ⧸ φ.ker ≃+ H
```

### Manual hint package
- **Condition B:** include `QuotientAddGroup.quotientKerEquivOfSurjective`.
- **Condition C:** include it + usage line:
```lean
exact ⟨QuotientAddGroup.quotientKerEquivOfSurjective φ hsurj⟩
```

---

## 4) MSC-180/08_003

### Formal target theorem
```lean
theorem exists_element_with_maximal_order {G : Type*} [CommGroup G] [Fintype G] :
    ∃ g : G, ∀ x : G, orderOf x ∣ orderOf g := by
```

### Baseline proof (Lean 4.15)
```lean
theorem exists_element_with_maximal_order {G : Type*} [CommGroup G] [Fintype G] :
    ∃ g : G, ∀ x : G, orderOf x ∣ orderOf g := by
  obtain ⟨g, hg⟩ :=
    Monoid.exists_orderOf_eq_exponent (G := G) (Monoid.ExponentExists.of_finite (G := G))
  refine ⟨g, ?_⟩
  intro x
  rw [hg]
  exact Monoid.order_dvd_exponent x
```

### Mathlib theorems used in this proof

`Monoid.ExponentExists.of_finite`
```lean
Monoid.ExponentExists.of_finite {G : Type u}
  [LeftCancelMonoid G] [Finite G] : Monoid.ExponentExists G
```

`Monoid.exists_orderOf_eq_exponent`
```lean
Monoid.exists_orderOf_eq_exponent {G : Type u} [CommMonoid G]
  (hG : Monoid.ExponentExists G) : ∃ g, orderOf g = Monoid.exponent G
```

`Monoid.order_dvd_exponent`
```lean
Monoid.order_dvd_exponent {G : Type u} [Monoid G]
  (g : G) : orderOf g ∣ Monoid.exponent G
```

### Manual hint package
- **Condition B:** include `Monoid.exists_orderOf_eq_exponent` and `Monoid.order_dvd_exponent`.
- **Condition C:** include both + usage lines:
```lean
obtain ⟨g, hg⟩ := Monoid.exists_orderOf_eq_exponent (G := G) (Monoid.ExponentExists.of_finite (G := G))
rw [hg]
exact Monoid.order_dvd_exponent x
```

---

## 5) MSC-180/14_003 (Corrected)

### Corrected formal target theorem
```lean
theorem root_multiplicity_factorization_nonzero {α : Type*} [Field α] {P : Polynomial α}
    {a : α} {k : ℕ} (hP : P ≠ 0) (h : multiplicity (Polynomial.X - Polynomial.C a) P = k) :
    ∃ g : Polynomial α,
      P = (Polynomial.X - Polynomial.C a) ^ k * g ∧ Polynomial.eval a g ≠ 0 := by
```

### Baseline proof (Lean 4.15)
```lean
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
```

### Mathlib theorems used in this proof

`Polynomial.rootMultiplicity_eq_multiplicity`
```lean
Polynomial.rootMultiplicity_eq_multiplicity
  (p : Polynomial R) (a : R) :
  Polynomial.rootMultiplicity a p = if p = 0 then 0 else multiplicity (Polynomial.X - Polynomial.C a) p
```

`Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
```lean
Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd
  (p : Polynomial R) (hp : p ≠ 0) (a : R) :
  ∃ q, p = (Polynomial.X - Polynomial.C a) ^ Polynomial.rootMultiplicity a p * q
    ∧ ¬ Polynomial.X - Polynomial.C a ∣ q
```

`Polynomial.dvd_iff_isRoot`
```lean
Polynomial.dvd_iff_isRoot :
  Polynomial.X - Polynomial.C a ∣ p ↔ p.IsRoot a
```

`Polynomial.IsRoot.def`
```lean
Polynomial.IsRoot.def :
  p.IsRoot a ↔ Polynomial.eval a p = 0
```

### Manual hint package
- **Condition B:** include `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`, `Polynomial.dvd_iff_isRoot`, `Polynomial.IsRoot.def`.
- **Condition C:** include these + usage line:
```lean
exact (Polynomial.dvd_iff_isRoot).2 ((Polynomial.IsRoot.def).2 hge)
```

---

## Cross-Problem Mathlib Theorem Index (Deduplicated)

1. `exists_deriv_eq_zero`
2. `ContinuousOn.mono`
3. `Set.Icc_subset_Icc`
4. `lt_or_gt_of_ne`
5. `convex_Icc`
6. `Convex.lipschitzOnWith_of_nnnorm_deriv_le`
7. `QuotientAddGroup.quotientKerEquivOfSurjective`
8. `Monoid.ExponentExists.of_finite`
9. `Monoid.exists_orderOf_eq_exponent`
10. `Monoid.order_dvd_exponent`
11. `Polynomial.rootMultiplicity_eq_multiplicity`
12. `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
13. `Polynomial.dvd_iff_isRoot`
14. `Polynomial.IsRoot.def`

---

## Further Work
- Build additional proof variants per problem using different primary theorems.
- Expand the manual theorem pool into a curated “useful theorem bank”.
- Scale to retrieval experiments: top-`K` statements and statement+usage retrieval.
- Evaluate robustness across models and prompt styles.
