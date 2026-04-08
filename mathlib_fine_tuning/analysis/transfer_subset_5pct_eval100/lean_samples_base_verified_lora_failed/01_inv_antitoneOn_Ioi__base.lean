import Mathlib

open Function OrderDual
variable {ι α β : Type*}
section
variable [LinearOrderedField α] {a b c d : α} {n : ℤ}

theorem manual_inv_antitoneOn_Ioi :
    AntitoneOn (fun x : α ↦ x⁻¹) (Set.Ioi 0) := by
  intro x hx y hy hxy
  have hx' : 0 < x := hx
  have hy' : 0 < y := hy
  have hxy' : x ≤ y := hxy
  rw [inv_le_inv] <;> linarith
end
