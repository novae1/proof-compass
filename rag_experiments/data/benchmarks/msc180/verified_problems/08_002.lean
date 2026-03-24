import Mathlib

theorem unique_relative_complement {L : Type*} [DistribLattice L] {a b c : L}
    (hab : a ≤ b) (hbc : b ≤ c) :
    ∀ (d₁ d₂ : L),
      a ≤ d₁ ∧ d₁ ≤ c ∧ d₁ ⊔ b = c ∧ d₁ ⊓ b = a →
      a ≤ d₂ ∧ d₂ ≤ c ∧ d₂ ⊔ b = c ∧ d₂ ⊓ b = a →
      d₁ = d₂ := by
  intro d₁ d₂ hd₁ hd₂
  rcases hd₁ with ⟨ha₁, h₁c, h₁sup, h₁inf⟩
  rcases hd₂ with ⟨ha₂, h₂c, h₂sup, h₂inf⟩
  apply le_antisymm
  · calc
      d₁ = d₁ ⊓ c := (inf_eq_left.2 h₁c).symm
      _ = d₁ ⊓ (d₂ ⊔ b) := by simpa [h₂sup]
      _ = (d₁ ⊓ d₂) ⊔ (d₁ ⊓ b) := by exact inf_sup_left d₁ d₂ b
      _ = (d₁ ⊓ d₂) ⊔ a := by simpa [h₁inf]
      _ ≤ d₂ ⊔ a := sup_le_sup inf_le_right le_rfl
      _ = d₂ := sup_eq_left.2 ha₂
  · calc
      d₂ = d₂ ⊓ c := (inf_eq_left.2 h₂c).symm
      _ = d₂ ⊓ (d₁ ⊔ b) := by simpa [h₁sup]
      _ = (d₂ ⊓ d₁) ⊔ (d₂ ⊓ b) := by exact inf_sup_left d₂ d₁ b
      _ = (d₂ ⊓ d₁) ⊔ a := by simpa [h₂inf]
      _ ≤ d₁ ⊔ a := sup_le_sup inf_le_right le_rfl
      _ = d₁ := sup_eq_left.2 ha₁

/-
Used theorem names explicitly mentioned in the proof above:
- le_antisymm
- inf_eq_left
- inf_sup_left
- sup_le_sup
- inf_le_right
- sup_eq_left
-/

/- Statements of the listed theorems -/
-- theorem le_antisymm : {α : Type u_1} [PartialOrder α] {a b : α} : a ≤ b → b ≤ a → a = b

-- theorem inf_eq_left : {α : Type u} [SemilatticeInf α] {a b : α} : a ⊓ b = a ↔ a ≤ b

-- theorem inf_sup_left : {α : Type u} [DistribLattice α] (a b c : α) : a ⊓ (b ⊔ c) = a ⊓ b ⊔ a ⊓ c

-- theorem sup_le_sup : {α : Type u} [SemilatticeSup α] {a b c d : α} (h₁ : a ≤ b) (h₂ : c ≤ d) : a ⊔ c ≤ b ⊔ d

-- theorem inf_le_right : {α : Type u} [SemilatticeInf α] {a b : α} : a ⊓ b ≤ b

-- theorem sup_eq_left : {α : Type u} [SemilatticeSup α] {a b : α} : a ⊔ b = a ↔ b ≤ a

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `le_antisymm`
-- Source: .lake/packages/mathlib/Mathlib/Order/Basic.lean:89
example [PartialOrder α] {a b : α} : a ≤ b → b ≤ a → b = a := by
  exact flip le_antisymm

-- Uses `inf_eq_left`
-- Source: .lake/packages/mathlib/Mathlib/Order/Lattice.lean:567
example {α : Type*} [Lattice α] {a b : α} : a ⊔ b = b ↔ a ⊓ b = a := by
  rw [sup_eq_right, ← inf_eq_left]

-- Uses `inf_sup_left`
-- Source: .lake/packages/mathlib/Mathlib/Order/Disjoint.lean:175
example {α : Type*} [DistribLattice α] {a b c : α} :
    a ⊓ (b ⊔ c) = a ⊓ b ⊔ a ⊓ c := by
  exact inf_sup_left a b c

-- Uses `sup_le_sup`
-- Source: .lake/packages/mathlib/Mathlib/Order/Filter/Basic.lean:1157
example {α : Type*} [SemilatticeSup α] {a b c d : α} (h₁ : a ≤ b) (h₂ : c ≤ d) :
    a ⊔ c ≤ b ⊔ d := by
  exact sup_le_sup h₁ h₂

-- Uses `inf_le_right`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/Lie/IdealOperations.lean:195
example {α : Type*} [SemilatticeInf α] {a b : α} : a ⊓ b ≤ b := by
  exact inf_le_right

-- Uses `sup_eq_left`
-- Source: .lake/packages/mathlib/Mathlib/Order/Interval/Set/UnorderedInterval.lean:70
example {α : Type*} [SemilatticeSup α] {a b : α} (h : b ≤ a) : a ⊔ b = a := by
  exact sup_eq_left.2 h
