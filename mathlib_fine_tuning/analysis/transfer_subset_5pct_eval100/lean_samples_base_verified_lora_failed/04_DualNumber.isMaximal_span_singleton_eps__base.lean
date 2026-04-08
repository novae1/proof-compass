import Mathlib

namespace DualNumber
variable {R : Type*}
open TrivSqZeroExt
section Field
variable {K : Type*}

lemma manual_isMaximal_span_singleton_eps [DivisionRing K] :
    (Ideal.span {ε} : Ideal K[ε]).IsMaximal := by
  apply?
  <;> simp_all [Ideal.span_singleton_eq_bot, Ideal.mem_span_singleton, Ideal.IsMaximal]
  <;> exact ⟨fun h => by simp_all [ε, TrivSqZeroExt.mk, TrivSqZeroExt.re, TrivSqZeroExt.im]
    , fun h => by simp_all [ε, TrivSqZeroExt.mk, TrivSqZeroExt.re, TrivSqZeroExt.im]⟩
end Field
end DualNumber
