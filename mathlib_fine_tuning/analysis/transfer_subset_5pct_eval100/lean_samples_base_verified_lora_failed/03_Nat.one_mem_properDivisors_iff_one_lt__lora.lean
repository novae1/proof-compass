import Mathlib

open Finset
namespace Nat
variable (n : ℕ)
variable {n}

theorem manual_one_mem_properDivisors_iff_one_lt : 1 ∈ n.properDivisors ↔ 1 < n := by
  rw [mem_properDivisors, Nat.dvd_one, and_true_iff, Nat.lt_succ_iff]
end Nat

-- Verification errors from held-out REPL check:
-- Error 1: tactic 'rewrite' failed, did not find instance of the pattern in the target expression
--     ?m.91 ∣ 1
--   n : ℕ
--   ⊢ 1 ∣ n ∧ 1 < n ↔ 1 < n
