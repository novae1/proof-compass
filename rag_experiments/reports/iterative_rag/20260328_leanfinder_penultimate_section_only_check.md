# LeanFinder Check: Penultimate Section Only

Source run: `rag_experiments/outputs/msc180/v2/20260217_msc180-v2_deepseekv2_7b_lean4-15_verified.json`
Condition prefix: `no-hint/`
LeanFinder top-k: `5`

## Aggregate

- problems analyzed: `19`
- mean penultimate section length: `1154.2` chars
- std penultimate section length: `2372.5` chars
- median penultimate section length: `586` chars

### Penultimate Section Types

- `lean_sketch`: `14` (73.7%)
- `explanation`: `3` (15.8%)
- `other`: `1` (5.3%)
- `analysis`: `1` (5.3%)

### Most Common Penultimate Headings

- `Lean 4 Proof Sketch with `have` Statements`: `5`
- `Step 2: Lean 4 `have` Statements`: `2`
- `Explanation of Sketch`: `1`
- `Lean 4 Proof Sketch (using `have` statements)`: `1`
- `Step 3: Lean `have` statements`: `1`
- `Lean 4 Proof Sketch with `have` statements`: `1`
- `Explanation`: `1`
- `Lean 4 Plan`: `1`
- `Lean Proof Sketch with `have``: `1`
- `Lean 4 Plan with `have` Statements`: `1`

### Most Common LeanFinder Top-1 Results

- `exists_prime_orderOf_dvd_card`: `2`
- `Finset.card_nbij'`: `1`
- `ext_of_adjoin_eq_top`: `1`
- `eq_of_le_of_inf_le_of_le_sup`: `1`
- `Polynomial.div_eq_quo_add_rem_div`: `1`
- `Nat.chineseRemainderOfList`: `1`
- `maximal_ideal_iff_isField_quotient`: `1`
- `AddCommGrp.kernelIsoKer`: `1`
- `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`: `1`
- `Matrix.rank`: `1`

### Most Common Retrieved Results Across Top-5

- `exists_prime_orderOf_dvd_card`: `2`
- `exists_prime_orderOf_dvd_card'`: `2`
- `orderOf_dvd_card`: `2`
- `Nat.chineseRemainder`: `2`
- `QuotientGroup.quotientKerEquivOfSurjective`: `2`
- `convexHull_diam`: `2`
- `convex_ball`: `2`
- `convex_closedBall`: `2`
- `Finset.card_nbij'`: `1`
- `Finset.card_bij'`: `1`
- `Finset.card_equiv`: `1`
- `Equiv.Perm.signAux_inv`: `1`
- `Equiv.Perm.set_support_inv_eq`: `1`
- `ext_of_adjoin_eq_top`: `1`
- `AlgHom.ext_of_adjoin_eq_top`: `1`

## Per Problem

### `MSC-180_05_003`

- selected attempt index: `0`
- penultimate heading: `Explanation of Sketch`
- heading category: `explanation`
- penultimate body length: `564` chars

#### Penultimate Section Body

```text
1. `h_main`: We first establish a set-theoretic equality between `excedances π` and `coexcedances π⁻¹`. The actual bijection is derived by swapping `i` with `n - 1 - i`, but we do not need the explicit bijection here. Instead, we rely on the fact that the number of `i` such that `i < π⁻¹ i` is the same as the number of `i` such that `i > π⁻¹ i`, given that `π⁻¹` is a permutation and `π * π⁻¹ = id`.

2. `h_final`: The cardinality of the two sets is the same because they are equal by `h_main`. 

The proof can then directly use `h_final` to conclude the result.
```

#### LeanFinder Top-5

1. `Finset.card_nbij'`
   - `theorem Finset.card_nbij' (i : α → β) (j : β → α) (hi : ∀ a ∈ s, i a ∈ t) (hj : ∀ a ∈ t, j a ∈ s) (left_inv : ∀ a ∈ s, j (i a) = a)`
2. `Finset.card_bij'`
   - `theorem Finset.card_bij' (i : ∀ a ∈ s, β) (j : ∀ a ∈ t, α) (hi : ∀ a ha, i a ha ∈ t) (hj : ∀ a ha, j a ha ∈ s)`
3. `Finset.card_equiv`
   - `theorem Finset.card_equiv (e : α ≃ β) (hst : ∀ i, i ∈ s ↔ e i ∈ t) : #s = #t := by`
4. `Equiv.Perm.signAux_inv`
   - `theorem Equiv.Perm.signAux_inv {n : ℕ} (f : Perm (Fin n)) : signAux f⁻¹ = signAux f :=`
5. `Equiv.Perm.set_support_inv_eq`
   - `theorem Equiv.Perm.set_support_inv_eq : {x | p⁻¹ x ≠ x} = {x | p x ≠ x} := by`

### `MSC-180_08_001`

- selected attempt index: `3`
- penultimate heading: `Lean 4 Proof Sketch (using `have` statements)`
- heading category: `lean_sketch`
- penultimate body length: `720` chars

#### Penultimate Section Body

```text
```lean4
theorem homomorphism_agreement {R A B : Type*} [CommSemiring R] [Semiring A] [Semiring B]
    [Algebra R A] [Algebra R B] {X : Set A} (hgen : Algebra.adjoin R X = ⊤)
    {α β : A →ₐ[R] B} (h_agree : ∀ x ∈ X, α x = β x) :
    α = β := by
  have h_main : ∀ a : A, α a = β a := by
    sorry
  have h_final : α = β := by
    sorry
  exact h_final
```

This sketch provides two `have` statements to mirror the main steps of the proof. The first `have` is `h_main : ∀ a : A, α a = β a`, which is the crux of the proof, and the second `have` is `h_final : α = β`, which trivially follows from `h_main`. The `sorry` is used to skip over the proof of these statements, and the proof can be completed by discharging them.
```

#### LeanFinder Top-5

1. `ext_of_adjoin_eq_top`
   - `theorem ext_of_adjoin_eq_top {s : Set A} (h : adjoin R s = ⊤) ⦃φ₁ φ₂ : A →ₐ[R] B⦄`
2. `AlgHom.ext_of_adjoin_eq_top`
   - `theorem AlgHom.ext_of_adjoin_eq_top {s : Set A} (h : adjoin R s = ⊤) ⦃φ₁ φ₂ : A →ₐ[R] B⦄ (hs : s.EqOn φ₁ φ₂) : φ₁ = φ₂ :=`
3. `ext_of_eq_adjoin`
   - `theorem ext_of_eq_adjoin {S : Subalgebra R A} {s : Set A} (hS : S = adjoin R s) ⦃φ₁ φ₂ : S →ₐ[R] B⦄`
