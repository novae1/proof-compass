import Mathlib

theorem bezout_identity (a b : ℤ) : ∃ s t : ℤ, s * a + t * b = Int.gcd a b := by
  refine ⟨Int.gcdA a b, Int.gcdB a b, ?_⟩
  simpa [mul_comm, add_comm, add_left_comm, add_assoc] using (Int.gcd_eq_gcd_ab a b).symm

/-
Used theorem names explicitly mentioned in the proof above:
- Int.gcd_eq_gcd_ab
-/

/- Statements of the listed theorems -/
-- theorem Int.gcd_eq_gcd_ab : (x y : ℤ) : ↑(x.gcd y) = x * x.gcdA y + y * x.gcdB y

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `Int.gcd_eq_gcd_ab`
-- Source: .lake/packages/mathlib/Mathlib/Data/Int/ModEq.lean:222
example (a b : ℕ) : (a : ℤ) * Nat.gcdA a b ≡ Nat.gcd a b [ZMOD b] := by
  have hbez : (Nat.gcd a b : ℤ) = (a : ℤ) * Nat.gcdA a b + (b : ℤ) * Nat.gcdB a b := by
    simpa using (Int.gcd_eq_gcd_ab (a : ℤ) (b : ℤ))
  rw [hbez]
  simpa [add_comm, add_left_comm, add_assoc] using
    (dvd_mul_right (b : ℤ) (Nat.gcdB a b)).zero_modEq_int.add_left ((a : ℤ) * Nat.gcdA a b)
