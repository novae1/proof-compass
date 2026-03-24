import Mathlib

open Polynomial

theorem polynomial_division_algorithm {F : Type*} [Field F] (f g : Polynomial F) (hg : g ≠ 0) :
    ∃ (q r : Polynomial F),
      f = g * q + r ∧
      (r = 0 ∨ r.degree < g.degree) ∧
      ∀ (q' r' : Polynomial F),
        (f = g * q' + r' ∧ (r' = 0 ∨ r'.degree < g.degree)) → q = q' ∧ r = r' := by
  refine ⟨f / g, f % g, ?_, ?_, ?_⟩
  · simpa [add_comm, add_left_comm, add_assoc] using (EuclideanDomain.mod_add_div f g).symm
  · right
    exact EuclideanDomain.mod_lt _ hg
  · intro q' r' h'
    rcases h' with ⟨hdecomp, hr'⟩
    have hstd : f = g * (f / g) + f % g := by
      simpa [add_comm, add_left_comm, add_assoc] using (EuclideanDomain.mod_add_div f g).symm
    have hdeg' : degree r' < degree g := by
      rcases hr' with hr'0 | hr'lt
      · subst hr'0
        have hgdeg : degree g ≠ ⊥ := mt Polynomial.degree_eq_bot.1 hg
        simpa using (bot_lt_iff_ne_bot.2 hgdeg)
      · exact hr'lt
    have h₁ : r' - f % g = -g * (q' - f / g) := by
      apply eq_of_sub_eq_zero
      rw [← sub_eq_zero_of_eq (hdecomp.symm.trans hstd)]
      ring
    have h₂ : degree (r' - f % g) = degree (g * (q' - f / g)) := by
      simpa [h₁]
    have h₃ : degree (r' - f % g) < degree g := by
      calc
        degree (r' - f % g) ≤ max (degree r') (degree (f % g)) := degree_sub_le _ _
        _ < degree g := max_lt_iff.2 ⟨hdeg', EuclideanDomain.mod_lt _ hg⟩
    have hq' : q' - f / g = 0 := by
      by_contra hq0
      have hdegmul : degree g ≤ degree (g * (q' - f / g)) := degree_le_mul_left _ hq0
      have : degree g ≤ degree (r' - f % g) := by simpa [h₂] using hdegmul
      exact (not_le_of_gt h₃) this
    have hq : q' = f / g := sub_eq_zero.mp hq'
    have hr : r' = f % g := by
      have hdecomp' : f = g * (f / g) + r' := by simpa [hq] using hdecomp
      have hs : g * (f / g) + r' = g * (f / g) + f % g := hdecomp'.symm.trans hstd
      exact add_left_cancel hs
    exact ⟨hq.symm, hr.symm⟩

/-
Used theorem names explicitly mentioned in the proof above (reduced to most relevant):
- EuclideanDomain.mod_add_div
- EuclideanDomain.mod_lt
- Polynomial.degree_eq_bot
- bot_lt_iff_ne_bot
- Polynomial.degree_sub_le
- max_lt_iff
- Polynomial.degree_le_mul_left
-/

/- Statements of the listed theorems -/
-- theorem EuclideanDomain.mod_add_div : {R : Type u} [EuclideanDomain R] (a b : R) : a % b + b * (a / b) = a

-- theorem EuclideanDomain.mod_lt : {R : Type u} [EuclideanDomain R] (a : R) {b : R} : b ≠ 0 → EuclideanDomain.r (a % b) b

-- theorem Polynomial.degree_eq_bot : {R : Type u} [Semiring R] {p : Polynomial R} : p.degree = ⊥ ↔ p = 0

-- theorem bot_lt_iff_ne_bot : {α : Type u} [PartialOrder α] [OrderBot α] {a : α} : ⊥ < a ↔ a ≠ ⊥

-- theorem Polynomial.degree_sub_le : {R : Type u} [Ring R] (p q : Polynomial R) : (p - q).degree ≤ p.degree ⊔ q.degree

-- theorem max_lt_iff : {α : Type u} [LinearOrder α] {a b c : α} : a ⊔ b < c ↔ a < c ∧ b < c

-- theorem Polynomial.degree_le_mul_left : {R : Type u} [Semiring R] [NoZeroDivisors R] {q : Polynomial R} (p : Polynomial R)
--   (hq : q ≠ 0) : p.degree ≤ (p * q).degree

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `EuclideanDomain.mod_add_div`
-- Source: .lake/packages/mathlib/Mathlib/Data/Nat/Defs.lean:1067
example {R : Type*} [EuclideanDomain R] (a b : R) : a % b + a / b * b = a := by
  simpa [mul_comm] using (EuclideanDomain.mod_add_div a b)

-- Uses `EuclideanDomain.mod_lt`
-- Source: .lake/packages/mathlib/Mathlib/Data/List/Rotate.lean:224
example {R : Type*} [EuclideanDomain R] (a b : R) (hb : b ≠ 0) :
    EuclideanDomain.r (a % b) b := by
  exact EuclideanDomain.mod_lt a hb

-- Uses `Polynomial.degree_eq_bot`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/Polynomial/Degree/Definitions.lean:368
example {R : Type*} [Semiring R] (p : Polynomial R) : p.degree = ⊥ ↔ p = 0 := by
  exact Polynomial.degree_eq_bot

-- Uses `bot_lt_iff_ne_bot`
-- Source: .lake/packages/mathlib/Mathlib/Order/CompleteLattice.lean:887
example {α : Type*} [PartialOrder α] [OrderBot α] {a : α} : ⊥ < a ↔ a ≠ ⊥ := by
  exact bot_lt_iff_ne_bot

-- Uses `Polynomial.degree_sub_le`
-- Source: .lake/packages/mathlib/Mathlib/RingTheory/Polynomial/Wronskian.lean:85
example {R : Type*} [CommRing R] {a b : R[X]} :
    (wronskian a b).degree ≤ max (a * derivative b).degree (derivative a * b).degree := by
  exact Polynomial.degree_sub_le _ _

-- Uses `max_lt_iff`
-- Source: .lake/packages/mathlib/Mathlib/Order/Interval/Set/Basic.lean:1399
example {α : Type*} [LinearOrder α] {a b c : α} : max a b < c ↔ a < c ∧ b < c := by
  exact max_lt_iff

-- Uses `Polynomial.degree_le_mul_left`
-- Source: .lake/packages/mathlib/Mathlib/Algebra/Polynomial/Degree/Domain.lean:65
example {R : Type*} [Semiring R] [NoZeroDivisors R] {p q : R[X]}
    (h1 : p ∣ q) (h2 : q ≠ 0) : p.degree ≤ q.degree := by
  rcases h1 with ⟨r, rfl⟩
  rw [mul_ne_zero_iff] at h2
  exact Polynomial.degree_le_mul_left p h2.2