4. `AlgHom.adjoin_ext`
   - `theorem AlgHom.adjoin_ext {s : Set A} ⦃φ₁ φ₂ : adjoin R s →ₐ[R] B⦄ (h : ∀ x hx, φ₁ ⟨x, subset_adjoin hx⟩ = φ₂ ⟨x, subset_adjoin hx⟩) : φ₁ = φ₂ :=`
5. `AlgHom.ext_of_eq_adjoin`
   - `theorem AlgHom.ext_of_eq_adjoin {S : Subalgebra R A} {s : Set A} (hS : S = adjoin R s) ⦃φ₁ φ₂ : S →ₐ[R] B⦄`

### `MSC-180_08_002`

- selected attempt index: `0`
- penultimate heading: `Lean 4 Proof Sketch with `have` Statements`
- heading category: `lean_sketch`
- penultimate body length: `552` chars

#### Penultimate Section Body

```text
```lean4
theorem unique_relative_complement {L : Type*} [DistribLattice L] {a b c : L}
    (hab : a ≤ b) (hbc : b ≤ c) :
    ∀ (d₁ d₂ : L),
      a ≤ d₁ ∧ d₁ ≤ c ∧ d₁ ⊔ b = c ∧ d₁ ⊓ b = a →
      a ≤ d₂ ∧ d₂ ≤ c ∧ d₂ ⊔ b = c ∧ d₂ ⊓ b = a →
      d₁ = d₂ := by
  intro d₁ d₂ h₁ h₂
  have h₃ : d₁ = d₂ := by
    sorry
  sorry
```

This proof sketch uses a `have` statement to assert that `d₁ = d₂` is the goal, with `sorry` to indicate that the actual proof is omitted. The full proof would fill in this `have` with the detailed reasoning provided above.
```

#### LeanFinder Top-5

1. `eq_of_le_of_inf_le_of_le_sup`
   - `theorem eq_of_le_of_inf_le_of_le_sup (hxy : x ≤ y) (hinf : y ⊓ z ≤ x) (hsup : y ≤ x ⊔ z) :`
2. `sdiff_unique`
   - `theorem sdiff_unique (s : x ⊓ y ⊔ z = x) (i : x ⊓ y ⊓ z = ⊥) : x \ y = z := by`
3. `eq_of_le_of_inf_le_of_sup_le`
   - `theorem eq_of_le_of_inf_le_of_sup_le (hxy : x ≤ y) (hinf : y ⊓ z ≤ x ⊓ z) (hsup : y ⊔ z ≤ x ⊔ z) :`
4. `eq_of_inf_eq_sup_eq`
   - `theorem eq_of_inf_eq_sup_eq {a b c : α} (h₁ : b ⊓ a = c ⊓ a) (h₂ : b ⊔ a = c ⊔ a) : b = c :=`
5. `IsCompl.right_unique`
   - `theorem IsCompl.right_unique (hxy : IsCompl x y) (hxz : IsCompl x z) : y = z :=`

### `MSC-180_08_003`

- selected attempt index: `6`
- penultimate heading: `Step 3: Lean `have` statements`
- heading category: `lean_sketch`
- penultimate body length: `437` chars

#### Penultimate Section Body

```text
```lean4
theorem exists_element_with_maximal_order {G : Type*} [CommGroup G] [Fintype G] :
    ∃ g : G, ∀ x : G, orderOf x ∣ orderOf g := by
  have h_main : ∃ g : G, ∀ x : G, orderOf x ∣ orderOf g := by
    sorry
  sorry
```

This `have` statement directly encodes that there exists a `g : G` such that `∀ x : G, orderOf x ∣ orderOf g`. The `sorry` is for the actual proof, which we have already reasoned through by choosing `g = 1 : G`.
```

#### LeanFinder Top-5

1. `exists_prime_orderOf_dvd_card`
   - `theorem exists_prime_orderOf_dvd_card {G : Type*} [Group G] [Fintype G] (p : ℕ) [hp : Fact p.Prime] (hdvd : p ∣ Fintype.card G) : ∃ x : G, orderOf x = p := by`
2. `exists_prime_orderOf_dvd_card'`
   - `theorem exists_prime_orderOf_dvd_card' {G : Type*} [Group G] [Finite G] (p : ℕ) [hp : Fact p.Prime] (hdvd : p ∣ Nat.card G) : ∃ x : G, orderOf x = p := by`
3. `orderOf_dvd_card`
   - `theorem orderOf_dvd_card : orderOf x ∣ Fintype.card G := by`
4. `Monoid.exists_orderOf_eq_exponent`
   - `theorem Monoid.exists_orderOf_eq_exponent (hG : ExponentExists G) : ∃ g : G, orderOf g = exponent G := by`
5. `IsCyclic.exists_ofOrder_eq_natCard`
   - `theorem IsCyclic.exists_ofOrder_eq_natCard [h : IsCyclic α] : ∃ g : α, orderOf g = Nat.card α := by`

### `MSC-180_12_001`

- selected attempt index: `1`
- penultimate heading: `Lean 4 Proof Sketch with `have` statements`
- heading category: `lean_sketch`
- penultimate body length: `835` chars

#### Penultimate Section Body

```text
```lean4
theorem polynomial_division_algorithm {F : Type*} [Field F] (f g : Polynomial F) (hg : g ≠ 0) :
    ∃ (q r : Polynomial F),
      f = g * q + r ∧
      (r = 0 ∨ r.degree < g.degree) ∧
      ∀ (q' r' : Polynomial F),
        (f = g * q' + r' ∧ (r' = 0 ∨ r'.degree < g.degree)) → q = q' ∧ r = r' := by
  -- Step 1: Use the polynomial division algorithm to find q and r
  have h_main : ∃ (q r : Polynomial F), f = g * q + r ∧ (r = 0 ∨ r.degree < g.degree) ∧ ∀ (q' r' : Polynomial F), (f = g * q' + r' ∧ (r' = 0 ∨ r'.degree < g.degree)) → q = q' ∧ r = r' := by
    sorry
  sorry
```

This `have` statement directly reflects our goal and uses `sorry` for the actual construction and proof. The `sorry` is a placeholder for the full proof, which we would fill in later by providing the detailed construction and uniqueness argument.
```

#### LeanFinder Top-5

1. `Polynomial.div_eq_quo_add_rem_div`
   - `theorem Polynomial.div_eq_quo_add_rem_div (f : R[X]) {g : R[X]} (hg : g.Monic) :`
2. `Polynomial.div_modByMonic_unique`
   - `theorem Polynomial.div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g) (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by`
3. `Polynomial.divModByMonicAux`
   - `definition Polynomial.divModByMonicAux : ∀ (_p : R[X]) {q : R[X]}, Monic q → R[X] × R[X] | p, q, hq =>`
4. `Polynomial.natDegree_mod_lt`
   - `theorem Polynomial.natDegree_mod_lt [Field k] (p : k[X]) {q : k[X]} (hq : q.natDegree ≠ 0) : (p % q).natDegree < q.natDegree := by`
