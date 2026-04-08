import Mathlib

open Finset
namespace Nat
variable (n : ℕ)
variable {n}

theorem manual_one_mem_properDivisors_iff_one_lt : 1 ∈ n.properDivisors ↔ 1 < n := by
  rw [mem_properDivisors]
  <;>
    rcases n with (_ | _ | n) <;>
    simp_all [Nat.lt_succ_iff, Nat.div_eq_of_lt]
  <;>
    omega
end Nat
