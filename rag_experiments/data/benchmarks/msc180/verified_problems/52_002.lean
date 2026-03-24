import Mathlib

theorem diameter_achieved_by_hull_vertices {n : ℕ} {S : Set (EuclideanSpace ℝ (Fin n))}
    (h_finite : Set.Finite S) (h_nonempty : S.Nonempty) :
    ∃ x ∈ (convexHull ℝ S).extremePoints ℝ, ∃ y ∈ (convexHull ℝ S).extremePoints ℝ,
      dist x y = Metric.diam S := by
  let K : Set (EuclideanSpace ℝ (Fin n)) := convexHull ℝ S
  let T : Set (EuclideanSpace ℝ (Fin n)) := K.extremePoints ℝ

  have hS_bdd : Bornology.IsBounded S := h_finite.isBounded
  have hKcompact : IsCompact K := by
    simpa [K] using h_finite.isCompact_convexHull
  have hKconv : Convex ℝ K := by
    simpa [K] using convex_convexHull ℝ S

  have hT_nonempty : T.Nonempty := by
    have hK_nonempty : K.Nonempty := by
      exact h_nonempty.mono (subset_convexHull ℝ S)
    simpa [T, K] using hKcompact.extremePoints_nonempty hK_nonempty

  have hT_subset_S : T ⊆ S := by
    simpa [T, K] using (extremePoints_convexHull_subset (𝕜 := ℝ) (A := S))
  have hT_finite : T.Finite := h_finite.subset hT_subset_S
  have hT_bdd : Bornology.IsBounded T := hT_finite.isBounded

  have hT_closed_hull : IsClosed (convexHull ℝ T) := by
    exact hT_finite.isClosed_convexHull
  have hK_eq_hullT : K = convexHull ℝ T := by
    have hcl : closure (convexHull ℝ T) = K := by
      simpa [T, K] using (closure_convexHull_extremePoints (s := K) hKcompact hKconv)
    have hcl' : closure (convexHull ℝ T) = convexHull ℝ T := hT_closed_hull.closure_eq
    have : convexHull ℝ T = K := by
      rw [← hcl', hcl]
    simpa using this.symm

  have hdiamS_le_hdiamT : Metric.diam S ≤ Metric.diam T := by
    refine Metric.diam_le_of_forall_dist_le Metric.diam_nonneg ?_
    intro x hx y hy
    have hxK : x ∈ K := (subset_convexHull ℝ S) hx
    have hyK : y ∈ K := (subset_convexHull ℝ S) hy
    have hxHullT : x ∈ convexHull ℝ T := by simpa [hK_eq_hullT] using hxK
    have hyHullT : y ∈ convexHull ℝ T := by simpa [hK_eq_hullT] using hyK
    rcases convexHull_exists_dist_ge2 (s := T) (t := T) hxHullT hyHullT with
      ⟨x', hx', y', hy', hxy⟩
    exact le_trans hxy (Metric.dist_le_diam_of_mem hT_bdd hx' hy')

  have hdiamT_le_hdiamS : Metric.diam T ≤ Metric.diam S :=
    Metric.diam_mono hT_subset_S hS_bdd
  have hdiam_eq : Metric.diam T = Metric.diam S :=
    le_antisymm hdiamT_le_hdiamS hdiamS_le_hdiamT

  let F : Finset (EuclideanSpace ℝ (Fin n)) := hT_finite.toFinset
  have hF_nonempty : F.Nonempty := by
    rcases hT_nonempty with ⟨x, hx⟩
    exact ⟨x, hT_finite.mem_toFinset.mpr hx⟩

  obtain ⟨p, hp_mem, hp_max⟩ :=
    Finset.exists_max_image (F.product F)
      (fun q : (EuclideanSpace ℝ (Fin n)) × (EuclideanSpace ℝ (Fin n)) => dist q.1 q.2)
      (Finset.Nonempty.product hF_nonempty hF_nonempty)

  have hp1T : p.1 ∈ T := hT_finite.mem_toFinset.mp ((Finset.mem_product.mp hp_mem).1)
  have hp2T : p.2 ∈ T := hT_finite.mem_toFinset.mp ((Finset.mem_product.mp hp_mem).2)

  have hdiamT_le : Metric.diam T ≤ dist p.1 p.2 := by
    refine Metric.diam_le_of_forall_dist_le dist_nonneg ?_
    intro a ha b hb
    have haF : a ∈ F := hT_finite.mem_toFinset.mpr ha
    have hbF : b ∈ F := hT_finite.mem_toFinset.mpr hb
    have hab_mem : (a, b) ∈ F.product F := Finset.mem_product.mpr ⟨haF, hbF⟩
    exact hp_max (a, b) hab_mem

  have hle : dist p.1 p.2 ≤ Metric.diam T :=
    Metric.dist_le_diam_of_mem hT_bdd hp1T hp2T
  have hdist_eq_diamT : dist p.1 p.2 = Metric.diam T := le_antisymm hle hdiamT_le

  refine ⟨p.1, ?_, p.2, ?_, ?_⟩
  · simpa [T, K] using hp1T
  · simpa [T, K] using hp2T
  · simpa [hdiam_eq] using hdist_eq_diamT

/-
Used theorem names explicitly mentioned in the proof above (reduced to most relevant):
- extremePoints_convexHull_subset
- closure_convexHull_extremePoints
- Metric.diam_le_of_forall_dist_le
- convexHull_exists_dist_ge2
- Metric.dist_le_diam_of_mem
- Metric.diam_mono
- Finset.exists_max_image
-/

/- Statements of the listed theorems -/
-- theorem extremePoints_convexHull_subset : {𝕜 : Type u_1} {E : Type u_2} [LinearOrderedRing 𝕜] [AddCommGroup E]
--   [Module 𝕜 E] [DenselyOrdered 𝕜] [NoZeroSMulDivisors 𝕜 E] {A : Set E} : Set.extremePoints 𝕜 ((convexHull 𝕜) A) ⊆ A

-- theorem closure_convexHull_extremePoints : {E : Type u_1} [AddCommGroup E] [Module ℝ E] [TopologicalSpace E] [T2Space E]
--   [TopologicalAddGroup E] [ContinuousSMul ℝ E] [LocallyConvexSpace ℝ E] {s : Set E} (hscomp : IsCompact s)
--   (hAconv : Convex ℝ s) : closure ((convexHull ℝ) (Set.extremePoints ℝ s)) = s

-- theorem Metric.diam_le_of_forall_dist_le : {α : Type u} [PseudoMetricSpace α] {s : Set α} {C : ℝ} (h₀ : 0 ≤ C)
--   (h : ∀ x ∈ s, ∀ y ∈ s, dist x y ≤ C) : Metric.diam s ≤ C

-- theorem convexHull_exists_dist_ge2 : {E : Type u_1} [SeminormedAddCommGroup E] [NormedSpace ℝ E] {s t : Set E} {x y : E}
--   (hx : x ∈ (convexHull ℝ) s) (hy : y ∈ (convexHull ℝ) t) : ∃ x' ∈ s, ∃ y' ∈ t, dist x y ≤ dist x' y'

-- theorem Metric.dist_le_diam_of_mem : {α : Type u} [PseudoMetricSpace α] {s : Set α} {x y : α} (h : Bornology.IsBounded s)
--   (hx : x ∈ s) (hy : y ∈ s) : dist x y ≤ Metric.diam s

-- theorem Metric.diam_mono : {α : Type u} [PseudoMetricSpace α] {s t : Set α} (h : s ⊆ t) (ht : Bornology.IsBounded t) :
--   Metric.diam s ≤ Metric.diam t

-- theorem Finset.exists_max_image : {α : Type u_2} {β : Type u_3} [LinearOrder α] (s : Finset β) (f : β → α)
--   (h : s.Nonempty) : ∃ x ∈ s, ∀ x' ∈ s, f x' ≤ f x

/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/

-- Uses `extremePoints_convexHull_subset`
-- Source: .lake/packages/mathlib/Mathlib/Analysis/Convex/Extreme.lean:256
example {n : ℕ} (A : Set (EuclideanSpace ℝ (Fin n))) :
    (convexHull ℝ A).extremePoints ℝ ⊆ A := by
  simpa using (extremePoints_convexHull_subset (𝕜 := ℝ) (A := A))

-- Uses `closure_convexHull_extremePoints`
-- Source: .lake/packages/mathlib/Mathlib/Analysis/Convex/KreinMilman.lean:92
example {n : ℕ} (s : Set (EuclideanSpace ℝ (Fin n))) (hscomp : IsCompact s) (hconv : Convex ℝ s) :
    closure (convexHull ℝ (s.extremePoints ℝ)) = s := by
  simpa using closure_convexHull_extremePoints (s := s) hscomp hconv

-- Uses `Metric.diam_le_of_forall_dist_le`
-- Source: .lake/packages/mathlib/Mathlib/Topology/Instances/ENNReal.lean:1239
example {α : Type*} [PseudoMetricSpace α] (s : Set α) {C : ℝ}
    (h0 : 0 ≤ C) (h : ∀ x ∈ s, ∀ y ∈ s, dist x y ≤ C) : Metric.diam s ≤ C := by
  exact Metric.diam_le_of_forall_dist_le h0 h

-- Uses `convexHull_exists_dist_ge2`
-- Source: .lake/packages/mathlib/Mathlib/Analysis/Convex/Normed.lean:92
example {E : Type*} [SeminormedAddCommGroup E] [NormedSpace ℝ E]
    {s t : Set E} {x y : E} (hx : x ∈ convexHull ℝ s) (hy : y ∈ convexHull ℝ t) :
    ∃ x' ∈ s, ∃ y' ∈ t, dist x y ≤ dist x' y' := by
  exact convexHull_exists_dist_ge2 hx hy

-- Uses `Metric.dist_le_diam_of_mem`
-- Source: .lake/packages/mathlib/Mathlib/Topology/MetricSpace/Lipschitz.lean:135
example {α : Type*} [PseudoMetricSpace α] {K : NNReal} {f : α → α}
    (hf : LipschitzWith K f) (s : Set α) (hs : Bornology.IsBounded s) :
    Metric.diam (f '' s) ≤ K * Metric.diam s := by
  refine Metric.diam_le_of_forall_dist_le (mul_nonneg K.coe_nonneg Metric.diam_nonneg) ?_
  rintro _ ⟨x, hx, rfl⟩ _ ⟨y, hy, rfl⟩
  exact hf.dist_le_mul_of_le (Metric.dist_le_diam_of_mem hs hx hy)

-- Uses `Metric.diam_mono`
-- Source: .lake/packages/mathlib/Mathlib/Topology/Instances/ENNReal.lean:1215
example {α : Type*} [PseudoMetricSpace α] {s t : Set α}
    (h : s ⊆ t) (ht : Bornology.IsBounded t) : Metric.diam s ≤ Metric.diam t := by
  exact Metric.diam_mono h ht

-- Uses `Finset.exists_max_image`
-- Source: .lake/packages/mathlib/Mathlib/Data/Fintype/Lattice.lean:56
example {α β : Type*} [Finite α] [Nonempty α] [LinearOrder β] (f : α → β) :
    ∃ x₀ : α, ∀ x, f x ≤ f x₀ := by
  cases nonempty_fintype α
  simpa using Finset.exists_max_image Finset.univ f Finset.univ_nonempty
