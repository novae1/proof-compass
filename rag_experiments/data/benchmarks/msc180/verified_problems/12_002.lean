import Mathlib

theorem chinese_remainder_theorem {k : ℕ} (n : ℕ → ℕ)
    (hpos : ∀ i, 0 < i → i ≤ k → n i > 0)
    (hcoprime : ∀ i j, 0 < i → i ≤ k → 0 < j → j ≤ k → i ≠ j → Nat.Coprime (n i) (n j))
    (a : ℕ → ℤ) :
    ∃ x : ℤ, ∀ i, 0 < i → i ≤ k → x ≡ a i [ZMOD (n i)] ∧
      ∀ y : ℤ, (∀ i, 0 < i → i ≤ k → y ≡ a i [ZMOD (n i)]) →
        x ≡ y [ZMOD ((Finset.Icc 1 k).prod fun i => (n i : ℤ))] := by
  classical
  let t : Finset ℕ := Finset.Icc 1 k
  let aNat : ℕ → ℕ := fun i => Int.toNat (a i % n i)
  have hsNat : ∀ i ∈ t, n i ≠ 0 := by
    intro i hi
    exact Nat.ne_of_gt (hpos i (Finset.mem_Icc.mp hi).1 (Finset.mem_Icc.mp hi).2)
  have hpairNat : Set.Pairwise t (Nat.Coprime on n) := by
    intro i hi j hj hij
    exact hcoprime i j (Finset.mem_Icc.mp hi).1 (Finset.mem_Icc.mp hi).2
      (Finset.mem_Icc.mp hj).1 (Finset.mem_Icc.mp hj).2 hij
  let xNat : ℕ := Nat.chineseRemainderOfFinset aNat n t hsNat hpairNat
  have hx_mod : ∀ i ∈ t, (xNat : ℤ) ≡ a i [ZMOD n i] := by
    intro i hi
    have hxNat_i : xNat ≡ aNat i [MOD n i] :=
      (Nat.chineseRemainderOfFinset aNat n t hsNat hpairNat).property i hi
    have hxInt_i : (xNat : ℤ) ≡ (aNat i : ℤ) [ZMOD n i] :=
      (Int.natCast_modEq_iff).2 hxNat_i
    have hni_pos : 0 < n i := hpos i (Finset.mem_Icc.mp hi).1 (Finset.mem_Icc.mp hi).2
    have hni_ne : (n i : ℤ) ≠ 0 := by exact_mod_cast (Nat.ne_of_gt hni_pos)
    have hnonneg : 0 ≤ a i % n i := Int.emod_nonneg _ hni_ne
    have haInt_i : (aNat i : ℤ) ≡ a i [ZMOD n i] := by
      change (Int.toNat (a i % n i) : ℤ) ≡ a i [ZMOD n i]
      simpa [Int.toNat_of_nonneg hnonneg] using (Int.mod_modEq (a i) (n i))
    exact hxInt_i.trans haInt_i
  have hpairInt : Set.Pairwise t (IsCoprime on fun i => (n i : ℤ)) := by
    intro i hi j hj hij
    exact (hpairNat hi hj hij).isCoprime
  have hunique : ∀ y : ℤ,
      (∀ i, 0 < i → i ≤ k → y ≡ a i [ZMOD n i]) →
      (xNat : ℤ) ≡ y [ZMOD ((Finset.Icc 1 k).prod fun i => (n i : ℤ))] := by
    intro y hy
    have hdivs : ∀ i ∈ t, (n i : ℤ) ∣ y - (xNat : ℤ) := by
      intro i hi
      have hyi : y ≡ a i [ZMOD n i] := hy i (Finset.mem_Icc.mp hi).1 (Finset.mem_Icc.mp hi).2
      have hxy : (xNat : ℤ) ≡ y [ZMOD n i] := (hx_mod i hi).trans hyi.symm
      exact hxy.dvd
    exact (Int.modEq_iff_dvd).2 (Finset.prod_dvd_of_coprime hpairInt hdivs)
  refine ⟨(xNat : ℤ), ?_⟩
  intro i hi0 hik
  have hiT : i ∈ t := Finset.mem_Icc.mpr ⟨hi0, hik⟩
  exact ⟨hx_mod i hiT, hunique⟩

