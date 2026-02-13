# Manual-Hint Pilot for 5 MSC-180 Problems

## Objective
Build a controlled benchmark on the same 5 problems with manual theorem context (no retriever yet), using these conditions:

1. **A: No hint**
2. **B-main: Statement of one primary theorem**
3. **B-all: Statements of all selected theorems for the problem**
4. **C-main: Primary theorem statement + one external full proof that uses it**
5. **C-all: All selected theorem statements + external full proofs that use each theorem**

Policy for usage examples in `C-*` (current decision):
- Use **full proofs** (not one-line snippets).
- Prefer **short** proofs.
- The usage proof must come from a **different theorem** than our benchmark proof, to avoid directly spoiling the target derivation.
- If no short direct usage is found, keep a short note and use the best available proof.

## Setup (fixed across all conditions)
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
- **B-main:** statement of `exists_deriv_eq_zero`.
- **B-all:** statements of `exists_deriv_eq_zero`, `ContinuousOn.mono`, `Set.Icc_subset_Icc`, `lt_or_gt_of_ne`.
- **C-main:** `B-main` + external full proof for `exists_deriv_eq_zero` (see External Usage Proof #1).
- **C-all:** `B-all` + external full proofs for all four theorems (see #1-#4).

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
- **B-main:** statement of `Convex.lipschitzOnWith_of_nnnorm_deriv_le`.
- **B-all:** statements of `convex_Icc`, `Convex.lipschitzOnWith_of_nnnorm_deriv_le`.
- **C-main:** `B-main` + external full proof for `Convex.lipschitzOnWith_of_nnnorm_deriv_le` (see #6).
- **C-all:** `B-all` + external full proofs for both theorems (see #5-#6).

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
- **B-main:** statement of `QuotientAddGroup.quotientKerEquivOfSurjective`.
- **B-all:** same as `B-main` (single theorem for this problem).
- **C-main:** `B-main` + external full proof for this theorem (see #7).
- **C-all:** same as `C-main`.

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
- **B-main:** statement of `Monoid.exists_orderOf_eq_exponent`.
- **B-all:** statements of `Monoid.ExponentExists.of_finite`, `Monoid.exists_orderOf_eq_exponent`, `Monoid.order_dvd_exponent`.
- **C-main:** `B-main` + external full proof for `Monoid.exists_orderOf_eq_exponent` (see #9).
- **C-all:** `B-all` + external full proofs for all three theorems (see #8-#10).

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
- **B-main:** statement of `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`.
- **B-all:** statements of `Polynomial.rootMultiplicity_eq_multiplicity`, `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`, `Polynomial.dvd_iff_isRoot`, `Polynomial.IsRoot.def`.
- **C-main:** `B-main` + external full proof for `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd` (see #12).
- **C-all:** `B-all` + external full proofs for all four theorems (see #11-#14).

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

## Theorems Requiring External Usage Proofs

| # | Target theorem | External theorem chosen | Note |
|---|---|---|---|
| 1 | `exists_deriv_eq_zero` | `Polynomial.card_roots_toFinset_le_card_roots_derivative_diff_roots_succ` | No shorter direct usage found in searched files |
| 2 | `ContinuousOn.mono` | `NNReal.continuousOn_rpow_const` | Short |
| 3 | `Set.Icc_subset_Icc` | `Set.Icc_subset_uIcc` | Short |
| 4 | `lt_or_gt_of_ne` | `exists_pair_lt` | Short |
| 5 | `convex_Icc` | `convex_uIcc` | Short |
| 6 | `Convex.lipschitzOnWith_of_nnnorm_deriv_le` | `_root_.lipschitzWith_of_nnnorm_deriv_le` | Short |
| 7 | `QuotientAddGroup.quotientKerEquivOfSurjective` | `zmodAddCyclicAddEquiv` | No shorter direct usage found in searched files |
| 8 | `Monoid.ExponentExists.of_finite` | `Monoid.exponent_ne_zero_of_finite` | Short |
| 9 | `Monoid.exists_orderOf_eq_exponent` | `Monoid.exponent_eq_iSup_orderOf` | No shorter direct usage found in searched files |
| 10 | `Monoid.order_dvd_exponent` | `CommGroup.dvd_exponent` | Short |
| 11 | `Polynomial.rootMultiplicity_eq_multiplicity` | `Polynomial.rootMultiplicity_eq_zero_iff` | Short |
| 12 | `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd` | `IsAlgebraic.exists_nonzero_coeff_and_aeval_eq_zero` | Short |
| 13 | `Polynomial.dvd_iff_isRoot` | `Polynomial.X_sub_C_dvd_sub_C_eval` | Short |
| 14 | `Polynomial.IsRoot.def` | `Polynomial.root_X_sub_C` | Short |

---

## External Usage Proofs (Mathlib, transcribed)

### 1) Target: `exists_deriv_eq_zero`
Source: `Mathlib/Analysis/Calculus/LocalExtr/Polynomial.lean:35`

```lean
theorem card_roots_toFinset_le_card_roots_derivative_diff_roots_succ (p : ℝ[X]) :
    p.roots.toFinset.card ≤ (p.derivative.roots.toFinset \ p.roots.toFinset).card + 1 := by
  rcases eq_or_ne (derivative p) 0 with hp' | hp'
  · rw [eq_C_of_derivative_eq_zero hp', roots_C, Multiset.toFinset_zero, Finset.card_empty]
    exact zero_le _
  have hp : p ≠ 0 := ne_of_apply_ne derivative (by rwa [derivative_zero])
  refine Finset.card_le_diff_of_interleaved fun x hx y hy hxy hxy' => ?_
  rw [Multiset.mem_toFinset, mem_roots hp] at hx hy
  obtain ⟨z, hz1, hz2⟩ := exists_deriv_eq_zero hxy p.continuousOn (hx.trans hy.symm)
  refine ⟨z, ?_, hz1⟩
  rwa [Multiset.mem_toFinset, mem_roots hp', IsRoot, ← p.deriv]
```

### 2) Target: `ContinuousOn.mono`
Source: `Mathlib/Analysis/SpecialFunctions/Pow/Continuity.lean:428`

```lean
theorem continuousOn_rpow_const {r : ℝ} {s : Set ℝ≥0}
    (h : 0 ∉ s ∨ 0 ≤ r) : ContinuousOn (fun z : ℝ≥0 => z ^ r) s :=
  h.elim (fun _ ↦ ContinuousOn.mono (s := {0}ᶜ) (by fun_prop) (by aesop))
    (NNReal.continuous_rpow_const · |>.continuousOn)
```

### 3) Target: `Set.Icc_subset_Icc`
Source: `Mathlib/Order/Interval/Set/UnorderedInterval.lean:81`

```lean
lemma Icc_subset_uIcc : Icc a b ⊆ [[a, b]] := Icc_subset_Icc inf_le_left le_sup_right
```

### 4) Target: `lt_or_gt_of_ne`
Source: `Mathlib/Logic/Nontrivial/Basic.lean:25`

```lean
theorem exists_pair_lt (α : Type*) [Nontrivial α] [LinearOrder α] : ∃ x y : α, x < y := by
  rcases exists_pair_ne α with ⟨x, y, hxy⟩
  cases lt_or_gt_of_ne hxy <;> exact ⟨_, _, ‹_›⟩
```

### 5) Target: `convex_Icc`
Source: `Mathlib/Analysis/Convex/Basic.lean:305`

```lean
theorem convex_uIcc (r s : β) : Convex 𝕜 (uIcc r s) :=
  convex_Icc _ _
```

### 6) Target: `Convex.lipschitzOnWith_of_nnnorm_deriv_le`
Source: `Mathlib/Analysis/Calculus/MeanValue.lean:667`

```lean
theorem _root_.lipschitzWith_of_nnnorm_deriv_le {C : ℝ≥0} (hf : Differentiable 𝕜 f)
    (bound : ∀ x, ‖deriv f x‖₊ ≤ C) : LipschitzWith C f :=
  lipschitzOnWith_univ.1 <|
    convex_univ.lipschitzOnWith_of_nnnorm_deriv_le (fun x _ => hf x) fun x _ => bound x
```

### 7) Target: `QuotientAddGroup.quotientKerEquivOfSurjective`
Source: `Mathlib/GroupTheory/SpecificGroups/Cyclic.lean:692`

```lean
noncomputable def zmodAddCyclicAddEquiv [AddGroup G] (h : IsAddCyclic G) :
    ZMod (Nat.card G) ≃+ G := by
  let n := Nat.card G
  let ⟨g, surj⟩ := Classical.indefiniteDescription _ h.exists_generator
  have kereq : ((zmultiplesHom G) g).ker = zmultiples ↑(Nat.card G) := by
    rw [zmultiplesHom_ker_eq]
    congr
    rw [← Nat.card_zmultiples]
    exact Nat.card_congr (Equiv.subtypeUnivEquiv surj)
  exact Int.quotientZMultiplesNatEquivZMod n
    |>.symm.trans <| QuotientAddGroup.quotientAddEquivOfEq kereq
    |>.symm.trans <| QuotientAddGroup.quotientKerEquivOfSurjective (zmultiplesHom G g) surj
```

### 8) Target: `Monoid.ExponentExists.of_finite`
Source: `Mathlib/GroupTheory/Exponent.lean:394`

```lean
theorem exponent_ne_zero_of_finite : exponent G ≠ 0 :=
  ExponentExists.of_finite.exponent_ne_zero
```

### 9) Target: `Monoid.exists_orderOf_eq_exponent`
Source: `Mathlib/GroupTheory/Exponent.lean:453`

```lean
theorem exponent_eq_iSup_orderOf (h : ∀ g : G, 0 < orderOf g) :
    exponent G = ⨆ g : G, orderOf g := by
  rw [iSup]
  by_cases ExponentExists G
  case neg he =>
    rw [← exponent_eq_zero_iff] at he
    rw [he, Set.Infinite.Nat.sSup_eq_zero <| (exponent_eq_zero_iff_range_orderOf_infinite h).1 he]
  case pos he =>
    rw [csSup_eq_of_forall_le_of_forall_lt_exists_gt (Set.range_nonempty _)]
    · simp_rw [Set.mem_range, forall_exists_index, forall_apply_eq_imp_iff]
      exact orderOf_le_exponent he
    intro x hx
    obtain ⟨g, hg⟩ := exists_orderOf_eq_exponent he
    rw [← hg] at hx
    simp_rw [Set.mem_range, exists_exists_eq_and]
    exact ⟨g, hx⟩
```

### 10) Target: `Monoid.order_dvd_exponent`
Source: `Mathlib/GroupTheory/FiniteAbelian/Duality.lean:24`

```lean
private
lemma dvd_exponent {ι G : Type*} [Finite ι] [CommGroup G] {n : ι → ℕ}
    (e : G ≃* ((i : ι) → Multiplicative (ZMod (n i)))) (i : ι) :
    n i ∣ Monoid.exponent G := by
  classical
  have : n i = orderOf (e.symm <| Pi.mulSingle i <| .ofAdd 1) := by
    simpa only [MulEquiv.orderOf_eq, orderOf_piMulSingle, orderOf_ofAdd_eq_addOrderOf]
      using (ZMod.addOrderOf_one (n i)).symm
  exact this ▸ Monoid.order_dvd_exponent _
```

### 11) Target: `Polynomial.rootMultiplicity_eq_multiplicity`
Source: `Mathlib/Algebra/Polynomial/Div.lean:627`

```lean
@[simp]
theorem rootMultiplicity_eq_zero_iff {p : R[X]} {x : R} :
    rootMultiplicity x p = 0 ↔ IsRoot p x → p = 0 := by
  classical
  simp only [rootMultiplicity_eq_multiplicity, ite_eq_left_iff,
    Nat.cast_zero, multiplicity_eq_zero, dvd_iff_isRoot, not_imp_not]
```

### 12) Target: `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
Source: `Mathlib/RingTheory/Algebraic/Basic.lean:537`

```lean
theorem IsAlgebraic.exists_nonzero_coeff_and_aeval_eq_zero
    {s : S} (hRs : IsAlgebraic R s) (hs : s ∈ nonZeroDivisors S) :
    ∃ q : R[X], q.coeff 0 ≠ 0 ∧ aeval s q = 0 := by
  obtain ⟨p, hp0, hp⟩ := hRs
  obtain ⟨q, hpq, hq⟩ := exists_eq_pow_rootMultiplicity_mul_and_not_dvd p hp0 0
  simp only [C_0, sub_zero, X_pow_mul, X_dvd_iff] at hpq hq
  rw [hpq, map_mul, aeval_X_pow] at hp
  exact ⟨q, hq, (nonZeroDivisors S).pow_mem hs (rootMultiplicity 0 p) (aeval s q) hp⟩
```

### 13) Target: `Polynomial.dvd_iff_isRoot`
Source: `Mathlib/Algebra/Polynomial/Div.lean:610`

```lean
theorem X_sub_C_dvd_sub_C_eval : X - C a ∣ p - C (p.eval a) := by
  rw [dvd_iff_isRoot, IsRoot, eval_sub, eval_C, sub_self]
```

### 14) Target: `Polynomial.IsRoot.def`
Source: `Mathlib/Algebra/Polynomial/Eval/Defs.lean:771`

```lean
theorem root_X_sub_C : IsRoot (X - C a) b ↔ a = b := by
  rw [IsRoot.def, eval_sub, eval_X, eval_C, sub_eq_zero, eq_comm]
```

---

## Further Work
- Add alternate external usage proofs per target theorem (multiple options per theorem).
- Add alternate full benchmark proofs per problem that pivot on different primary theorems.
- After scaling up, compare these manual conditions against retriever-generated contexts.