5. `Polynomial.div`
   - `definition Polynomial.div (p q : R[X]) :=`

### `MSC-180_12_002`

- selected attempt index: `1`
- penultimate heading: `Explanation`
- heading category: `explanation`
- penultimate body length: `815` chars

#### Penultimate Section Body

```text
1. The `h_main` statement directly mirrors the original goal. We use Lean's `Int.ModEq` with the modulus `(n i : ℤ)` for the congruences, and the final modulus is the product of the `n i` as integers.
2. The proof of `h_main` would rely on the Chinese Remainder Theorem and properties of the `Nat.Coprime` condition to ensure that the system of congruences has a unique solution modulo the product. The actual proof of `h_main` would involve setting up the system correctly and applying Lean's `Int.ModEq` tools, but this is omitted here (hence `sorry`). 

The sketch above provides the necessary high-level structure, and the `have` statements summarize the key parts of the proof. The `sorry` can be removed by filling in the Lean proof script using the `Int.ModEq.chineseRemainder` lemma or the CRT in `Mathlib`.
```

#### LeanFinder Top-5

1. `Nat.chineseRemainderOfList`
   - `definition Nat.chineseRemainderOfList : (l : List ι) → l.Pairwise (Coprime on s) → { k // ∀ i ∈ l, k ≡ a i [MOD s i] } | [],     _  => ⟨0, by simp⟩`
2. `Nat.chineseRemainderOfFinset`
   - `definition Nat.chineseRemainderOfFinset (t : Finset ι) (hs : ∀ i ∈ t, s i ≠ 0) (pp : Set.Pairwise t (Coprime on s)) : { k // ∀ i ∈ t, k ≡ a i [MOD s i] } := by`
3. `Nat.chineseRemainder`
   - `definition Nat.chineseRemainder (co : n.Coprime m) (a b : ℕ) : { k // k ≡ a [MOD n] ∧ k ≡ b [MOD m] } :=`
4. `Nat.chineseRemainderOfList_modEq_unique`
   - `theorem Nat.chineseRemainderOfList_modEq_unique (l : List ι) (co : l.Pairwise (Coprime on s)) {z} (hz : ∀ i ∈ l, z ≡ a i [MOD s i]) :`
5. `Nat.chineseRemainder`
   - `definition Nat.chineseRemainder' (h : a ≡ b [MOD gcd n m]) : { k // k ≡ a [MOD n] ∧ k ≡ b [MOD m] } :=`

### `MSC-180_12_003`

- selected attempt index: `6`
- penultimate heading: `Lean 4 Plan`
- heading category: `other`
- penultimate body length: `533` chars

#### Penultimate Section Body

```text
```lean4
theorem maximal_ideal_iff_quotient_field {R : Type*} [CommRing R] [Nontrivial R]
    (M : Ideal R) :
    M.IsMaximal ↔ IsField (R ⧸ M) := by
  have h_forward : M.IsMaximal → IsField (R ⧸ M) := by sorry
  have h_backward : IsField (R ⧸ M) → M.IsMaximal := by sorry
  exact ⟨h_forward, h_backward⟩
```

This completes the sketch. Each `have` statement marks a high-level part of the proof that needs to be addressed, and their combination gives the complete theorem. The `sorry` placeholder marks the end of each part's proof.
```

#### LeanFinder Top-5

1. `maximal_ideal_iff_isField_quotient`
   - `theorem maximal_ideal_iff_isField_quotient (I : Ideal R) : I.IsMaximal ↔ IsField (R ⧸ I) :=`
2. `Ideal.Quotient.maximal_ideal_iff_isField_quotient`
   - `theorem Ideal.Quotient.maximal_ideal_iff_isField_quotient (I : Ideal R) : I.IsMaximal ↔ IsField (R ⧸ I) :=`
3. `Ideal.Quotient.maximal_of_isField`
   - `theorem Ideal.Quotient.maximal_of_isField (I : Ideal R) (hqf : IsField (R ⧸ I)) : I.IsMaximal := by`
4. `maximal_of_isField`
   - `theorem maximal_of_isField (I : Ideal R) (hqf : IsField (R ⧸ I)) : I.IsMaximal := by`
5. `Ideal.bot_quotient_isMaximal_iff`
   - `theorem Ideal.bot_quotient_isMaximal_iff (I : Ideal R) : (⊥ : Ideal (R ⧸ I)).IsMaximal ↔ I.IsMaximal :=`

### `MSC-180_14_001`

- selected attempt index: `4`
- penultimate heading: `Lean 4 Proof Sketch with `have` Statements`
- heading category: `lean_sketch`
- penultimate body length: `577` chars

#### Penultimate Section Body

```text
```lean4
theorem kernel_subgroup_and_isomorphism {G H : Type*} [AddCommGroup G] [AddCommGroup H]
    (φ : G →+ H) :
    φ.ker = {g | φ g = 0} ∧ (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H)) := by
  have h_kernel_def : φ.ker = {g | φ g = 0} := by sorry
  have h_surjective_gives_iso : (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H)) := by sorry
  exact ⟨h_kernel_def, h_surjective_gives_iso⟩
``` 

This uses `have` statements to break down the problem into two key parts: the definition of the kernel and the surjectivity condition. Each of these is marked with `sorry` for later proof.
```

#### LeanFinder Top-5

1. `AddCommGrp.kernelIsoKer`
   - `definition AddCommGrp.kernelIsoKer {G H : AddCommGrp.{u}} (f : G ⟶ H) : kernel f ≅ AddCommGrp.of f.hom.ker where`
2. `QuotientGroup.quotientKerEquivOfSurjective`
   - `/-- The canonical isomorphism `G/(ker φ) ≃* H` induced by a surjection `φ : G →* H`.`
3. `AddCommGrp.kernelIsoKer_hom_comp_subtype`
   - `theorem AddCommGrp.kernelIsoKer_hom_comp_subtype {G H : AddCommGrp.{u}} (f : G ⟶ H) : (kernelIsoKer f).hom ≫ ofHom (AddSubgroup.subtype f.hom.ker) = kernel.ι f := by ext; rfl`
4. `QuotientGroup.quotientKerEquivOfSurjective`
   - `definition QuotientGroup.quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=`
5. `NormedAddGroupHom.ker`
   - `definition NormedAddGroupHom.ker : AddSubgroup V₁ :=`

### `MSC-180_14_003`

- selected attempt index: `3`
- penultimate heading: `Step 2: Lean 4 `have` Statements`
- heading category: `lean_sketch`
- penultimate body length: `751` chars

#### Penultimate Section Body

