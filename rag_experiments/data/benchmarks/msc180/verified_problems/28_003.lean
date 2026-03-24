import Mathlib

open MeasureTheory Metric Set

variable {d : ℕ}

theorem outer_measure_additive_of_separated {E F : Set (Fin d → ℝ)}
    (h : ∃ δ > 0, ∀ x ∈ E, ∀ y ∈ F, δ ≤ dist x y) :
    MeasureTheory.OuterMeasure.measureOf (MeasureTheory.volume.toOuterMeasure) (E ∪ F) =
      MeasureTheory.OuterMeasure.measureOf (MeasureTheory.volume.toOuterMeasure) E +
        MeasureTheory.OuterMeasure.measureOf (MeasureTheory.volume.toOuterMeasure) F := by
  rcases h with ⟨δ, hδpos, hδ⟩
  have hsep : IsMetricSeparated E F := by
    refine ⟨ENNReal.ofReal δ, ne_of_gt ((ENNReal.ofReal_pos).2 hδpos), ?_⟩
    intro x hx y hy
    have hxy : δ ≤ dist x y := hδ x hx y hy
    simpa [edist_dist] using (ENNReal.ofReal_le_ofReal hxy)
  have hmetric : ((MeasureTheory.volume : MeasureTheory.Measure (Fin d → ℝ)).toOuterMeasure).IsMetric := by
    have hH :
        ((MeasureTheory.Measure.hausdorffMeasure (X := Fin d → ℝ) (d := (d : ℝ))).toOuterMeasure).IsMetric := by
      rw [MeasureTheory.Measure.hausdorffMeasure, MeasureTheory.Measure.mkMetric_toOuterMeasure]
      simpa [MeasureTheory.OuterMeasure.mkMetric] using
        (MeasureTheory.OuterMeasure.mkMetric'_isMetric (X := Fin d → ℝ)
          (m := fun s : Set (Fin d → ℝ) => EMetric.diam s ^ (d : ℝ)))
    have hEq :
        (MeasureTheory.Measure.hausdorffMeasure (X := Fin d → ℝ) (d := (d : ℝ))) =
          MeasureTheory.volume := by
      simpa using (MeasureTheory.hausdorffMeasure_pi_real (ι := Fin d))
    simpa [hEq] using hH
  simpa using hmetric E F hsep

/-
Used theorem names explicitly mentioned in the proof above (reduced to most relevant):
- MeasureTheory.Measure.mkMetric_toOuterMeasure
- MeasureTheory.OuterMeasure.mkMetric'_isMetric
- MeasureTheory.hausdorffMeasure_pi_real
-/

/- Statements of the listed theorems -/
-- theorem MeasureTheory.Measure.mkMetric_toOuterMeasure : {X : Type u_2} [EMetricSpace X] [MeasurableSpace X] [BorelSpace X]
--   (m : ENNReal → ENNReal) : (MeasureTheory.Measure.mkMetric m).toOuterMeasure = MeasureTheory.OuterMeasure.mkMetric m

-- theorem MeasureTheory.OuterMeasure.mkMetric'_isMetric : {X : Type u_2} [EMetricSpace X] (m : Set X → ENNReal) :
--   (MeasureTheory.OuterMeasure.mkMetric' m).IsMetric

-- theorem MeasureTheory.hausdorffMeasure_pi_real : {ι : Type u_4} [Fintype ι] :
--   MeasureTheory.Measure.hausdorffMeasure ↑(Fintype.card ι) = MeasureTheory.volume

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `MeasureTheory.Measure.mkMetric_toOuterMeasure`
-- Source: .lake/packages/mathlib/Mathlib/MeasureTheory/Measure/Hausdorff.lean:452
example {X : Type*} [EMetricSpace X] [MeasurableSpace X] [BorelSpace X] :
    (MeasureTheory.Measure.mkMetric (fun _ => (⊤ : ENNReal)) : MeasureTheory.Measure X) = ⊤ := by
  apply MeasureTheory.Measure.toOuterMeasure_injective
  rw [MeasureTheory.Measure.mkMetric_toOuterMeasure, MeasureTheory.OuterMeasure.mkMetric_top,
    MeasureTheory.Measure.toOuterMeasure_top]

-- If `m₁ d ≤ m₂ d` for `d < ε` for some `ε > 0` (we use `≤ᶠ[𝓝[≥] 0]` to state this), then
-- `mkMetric m₁ hm₁ ≤ mkMetric m₂ hm₂`.

-- Uses `MeasureTheory.OuterMeasure.mkMetric'_isMetric`
-- Source: .lake/packages/mathlib/Mathlib/MeasureTheory/Measure/Hausdorff.lean:304
example {X : Type*} [EMetricSpace X] (m : Set X → ENNReal) :
    (MeasureTheory.OuterMeasure.mkMetric' m).IsMetric := by
  simpa using MeasureTheory.OuterMeasure.mkMetric'_isMetric (X := X) m

-- Uses `MeasureTheory.hausdorffMeasure_pi_real`
-- Source: .lake/packages/mathlib/Mathlib/MeasureTheory/Measure/Hausdorff.lean:999
example : (μH[1] : Measure ℝ) = volume := by
  rw [← (volume_preserving_funUnique Unit ℝ).map_eq,
    ← (hausdorffMeasure_measurePreserving_funUnique Unit ℝ 1).map_eq,
    ← MeasureTheory.hausdorffMeasure_pi_real, Fintype.card_unit, Nat.cast_one]

-- In the space `ℝ × ℝ`, the Hausdorff measure coincides exactly with the Lebesgue measure.
