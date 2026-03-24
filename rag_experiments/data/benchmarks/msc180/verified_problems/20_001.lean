import Mathlib

theorem my_favorite_theorem {G : Type*} [CommGroup G] [Fintype G]
    (hG : Fintype.card G ≠ 0) (p : ℕ) (hp : Nat.Prime p)
    (hG1 : p ∣ Fintype.card G) :
    ∃ x : G, orderOf x = p := by
  let _ := hG
  let _ := hp
  haveI : Fact p.Prime := ⟨hp⟩
  exact exists_prime_orderOf_dvd_card p hG1

/-
Used theorem names explicitly mentioned in the proof above:
- exists_prime_orderOf_dvd_card
-/

/- Statements of the listed theorems -/
-- theorem exists_prime_orderOf_dvd_card : {G : Type u_3} [Group G] [Fintype G] (p : ℕ) [hp : Fact (Nat.Prime p)]
--   (hdvd : p ∣ Fintype.card G) : ∃ x, orderOf x = p

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `exists_prime_orderOf_dvd_card`
-- Source: .lake/packages/mathlib/Mathlib/GroupTheory/FixedPointFree.lean:83
example {G : Type*} [Group G] [Fintype G] (h : 2 ∣ Fintype.card G) :
    ∃ g : G, orderOf g = 2 := by
  haveI : Fact (Nat.Prime 2) := ⟨by decide⟩
  exact exists_prime_orderOf_dvd_card 2 h
