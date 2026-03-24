import Mathlib

open Real Filter

theorem convergence_of_log_series {a b : ℝ} (ha : a > 0) (hb : b > 1) :
    Summable (fun n : ℕ => (Real.log (n + 1)) ^ a / (n + 1) ^ b) := by
  let s : ℝ := (b - 1) / 2
  let p : ℝ := b - s
  have hs : 0 < s := by
    dsimp [s]
    linarith
  have hp : 1 < p := by
    dsimp [p, s]
    linarith
  have hg_abs : Summable (fun n : ℕ => 1 / |((n : ℝ) + 1)| ^ p) :=
    (Real.summable_one_div_nat_add_rpow (1 : ℝ) p).2 hp
  have hg : Summable (fun n : ℕ => (((n : ℝ) + 1) ^ p)⁻¹) := by
    refine hg_abs.congr ?_
    intro n
    have hx : 0 ≤ (n : ℝ) + 1 := by positivity
    simp [one_div, abs_of_nonneg hx]
  have h_nat_tendsto : Tendsto (fun n : ℕ => (n : ℝ) + 1) atTop atTop := by
    simpa using
      (Filter.tendsto_atTop_add_const_right atTop (1 : ℝ) tendsto_natCast_atTop_atTop)
  have hnum :
      (fun n : ℕ => (Real.log ((n : ℝ) + 1)) ^ a) =O[atTop]
        (fun n : ℕ => ((n : ℝ) + 1) ^ s) := by
    exact ((isLittleO_log_rpow_rpow_atTop a hs).comp_tendsto h_nat_tendsto).isBigO
  have hpow_ne : ∀ᶠ n : ℕ in atTop, ((n : ℝ) + 1) ^ b ≠ 0 := by
    filter_upwards with n
    exact (Real.rpow_pos_of_pos (by positivity) b).ne'
  have hmul :
      (fun n : ℕ =>
          ((n : ℝ) + 1) ^ b * ((Real.log ((n : ℝ) + 1)) ^ a / ((n : ℝ) + 1) ^ b))
        =O[atTop] (fun n : ℕ => ((n : ℝ) + 1) ^ s) := by
    refine hnum.congr' ?_ (Filter.EventuallyEq.rfl)
    filter_upwards [hpow_ne] with n hn
    field_simp [hn]
  have hmain :
      (fun n : ℕ => (Real.log ((n : ℝ) + 1)) ^ a / ((n : ℝ) + 1) ^ b)
        =O[atTop] (fun n : ℕ => ((n : ℝ) + 1) ^ s / ((n : ℝ) + 1) ^ b) :=
    (Asymptotics.isBigO_mul_iff_isBigO_div hpow_ne).1 hmul
  have hdiv : (fun n : ℕ => ((n : ℝ) + 1) ^ s / ((n : ℝ) + 1) ^ b) =
      (fun n : ℕ => (((n : ℝ) + 1) ^ p)⁻¹) := by
    funext n
    have hx : 0 < (n : ℝ) + 1 := by positivity
    calc
      ((n : ℝ) + 1) ^ s / ((n : ℝ) + 1) ^ b = ((n : ℝ) + 1) ^ (s - b) := by
        rw [← Real.rpow_sub hx s b]
      _ = ((n : ℝ) + 1) ^ (-p) := by
        dsimp [p]
        ring_nf
      _ = (((n : ℝ) + 1) ^ p)⁻¹ := by
        rw [Real.rpow_neg hx.le]
  have hmain' :
      (fun n : ℕ => (Real.log ((n : ℝ) + 1)) ^ a / ((n : ℝ) + 1) ^ b) =O[atTop]
        (fun n : ℕ => (((n : ℝ) + 1) ^ p)⁻¹) := by
    exact hmain.congr
      (fun _ => rfl)
      (fun n => by
        have hdivn := congrArg (fun f : ℕ → ℝ => f n) hdiv
        simpa using hdivn)
  have hsummable_cast :
      Summable (fun n : ℕ => (Real.log ((n : ℝ) + 1)) ^ a / ((n : ℝ) + 1) ^ b) :=
    summable_of_isBigO_nat hg hmain'
  simpa [Nat.cast_add, Nat.cast_one] using hsummable_cast

