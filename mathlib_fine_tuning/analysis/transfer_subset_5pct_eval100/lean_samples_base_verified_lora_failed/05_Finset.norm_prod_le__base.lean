import Mathlib

variable {α : Type*} {β : Type*} {ι : Type*}
open Filter
open scoped Topology NNReal
section SeminormedRing
variable [SeminormedRing α] {a b c : α}

theorem Finset.manual_norm_prod_le {α : Type*} [NormedCommRing α] [NormOneClass α] (s : Finset ι)
    (f : ι → α) : ‖∏ i ∈ s, f i‖ ≤ ∏ i ∈ s, ‖f i‖ := by
  classical
  induction' s using Finset.induction_on with i s hi ih
  · simp
  · rw [Finset.prod_insert hi]
    rw [Finset.prod_insert hi]
    exact norm_mul_le_of_le (by simp) (ih)
end SeminormedRing
