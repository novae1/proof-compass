import Mathlib

variable {α : Type*} {β : Type*} {ι : Type*}
open Filter
open scoped Topology NNReal
section SeminormedRing
variable [SeminormedRing α] {a b c : α}

theorem Finset.manual_norm_prod_le {α : Type*} [NormedCommRing α] [NormOneClass α] (s : Finset ι)
    (f : ι → α) : ‖∏ i ∈ s, f i‖ ≤ ∏ i ∈ s, ‖f i‖ := by
  simpa only [Finset.prod_const] using s.norm_prod_le fun i _ => ‖f i‖
end SeminormedRing

-- Verification errors from held-out REPL check:
-- Error 1: typeclass instance problem is stuck, it is often due to metavariables
--     NormOneClass (?m.1000 → ℝ)
-- Error 2: stuck at solving universe constraint
--     ?u.903+1 =?= max 1 ?u.918
--   while trying to unify
--     ι → ?m.1000 → ℝ : Sort (max (u_3 + 1) ?u.918)
--   with
--     ι → ?m.1000 → ℝ : Sort (max (u_3 + 1) ?u.918)
