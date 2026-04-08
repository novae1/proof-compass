import Mathlib

namespace DualNumber
variable {R : Type*}
open TrivSqZeroExt
section Field
variable {K : Type*}

lemma manual_isMaximal_span_singleton_eps [DivisionRing K] :
    (Ideal.span {ε} : Ideal K[ε]).IsMaximal := by
  rw [← isMaximal_iff_isMaximal_span_singleton_eps]
  exact isMaximal_span_singleton_eps
end Field
end DualNumber

-- Verification errors from held-out REPL check:
-- Error 1: unknown identifier 'isMaximal_iff_isMaximal_span_singleton_eps'
-- Error 2: tactic 'rewrite' failed, equality or iff proof expected
--     ?m.9981
--   K : Type u_2
--   inst✝ : DivisionRing K
--   ⊢ (Ideal.span {ε}).IsMaximal
