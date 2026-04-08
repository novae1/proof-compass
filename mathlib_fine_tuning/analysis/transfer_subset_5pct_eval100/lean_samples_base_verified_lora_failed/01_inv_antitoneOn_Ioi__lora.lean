import Mathlib

open Function OrderDual
variable {ι α β : Type*}
section
variable [LinearOrderedField α] {a b c d : α} {n : ℤ}

theorem manual_inv_antitoneOn_Ioi :
    AntitoneOn (fun x : α ↦ x⁻¹) (Set.Ioi 0) := by
  rintro x (hx : 0 < x) y (hy : 0 < y) hxy
  rw [inv_le_inv hx hy]
  exact hxy
end

-- Verification errors from held-out REPL check:
-- Error 1: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
--     x⁻¹ ≤ y⁻¹
--   α : Type u_2
--   inst✝ : LinearOrderedField α
--   x : α
--   hx : 0 < x
--   y : α
--   hy : 0 < y
--   hxy : x ≤ y
--   ⊢ (fun x => x⁻¹) y ≤ (fun x => x⁻¹) x