/-
Used theorem names explicitly mentioned in the proof above (reduced to most relevant):
- Real.summable_one_div_nat_add_rpow
- isLittleO_log_rpow_rpow_atTop
- Asymptotics.isBigO_mul_iff_isBigO_div
- summable_of_isBigO_nat
-/

/- Statements of the listed theorems -/
-- theorem Real.summable_one_div_nat_add_rpow : (a s : ℝ) : (Summable fun n => 1 / |↑n + a| ^ s) ↔ 1 < s

-- theorem isLittleO_log_rpow_rpow_atTop : {s : ℝ} (r : ℝ) (hs : 0 < s) : (fun x => Real.log x ^ r) =o[Filter.atTop] fun x => x ^ s

-- theorem Asymptotics.isBigO_mul_iff_isBigO_div : {α : Type u_1} {𝕜 : Type u_15} [NormedDivisionRing 𝕜] {l : Filter α}
--   {f g h : α → 𝕜} (hf : ∀ᶠ (x : α) in l, f x ≠ 0) : (fun x => f x * g x) =O[l] h ↔ g =O[l] fun x => h x / f x

-- theorem summable_of_isBigO_nat : {E : Type u_1} [SeminormedAddCommGroup E] [CompleteSpace E] {f : ℕ → E} {g : ℕ → ℝ}
--   (hg : Summable g) (h : f =O[Filter.atTop] g) : Summable f

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `Real.summable_one_div_nat_add_rpow`
-- Source: .lake/packages/mathlib/Mathlib/Analysis/PSeries.lean:465
example (a : ℝ) (s : ℝ) :
    Summable (fun n : ℤ ↦ 1 / |n + a| ^ s) ↔ 1 < s := by
  simp_rw [summable_int_iff_summable_nat_and_neg, ← abs_neg (↑(-_ : ℤ) + a), neg_add,
    Int.cast_neg, neg_neg, Int.cast_natCast, Real.summable_one_div_nat_add_rpow, and_self]

-- Uses `isLittleO_log_rpow_rpow_atTop`
-- Source: .lake/packages/mathlib/Mathlib/Analysis/SpecialFunctions/Pow/Asymptotics.lean:336
example {s : ℝ} (r : ℝ) (hs : s < 0) :
    (fun x => Real.log x ^ r) =o[Filter.atTop] fun x => x ^ (-s) := by
  simpa using isLittleO_log_rpow_rpow_atTop r (neg_pos.2 hs)

-- Uses `Asymptotics.isBigO_mul_iff_isBigO_div`
-- Source: .lake/packages/mathlib/Mathlib/NumberTheory/LSeries/Nonvanishing.lean:313
example {α 𝕜 : Type*} [NormedField 𝕜] {l : Filter α}
    {f g h : α → 𝕜} (hf : ∀ᶠ x in l, f x ≠ 0) :
    (fun x ↦ f x * g x) =O[l] h ↔ g =O[l] (fun x ↦ h x / f x) := by
  simpa using Asymptotics.isBigO_mul_iff_isBigO_div (l := l) (f := f) (g := g) (h := h) hf

-- Uses `summable_of_isBigO_nat`
-- Source: .lake/packages/mathlib/Mathlib/NumberTheory/ModularForms/JacobiTheta/TwoVariable.lean:103
example {E : Type*} [SeminormedAddCommGroup E] [CompleteSpace E]
    {f : ℕ → E} {g : ℕ → ℝ} (hg : Summable g) (h : f =O[atTop] g) :
    Summable f := by
  exact summable_of_isBigO_nat hg h
