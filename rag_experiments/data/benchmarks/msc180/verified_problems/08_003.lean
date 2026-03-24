import Mathlib

theorem exists_element_with_maximal_order {G : Type*} [CommGroup G] [Fintype G] :
    ∃ g : G, ∀ x : G, orderOf x ∣ orderOf g := by
  obtain ⟨g, hg⟩ :=
    Monoid.exists_orderOf_eq_exponent (G := G) (Monoid.ExponentExists.of_finite (G := G))
  refine ⟨g, ?_⟩
  intro x
  rw [hg]
  exact Monoid.order_dvd_exponent x

/-
Used theorem names explicitly mentioned in the proof above:
- Monoid.exists_orderOf_eq_exponent
- Monoid.ExponentExists.of_finite
- Monoid.order_dvd_exponent
-/

/- Statements of the listed theorems -/
-- theorem Monoid.exists_orderOf_eq_exponent : {G : Type u} [CommMonoid G] (hG : Monoid.ExponentExists G) :
--   ∃ g, orderOf g = Monoid.exponent G

-- theorem Monoid.ExponentExists.of_finite : {G : Type u} [LeftCancelMonoid G] [Finite G] : Monoid.ExponentExists G

-- theorem Monoid.order_dvd_exponent : {G : Type u} [Monoid G] (g : G) : orderOf g ∣ Monoid.exponent G

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `Monoid.exists_orderOf_eq_exponent`
-- Source: .lake/packages/mathlib/Mathlib/GroupTheory/Exponent.lean:453
example {G : Type*} [CommMonoid G] (hG : Monoid.ExponentExists G) :
    ∃ g : G, orderOf g = Monoid.exponent G := by
  simpa using Monoid.exists_orderOf_eq_exponent (G := G) hG

-- Uses `Monoid.ExponentExists.of_finite`
-- Source: .lake/packages/mathlib/Mathlib/ModelTheory/FinitelyGenerated.lean:242
example {G : Type*} [LeftCancelMonoid G] [Finite G] : Monoid.ExponentExists G := by
  exact Monoid.ExponentExists.of_finite (G := G)

-- Uses `Monoid.order_dvd_exponent`
-- Source: .lake/packages/mathlib/Mathlib/GroupTheory/Exponent.lean:214
example {G : Type*} [Monoid G] [Fintype G] :
    (Finset.univ : Finset G).lcm orderOf ∣ Monoid.exponent G := by
  apply Finset.lcm_dvd
  intro g _
  exact Monoid.order_dvd_exponent g

-- [to_additive exists_addOrderOf_eq_pow_padic_val_nat_add_exponent]
