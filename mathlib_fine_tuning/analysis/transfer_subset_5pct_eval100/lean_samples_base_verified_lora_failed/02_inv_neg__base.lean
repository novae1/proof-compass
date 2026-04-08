import Mathlib

open Function
variable {M₀ G₀ : Type*} (α : Type*)
variable {α} {a b c d : α}
section MonoidWithZero
variable [MonoidWithZero M₀]
section GroupWithZero
variable [GroupWithZero G₀]
section LinearOrder
variable [LinearOrder G₀] [ZeroLEOneClass G₀] {a b c d : G₀}
section PosMulMono
variable [PosMulMono G₀]

lemma manual_inv_neg : a⁻¹ < 0 ↔ a < 0 := by
  by_cases h : a = 0 <;> simp_all [h, inv_eq_zero, not_lt]
  <;> exact?
end PosMulMono
end LinearOrder
end GroupWithZero
end MonoidWithZero