/-
Used theorem names explicitly mentioned in the proof above (reduced to most relevant):
- Nat.chineseRemainderOfFinset
- Int.natCast_modEq_iff
- Int.mod_modEq
- Int.modEq_iff_dvd
- Finset.prod_dvd_of_coprime
-/

/- Statements of the listed theorems -/
-- theorem Nat.chineseRemainderOfFinset : {ι : Type u_1} (a s : ι → ℕ) (t : Finset ι) (hs : ∀ i ∈ t, s i ≠ 0)
--   (pp : (↑t).Pairwise (Nat.Coprime on s)) : { k // ∀ i ∈ t, k ≡ a i [MOD s i] }

-- theorem Int.natCast_modEq_iff : {a b n : ℕ} : ↑a ≡ ↑b [ZMOD ↑n] ↔ a ≡ b [MOD n]

-- theorem Int.mod_modEq : (a n : ℤ) : a % n ≡ a [ZMOD n]

-- theorem Int.modEq_iff_dvd : {n a b : ℤ} : a ≡ b [ZMOD n] ↔ n ∣ b - a

-- theorem Finset.prod_dvd_of_coprime : {R : Type u} {I : Type v} [CommSemiring R] {z : R} {s : I → R} {t : Finset I} :
--   (↑t).Pairwise (IsCoprime on s) → (∀ i ∈ t, s i ∣ z) → ∏ x ∈ t, s x ∣ z

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `Nat.chineseRemainderOfFinset`
-- Source: .lake/packages/mathlib/Mathlib/Data/Nat/ChineseRemainder.lean:160
example {ι : Type*} (a s : ι → ℕ) (t : Finset ι)
    (hs : ∀ i ∈ t, s i ≠ 0) (pp : Set.Pairwise (↑t : Set ι) (Nat.Coprime on s)) :
    ∀ i ∈ t, (Nat.chineseRemainderOfFinset a s t hs pp).1 ≡ a i [MOD s i] := by
  exact (Nat.chineseRemainderOfFinset a s t hs pp).2

-- Uses `Int.natCast_modEq_iff`
-- Source: .lake/packages/mathlib/Mathlib/Data/ZMod/Basic.lean:554
example (a b c : ℕ) : (a : ZMod c) = (b : ZMod c) ↔ a ≡ b [MOD c] := by
  simpa [Int.natCast_modEq_iff] using ZMod.intCast_eq_intCast_iff a b c

-- Uses `Int.mod_modEq`
-- Source: .lake/packages/mathlib/Mathlib/Data/ZMod/Basic.lean:654
example (a n : ℤ) : a % n ≡ a [ZMOD n] := by
  exact Int.mod_modEq a n

-- [deprecated (since := "2024-04-17")]
-- alias int_cast_mod := intCast_mod

-- Uses `Int.modEq_iff_dvd`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/CharP/Defs.lean:104
example {n a b : ℤ} : a ≡ b [ZMOD n] ↔ n ∣ b - a := by
  exact Int.modEq_iff_dvd

-- Uses `Finset.prod_dvd_of_coprime`
-- Source: .lake/packages/mathlib/Mathlib/RingTheory/Ideal/Operations.lean:487
example {R I : Type*} [CommSemiring R] (t : Finset I) (s : I → R) {z : R}
    (hpair : (↑t : Set I).Pairwise (IsCoprime on s)) (hz : ∀ i ∈ t, s i ∣ z) :
    ∏ x ∈ t, s x ∣ z := by
  exact Finset.prod_dvd_of_coprime hpair hz
