import Mathlib

open Metric Set

theorem euclidean_ball_convex {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    (c : E) (r : ℝ) (hr : 0 ≤ r) :
    Convex ℝ (ball c r) := by
  simpa using convex_ball c r

/-
Used theorem names explicitly mentioned in the proof above:
- convex_ball
-/

/- Statements of the listed theorems -/
-- theorem convex_ball : {E : Type u_1} [SeminormedAddCommGroup E] [NormedSpace ℝ E] (a : E) (r : ℝ) :
--   Convex ℝ (Metric.ball a r)

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `convex_ball`
-- Source: .lake/packages/mathlib/Mathlib/NumberTheory/NumberField/CanonicalEmbedding/ConvexBody.lean:185
example {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] (x : E) (r : ℝ) :
    Convex ℝ (Metric.ball x r) := by
  exact convex_ball _ _