```text
```lean4
theorem root_multiplicity_factorization_nonzero {α : Type*} [Field α] {P : Polynomial α}
    {a : α} {k : ℕ} (hP : P ≠ 0) (h : multiplicity (Polynomial.X - Polynomial.C a) P = k) :
    ∃ g : Polynomial α,
      P = (Polynomial.X - Polynomial.C a) ^ k * g ∧ Polynomial.eval a g ≠ 0 := by
  -- Step 1: Use the hypothesis to get that (X - C a)^k divides P
  have h_dvd : (Polynomial.X - Polynomial.C a) ^ k ∣ P := by sorry
  -- Step 2: Obtain the polynomial g such that P = (X - C a)^k * g
  have h_main : ∃ g : Polynomial α, P = (Polynomial.X - Polynomial.C a) ^ k * g := by sorry
  -- Step 3: Prove that g(a) ≠ 0
  have h_final : ∃ g : Polynomial α, P = (Polynomial.X - Polynomial.C a) ^ k * g ∧ Polynomial.eval a g ≠ 0 := by sorry
  sorry
```
```

#### LeanFinder Top-5

1. `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
   - `theorem Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd (p : R[X]) (hp : p ≠ 0) (a : R) : ∃ q : R[X], p = (X - C a) ^ p.rootMultiplicity a * q ∧ ¬(X - C a) ∣ q := by`
2. `le_rootMultiplicity_iff`
   - `theorem le_rootMultiplicity_iff {p : R[X]} (p0 : p ≠ 0) {a : R} {n : ℕ} :`
3. `Polynomial.pow_rootMultiplicity_dvd`
   - `theorem Polynomial.pow_rootMultiplicity_dvd (p : R[X]) (a : R) : (X - C a) ^ rootMultiplicity a p ∣ p :=`
4. `Polynomial.eval_divByMonic_pow_rootMultiplicity_ne_zero`
   - `theorem Polynomial.eval_divByMonic_pow_rootMultiplicity_ne_zero {p : R[X]} (a : R) (hp : p ≠ 0) : eval a (p /ₘ (X - C a) ^ rootMultiplicity a p) ≠ 0 := by`
5. `Polynomial.le_rootMultiplicity_iff`
   - `theorem Polynomial.le_rootMultiplicity_iff (p0 : p ≠ 0) {a : R} {n : ℕ} : n ≤ rootMultiplicity a p ↔ (X - C a) ^ n ∣ p := by`

### `MSC-180_15_003`

- selected attempt index: `1`
- penultimate heading: `Lean Proof Sketch with `have``
- heading category: `lean_sketch`
- penultimate body length: `625` chars

#### Penultimate Section Body

```text
```lean4
theorem column_row_factorization {m n : ℕ} (A : Matrix (Fin m) (Fin n) ℂ) (hc : A.rank ≥ 1) :
    ∃ (c : ℕ) (h : c = A.rank) (C : Matrix (Fin m) (Fin c) ℂ)
      (R : Matrix (Fin c) (Fin n) ℂ), A = C * R := by
  have h_main : ∃ (c : ℕ) (h : c = A.rank) (C : Matrix (Fin m) (Fin c) ℂ) (R : Matrix (Fin c) (Fin n) ℂ), A = C * R := by
    sorry
  sorry
```

The `have` statement reflects that we can find `C` and `R` explicitly given `A.rank ≥ 1`. The actual proof is omitted (`sorry`ed), but the `h_main` statement is correct because Lean's libraries support this decomposition (though we did not provide the details).
```

#### LeanFinder Top-5

1. `Matrix.rank`
   - `definition Matrix.rank (A : Matrix m n R) : ℕ :=`
2. `Matrix.cRank_toNat_eq_rank`
   - `@[simp]`
3. `Matrix.rank_add_rank_le_card_of_mul_eq_zero`
   - `theorem Matrix.rank_add_rank_le_card_of_mul_eq_zero [Field R] [Finite l] [Fintype m] {A : Matrix l m R} {B : Matrix m n R} (hAB : A * B = 0) :`
4. `Matrix.rank_le_width`
   - `theorem Matrix.rank_le_width [StrongRankCondition R] {m n : ℕ} (A : Matrix (Fin m) (Fin n) R) : A.rank ≤ n :=`
5. `Matrix.Pivot.exists_list_transvec_mul_mul_list_transvec_eq_diagonal`
   - `theorem Matrix.Pivot.exists_list_transvec_mul_mul_list_transvec_eq_diagonal (M : Matrix n n 𝕜) :`

### `MSC-180_20_001`

- selected attempt index: `6`
- penultimate heading: `Lean 4 Plan with `have` Statements`
- heading category: `lean_sketch`
- penultimate body length: `545` chars

#### Penultimate Section Body

```text
```lean4
theorem my_favorite_theorem {G : Type*} [CommGroup G] [Fintype G]
    (hG : Fintype.card G ≠ 0) (p : ℕ) (hp : Nat.Prime p)
    (hG1 : p ∣ Fintype.card G) :
    ∃ x : G, orderOf x = p := by
  have h_main : ∃ x : G, orderOf x = p := by
    sorry
  sorry
```

This completes the sketch. The `have` statement `h_main` directly encodes the goal, and we mark it with `sorry` because we are only required to provide a sketch here. The actual Lean proof will need to fill in the `sorry` using Cauchy's theorem (`exists_prime_orderOf_dvd_card`).
```

#### LeanFinder Top-5

1. `exists_prime_orderOf_dvd_card`
   - `theorem exists_prime_orderOf_dvd_card {G : Type*} [Group G] [Fintype G] (p : ℕ) [hp : Fact p.Prime] (hdvd : p ∣ Fintype.card G) : ∃ x : G, orderOf x = p := by`
2. `exists_prime_orderOf_dvd_card'`
   - `theorem exists_prime_orderOf_dvd_card' {G : Type*} [Group G] [Finite G] (p : ℕ) [hp : Fact p.Prime] (hdvd : p ∣ Nat.card G) : ∃ x : G, orderOf x = p := by`
3. `exists_prime_addOrderOf_dvd_card`
   - `theorem exists_prime_addOrderOf_dvd_card {G : Type*} [AddGroup G] [Fintype G] (p : ℕ) [Fact p.Prime] (hdvd : p ∣ Fintype.card G) : ∃ x : G, addOrderOf x = p :=`
4. `orderOf_dvd_card`
   - `theorem orderOf_dvd_card : orderOf x ∣ Fintype.card G := by`
5. `Sylow.exists_subgroup_card_pow_prime`
   - `theorem Sylow.exists_subgroup_card_pow_prime [Finite G] (p : ℕ) {n : ℕ} [Fact p.Prime] (hdvd : p ^ n ∣ Nat.card G) : ∃ K : Subgroup G, Nat.card K = p ^ n :=`

### `MSC-180_28_003`

- selected attempt index: `4`
- penultimate heading: `Lean 4 `have` statements:`
- heading category: `lean_sketch`
- penultimate body length: `889` chars

#### Penultimate Section Body

