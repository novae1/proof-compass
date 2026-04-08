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
  rw [← not_le, ← not_le, inv_nonneg]
end PosMulMono
end LinearOrder
end GroupWithZero
end MonoidWithZero

-- Verification errors from held-out REPL check:
-- Error 1: failed to synthesize
--     PosMulReflectLT G₀
--   Additional diagnostic information may be available using the `set_option diagnostics true` command.
-- Error 2: unsolved goals
--   G₀ : Type u_2
--   inst✝³ : GroupWithZero G₀
--   inst✝² : LinearOrder G₀
--   inst✝¹ : ZeroLEOneClass G₀
--   a : G₀
--   inst✝ : PosMulMono G₀
--   ⊢ PosMulReflectLT G₀