```text
```lean4
theorem outer_measure_additive_of_separated {E F : Set (Fin d → ℝ)}
    (h : ∃ δ > 0, ∀ x ∈ E, ∀ y ∈ F, δ ≤ dist x y) :
    MeasureTheory.OuterMeasure.measureOf (MeasureTheory.volume.toOuterMeasure) (E ∪ F) =
      MeasureTheory.OuterMeasure.measureOf (MeasureTheory.volume.toOuterMeasure) E +
        MeasureTheory.OuterMeasure.measureOf (MeasureTheory.volume.toOuterMeasure) F := by
  -- Step 1: Prove E and F are disjoint
  have h_disjoint : Disjoint E F := by
    sorry
  -- Step 2: Apply the additivity of the outer measure for disjoint sets
  have h_main : MeasureTheory.OuterMeasure.measureOf (MeasureTheory.volume.toOuterMeasure) (E ∪ F) = MeasureTheory.OuterMeasure.measureOf (MeasureTheory.volume.toOuterMeasure) E + MeasureTheory.OuterMeasure.measureOf (MeasureTheory.volume.toOuterMeasure) F := by
    sorry
  -- The conclusion follows from the main result
  sorry
```
```

#### LeanFinder Top-5

1. `measureReal_union'`
   - `theorem measureReal_union' (hd : Disjoint s₁ s₂) (h : MeasurableSet s₁)`
2. `measureReal_union`
   - `theorem measureReal_union (hd : Disjoint s₁ s₂) (h : MeasurableSet s₂)`
3. `of_union`
   - `theorem of_union {A B : Set α} (h : Disjoint A B) (hA : MeasurableSet A) (hB : MeasurableSet B) :`
4. `MeasureTheory.measure_union`
   - `theorem MeasureTheory.measure_union (hd : Disjoint s₁ s₂) (h : MeasurableSet s₂) : μ (s₁ ∪ s₂) = μ s₁ + μ s₂ :=`
5. `MeasureTheory.inducedOuterMeasure_union_of_false_of_nonempty_inter`
   - `theorem MeasureTheory.inducedOuterMeasure_union_of_false_of_nonempty_inter {s t : Set α} (h : ∀ u, (s ∩ u).Nonempty → (t ∩ u).Nonempty → ¬P u) :`

### `MSC-180_40_003`

- selected attempt index: `4`
- penultimate heading: `Explanation:`
- heading category: `explanation`
- penultimate body length: `284` chars

#### Penultimate Section Body

```text
1. The `have` statement `h_main` is a placeholder for the main proof that the series is summable. 
2. The actual Lean code will need to be adjusted to correctly reflect the hypotheses under which the sum is finite (likely `a - b > 1`), but this sketch reflects the `sorry`-based plan.
```

#### LeanFinder Top-5

1. `HurwitzKernelBounds.summable_f_nat`
   - `theorem HurwitzKernelBounds.summable_f_nat (k : ℕ) (a : ℝ) {t : ℝ} (ht : 0 < t) : Summable (f_nat k a t) := by`
2. `Real.hasSum_log_one_add_inv`
   - `theorem Real.hasSum_log_one_add_inv {a : ℝ} (h : 0 < a) :`
3. `Real.hasSum_pow_div_log_of_abs_lt_one`
   - `theorem Real.hasSum_pow_div_log_of_abs_lt_one {x : ℝ} (h : |x| < 1) : HasSum (fun n : ℕ => x ^ (n + 1) / (n + 1)) (-log (1 - x)) := by`
4. `LSeriesSummable_of_isBigO_rpow`
   - `theorem LSeriesSummable_of_isBigO_rpow {f : ℕ → ℂ} {x : ℝ} {s : ℂ} (hs : x < s.re) (h : f =O[atTop] fun n ↦ (n : ℝ) ^ (x - 1)) : LSeriesSummable f s := by`
5. `Summable.clog_one_sub`
   - `theorem Summable.clog_one_sub {α : Type*} {f : α → ℂ} (hsum : Summable f) : Summable fun n ↦ log (1 - f n) := by`

### `MSC-180_52_002`

- selected attempt index: `7`
- penultimate heading: `Detailed Proof and Analysis`
- heading category: `analysis`
- penultimate body length: `10928` chars

#### Penultimate Section Body

```text
**Problem Analysis:**
We are given a finite nonempty set `S` of points in `ℝ^n` (here `EuclideanSpace ℝ (Fin n)`, but Lean's `n` is natural, so `ℝ^n` is not directly available unless `n` is fixed or we use `Module ℝ (Fin n → ℝ)`). We need to find extreme points `x` and `y` in the convex hull of `S` such that the distance between them is equal to the diameter of `S`. 

However, the problem is a bit misstated because the set `S` is finite and the set `convexHull ℝ S` is the convex hull of `S`. The diameter of `S` is `sup_{x, y ∈ S} dist x y`. 

But Lean's `Metric.diam S` is defined as `⨆ (x ∈ S) (y ∈ S), dist x y` if `S` is nonempty, or `0` if `S` is empty (but `h_nonempty` guarantees `S` is nonempty). 

Since `S` is finite, `⨆ (x ∈ S) (y ∈ S), dist x y` is `⨆ (x : S), ⨆ (y : S), dist x.val y.val`. 

But we can find the maximum distance by considering a bijection `f` from `S` to `Fin S.toFinset.card` (or `S.toFinset`). Then the suprema can be simplified to a finite set.

However, the problem does not assume that the extreme points exist, so we need to find them. In practice, the extreme points are just the vertices of the convex hull of `S`, and the maximum distance is achieved between two vertices (unless the set is a singleton, where the maximum distance is zero). 

But the statement is a bit too weak because the extreme points are just the vertices of the convex hull, not necessarily the ones on the boundary (or all vertices are extreme points). 

The `Metric.diam S` is the largest distance between any two points in `S`. But we need the points in the extreme points of the convex hull to achieve this distance. 

This is true because:
1. The convex hull of `S` is compact, and `S` is finite, so the maximum distance is achieved.
2. The extreme points of a polytope are its vertices (assuming `S` is in `ℝ^n`). 

But here is the confusion: `convexHull ℝ S` is the convex hull of `S`, but if `S` is finite, `convexHull ℝ S` might not be the same as the convex hull of the embedded set `S` (but Lean's `convexHull` is the same as the standard convex hull).

But in Lean's `convexHull` notation, `convexHull ℝ S` is the convex hull of `S`, and `S` is finite, so it's compact, and the maximum distance is achieved. 

But actually, the extreme points of `convexHull ℝ S` are its vertices, which are just points in `S` since `S` is finite. 

So, we can prove:
1. The convex hull of `S` is compact (because `S` is finite, and `convexHull ℝ S` is the convex hull of `S`, and `convexHull ℝ S` is compact).
2. The diameter is achieved between two points `x` and `y` in `S`.
3. The points `x` and `y` lie in `convexHull ℝ S` (`convexHull ℝ S` is the convex hull of `S`, so it contains `S`).
4. They are extreme points of `convexHull ℝ S` (in Lean `extremePoints ℝ` means they are extreme points).

But the Lean statement says that `x` and `y` are in `extremePoints ℝ (convexHull ℝ S)`, which is just "extreme points of the convex hull of `S`" (`convexHull ℝ S`). 

In Lean, `convexHull ℝ S` is `convexHull ℝ S`, and `extremePoints ℝ (convexHull ℝ S)` are the points in `convexHull ℝ S` that are not in the interior of any larger subset that is a subset of `convexHull ℝ S`. 

But since `S` is finite, `convexHull ℝ S` is compact, and the maximum distance is achieved on `S`. 

But we need the extreme points to be in `convexHull ℝ S`, not in `S` itself. 

But we don't need that here because if `x` and `y` are in `S`, they are in `convexHull ℝ S` (`convexHull_mono`). 

Thus:
1. The set of `convexHull ℝ S` is the convex hull of `S`, which contains `S`, so if `x ∈ S`, then `x ∈ convexHull ℝ S`. 
2. The maximum distance is achieved by some `x`, `y ∈ S` (since `S` is finite and `dist` is continuous). 

Thus:
- The diameter is `sup_{x, y ∈ S} dist x y`. 
- Since `S` is finite, there exist `x, y ∈ S` achieving the supremum. 
- The points `x` and `y` are in `convexHull ℝ S` (since `S ⊆ convexHull ℝ S`). 
- `x` and `y` are extreme points of `convexHull ℝ S`. 

To check if `x` is an extreme point:
If `x` is in the interior of a larger subset of `convexHull ℝ S`, then it's not an extreme point. But `convexHull ℝ S` is compact (as `S` is finite and convex), so extreme points are its vertices. 

But `convexHull ℝ S` is the convex hull of `S`, which is `S` itself (if `S` is convex, but it's not guaranteed unless `n = 0` or `S` is a singleton). 

But we don't have this information. 

But Lean uses `convexHull ℝ S` as the convex hull of `S`, which is `S` itself if `S` is convex, but that's not the case here. 

Wait no: in Lean, `convexHull ℝ S` is the convex hull of `S`, which is `S` if `S` is already convex. 

But in Lean, `convexHull ℝ S` is the convex hull of `S`, not necessarily `S` itself unless `S` is already convex. 

But the theorem is true: 
The extreme points of `convexHull ℝ S` are the points of `S` (because `convexHull ℝ S` is `S` itself). 

But this is not necessarily true unless `S` is already convex. 

But `convexHull ℝ S` is `S` if `S` is convex, but Lean uses a different definition. 

Alternatively, perhaps Lean's `convexHull ℝ S` is `S` when `S` is convex, but that's not true unless `S` is already convex. 

In any case, we can use the following strategy:
1. The set `convexHull ℝ S` is the convex hull of `S`, and it's compact since `S` is finite. 
2. The maximum distance is achieved by some `x`, `y ∈ S` (`S` is finite and `dist` is continuous).
3. `x` and `y` are extreme points of `convexHull ℝ S` (`convexHull ℝ S` is `S`, so `x`, `y` are extreme points).

But is `convexHull ℝ S` just `S`? No, unless `S` is already convex. 

But in Lean, `convexHull ℝ S` is `convexHull ℝ S`. 

But if `S` is finite and nonempty, then `convexHull ℝ S` is compact and contains `S`. 

But we have to ensure that the diameter is achieved by extreme points of `convexHull ℝ S`. 

But Lean's `extremePoints ℝ` for `convexHull ℝ S` is the set of points in `convexHull ℝ S` that are not in the interior of a larger convex set. 

But since `convexHull ℝ S` is compact, its extreme points are its vertices, i.e., points in `S`. 

But this is not true unless `convexHull ℝ S` is `S`, which it is not unless `S` is convex. 

However, the maximum distance is achieved on `S`, and `S` is finite, so `dist` is continuous, and the extrema are in `S`. 

Thus, if we can show that `convexHull ℝ S` is compact and the diameter is achieved on `S`, we are done. 

Alternatively, note that:
1. `convexHull ℝ S` is compact (since `S` is finite and `convexHull ℝ S` is closed).
2. `dist` is continuous, so the sup is achieved.
3. The `Metric.diam S` is `⨆ (x : S) (y : S), dist x.val y.val` (`S` is nonempty, so `Metric.diam S` is `sup_{x, y ∈ S} dist x y`).
4. The points `x`, `y ∈ S` achieving the diameter are extreme points of `convexHull ℝ S` (because `convexHull ℝ S` is the convex hull of `S`, so they are in `convexHull ℝ S`, and they are vertices). 

But the problem is with Lean's definition of `convexHull` for sets of real functions. 

But the problem is trivial because `S` is finite and `convexHull ℝ S` is compact (`S` is finite), and the maximum distance is achieved between some `x`, `y ∈ S`, and `x`, `y` are extreme points of `convexHull ℝ S` (`convexHull ℝ S` is `S`). 

But Lean's `convexHull ℝ S` is `convexHull ℝ S`, and it's not necessarily `S`. 

But perhaps we can use that `convexHull ℝ S` is the smallest convex set containing `S`, and `S` is finite, so `convexHull ℝ S` is `S` (`convexHull ℝ S` is `S` because `S` is convex). 

But this is not true in general unless `S` is already convex. 

Alternatively, perhaps `convexHull ℝ S = convexHull ℝ S` (no need to think further). 

But Lean's `convexHull` is the standard convex hull, so perhaps the extreme points are in `S`. 

However, the Lean statement is `∃ x ∈ (convexHull ℝ S).extremePoints ℝ, ∃ y ∈ (convexHull ℝ S).extremePoints ℝ, dist x y = Metric.diam S`, and this is true because:
1. `convexHull ℝ S` is compact (since `S` is finite). 
2. The maximum distance is achieved between some `x`, `y ∈ S` (`S` is finite). 
3. Then `x`, `y ∈ convexHull ℝ S` (`convexHull ℝ S` contains `S`). 
4. `x`, `y` are extreme points of `convexHull ℝ S`. 

But is `convexHull ℝ S` the smallest convex set containing `S`? 

But no, `convexHull ℝ S` is the convex hull of `S` (`S` is finite or infinite, but the definition is the same). 

But the maximum distance is achieved in `S` (`S` is finite, `dist` is continuous, and the supremum is achieved), and `x`, `y ∈ S` lie in `convexHull ℝ S` (`S` is a subset of `convexHull ℝ S`). 

Thus, `x`, `y` are extreme points of `convexHull ℝ S` because `convexHull ℝ S` is `convexHull ℝ S` and they are in `S`. 

This is true because if `convexHull ℝ S` is compact (which it is because `S` is finite), and `S ⊆ convexHull ℝ S`, then the extreme points of `convexHull ℝ S` are in `S` (`convexHull ℝ S` is `convexHull ℝ S`). 

Alternatively, use the fact that the extreme points of `convexHull ℝ S` are in `S` if `S` is finite, but this is not true unless `S` is already convex. 

But it turns out Lean's `convexHull` is the same as the standard convex hull, so perhaps the extreme points are `S`. 

But no: in Lean, `convexHull ℝ S` is the convex hull of `S`, and the extreme points are points not in the interior of a larger subset. 

But `convexHull ℝ S` is compact, so its extreme points are its vertices, i.e., points in `S`. 

Thus, if `x` and `y` are in `S`, they are extreme points of `convexHull ℝ S`. 

But we have `S.Nonempty`, so `Metric.diam S` is `⨆ (x : S) (y : S), dist x.val y.val`. 

Thus, `x` and `y` are in `S`, hence in `convexHull ℝ S`, and they are extreme points. 

This completes the proof. 

**Final Abstract Plan:**
1. The set `S` is finite and nonempty, so `Metric.diam S` is `⨆ (x : S) (y : S), dist x.val y.val`.
2. Since `S` is finite, the supremum is achieved. Choose `x`, `y ∈ S` maximizing `dist x y`.
3. These points are in `convexHull ℝ S` (`convexHull_mono` since `S ⊆ convexHull ℝ S`).
4. The points `x` and `y` are extreme points of `convexHull ℝ S` (because they are in `S`, and `S` is a subset of `convexHull ℝ S`).

**Lean `have` statements:**

```lean4
theorem diameter_achieved_by_hull_vertices {n : ℕ} {S : Set (EuclideanSpace ℝ (Fin n))}
    (h_finite : Set.Finite S) (h_nonempty : S.Nonempty) :
    ∃ x ∈ (convexHull ℝ S).extremePoints ℝ, ∃ y ∈ (convexHull ℝ S).extremePoints ℝ,
      dist x y = Metric.diam S := by
  have h_main : ∃ (x : EuclideanSpace ℝ (Fin n)) (y : EuclideanSpace ℝ (Fin n)), (x ∈ (convexHull ℝ S).extremePoints ℝ) ∧ (y ∈ (convexHull ℝ S).extremePoints ℝ) ∧ (dist x y = Metric.diam S) := by
    sorry
  sorry
```

This `have` statement corresponds to the main statement that we need to prove: there exist `x` and `y` in the extreme points of `convexHull ℝ S` such that `dist x y = Metric.diam S`. 

The actual Lean code will fill in the details to construct `x` and `y` from the existence of points in `S` that maximize `dist x y`.
```

#### LeanFinder Top-5

1. `convexHull_diam`
   - `/-- Diameter of the convex hull of a set `s` equals the emetric diameter of `s`. -/`
2. `convexHull_ediam`
   - `/-- Emetric diameter of the convex hull of a set `s` equals the emetric diameter of `s`. -/`
3. `convexHull_diam`
   - `theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by`
4. `convexHull_exists_dist_ge2`
   - `/-- Given a point `x` in the convex hull of `s` and a point `y` in the convex hull of `t`,`
5. `IsCompact.extremePoints_nonempty`
   - `theorem IsCompact.extremePoints_nonempty (hscomp : IsCompact s) (hsnemp : s.Nonempty) : (s.extremePoints ℝ).Nonempty := by`

### `MSC-180_60_002`

- selected attempt index: `6`
- penultimate heading: `Lean 4 Proof Sketch with `have` Statements`
- heading category: `lean_sketch`
- penultimate body length: `618` chars

#### Penultimate Section Body

```text
```lean4
theorem weierstrass_approximation (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
    (ε : ℝ) (hε : ε > 0) :
    ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε := by
  have h_main : ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε := by
    sorry
  sorry
```

This sketch reflects the main step, which is straightforward in Lean. The `sorry` here can be directly replaced by invoking the Weierstrass approximation theorem, but we omit the exact invocation because it is straightforward in `Mathlib`. The `h_main` statement is the goal, and we use it to directly complete the proof.
```

#### LeanFinder Top-5

1. `exists_polynomial_near_of_continuousOn`
   - `theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ) (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :`
2. `exists_polynomial_near_continuousMap`
   - `theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ) (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by`
3. `bernsteinApproximation_uniform`
   - `theorem bernsteinApproximation_uniform (f : C(I, ℝ)) : Tendsto (fun n : ℕ => bernsteinApproximation n f) atTop (𝓝 f) := by`
4. `exists_taylor_mean_remainder_bound`
   - `theorem exists_taylor_mean_remainder_bound {f : ℝ → E} {a b : ℝ} {n : ℕ} (hab : a ≤ b) (hf : ContDiffOn ℝ (n + 1) f (Icc a b)) :`
5. `ContinuousMap.exists_mem_subalgebra_near_continuous_of_isCompact_of_separatesPoints`
   - `/-- A variant of the Stone-Weierstrass theorem where `X` need not be compact:`

### `MSC-180_65_001`

- selected attempt index: `4`
- penultimate heading: `Lean 4 `have` statements`
- heading category: `lean_sketch`
- penultimate body length: `586` chars

#### Penultimate Section Body

```text
```lean4
theorem unique_root_of_nonzero_deriv {a b : ℝ} (hab : a < b) (f : ℝ → ℝ)
    (hf : ContinuousOn f (Icc a b))
    (hderiv : ∀ x ∈ Ioo a b, DifferentiableAt ℝ f x)
    (hnonzero : ∀ x ∈ Ioo a b, deriv f x ≠ 0) :
    ∀ (p q : ℝ), p ∈ Icc a b → q ∈ Icc a b → f p = 0 → f q = 0 → p = q := by
  have h_main : ∀ (p q : ℝ), p ∈ Icc a b → q ∈ Icc a b → f p = 0 → f q = 0 → p = q := by
    sorry
  sorry
```

This concludes the abstract plan and Lean 4 `have` statements. The `have h_main` directly encodes the final result, and its proof can be constructed based on the reasoning above.
```

#### LeanFinder Top-5

1. `exists_deriv_eq_zero`
   - `theorem exists_deriv_eq_zero (hab : a < b) (hfc : ContinuousOn f (Icc a b)) (hfI : f a = f b) : ∃ c ∈ Ioo a b, deriv f c = 0 :=`
2. `exists_hasDerivAt_eq_zero`
   - `theorem exists_hasDerivAt_eq_zero (hab : a < b) (hfc : ContinuousOn f (Icc a b)) (hfI : f a = f b) (hff' : ∀ x ∈ Ioo a b, HasDerivAt f (f' x) x) :`
3. `constant_of_derivWithin_zero`
   - `theorem constant_of_derivWithin_zero (hdiff : DifferentiableOn ℝ f (Icc a b)) (hderiv : ∀ x ∈ Ico a b, derivWithin f (Icc a b) x = 0) :`
4. `constant_of_has_deriv_right_zero`
   - `theorem constant_of_has_deriv_right_zero (hcont : ContinuousOn f (Icc a b)) (hderiv : ∀ x ∈ Ico a b, HasDerivWithinAt f 0 (Ici x) x) : ∀ x ∈ Icc a b, f x = f a := by`
5. `exists_deriv_eq_zero'`
   - `theorem exists_deriv_eq_zero' (hab : a < b) (hfa : Tendsto f (𝓝[>] a) (𝓝 l)) (hfb : Tendsto f (𝓝[<] b) (𝓝 l)) : ∃ c ∈ Ioo a b, deriv f c = 0 := by`

### `MSC-180_65_003`

- selected attempt index: `4`
- penultimate heading: `Step 2: Lean 4 `have` Statements`
- heading category: `lean_sketch`
- penultimate body length: `833` chars

#### Penultimate Section Body

```text
```lean4
theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
  have h_main : ∀ (x : ℝ), x ∈ Icc a b → ∀ (y : ℝ), y ∈ Icc a b → ‖f y - f x‖ ≤ (L : ℝ) * ‖y - x‖ := by
    sorry
  have h_final : LipschitzOnWith L f (Icc a b) := by
    sorry
  exact h_final
  <;> try norm_num
  <;> linarith
```

This sets up the main lemma (`h_main`) that directly provides the Lipschitz condition, and then derives the main goal (`h_final`) from `h_main`. The `sorry` in `h_main` is where we need to apply MVT and use `hbounded` to bound the derivative. The `sorry` in `h_final` is trivial because `h_main` directly provides the definition of Lipschitz continuity on `Icc a b`.
```

#### LeanFinder Top-5

1. `Convex.lipschitzOnWith_of_nnnorm_deriv_le`
   - `theorem Convex.lipschitzOnWith_of_nnnorm_deriv_le {C : ℝ≥0} (hf : ∀ x ∈ s, DifferentiableAt 𝕜 f x) (bound : ∀ x ∈ s, ‖deriv f x‖₊ ≤ C) (hs : Convex ℝ s) :`
2. `norm_image_sub_le_of_norm_deriv_le_segment`
   - `theorem norm_image_sub_le_of_norm_deriv_le_segment {C : ℝ} (hf : DifferentiableOn ℝ f (Icc a b)) (bound : ∀ x ∈ Ico a b, ‖derivWithin f (Icc a b) x‖ ≤ C) :`
3. `Convex.lipschitzOnWith_of_nnnorm_derivWithin_le`
   - `theorem Convex.lipschitzOnWith_of_nnnorm_derivWithin_le {C : ℝ≥0} (hs : Convex ℝ s) (hf : DifferentiableOn 𝕜 f s) (bound : ∀ x ∈ s, ‖derivWithin f s x‖₊ ≤ C) :`
4. `lipschitzWith_of_nnnorm_deriv_le`
   - `theorem lipschitzWith_of_nnnorm_deriv_le {C : ℝ≥0} (hf : Differentiable 𝕜 f) (bound : ∀ x, ‖deriv f x‖₊ ≤ C) : LipschitzWith C f :=`
5. `Convex.lipschitzOnWith_of_nnnorm_fderiv_le`
   - `theorem Convex.lipschitzOnWith_of_nnnorm_fderiv_le {C : ℝ≥0} (hf : ∀ x ∈ s, DifferentiableAt 𝕜 f x) (bound : ∀ x ∈ s, ‖fderiv 𝕜 f x‖₊ ≤ C) (hs : Convex ℝ s) :`

### `MSC-180_68_002`

- selected attempt index: `2`
- penultimate heading: `Lean 4 Proof Sketch with `have` Statements`
- heading category: `lean_sketch`
- penultimate body length: `411` chars

#### Penultimate Section Body

```text
```lean4
theorem bezout_identity (a b : ℤ) : ∃ s t : ℤ, s * a + t * b = Int.gcd a b := by
  have h_main : ∃ s t : ℤ, s * a + t * b = Int.gcd a b := by
    sorry
  sorry
```

This sketch directly uses `h_main` to reflect the statement we need to prove. The `have` statement is marked with `sorry`, but its proof would invoke `Int.gcd_eq_gcd_ab` or Lean's library lemmas to guarantee the existence of `s` and `t`.
```

#### LeanFinder Top-5

1. `Int.gcd_eq_gcd_ab`
   - `theorem Int.gcd_eq_gcd_ab : ∀ x y : ℤ, (gcd x y : ℤ) = x * gcdA x y + y * gcdB x y | (m : ℕ), (n : ℕ) => Nat.gcd_eq_gcd_ab _ _`
2. `Nat.gcd_eq_gcd_ab`
   - `theorem Nat.gcd_eq_gcd_ab : (gcd x y : ℤ) = x * gcdA x y + y * gcdB x y := by`
3. `exists_gcd_eq_mul_add_mul`
   - `theorem exists_gcd_eq_mul_add_mul (a b : R) : ∃ x y, gcd a b = a * x + b * y := by`
4. `IsBezout.gcd_eq_sum`
   - `theorem IsBezout.gcd_eq_sum : ∃ a b : R, a * x + b * y = gcd x y :=`
5. `Int.gcd_dvd_iff`
   - `theorem Int.gcd_dvd_iff {a b : ℤ} {n : ℕ} : gcd a b ∣ n ↔ ∃ x y : ℤ, ↑n = a * x + b * y := by`

### `MSC-180_90_001`

- selected attempt index: `7`
- penultimate heading: `Lean 4 Proof Sketch with `have` Statements`
- heading category: `lean_sketch`
- penultimate body length: `426` chars

#### Penultimate Section Body

```text
```lean4
theorem euclidean_ball_convex {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    (c : E) (r : ℝ) (hr : 0 ≤ r) :
    Convex ℝ (ball c r) := by
  -- Step 1: Prove that `ball c r` is convex
  have h_main : Convex ℝ (ball c r) := by
    sorry
  sorry
```

This `have` statement encapsulates the entire proof, as `ball c r` being convex follows directly from the triangle inequality and the definition of `ball c r`.
```

#### LeanFinder Top-5

1. `convex_ball`
   - `theorem convex_ball (a : E) (r : ℝ) : Convex ℝ (Metric.ball a r) := by`
2. `convex_ball`
   - `theorem convex_ball (a : E) (r : ℝ) : Convex ℝ (Metric.ball a r) := by`
3. `Seminorm.convex_ball`
   - `theorem Seminorm.convex_ball : Convex ℝ (ball p x r) := by`
4. `convex_closedBall`
   - `theorem convex_closedBall (a : E) (r : ℝ) : Convex ℝ (Metric.closedBall a r) := by`
5. `convex_closedBall`
   - `theorem convex_closedBall (a : E) (r : ℝ) : Convex ℝ (Metric.closedBall a r) := by`
