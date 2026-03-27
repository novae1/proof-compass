# MSC-180 v2 Hallucination Casebook For Iterative RAG

## Purpose

This is a small manual casebook for the first iterative-RAG pass.

The goal is not to automate anything yet. The goal is to inspect a few high-signal
cases where:

- the `A` no-hint condition produced theorem-like unresolved names,
- and a hint condition (`B` theorem statements or `C` theorem statements + examples)
  did better on the same problem.

These are the best first cases for testing whether hallucinated theorem names can
be turned into useful retrieval queries over Mathlib.

## Source Artifacts

Main run used for this first pass:
- `rag_experiments/outputs/msc180/v2/20260301_msc180-v2_deepseekv2_7b_lean4-15_verified.json`

Specs:
- `rag_experiments/data/specs/msc180_v2_A_spec.json`
- `rag_experiments/data/specs/msc180_v2_B_spec.json`
- `rag_experiments/data/specs/msc180_v2_C_spec.json`

## Selection Rule

A case is included if:
- `A` no-hint has at least one unresolved theorem-like identifier,
- and `B` or `C` has strictly more successful attempts than `A`,
- using the later `20260301` verified run.

This first pass intentionally stays small.

## How To Use This File

For each case:
- try semantic search with the hallucinated theorem names,
- try semantic search with the formal statement,
- try a combined query,
- note whether the expected helpful theorem appears.

If this works often enough by eye, the next step is to implement the full
iterative loop.

## Case 1: `MSC-180_60_002`

### Benchmark outcomes
- `A` no-hint: `0/8`
- `B` theorem statements: `3/8`
- `C` theorem statements + examples: `1/8`

### Formal statement
```lean
 theorem weierstrass_approximation (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
     (ε : ℝ) (hε : ε > 0) :
     ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε := by
   sorry
```

### Natural-language proof
- Not present in the stored v2 spec.

### Hallucinated names in no-hint failures
- `abs_sub_self`
- `exists_poly_lt`
- `exists_polynomial_`
- `exists_polynomial_onic_forall_Icc_norm_lt`

### Representative no-hint failure
Attempt: `2`

Errors:
- `linarith failed to find a contradiction`
- `unknown identifier 'abs_sub_self'`

Snippet:
```lean
 theorem weierstrass_approximation (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
     (ε : ℝ) (hε : ε > 0) :
     ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε := by
   obtain ⟨n, hn⟩ := exists_nat_gt (1 / ε)
   have hn' : 0 < ε := by linarith
   have hn'' : 0 < n := by linarith
   -- Use the Stone-Weierstrass theorem to find a polynomial approximation
```

### Expected helpful theorem from hints
Primary expected theorem:
- `exists_polynomial_near_of_continuousOn`

`B` hint theorem:
```lean
 theorem exists_polynomial_near_of_continuousOn :
   (a b : ℝ) (f : ℝ → ℝ) (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
   ∃ p, ∀ x ∈ Set.Icc a b, |Polynomial.eval x p - f x| < ε
```

### Manual retrieval notes
- Best query candidates:
  - `exists_polynomial_onic_forall_Icc_norm_lt`
  - `exists_poly_lt`
  - full theorem statement
  - hallucinated name + theorem statement
- Observation target:
  - does search recover `exists_polynomial_near_of_continuousOn` or a very close equivalent?

## Case 2: `MSC-180_26_002`

### Benchmark outcomes
- `A` no-hint: `6/8`
- `B` theorem statements: `8/8`
- `C` theorem statements + examples: `5/8`

### Formal statement
```lean
 theorem exists_sup_of_bddAbove {A : Set ℝ} (hne : A.Nonempty) (hbd : BddAbove A) :
     ∃ s : ℝ, IsLUB A s := by
   sorry
```

### Natural-language proof
- Not present in the stored v2 spec.

### Hallucinated names in no-hint failures
- `exists_sup_of_bddAbove'`

### Representative no-hint failure
Attempt: `4`

Errors:
- `unknown identifier 'exists_sup_of_bddAbove''`

Snippet:
```lean
 theorem exists_sup_of_bddAbove {A : Set ℝ} (hne : A.Nonempty) (hbd : BddAbove A) :
     ∃ s : ℝ, IsLUB A s := by
   apply ExistsUnique.exists
   exact exists_sup_of_bddAbove' hne hbd
   <;> simp_all [IsLUB, IsLeast]
```

### Expected helpful theorem from hints
Primary expected theorem:
- `Real.exists_isLUB`

`B` hint theorem:
```lean
 theorem Real.exists_isLUB : {s : Set ℝ} (hne : s.Nonempty) (hbdd : BddAbove s) :
   ∃ x, IsLUB s x
```

### Manual retrieval notes
- Best query candidates:
  - `exists_sup_of_bddAbove'`
  - full theorem statement
  - hallucinated name + theorem statement
- Observation target:
  - does search recover `Real.exists_isLUB` near the top?

## Case 3: `MSC-180_05_003`

### Benchmark outcomes
- `A` no-hint: `0/8`
- `B` theorem statements: `2/8`
- `C` theorem statements + examples: `2/8`

### Formal statement
```lean
 theorem excedance_coexcedance_dual {n : ℕ} (π : Perm (Fin n)) :
     (excedances π).card = (coexcedances π⁻¹).card := by
   sorry
```

### Natural-language proof
- Not present in the stored v2 spec.

### Hallucinated names in no-hint failures
- `card_univ` (appears twice)

### Representative no-hint failure
Attempt: `1`

Errors:
- `unknown identifier 'card_univ'`
- `tactic 'rewrite' failed, equality or iff proof expected`

Snippet:
```lean
 theorem excedance_coexcedance_dual {n : ℕ} (π : Perm (Fin n)) :
     (excedances π).card = (coexcedances π⁻¹).card := by
   simp [excedances, coexcedances, mul_comm]
   <;> rw [← card_univ]
   <;>
     exact
       Finset.card_congr (fun i _ => π⁻¹ i)
```

### Expected helpful theorems from hints
Primary expected theorems:
- `Finset.mem_image`
- `Finset.card_image_of_injective`

`B` hint theorems:
```lean
 theorem Finset.mem_image : {α : Type u_1} {β : Type u_2} [DecidableEq β]
   {f : α → β} {s : Finset α} {b : β} :
   b ∈ Finset.image f s ↔ ∃ a ∈ s, f a = b

 theorem Finset.card_image_of_injective : {α : Type u_1} {β : Type u_2}
   {f : α → β} [DecidableEq β] (s : Finset α)
   (H : Function.Injective f) : (Finset.image f s).card = s.card
```

### Manual retrieval notes
- Best query candidates:
  - `card_univ`
  - full theorem statement
  - hallucinated name + theorem statement
- Observation target:
  - does search retrieve image/cardinality lemmas that are actually useful here,
    even if it does not recover the exact hint pair immediately?

## Case 4: `MSC-180_14_001`

### Benchmark outcomes
- `A` no-hint: `7/8`
- `B` theorem statements: `8/8`
- `C` theorem statements + examples: `7/8`

### Formal statement
```lean
 theorem kernel_subgroup_and_isomorphism {G H : Type*} [AddCommGroup G] [AddCommGroup H]
     (φ : G →+ H) :
     φ.ker = {g | φ g = 0} ∧ (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H)) := by
   sorry
```

### Natural-language proof
- Not present in the stored v2 spec.

### Hallucinated names in no-hint failures
- `quotientAddGroup.quotientKerEquivOfSurjective`

### Representative no-hint failure
Attempt: `8`

Errors:
- `unknown identifier 'quotientAddGroup.quotientKerEquivOfSurjective'`

Snippet:
```lean
 theorem kernel_subgroup_and_isomorphism {G H : Type*} [AddCommGroup G] [AddCommGroup H]
     (φ : G →+ H) :
     φ.ker = {g | φ g = 0} ∧ (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H)) := by
   refine ⟨?_, ?_⟩
   · ext
     simp [AddMonoidHom.mem_ker]
   · intro h
     exact ⟨(quotientAddGroup.quotientKerEquivOfSurjective φ h)⟩
```

### Expected helpful theorem from hints
Primary expected theorem:
- `QuotientAddGroup.quotientKerEquivOfSurjective`

`B` hint theorem:
```lean
 theorem QuotientAddGroup.quotientKerEquivOfSurjective :
   {G : Type u} [AddGroup G] {H : Type v} [AddGroup H] (φ : G →+ H)
   (hφ : Function.Surjective ⇑φ) : G ⧸ φ.ker ≃+ H
```

### Manual retrieval notes
- Best query candidates:
  - `quotientAddGroup.quotientKerEquivOfSurjective`
  - full theorem statement
  - hallucinated name + theorem statement
- Observation target:
  - does search recover the exact theorem despite the namespace capitalization error?

## Expansion Candidates From The Earlier `20260217` Run

These are reasonable next cases once the first four are inspected:

- `MSC-180_28_003`
  - `A/B/C = 0/2/0`
  - hallucinated name: `dist_same`
- `MSC-180_52_002`
  - `A/B/C = 0/1/0`
  - hallucinated names include: `diam`, `Metric.diam_convexHull`, `isCompact_convexHull_of_finite`
- `MSC-180_65_003`
  - `A/B/C = 0/1/2`
  - hallucinated names include: `norm_eq_abs`, `hc`
- `MSC-180_90_001`
  - `A/B/C = 0/1/0`
  - hallucinated name: `convex_iff_forall_pos_mem_segment`

## Current Decision Gate

If manual retrieval often surfaces the expected helpful theorem, or something
close enough to play the same role, then the next step is to implement the
full iterative loop:

- generate
- detect unresolved theorem-like names
- retrieve similar real theorems
- retry with retrieved context

If manual retrieval mostly fails even on these curated cases, then the first
thing to rethink is query construction and theorem indexing, not the iterative
loop itself.

## Search Scratchpad

### abs_sub_self

#### LeanExplore
lemma abs_sub_self (a : A) (ha : IsSelfAdjoint a := by cfc_tac) : abs a - a = 2 • a⁻ := by
  simpa [two_smul] using
    congr($(CFC.posPart_add_negPart a) - $(CFC.posPart_sub_negPart a)).symm
Gemini 3.0 Flash:
Difference Between the Absolute Value and a Self-Adjoint Element. For any self-adjoint element 
 in an algebra admitting a continuous functional calculus, the difference between its absolute value and itself is equal to twice its negative part, i.e., 
.

Find similar
View Dependencies ▼
abs_mul_self
In: Mathlib.Algebra.Order.Ring.Abs

Lean Code:
lemma abs_mul_self (a : α) : |a * a| = a * a := by simp
Gemini 3.0 Flash:
Absolute Value of a Square. For any element 
 in a linearly ordered ring, the absolute value of the product of 
 with itself is equal to the product of 
 with itself.

Find similar
View Dependencies ▼
abs_sub_sq
In: Mathlib.Algebra.Order.Ring.Abs

Lean Code:
theorem abs_sub_sq (a b : α) : |a - b| * |a - b| = a * a + b * b - (1 + 1) * a * b := by
  rw [abs_mul_abs_self]
  simp only [mul_add, add_comm, add_left_comm, mul_comm, sub_eq_add_neg, mul_one, mul_neg,
    neg_add_rev, neg_neg, add_assoc]
Gemini 3.0 Flash:
Square of the Absolute Difference. For any two elements 
 and 
 in a linearly ordered commutative ring, the product of the absolute value of their difference with itself is equal to 
.

Find similar
View Dependencies ▼
sub_self
In: Mathlib.Algebra.Group.Defs

Lean Code:
@[to_additive (attr := simp) sub_self]
theorem div_self' (a : G) : a / a = 1 := by rw [div_eq_mul_inv, mul_inv_cancel a]
Gemini 3.0 Flash:
Subtraction of an Element from Itself. For any element 
 in an additive group, the result of subtracting 
 from itself is the additive identity 
.

Find similar
View Dependencies ▼
ISize.sub_self
In: Init.Data.SInt.Lemmas

Lean Code:
@[simp] protected theorem ISize.sub_self (a : ISize) : a - a = 0 := ISize.toBitVec_inj.1 (BitVec.sub_self _)
Gemini 3.0 Flash:
Self-Subtraction of Platform-Sized Signed Integers. For any platform-sized signed integer 
, the result of subtracting 
 from itself is zero.

Find similar
View Dependencies ▼
#### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem abs_sub (a b : α) : |a - b| ≤ |a| + |b| := by
  rw [sub_eq_add_neg, ← abs_neg b]
  exact abs_add a _
Doc
Copy
👍
👎
For any elements 
a
a and 
b
b in a linearly ordered additive commutative group 
α
α, the absolute value of their difference satisfies the inequality 
∣
a
−
b
∣
≤
∣
a
∣
+
∣
b
∣
∣a−b∣≤∣a∣+∣b∣.
Copy
2	
theorem abs_one : |(1 : α)| = 1 := abs_of_pos zero_lt_one
Doc
Copy
👍
👎
In any linearly ordered ring 
α
α, the absolute value of the multiplicative identity 
1
1 is equal to 
1
1, i.e., 
∣
1
∣
=
1
∣1∣=1.
Copy
3	
theorem abs_sub_abs_le_abs_sub (a b : α) : |a| - |b| ≤ |a - b| :=
  sub_le_iff_le_add.2 <|
    calc
      |a| = |a - b + b| := by rw [sub_add_cancel]
      _ ≤ |a - b| + |b| := abs_add _ _
Doc
Copy
👍
👎
For any elements 
a
a and 
b
b in a linearly ordered additive commutative group 
α
α, the difference of their absolute values is bounded by the absolute value of their difference, i.e., 
∣
a
∣
−
∣
b
∣
≤
∣
a
−
b
∣
∣a∣−∣b∣≤∣a−b∣.
Copy
4	
theorem abs_eq_self : |a| = a ↔ 0 ≤ a := by
  rw [abs_eq_max_neg, max_eq_left_iff, neg_le_self_iff]
Doc
Copy
👍
👎
For any element 
a
a in a linearly ordered additive commutative group, the absolute value of 
a
a equals 
a
a if and only if 
0
≤
a
0≤a. That is, 
∣
a
∣
=
a
↔
0
≤
a
∣a∣=a↔0≤a.
Copy
5	
theorem le_of_abs_le (h : |a| ≤ b) : a ≤ b :=
  (abs_le.mp h).2
Doc
Copy
👍
👎
For any elements 
a
a and 
b
b in a linearly ordered additive commutative group, if the absolute value 
∣
a
∣
∣a∣ is less than or equal to 
b
b, then 
a
a is less than or equal to 
b
b.
Copy

### exists_poly_lt

#### LeanExplore
exists_pos_mul_lt
In: Mathlib.Algebra.Order.Field.Basic

Lean Code:
theorem exists_pos_mul_lt {a : α} (h : 0 < a) (b : α) : ∃ c : α, 0 < c ∧ b * c < a := by
  have : 0 < a / max (b + 1) 1 := div_pos h (lt_max_iff.2 (Or.inr zero_lt_one))
  refine ⟨a / max (b + 1) 1, this, ?_⟩
  rw [← lt_div_iff₀ this, div_div_cancel₀ h.ne']
  exact lt_max_iff.2 (Or.inl <| lt_add_one _)
...
Show all
Gemini 3.0 Flash:
Existence of a Positive Multiplier for Small Products. For any positive element 
 and any element 
 in a linearly ordered semifield, there exists a positive element 
 such that the product 
 is strictly less than 
.

Find similar
View Dependencies ▼
exists_pow_lt
In: Mathlib.Algebra.Order.Archimedean.Basic

Lean Code:
@[to_additive]
theorem exists_pow_lt {a : G} (ha : a < 1) (b : G) : ∃ n : ℕ, a ^ n < b :=
  (exists_lt_pow (one_lt_inv'.mpr ha) b⁻¹).imp <| by simp
Gemini 3.0 Flash:
Existence of a Power Less Than a Given Element. In a multiplicatively Archimedean linear ordered commutative group, for any element 
 and any element 
, there exists a natural number 
 such that 
.

Find similar
View Dependencies ▼
exists_int_lt
In: Mathlib.Algebra.Order.Archimedean.Basic

Lean Code:
theorem exists_int_lt (x : R) : ∃ n : ℤ, (n : R) < x :=
  let ⟨n, h⟩ := exists_int_gt (-x)
  ⟨-n, by rw [Int.cast_neg]; exact neg_lt.1 h⟩
Gemini 3.0 Flash:
Existence of a Smaller Integer. For any element 
 in an Archimedean strictly ordered ring, there exists an integer 
 such that 
.

Find similar
View Dependencies ▼
exists_rat_lt
In: Mathlib.Algebra.Order.Archimedean.Basic

Lean Code:
theorem exists_rat_lt (x : K) : ∃ q : ℚ, (q : K) < x :=
  let ⟨n, h⟩ := exists_int_lt x
  ⟨n, by rwa [Rat.cast_intCast]⟩
Gemini 3.0 Flash:
Existence of a Rational Lower Bound. For any element 
 in an Archimedean linear ordered field 
, there exists a rational number 
 such that its image under the canonical embedding into 
 is strictly less than 
.

Find similar
View Dependencies ▼
exists_pair_lt
In: Mathlib.Logic.Nontrivial.Basic

Lean Code:
theorem exists_pair_lt (α : Type*) [Nontrivial α] [LinearOrder α] : ∃ x y : α, x < y := by
  rcases exists_pair_ne α with ⟨x, y, hxy⟩
  cases lt_or_gt_of_ne hxy <;> exact ⟨_, _, ‹_›⟩
Gemini 3.0 Flash:
Existence of an Ordered Pair. In any nontrivial linearly ordered set, there exist two elements 
 and 
 such that 
.

Find similar
View Dependencies ▼
#### LeanFinder

Rank	Formal statement	Informal statement
1	
noncomputable def P : (Polynomial ℚ) := X ^ 3 - Polynomial.C 2
Doc
Copy
👍
👎
The polynomial 
P
(
X
)
P(X) is defined as 
X
3
−
2
X 
3
 −2 over the rational numbers 
Q
Q. This is a cubic polynomial with a leading term 
X
3
X 
3
  and a constant term 
−
2
−2.
Copy
2	
definition Poly (α : Type u) := { f : (α → ℕ) → ℤ // IsPoly f }
Doc
Copy
👍
👎
The type Poly α represents multivariate integer polynomial functions with variables indexed by type α. A function f : (α → ℕ) → ℤ belongs to Poly α if it satisfies the IsPoly predicate, meaning it can be expressed as a multivariate integer polynomial. This allows flexible representations of polynomials beyond just monomials and addition.
Copy
3	
theorem Poly.isPoly (f : Poly α) : IsPoly f := f.2
Doc
Copy
👍
👎
For any multivariate integer polynomial function 
f
 ⁣
:
Poly
 
α
f:Polyα, the predicate 
IsPoly
 
f
IsPolyf holds, meaning 
f
f is indeed a multivariate integer polynomial.
Copy
4	
definition Polynomial.eval : R → R[X] → R :=
  eval₂ (RingHom.id _)
Doc
Copy
👍
👎
The function 
eval
(
x
,
p
)
eval(x,p) evaluates the polynomial 
p
∈
R
[
X
]
p∈R[X] at the point 
x
∈
R
x∈R, defined as 
∑
e
a
e
⋅
x
e
∑ 
e
​
 a 
e
​
 ⋅x 
e
  where 
a
e
a 
e
​
  are the coefficients of 
p
p.
Copy
5	
theorem Polynomial.eval_C : (C a).eval x = a :=
  eval₂_C _ _
Doc
Copy
👍
👎
For any element 
a
a in a semiring 
R
R and any element 
x
∈
R
x∈R, the evaluation of the constant polynomial 
C
(
a
)
∈
R
[
X
]
C(a)∈R[X] at 
x
x equals 
a
a, i.e.,
(
C
(
a
)
)
.
eval
(
x
)
=
a
.
(C(a)).eval(x)=a.
Copy

### exists_polynomial_

#### LeanExplore
Polynomial
In: Mathlib.Algebra.Polynomial.Basic

Lean Code:
structure Polynomial (R : Type*) [Semiring R] where ofFinsupp ::
  toFinsupp : AddMonoidAlgebra R ℕ
Show all
Docstring:
Polynomial R is the type of univariate polynomials over R, denoted as R[X] within the Polynomial namespace.

Polynomials should be seen as (semi-)rings with the additional constructor X. The embedding from R is called C.

Gemini 3.0 Flash:
Univariate Polynomials. For a semiring 
, the type of univariate polynomials 
 is defined as the set of finitely supported functions from 
 to 
. This structure represents polynomials as an algebra where 
 denotes the embedding of constant coefficients from 
 and 
 represents the indeterminate variable.

Find similar
View Dependencies ▼
Polynomial.exists_partition_polynomial
In: Mathlib.NumberTheory.ClassNumber.AdmissibleCardPowDegree

Lean Code:
theorem exists_partition_polynomial (n : ℕ) {ε : ℝ} (hε : 0 < ε) {b : Fq[X]} (hb : b ≠ 0)
    (A : Fin n → Fq[X]) : ∃ t : Fin n → Fin (Fintype.card Fq ^ ⌈-log ε / log (Fintype.card Fq)⌉₊),
      ∀ i₀ i₁ : Fin n, t i₀ = t i₁ →
        (cardPowDegree (A i₁ % b - A i₀ % b) : ℝ) < cardPowDegree b • ε := by
  obtain ⟨t, ht⟩ := exists_partition_polynomial_aux n hε hb A
...
Show all
Docstring:
For all ε > 0, we can partition the remainders of any family of polynomials A into classes, where all remainders in a class are close together.

Gemini 3.0 Flash:
Partitioning Polynomial Remainders. For any finite field 
, any positive real number 
, and any non-zero polynomial 
, any finite family of polynomials 
 can be partitioned into a finite number of classes such that for any two indices 
 in the same class, the difference of their remainders modulo 
 is small. Specifically, there exists a labeling function 
 into a set of size 
 such that if 
, then the absolute value of the difference of their remainders satisfies 
, where 
 denotes the standard absolute value on 
.

Find similar
View Dependencies ▼
Polynomial.exists_iff_exists_finsupp
In: Mathlib.Algebra.Polynomial.Basic

Lean Code:
theorem exists_iff_exists_finsupp (P : R[X] → Prop) :
    (∃ p, P p) ↔ ∃ q : R[ℕ], P ⟨q⟩ :=
  ⟨fun ⟨⟨p⟩, hp⟩ => ⟨p, hp⟩, fun ⟨q, hq⟩ => ⟨⟨q⟩, hq⟩⟩
Gemini 3.0 Flash:
Equivalence of Existence for Polynomials and Finitely Supported Functions. For any property 
 defined on the set of univariate polynomials 
, there exists a polynomial 
 satisfying 
 if and only if there exists a finitely supported function 
 such that 
 holds for the polynomial induced by 
.

Find similar
View Dependencies ▼
Polynomial.exists_eq_supNorm
In: Mathlib.Analysis.Polynomial.Norm

Lean Code:
lemma exists_eq_supNorm : ∃ i : ℕ, p.supNorm = ‖p.coeff i‖ := by
  simpa using p.exists_eq_gaussNorm (SeminormedRing.toRingSeminorm A) 1
Gemini 3.0 Flash:
Existence of a Coefficient Attaining the Supremum Norm. For any polynomial 
 over a seminormed ring, there exists a natural number 
 such that the supremum norm of 
 is equal to the norm of its 
-th coefficient.

Find similar
View Dependencies ▼
Polynomial.exists_root_of_splits
In: Mathlib.Algebra.Polynomial.Splits

Lean Code:
@[deprecated (since := "2025-12-01")]
alias exists_root_of_splits := Splits.exists_eval_eq_zero
Docstring:
Alias of Polynomial.Splits.exists_eval_eq_zero.

Gemini 3.0 Flash:
Existence of a Root for a Splitting Polynomial. If a non-constant polynomial 
 over a commutative ring splits into linear factors, then there exists an element 
 in the ring such that 
.

Find similar
View Dependencies ▼
#### LeanFinder
Rank	Formal statement	Informal statement
1	
noncomputable def P : (Polynomial ℚ) := X ^ 3 - Polynomial.C 2
Doc
Copy
👍
👎
The polynomial 
P
(
X
)
P(X) is defined as 
X
3
−
2
X 
3
 −2 over the rational numbers 
Q
Q. This is a cubic polynomial with a leading term 
X
3
X 
3
  and a constant term 
−
2
−2.
Copy
2	
structure Polynomial (R : Type*) [Semiring R] None
Doc
Copy
👍
👎
The structure Polynomial R represents the type of univariate polynomials over a semiring R, denoted as R[X]. Polynomials are constructed using the variable X and constant embedding C from R, forming a semiring structure.
Copy
3	
theorem Polynomial.eval_X : X.eval x = x :=
  eval₂_X _ _
Doc
Copy
👍
👎
For any element 
x
x in a semiring 
R
R, the evaluation of the polynomial variable 
X
∈
R
[
X
]
X∈R[X] at 
x
x equals 
x
x, i.e.,
X
(
x
)
=
x
.
X(x)=x.
Copy
4	
definition Polynomial.eval : R → R[X] → R :=
  eval₂ (RingHom.id _)
Doc
Copy
👍
👎
The function 
eval
(
x
,
p
)
eval(x,p) evaluates the polynomial 
p
∈
R
[
X
]
p∈R[X] at the point 
x
∈
R
x∈R, defined as 
∑
e
a
e
⋅
x
e
∑ 
e
​
 a 
e
​
 ⋅x 
e
  where 
a
e
a 
e
​
  are the coefficients of 
p
p.
Copy
5	
theorem Polynomial.eval_map (x : S) : (p.map f).eval x = p.eval₂ f x :=
  (eval₂_eq_eval_map f).symm
Doc
Copy
👍
👎
Let 
R
R and 
S
S be semirings, 
f
 ⁣
:
R
→
S
f:R→S a ring homomorphism, 
p
∈
R
[
X
]
p∈R[X] a polynomial, and 
x
∈
S
x∈S. Then the evaluation of the mapped polynomial 
p
.
map
 
f
∈
S
[
X
]
p.mapf∈S[X] at 
x
x equals the evaluation of 
p
p at 
x
x via 
f
f, i.e.,
(
p
.
map
 
f
)
(
x
)
=
p
.
eval
2
 
f
 
x
.
(p.mapf)(x)=p.eval 
2
​
 fx.
Copy

### exists_polynomial_onic_forall_Icc_norm_lt

#### LeanExplore
Polynomial.exists_forall_norm_le
In: Mathlib.Topology.Algebra.Polynomial

Lean Code:
theorem exists_forall_norm_le [ProperSpace R] (p : R[X]) : ∃ x, ∀ y, ‖p.eval x‖ ≤ ‖p.eval y‖ :=
  if hp0 : 0 < degree p then
    p.continuous.norm.exists_forall_le <| p.tendsto_norm_atTop hp0 tendsto_norm_cocompact_atTop
  else
    ⟨p.coeff 0, by rw [eq_C_of_degree_le_zero (le_of_not_gt hp0)]; simp⟩
...
Show all
Gemini 3.0 Flash:
Existence of a Global Minimum for the Norm of a Polynomial. Let 
 be a proper normed ring. For any polynomial 
 with coefficients in 
, there exists an element 
 such that the norm of the evaluation of 
 at 
 is less than or equal to the norm of the evaluation of 
 at any other element 
. That is, the function 
 attains a global minimum on 
.

Find similar
View Dependencies ▼
IsPicardLindelof.exists_eq_forall_mem_Icc_eq_picard
In: Mathlib.Analysis.ODE.PicardLindelof

Lean Code:
theorem exists_eq_forall_mem_Icc_eq_picard
    (hf : IsPicardLindelof f t₀ x₀ a r L K) (hx : x ∈ closedBall x₀ r) :
    ∃ α : ℝ → E, α t₀ = x ∧ ∀ t ∈ Icc tmin tmax, α t = ODE.picard f t₀ x α t := by
  obtain ⟨α, hα⟩ := FunSpace.exists_isFixedPt_next hf hx
  refine ⟨(FunSpace.next hf hx α).compProj, by simp, fun t ht ↦ ?_⟩
...
Show all
Docstring:
Picard-Lindelöf (Cauchy-Lipschitz) theorem, integral form. This version shows the existence of a local solution whose initial point x may be different from the centre x₀ of the closed ball within which the properties of the vector field hold.

Gemini 3.0 Flash:
The Picard-Lindelöf (Cauchy-Lipschitz) Theorem (Integral Form). Suppose a time-dependent vector field 
 satisfies the Picard-Lindelöf conditions on a time interval 
 centered at 
 and within a closed ball of radius 
 centered at 
. For any initial value 
 in the closed ball 
, there exists a continuous function 
 such that 
 and, for all 
, 
 is a fixed point of the Picard operator. Specifically, 
 satisfies the integral equation 
 for all 
 in the specified interval.

Find similar
View Dependencies ▼
Int.Linear.norm_le
In: Init.Data.Int.Linear

Lean Code:
theorem norm_le (ctx : Context) (lhs rhs : Expr) (p : Poly) (h : norm_eq_cert lhs rhs p) : (lhs.denote ctx ≤ rhs.denote ctx) = (p.denote' ctx ≤ 0) := by
  simp [norm_eq_cert] at h; subst p
  simp
  constructor
  · exact Int.sub_nonpos_of_le
...
Show all
Gemini 3.0 Flash:
Equivalence of Expression Inequality and Polynomial Normalization. Given two integer linear expressions and an integer linear polynomial, if the polynomial is the certified normalization of the difference between the first and second expressions, then the first expression is less than or equal to the second expression if and only if the evaluation of the polynomial is less than or equal to zero.

Find similar
View Dependencies ▼
Polynomial.cauchyBound
In: Mathlib.Analysis.Polynomial.CauchyBound

Lean Code:
noncomputable def cauchyBound (p : K[X]) : ℝ≥0 :=
  sup (range p.natDegree) (‖p.coeff ·‖₊) / ‖p.leadingCoeff‖₊ + 1
Show all
Docstring:
Cauchy's bound on the roots of a given polynomial. See IsRoot.norm_lt_cauchyBound for the proof that the roots satisfy this bound.

Gemini 3.0 Flash:
Cauchy's bound. For a polynomial 
 over a normed division ring, the Cauchy bound is the non-negative real number defined as the ratio of the maximum norm of the coefficients (excluding the leading coefficient's index) to the norm of the leading coefficient, plus one. Specifically, it is given by 
 
, where 
 are the coefficients and 
 is the degree of 
.

Find similar
View Dependencies ▼
Lean.Grind.CommRing.le_norm
In: Init.Grind.Ring.CommSolver

Lean Code:
theorem le_norm {α} [CommRing α] [LE α] [LT α] [IsPreorder α] [OrderedRing α] (ctx : Context α) (lhs rhs : Expr) (p : Poly)
    : core_cert lhs rhs p → lhs.denote ctx ≤ rhs.denote ctx → p.denote ctx ≤ 0 := by
  simp [core_cert]; intro _ h; subst p; simp [Expr.denote_toPoly, Expr.denote]
  replace h := add_le_left h ((-1) * rhs.denote ctx)
  rw [neg_mul, ← sub_eq_add_neg, one_mul, ← sub_eq_add_neg, sub_self] at h
...
Show all
Gemini 3.0 Flash:
Polynomial Normalization of Inequalities. In an ordered commutative ring, if a polynomial 
 is the formal representation of the difference between two expressions 
 and 
 (i.e., 
 is a certificate for 
), then the inequality 
 implies that the evaluation of the polynomial 
 is less than or equal to zero.

Find similar
View Dependencies ▼
#### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ) (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
  ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
  use p
  rw [norm_lt_iff _ pos] at b
  intro x m
  exact b ⟨x, m⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any function 
f
 ⁣
:
R
→
R
f:R→R that is continuous on the closed interval 
[
a
,
b
]
[a,b], and any 
ε
>
0
ε>0, there exists a polynomial 
p
p with real coefficients such that for all 
x
∈
[
a
,
b
]
x∈[a,b], the absolute difference between 
p
(
x
)
p(x) and 
f
(
x
)
f(x) is less than 
ε
ε.
Copy
2	
theorem exists_taylor_mean_remainder_bound {f : ℝ → E} {a b : ℝ} {n : ℕ} (hab : a ≤ b) (hf : ContDiffOn ℝ (n + 1) f (Icc a b)) :
  ∃ C, ∀ x ∈ Icc a b, ‖f x - taylorWithinEval f n (Icc a b) a x‖ ≤ C * (x - a) ^ (n + 1) := by
  rcases eq_or_lt_of_le hab with (rfl | h)
  · refine ⟨0, fun x hx => ?_⟩
    have : x = a := by simpa [← le_antisymm_iff] using hx
    simp [← this]
  -- We estimate by the supremum of the norm of the iterated derivative
  let g : ℝ → ℝ := fun y => ‖iteratedDerivWithin (n + 1) f (Icc a b) y‖
  use SupSet.sSup (g '' Icc a b) / (n !)
  intro x hx
  rw [div_mul_eq_mul_div₀]
  refine taylor_mean_remainder_bound hab hf hx fun y => ?_
  exact (hf.continuousOn_iteratedDerivWithin rfl.le <| uniqueDiffOn_Icc h).norm.le_sSup_image_Icc
Doc
Copy
👍
👎
Let 
f
 ⁣
:
R
→
E
f:R→E be a function where 
E
E is a normed vector space over 
R
R. Given real numbers 
a
≤
b
a≤b and a natural number 
n
∈
N
n∈N, if 
f
f is 
(
n
+
1
)
(n+1)-times continuously differentiable on the closed interval 
[
a
,
b
]
[a,b], then there exists a constant 
C
≥
0
C≥0 such that for all 
x
∈
[
a
,
b
]
x∈[a,b], the difference between 
f
(
x
)
f(x) and its 
n
n-th degree Taylor polynomial centered at 
a
a is bounded by:
∥
f
(
x
)
−
T
n
(
f
)
(
a
,
x
)
∥
≤
C
(
x
−
a
)
n
+
1
∥f(x)−T 
n
​
 (f)(a,x)∥≤C(x−a) 
n+1
 

where 
T
n
(
f
)
(
a
,
x
)
T 
n
​
 (f)(a,x) denotes the Taylor polynomial of degree 
n
n evaluated at 
x
x.
Copy
3	
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ) (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
  rw [Metric.mem_ball, dist_eq_norm] at H
  exact ⟨m, H⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any continuous function 
f
 ⁣
:
[
a
,
b
]
→
R
f:[a,b]→R, and any 
ε
>
0
ε>0, there exists a polynomial 
p
p such that the uniform norm of 
p
−
f
p−f on 
[
a
,
b
]
[a,b] is less than 
ε
ε.
Copy
4	
/--
Given a sequence of complex polynomials `fₚ`, a complex constant `s`, and a real constant `c` such
that `|fₚ(xs)| ≤ c ^ p` for all `p ∈ ℕ` and `x ∈ Ioc 0 1`, then there is also a nonnegative
constant `c'` such that for all nonzero `p ∈ ℕ`, `|P(fₚ, s)| ≤ c' ^ p`.
-/
private theorem P_le (f : ℕ → ℂ[X]) (s : ℂ) (c : ℝ)
    (hc : ∀ p : ℕ, ∀ x ∈ Set.Ioc (0 : ℝ) 1, ‖(f p).eval (x • s)‖ ≤ c ^ p) :
    ∃ c' ≥ 0, ∀ p ≠ 0, ‖P (f p) s‖ ≤ c' ^ p := by
  obtain ⟨c', hc', h'⟩ := P_le_aux f s c hc; clear c hc
  let c₁ := max (Real.exp s.re) 1
  let c₂ := max (Real.exp ‖s‖) 1
  let c₃ := max ‖s‖ 1
  use c₁ * (c₂ * c' * c₃), by positivity
  intro p hp
  refine (h' p).trans ?_
  simp_rw [mul_pow]
  have le_max_one_pow {x : ℝ} : x ≤ max x 1 ^ p :=
    (max_cases x 1).elim (fun h ↦ h.1.symm ▸ le_self_pow₀ h.2 hp)
      fun h ↦ by rw [h.1, one_pow]; exact h.2.le
  gcongr <;> exact le_max_one_pow
Doc
Copy
👍
👎
Given a sequence of complex polynomials 
f
p
f 
p
​
 , a complex constant 
s
s, and a real constant 
c
c such that 
∣
f
p
(
x
s
)
∣
≤
c
p
∣f 
p
​
 (xs)∣≤c 
p
  for all 
p
∈
N
p∈N and 
x
∈
(
0
,
1
]
x∈(0,1], there exists a nonnegative constant 
c
′
c 
′
  such that for all nonzero 
p
∈
N
p∈N, 
∣
P
(
f
p
,
s
)
∣
≤
(
c
′
)
p
∣P(f 
p
​
 ,s)∣≤(c 
′
 ) 
p
 . This means that the evaluations of the polynomials at the complex point 
s
s are also bounded by an exponential function.
Copy
5	
/--
Given a sequence of complex polynomials `fₚ`, a complex constant `s`, and a real constant `c` such
that `|fₚ(xs)| ≤ c ^ p` for all `p ∈ ℕ` and `x ∈ Ioc 0 1`, then there is also a nonnegative
constant `c'` such that for all nonzero `p ∈ ℕ`, `|P(fₚ, s)| ≤ c' ^ p`.
-/
private theorem P_le_aux (f : ℕ → ℂ[X]) (s : ℂ) (c : ℝ)
    (hc : ∀ p : ℕ, ∀ x ∈ Set.Ioc (0 : ℝ) 1, ‖(f p).eval (x • s)‖ ≤ c ^ p) :
    ∃ c' ≥ 0, ∀ p : ℕ,
      ‖P (f p) s‖ ≤
        Real.exp s.re * (Real.exp ‖s‖ * c' ^ p * ‖s‖) := by
  refine ⟨|c|, abs_nonneg _, fun p => ?_⟩
  rw [P_eq_integral_exp_mul_eval (f p) s, mul_comm s, norm_mul, norm_mul, norm_exp]
  gcongr
  rw [intervalIntegral.integral_of_le zero_le_one, ← mul_one (_ * _)]
  convert MeasureTheory.norm_setIntegral_le_of_norm_le_const _ _
  · rw [Real.volume_real_Ioc_of_le zero_le_one, sub_zero]
  · rw [Real.volume_Ioc, sub_zero]; exact ENNReal.ofReal_lt_top
  intro x hx
  rw [norm_mul, norm_exp]
  gcongr
  · simp only [Set.mem_Ioc] at hx
    apply (re_le_norm _).trans
    rw [norm_neg, norm_smul, Real.norm_of_nonneg hx.1.le]
    exact mul_le_of_le_one_left (norm_nonneg _) hx.2
  · rw [← abs_pow]
    exact (hc p x hx).trans (le_abs_self _)
Doc
Copy
👍
👎
Given a sequence of complex polynomials 
f
p
f 
p
​
 , a complex constant 
s
s, and a real constant 
c
c such that 
∣
f
p
(
x
s
)
∣
≤
c
p
∣f 
p
​
 (xs)∣≤c 
p
  for all 
p
∈
N
p∈N and 
x
∈
(
0
,
1
]
x∈(0,1], there exists a nonnegative constant 
c
′
c 
′
  such that for all nonzero 
p
∈
N
p∈N, 
∣
P
(
f
p
,
s
)
∣
≤
e
Re
(
s
)
⋅
(
e
∥
s
∥
⋅
c
′
p
⋅
∥
s
∥
)
∣P(f 
p
​
 ,s)∣≤e 
Re(s)
 ⋅(e 
∥s∥
 ⋅c 
′p
 ⋅∥s∥). Here, 
P
(
f
p
,
s
)
P(f 
p
​
 ,s) is a specific integral transformation of the polynomial 
f
p
f 
p
​
  evaluated at the complex number 
s
s. This result provides a bound on the norm of this transformation in terms of the exponential of the real and norm parts of 
s
s.
Copy

### exists_sup_of_bddAbove'

#### LeanExplore
Real.iSup_of_not_bddAbove
In: Mathlib.Data.Real.Archimedean

Lean Code:
lemma iSup_of_not_bddAbove (hf : ¬BddAbove (Set.range f)) : ⨆ i, f i = 0 := sSup_of_not_bddAbove hf
Gemini 3.0 Flash:
Supremum of an Unbounded Family of Reals. If the range of a family of real numbers 
 is not bounded above, then its supremum 
 is defined to be 
.

Find similar
View Dependencies ▼
ciSup_of_not_bddAbove
In: Mathlib.Order.ConditionallyCompleteLattice.Basic

Lean Code:
@[simp] lemma ciSup_of_not_bddAbove (hf : ¬BddAbove (range f)) : ⨆ i, f i = sSup ∅ :=
  csSup_of_not_bddAbove hf
Gemini 3.0 Flash:
Supremum of an Unbounded Range. In a conditionally complete linear order, if the range of a function 
 is not bounded above, then the supremum of 
 is equal to the supremum of the empty set.

Find similar
View Dependencies ▼
Real.sSup_of_not_bddAbove
In: Mathlib.Data.Real.Archimedean

Lean Code:
lemma sSup_of_not_bddAbove (hs : ¬BddAbove s) : sSup s = 0 := dif_neg fun h => hs h.2
Gemini 3.0 Flash:
Supremum of an Unbounded Set of Reals. If a set of real numbers 
 is not bounded above, then its supremum is defined to be 
.

Find similar
View Dependencies ▼
Int.csSup_of_not_bddAbove
In: Mathlib.Data.Int.ConditionallyCompleteOrder

Lean Code:
theorem csSup_of_not_bddAbove {s : Set ℤ} (h : ¬BddAbove s) : sSup s = 0 :=
  dif_neg (by simp [h])
Gemini 3.0 Flash:
Supremum of an Unbounded Set of Integers. For any set of integers 
, if 
 is not bounded above, then its supremum 
 is defined to be 
.

Find similar
View Dependencies ▼
csSup_of_not_bddAbove
In: Mathlib.Order.ConditionallyCompleteLattice.Basic

Lean Code:
@[simp] lemma csSup_of_not_bddAbove (hs : ¬BddAbove s) : sSup s = sSup ∅ :=
  ConditionallyCompleteLinearOrder.csSup_of_not_bddAbove s hs
Gemini 3.0 Flash:
Supremum of an Unbounded Set. In a conditionally complete linear order, if a set is not bounded above, its supremum is equal to the supremum of the empty set.

Find similar
View Dependencies ▼
#### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem bddAbove_iff_exists_ge [SemilatticeSup γ] {s : Set γ} (x₀ : γ) : BddAbove s ↔ ∃ x, x₀ ≤ x ∧ ∀ y ∈ s, y ≤ x := by
  rw [bddAbove_def, exists_ge_and_iff_exists]
  exact Monotone.ball fun x _ => monotone_le
Doc
Copy
👍
👎
Let 
γ
γ be a join-semilattice and 
s
s a subset of 
γ
γ. For any element 
x
0
∈
γ
x 
0
​
 ∈γ, the set 
s
s is bounded above if and only if there exists an element 
x
∈
γ
x∈γ such that 
x
0
≤
x
x 
0
​
 ≤x and 
y
≤
x
y≤x for all 
y
∈
s
y∈s.
Copy
2	
theorem BddAbove.exists_ge [SemilatticeSup γ] {s : Set γ} (hs : BddAbove s) (x₀ : γ) : ∃ x, x₀ ≤ x ∧ ∀ y ∈ s, y ≤ x :=
  (bddAbove_iff_exists_ge x₀).mp hs
Doc
Copy
👍
👎
Let 
γ
γ be a join-semilattice and 
s
s a subset of 
γ
γ. If 
s
s is bounded above, then for any element 
x
0
∈
γ
x 
0
​
 ∈γ, there exists an element 
x
∈
γ
x∈γ such that 
x
0
≤
x
x 
0
​
 ≤x and 
y
≤
x
y≤x for all 
y
∈
s
y∈s.
Copy
3	
definition BddAbove (s : Set α) :=
  (upperBounds s).Nonempty
Doc
Copy
👍
👎
A set 
s
s in a type 
α
α equipped with a preorder is called *bounded above* if there exists an element 
x
∈
α
x∈α such that 
a
≤
x
a≤x for every 
a
∈
s
a∈s (i.e., the set of upper bounds of 
s
s is nonempty).
Copy
4	
theorem bddAbove_def : BddAbove s ↔ ∃ x, ∀ y ∈ s, y ≤ x :=
  Iff.rfl
Doc
Copy
👍
👎
A set 
s
s in a preordered type 
α
α is bounded above if and only if there exists an element 
x
∈
α
x∈α such that 
y
≤
x
y≤x for all 
y
∈
s
y∈s.
Copy
5	
theorem OrderTop.bddAbove [OrderTop α] (s : Set α) : BddAbove s :=
  ⟨⊤, fun a _ => OrderTop.le_top a⟩
Doc
Copy
👍
👎
In a preorder 
α
α with a greatest element (order top), every subset 
s
⊆
α
s⊆α is bounded above.
Copy

### card_univ

#### LeanExplore
Cardinal.univ
In: Mathlib.SetTheory.Ordinal.Basic

Lean Code:
@[pp_with_univ, nolint checkUnivs]
def univ :=
  lift.{v, u + 1} #Ordinal
Show all
Docstring:
The cardinal univ is the cardinality of ordinal univ, or equivalently the cardinal of Ordinal.{u}, or Cardinal.{u}, as an element of Cardinal.{v} (when u < v).

Gemini 3.0 Flash:
The Cardinality of the Universe. The cardinal number univ is defined as the cardinality of the type of all ordinals of a given universe level. It represents the size of the collection of all ordinals (or equivalently, all cardinals) of that level, lifted into a higher universe.

Find similar
View Dependencies ▼
Nat.card_univ
In: Mathlib.SetTheory.Cardinal.Finite

Lean Code:
lemma card_univ : Nat.card (univ : Set α) = Nat.card α :=
  card_congr (Equiv.Set.univ α)
Gemini 3.0 Flash:
Cardinality of the Universal Set. The cardinality of the universal set of a type is equal to the cardinality of the type itself.

Find similar
View Dependencies ▼
Finset.card_univ
In: Mathlib.Data.Fintype.Card

Lean Code:
@[simp, grind =]
theorem Finset.card_univ [Fintype α] : #(univ : Finset α) = Fintype.card α := rfl
Gemini 3.0 Flash:
Cardinality of the Universal Finset. For any finite type, the number of elements in its universal finite set is equal to the cardinality of the type itself.

Find similar
View Dependencies ▼
Cardinal.lt_univ
In: Mathlib.SetTheory.Ordinal.Basic

Lean Code:
theorem lt_univ {c} : c < univ.{u, u + 1} ↔ ∃ c', c = lift.{u + 1, u} c' :=
  ⟨fun h => by
    have := ord_lt_ord.2 h
    rw [ord_univ] at this
    obtain ⟨o, e⟩ := liftPrincipalSeg.mem_range_of_rel_top (by simpa only [liftPrincipalSeg_top])
...
Show all
Gemini 3.0 Flash:
Characterization of Cardinals Less Than the Universe Cardinal. A cardinal 
 is strictly less than the cardinality of the universe of a given level if and only if 
 is the lift of a cardinal from that lower universe.

Find similar
View Dependencies ▼
Cardinal.lift
In: Mathlib.SetTheory.Cardinal.Defs

Lean Code:
@[pp_with_univ]
def lift (c : Cardinal.{v}) : Cardinal.{max v u} :=
  map ULift.{u, v} (fun _ _ e => Equiv.ulift.trans <| e.trans Equiv.ulift.symm) c
Show all
Docstring:
The universe lift operation on cardinals. You can specify the universes explicitly with lift.{u v} : Cardinal.{v} → Cardinal.{max v u}

Gemini 3.0 Flash:
Cardinal Universe Lift. The operation that maps a cardinal number in one universe to its corresponding cardinal in a higher universe, specifically by lifting the underlying types to a universe of at least level 
. This is defined by applying the universe lift operation for types to the equivalence classes representing the cardinal numbers.

Find similar
View Dependencies ▼
#### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Finset.card_univ [Fintype α] : #(univ : Finset α) = Fintype.card α := rfl
Doc
Copy
👍
👎
For any finite type 
α
α, the cardinality of the universal finite set univ (containing all elements of 
α
α) is equal to the cardinality of 
α
α itself, i.e., 
∣
univ
∣
=
card
(
α
)
∣univ∣=card(α).
Copy
2	
definition Finset.univ : Finset α :=
  @Fintype.elems α _
Doc
Copy
👍
👎
The universal finite set of type Finset α, which contains all elements of the finite type α. This is constructed from the Fintype α instance, which provides a finite set containing all elements of α.
Copy
3	
theorem Finset.card_fin (n : ℕ) : #(univ : Finset (Fin n)) = n := by simp
Doc
Copy
👍
👎
For any natural number 
n
n, the cardinality of the universal finite set of 
Fin
(
n
)
Fin(n) is equal to 
n
n.
Copy
4	
definition Fintype.card (α) [Fintype α] : ℕ :=
  (@univ α _).card
Doc
Copy
👍
👎
For a finite type 
α
α, 
card
(
α
)
card(α) is the number of elements in 
α
α, defined as the cardinality of the universal finite set of 
α
α.
Copy
5	
theorem Finset.mem_univ (x : α) : x ∈ (univ : Finset α) :=
  Fintype.complete x
Doc
Copy
👍
👎
For any element 
x
x of a finite type 
α
α, 
x
x belongs to the universal finite set 
univ
:
Finset
α
univ:Finsetα.
Copy

### quotientAddGroup.quotientKerEquivOfSurjective

#### LeanExplore
QuotientGroup.quotientKerEquivOfSurjective
In: Mathlib.GroupTheory.QuotientGroup.Basic

Lean Code:
@[to_additive ]
noncomputable def quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
  quotientKerEquivOfRightInverse φ _ hφ.hasRightInverse.choose_spec
Show all
Docstring:
The canonical isomorphism G/(ker φ) ≃* H induced by a surjection φ : G →* H.

For a computable version, see QuotientGroup.quotientKerEquivOfRightInverse.

Gemini 3.0 Flash:
First Isomorphism Theorem for Surjective Group Homomorphisms. For any surjective group homomorphism 
, there exists a canonical isomorphism between the quotient group 
 and the codomain 
. This result also holds for additive groups, providing a canonical isomorphism 
 for any surjective additive group homomorphism 
.

Find similar
View Dependencies ▼
QuotientAddGroup.quotientKerEquivOfSurjective
In: Mathlib.GroupTheory.QuotientGroup.Basic

Lean Code:
@[to_additive ]
noncomputable def quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
Show all
Docstring:
The canonical isomorphism G/(ker φ) ≃+ H induced by a surjection φ : G →+ H. For a computable version, see QuotientAddGroup.quotientKerEquivOfRightInverse.

Gemini 3.0 Flash:
First Isomorphism Theorem for Additive Groups. For any surjective additive group homomorphism 
, there exists a canonical additive isomorphism between the quotient group 
 and the codomain 
.

Find similar
View Dependencies ▼
QuotientAddGroup.quotientKerEquivOfRightInverse
In: Mathlib.GroupTheory.QuotientGroup.Basic

Lean Code:
@[to_additive (attr := simps) ]
def quotientKerEquivOfRightInverse (ψ : H → G) (hφ : RightInverse ψ φ) : G ⧸ ker φ ≃* H :=
Show all
Docstring:
The canonical isomorphism G/(ker φ) ≃+ H induced by a homomorphism φ : G →+ H with a right inverse ψ : H → G.

Gemini 3.0 Flash:
Isomorphism from Quotient by Kernel for Homomorphisms with a Right Inverse. Given an additive group homomorphism 
 and a function 
 such that 
 is a right inverse of 
 (i.e., 
), there exists a canonical additive isomorphism between the quotient group 
 and the codomain 
.

Find similar
View Dependencies ▼
AddCon.quotientKerEquivOfSurjective
In: Mathlib.GroupTheory.Congruence.Basic

Lean Code:
@[to_additive ]
noncomputable def quotientKerEquivOfSurjective (f : M →* P) (hf : Surjective f) :
Show all
Docstring:
The first isomorphism theorem for AddMonoids in the case of a surjective homomorphism.

For a computable version, see AddCon.quotientKerEquivOfRightInverse.

Gemini 3.0 Flash:
First Isomorphism Theorem for Surjective Additive Monoid Homomorphisms. For any surjective additive monoid homomorphism 
, there exists an additive isomorphism between the quotient of 
 by the kernel of 
 and the codomain 
.

Find similar
View Dependencies ▼
QuotientAddGroup.rangeKerLift_surjective
In: Mathlib.GroupTheory.QuotientGroup.Basic

Lean Code:
@[to_additive]
theorem rangeKerLift_surjective : Surjective (rangeKerLift φ) := by
Gemini 3.0 Flash:
Surjectivity of the Induced Map from the Quotient by the Kernel to the Range. For any additive group homomorphism 
, the induced homomorphism from the quotient of the domain by the kernel of 
 to the range of 
 is surjective.

Find similar
View Dependencies ▼
#### LeanFinder
Rank	Formal statement	Informal statement
1	
definition QuotientGroup.quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
  quotientKerEquivOfRightInverse φ _ hφ.hasRightInverse.choose_spec
Doc
Copy
👍
👎
Given a surjective group homomorphism 
φ
:
G
→
H
φ:G→H, there is a canonical group isomorphism between the quotient group 
G
/
ker
⁡
φ
G/kerφ and 
H
H. The isomorphism maps each coset 
g
ker
⁡
φ
gkerφ to 
φ
(
g
)
φ(g).
Copy
2	
definition Setoid.quotientKerEquivOfSurjective (hf : Surjective f) : Quotient (ker f) ≃ β :=
  quotientKerEquivOfRightInverse _ (Function.surjInv hf) (rightInverse_surjInv hf)
Doc
Copy
👍
👎
Given a surjective function 
f
:
α
→
β
f:α→β, the quotient of 
α
α by the kernel of 
f
f is in bijection with 
β
β. 

The bijection is constructed as:
- The forward map sends an equivalence class 
[
a
]
[a] to 
f
(
a
)
f(a)
- The inverse map sends 
b
∈
β
b∈β to the equivalence class 
[
f
−
1
(
b
)
]
[f 
−1
 (b)], where 
f
−
1
f 
−1
  is any right inverse of 
f
f (which exists by surjectivity)
- This satisfies 
f
(
[
a
]
)
=
b
f([a])=b if and only if 
[
a
]
=
[
f
−
1
(
b
)
]
[a]=[f 
−1
 (b)] for all 
a
∈
α
a∈α and 
b
∈
β
b∈β
Copy
3	
/-- The canonical isomorphism `G/(ker φ) ≃* H` induced by a surjection `φ : G →* H`.

For a `computable` version, see `QuotientGroup.quotientKerEquivOfRightInverse`.
-/
@[to_additive "The canonical isomorphism `G/(ker φ) ≃+ H` induced by a surjection `φ : G →+ H`.
For a `computable` version, see `QuotientAddGroup.quotientKerEquivOfRightInverse`."]
noncomputable def quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
  quotientKerEquivOfRightInverse φ _ hφ.hasRightInverse.choose_spec
Doc
Copy
👍
👎
Given a surjective group homomorphism 
φ
:
G
→
H
φ:G→H, there exists a canonical group isomorphism 
G
/
ker
⁡
φ
≅
H
G/kerφ≅H. This isomorphism maps each coset 
g
ker
⁡
φ
gkerφ to 
φ
(
g
)
φ(g). This result is noncomputable and relies on the existence of a right inverse for 
φ
φ.
Copy
4	
definition Con.quotientKerEquivOfSurjective (f : M →* P) (hf : Surjective f) : (ker f).Quotient ≃* P :=
  quotientKerEquivOfRightInverse _ _ hf.hasRightInverse.choose_spec
Doc
Copy
👍
👎
Given a surjective monoid homomorphism 
f
 ⁣
:
M
→
P
f:M→P, the quotient of 
M
M by the kernel congruence relation of 
f
f is isomorphic as a monoid to 
P
P via the map sending each equivalence class 
[
x
]
ker
⁡
f
[x] 
kerf
​
  to 
f
(
x
)
f(x).
Copy
5	
theorem QuotientGroup.mk_surjective : Function.Surjective <| @mk _ _ s :=
  Quotient.mk''_surjective
Doc
Copy
👍
👎
The canonical projection map 
π
:
α
→
α
⧸
s
π:α→α⧸s from a group 
α
α to its quotient by a subgroup 
s
s is surjective. That is, for every element 
q
q in the quotient 
α
⧸
s
α⧸s, there exists an element 
a
∈
α
a∈α such that 
π
(
a
)
=
q
π(a)=q.
Copy

## Search Scratchpad: Name + Statement Queries

### abs_sub_self

#### Query (name + statement)

```text
abs_sub_self
theorem weierstrass_approximation (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
    (ε : ℝ) (hε : ε > 0) :
    ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε
```

#### LeanExplore (name + statement)
exists_polynomial_near_of_continuousOn
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ)
    (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
    ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
...
Show all
Docstring:
Another alternative statement of Weierstrass's theorem, for those who like epsilons, but not bundled continuous functions.

Every real-valued function ℝ → ℝ which is continuous on [a,b] can be approximated to within any ε > 0 on [a,b] by some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real-valued function 
 that is continuous on a closed interval 
 and for any 
, there exists a polynomial 
 such that for all 
, the inequality 
 holds.

Find similar
View Dependencies ▼
taylor_mean_remainder_bound
In: Mathlib.Analysis.Calculus.Taylor

Lean Code:
theorem taylor_mean_remainder_bound {f : ℝ → E} {a b C x : ℝ} {n : ℕ} (hab : a ≤ b)
    (hf : ContDiffOn ℝ (n + 1) f (Icc a b)) (hx : x ∈ Icc a b)
    (hC : ∀ y ∈ Icc a b, ‖iteratedDerivWithin (n + 1) f (Icc a b) y‖ ≤ C) :
    ‖f x - taylorWithinEval f n (Icc a b) a x‖ ≤ C * (x - a) ^ (n + 1) / n ! := by
  rcases eq_or_lt_of_le hab with (rfl | h)
...
Show all
Docstring:
Taylor's theorem with a polynomial bound on the remainder

We assume that f is n+1-times continuously differentiable on the closed set Icc a b. The difference of f and its n-th Taylor polynomial can be estimated by C * (x - a)^(n+1) / n! where C is a bound for the n+1-th iterated derivative of f.

Gemini 3.0 Flash:
Taylor's Theorem with a Polynomial Remainder Bound. Let 
 be a function into a normed space 
 that is 
-times continuously differentiable on the closed interval 
. Suppose there exists a constant 
 such that the norm of the 
-th iterated derivative of 
 (taken within 
) is bounded by 
 for all 
. Then for any 
, the norm of the difference between 
 and its 
-th order Taylor polynomial evaluated at 
 (with base point 
) is bounded by: 
 

Find similar
View Dependencies ▼
ApproximatesLinearOn
In: Mathlib.Analysis.Calculus.InverseFunctionTheorem.ApproximatesLinearOn

Lean Code:
def ApproximatesLinearOn (f : E → F) (f' : E →L[𝕜] F) (s : Set E) (c : ℝ≥0) : Prop :=
  ∀ x ∈ s, ∀ y ∈ s, ‖f x - f y - f' (x - y)‖ ≤ c * ‖x - y‖
Show all
Docstring:
We say that f approximates a continuous linear map f' on s with constant c, if ‖f x - f y - f' (x - y)‖ ≤ c * ‖x - y‖ whenever x, y ∈ s.

This predicate is defined to facilitate the splitting of the inverse function theorem into small lemmas. Some of these lemmas can be useful, e.g., to prove that the inverse function is defined on a specific set.

Gemini 3.0 Flash:
Linear Approximation on a Set. A function 
 is said to approximate a continuous linear map 
 on a set 
 with constant 
 if, for all 
, the inequality 
 holds.

Find similar
View Dependencies ▼
exists_polynomial_near_continuousMap
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ)
    (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
...
Show all
Docstring:
An alternative statement of Weierstrass' theorem, for those who like their epsilons.

Every real-valued continuous function on [a,b] is within any ε > 0 of some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real numbers 
 and 
, and any continuous real-valued function 
 defined on the closed interval 
, there exists a polynomial 
 such that for any 
, the supremum norm of the difference between 
 and the restriction of 
 to 
 is strictly less than 
.

Find similar
View Dependencies ▼
Continuous.exists_contDiff_approx_and_eqOn
In: Mathlib.Geometry.Manifold.SmoothApprox

Lean Code:
theorem Continuous.exists_contDiff_approx_and_eqOn (n : ℕ∞)
    (f_cont : Continuous f) (ε_cont : Continuous ε) (ε_pos : ∀ x, 0 < ε x)
    {S U : Set E} (hS : IsClosed S) (hU : U ∈ 𝓝ˢ S) (hfU : ContDiffOn ℝ n f U) :
    ∃ g : E → F, ContDiff ℝ n g ∧
      (∀ x, dist (g x) (f x) < ε x) ∧ EqOn g f S ∧ support g ⊆ support f := by
...
Show all
Gemini 3.0 Flash:
Approximation of Continuous Functions by 
 Functions with Fixed Values on a Closed Set. Let 
 be a continuous function between normed spaces, and let 
. Suppose 
 is a closed subset of 
 and 
 is a neighborhood of 
 such that 
 is 
 on 
. Given a strictly positive continuous function 
, there exists a 
 function 
 such that:

 is an 
-approximation of 
, i.e., 
 for all 
;
 agrees with 
 on the set 
;
the support of 
 is contained within the support of 
.
Find similar
View Dependencies ▼
#### LeanFinder (name + statement)
Rank	Formal statement	Informal statement
1	
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ) (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
  ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
  use p
  rw [norm_lt_iff _ pos] at b
  intro x m
  exact b ⟨x, m⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any function 
f
 ⁣
:
R
→
R
f:R→R that is continuous on the closed interval 
[
a
,
b
]
[a,b], and any 
ε
>
0
ε>0, there exists a polynomial 
p
p with real coefficients such that for all 
x
∈
[
a
,
b
]
x∈[a,b], the absolute difference between 
p
(
x
)
p(x) and 
f
(
x
)
f(x) is less than 
ε
ε.
Copy
2	
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ) (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
  rw [Metric.mem_ball, dist_eq_norm] at H
  exact ⟨m, H⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any continuous function 
f
 ⁣
:
[
a
,
b
]
→
R
f:[a,b]→R, and any 
ε
>
0
ε>0, there exists a polynomial 
p
p such that the uniform norm of 
p
−
f
p−f on 
[
a
,
b
]
[a,b] is less than 
ε
ε.
Copy
3	
theorem bernsteinApproximation_uniform (f : C(I, ℝ)) : Tendsto (fun n : ℕ => bernsteinApproximation n f) atTop (𝓝 f) := by
  simp only [Metric.nhds_basis_ball.tendsto_right_iff, Metric.mem_ball, dist_eq_norm]
  intro ε h
  let δ := δ f ε h
  have nhds_zero := tendsto_const_div_atTop_nhds_zero_nat (2 * ‖f‖ * δ ^ (-2 : ℤ))
  filter_upwards [nhds_zero.eventually (gt_mem_nhds (half_pos h)), eventually_gt_atTop 0] with n nh
    npos'
  have npos : 0 < (n : ℝ) := by positivity
  -- As `[0,1]` is compact, it suffices to check the inequality pointwise.
  rw [ContinuousMap.norm_lt_iff _ h]
  intro x
  -- The idea is to split up the sum over `k` into two sets,
  -- `S`, where `x - k/n < δ`, and its complement.
  let S := S f ε h n x
  calc
    |(bernsteinApproximation n f - f) x| = |bernsteinApproximation n f x - f x| := rfl
    _ = |bernsteinApproximation n f x - f x * 1| := by rw [mul_one]
    _ = |bernsteinApproximation n f x - f x * ∑ k : Fin (n + 1), bernstein n k x| := by
      rw [bernstein.probability]
    _ = |∑ k : Fin (n + 1), (f k/ₙ - f x) * bernstein n k x| := by
      simp [bernsteinApproximation, Finset.mul_sum, sub_mul]
    _ ≤ ∑ k : Fin (n + 1), |(f k/ₙ - f x) * bernstein n k x| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ k : Fin (n + 1), |f k/ₙ - f x| * bernstein n k x := by
      simp_rw [abs_mul, abs_eq_self.mpr bernstein_nonneg]
    _ = (∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x) + ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x :=
      (S.sum_add_sum_compl _).symm
    -- We'll now deal with the terms in `S` and the terms in `Sᶜ` in separate calc blocks.
    _ < ε / 2 + ε / 2 :=
      (add_lt_add_of_le_of_lt ?_ ?_)
    _ = ε := add_halves ε
  · -- We now work on the terms in `S`: uniform continuity and `bernstein.probability`
    -- quickly give us a bound.
    calc
      ∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ S, ε / 2 * bernstein n k x := by
        gcongr with _ m
        exact le_of_lt (lt_of_mem_S m)
      _ = ε / 2 * ∑ k ∈ S, bernstein n k x := by rw [Finset.mul_sum]
      -- In this step we increase the sum over `S` back to a sum over all of `Fin (n+1)`,
      -- so that we can use `bernstein.probability`.
      _ ≤ ε / 2 * ∑ k : Fin (n + 1), bernstein n k x := by gcongr; exact S.subset_univ
      _ = ε / 2 := by rw [bernstein.probability, mul_one]
  · -- We now turn to working on `Sᶜ`: we control the difference term just using `‖f‖`,
    -- and then insert a `δ^(-2) * (x - k/n)^2` factor
    -- (which is at least one because we are not in `S`).
    calc
      ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ Sᶜ, 2 * ‖f‖ * bernstein n k x := by
        gcongr
        apply f.dist_le_two_norm
      _ = 2 * ‖f‖ * ∑ k ∈ Sᶜ, bernstein n k x := by rw [Finset.mul_sum]
      _ ≤ 2 * ‖f‖ * ∑ k ∈ Sᶜ, δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr with _ m
        conv_lhs => rw [← one_mul (bernstein _ _ _)]
        gcongr
        exact le_of_mem_S_compl m
      -- Again enlarging the sum from `Sᶜ` to all of `Fin (n+1)`
      _ ≤ 2 * ‖f‖ * ∑ k : Fin (n + 1), δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr; exact Sᶜ.subset_univ
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * ∑ k : Fin (n + 1), ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        conv_rhs =>
          rw [mul_assoc, Finset.mul_sum]
          simp only [← mul_assoc]
      -- `bernstein.variance` and `x ∈ [0,1]` gives the uniform bound
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * x * (1 - x) / n := by rw [variance npos]; ring
      _ ≤ 2 * ‖f‖ * δ ^ (-2 : ℤ) * 1 * 1 / n := by gcongr <;> unit_interval
      _ < ε / 2 := by simp only [mul_one]; exact nh
Doc
Copy
👍
👎
For any continuous function 
f
∈
C
(
[
0
,
1
]
,
R
)
f∈C([0,1],R), the sequence of Bernstein approximations 
(
B
n
(
f
)
)
n
∈
N
(B 
n
​
 (f)) 
n∈N
​
  converges uniformly to 
f
f as 
n
→
∞
n→∞, where the 
n
n-th Bernstein approximation is given by:
\[ B_n(f)(x) = \sum_{k=0}^n f\left(\frac{k}{n}\right) \binom{n}{k} x^k (1-x)^{n-k}. \]
Copy
4	
definition bernsteinApproximation.δ (f : C(I, ℝ)) (ε : ℝ) (h : 0 < ε) : ℝ :=
  f.modulus (ε / 2) (half_pos h)
Doc
Copy
👍
👎
For a continuous function \( f \in C([0,1], \mathbb{R}) \) and \( \varepsilon > 0 \), the modulus of uniform continuity \( \delta(f, \varepsilon) \) is chosen such that for any \( x, y \in [0,1] \), if \( |x - y| < \delta \) then \( |f(x) - f(y)| < \varepsilon/2 \).
Copy
5	
definition bernsteinApproximation (n : ℕ) (f : C(I, ℝ)) : C(I, ℝ) :=
  ∑ k : Fin (n + 1), f k/ₙ • bernstein n k
Doc
Copy
👍
👎
The 
n
n-th Bernstein approximation of a continuous function 
f
∈
C
(
[
0
,
1
]
,
R
)
f∈C([0,1],R) is the continuous function on 
[
0
,
1
]
[0,1] defined by:
\[ B_n(f)(x) = \sum_{k=0}^n f\left(\frac{k}{n}\right) \cdot B_{n,k}(x) \]
where 
B
n
,
k
(
x
)
=
(
n
k
)
x
k
(
1
−
x
)
n
−
k
B 
n,k
​
 (x)=( 
k
n
​
 )x 
k
 (1−x) 
n−k
  is the Bernstein polynomial of degree 
n
n and index 
k
k.
Copy
### exists_poly_lt

#### Query (name + statement)

```text
exists_poly_lt
theorem weierstrass_approximation (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
    (ε : ℝ) (hε : ε > 0) :
    ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε
```

#### LeanExplore (name + statement)
exists_polynomial_near_of_continuousOn
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ)
    (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
    ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
...
Show all
Docstring:
Another alternative statement of Weierstrass's theorem, for those who like epsilons, but not bundled continuous functions.

Every real-valued function ℝ → ℝ which is continuous on [a,b] can be approximated to within any ε > 0 on [a,b] by some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real-valued function 
 that is continuous on a closed interval 
 and for any 
, there exists a polynomial 
 such that for all 
, the inequality 
 holds.

Find similar
View Dependencies ▼
ApproximatesLinearOn
In: Mathlib.Analysis.Calculus.InverseFunctionTheorem.ApproximatesLinearOn

Lean Code:
def ApproximatesLinearOn (f : E → F) (f' : E →L[𝕜] F) (s : Set E) (c : ℝ≥0) : Prop :=
  ∀ x ∈ s, ∀ y ∈ s, ‖f x - f y - f' (x - y)‖ ≤ c * ‖x - y‖
Show all
Docstring:
We say that f approximates a continuous linear map f' on s with constant c, if ‖f x - f y - f' (x - y)‖ ≤ c * ‖x - y‖ whenever x, y ∈ s.

This predicate is defined to facilitate the splitting of the inverse function theorem into small lemmas. Some of these lemmas can be useful, e.g., to prove that the inverse function is defined on a specific set.

Gemini 3.0 Flash:
Linear Approximation on a Set. A function 
 is said to approximate a continuous linear map 
 on a set 
 with constant 
 if, for all 
, the inequality 
 holds.

Find similar
View Dependencies ▼
exists_polynomial_near_continuousMap
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ)
    (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
...
Show all
Docstring:
An alternative statement of Weierstrass' theorem, for those who like their epsilons.

Every real-valued continuous function on [a,b] is within any ε > 0 of some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real numbers 
 and 
, and any continuous real-valued function 
 defined on the closed interval 
, there exists a polynomial 
 such that for any 
, the supremum norm of the difference between 
 and the restriction of 
 to 
 is strictly less than 
.

Find similar
View Dependencies ▼
polynomialFunctions_closure_eq_top'
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem polynomialFunctions_closure_eq_top' : (polynomialFunctions I).topologicalClosure = ⊤ := by
  apply top_unique
  rintro f -
  refine mem_closure_of_tendsto (bernsteinApproximation_uniform f) <| .of_forall fun n ↦ ?_
  apply Subalgebra.sum_mem
...
Show all
Docstring:
The special case of the Weierstrass approximation theorem for the interval [0,1]. This is just a matter of unravelling definitions and using the Bernstein approximations.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem on the Unit Interval. The subalgebra of polynomial functions on the unit interval 
 is dense in the algebra of all continuous real-valued functions on 
 under the topology of uniform convergence. That is, the topological closure of the set of polynomial functions is equal to the entire space of continuous functions.

Find similar
View Dependencies ▼
polynomialFunctions_closure_eq_top
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem polynomialFunctions_closure_eq_top (a b : ℝ) :
    (polynomialFunctions (Set.Icc a b)).topologicalClosure = ⊤ := by
  rcases lt_or_ge a b with h | h
  · 
    let W : C(Set.Icc a b, ℝ) →ₐ[ℝ] C(I, ℝ) :=
...
Show all
Docstring:
The Weierstrass Approximation Theorem: polynomials functions on [a, b] ⊆ ℝ are dense in C([a,b],ℝ)

(While we could deduce this as an application of the Stone-Weierstrass theorem, our proof of that relies on the fact that abs is in the closure of polynomials on [-M, M], so we may as well get this done first.)

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any two real numbers 
 and 
, the subalgebra of polynomial functions on the closed interval 
 is dense in the algebra of continuous real-valued functions 
 with respect to the uniform topology. That is, the topological closure of the set of polynomial functions is equal to the entire space of continuous functions.

Find similar
View Dependencies ▼
#### LeanFinder (name + statement)
Rank	Formal statement	Informal statement
1	
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ) (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
  ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
  use p
  rw [norm_lt_iff _ pos] at b
  intro x m
  exact b ⟨x, m⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any function 
f
 ⁣
:
R
→
R
f:R→R that is continuous on the closed interval 
[
a
,
b
]
[a,b], and any 
ε
>
0
ε>0, there exists a polynomial 
p
p with real coefficients such that for all 
x
∈
[
a
,
b
]
x∈[a,b], the absolute difference between 
p
(
x
)
p(x) and 
f
(
x
)
f(x) is less than 
ε
ε.
Copy
2	
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ) (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
  rw [Metric.mem_ball, dist_eq_norm] at H
  exact ⟨m, H⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any continuous function 
f
 ⁣
:
[
a
,
b
]
→
R
f:[a,b]→R, and any 
ε
>
0
ε>0, there exists a polynomial 
p
p such that the uniform norm of 
p
−
f
p−f on 
[
a
,
b
]
[a,b] is less than 
ε
ε.
Copy
3	
theorem bernsteinApproximation_uniform (f : C(I, ℝ)) : Tendsto (fun n : ℕ => bernsteinApproximation n f) atTop (𝓝 f) := by
  simp only [Metric.nhds_basis_ball.tendsto_right_iff, Metric.mem_ball, dist_eq_norm]
  intro ε h
  let δ := δ f ε h
  have nhds_zero := tendsto_const_div_atTop_nhds_zero_nat (2 * ‖f‖ * δ ^ (-2 : ℤ))
  filter_upwards [nhds_zero.eventually (gt_mem_nhds (half_pos h)), eventually_gt_atTop 0] with n nh
    npos'
  have npos : 0 < (n : ℝ) := by positivity
  -- As `[0,1]` is compact, it suffices to check the inequality pointwise.
  rw [ContinuousMap.norm_lt_iff _ h]
  intro x
  -- The idea is to split up the sum over `k` into two sets,
  -- `S`, where `x - k/n < δ`, and its complement.
  let S := S f ε h n x
  calc
    |(bernsteinApproximation n f - f) x| = |bernsteinApproximation n f x - f x| := rfl
    _ = |bernsteinApproximation n f x - f x * 1| := by rw [mul_one]
    _ = |bernsteinApproximation n f x - f x * ∑ k : Fin (n + 1), bernstein n k x| := by
      rw [bernstein.probability]
    _ = |∑ k : Fin (n + 1), (f k/ₙ - f x) * bernstein n k x| := by
      simp [bernsteinApproximation, Finset.mul_sum, sub_mul]
    _ ≤ ∑ k : Fin (n + 1), |(f k/ₙ - f x) * bernstein n k x| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ k : Fin (n + 1), |f k/ₙ - f x| * bernstein n k x := by
      simp_rw [abs_mul, abs_eq_self.mpr bernstein_nonneg]
    _ = (∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x) + ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x :=
      (S.sum_add_sum_compl _).symm
    -- We'll now deal with the terms in `S` and the terms in `Sᶜ` in separate calc blocks.
    _ < ε / 2 + ε / 2 :=
      (add_lt_add_of_le_of_lt ?_ ?_)
    _ = ε := add_halves ε
  · -- We now work on the terms in `S`: uniform continuity and `bernstein.probability`
    -- quickly give us a bound.
    calc
      ∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ S, ε / 2 * bernstein n k x := by
        gcongr with _ m
        exact le_of_lt (lt_of_mem_S m)
      _ = ε / 2 * ∑ k ∈ S, bernstein n k x := by rw [Finset.mul_sum]
      -- In this step we increase the sum over `S` back to a sum over all of `Fin (n+1)`,
      -- so that we can use `bernstein.probability`.
      _ ≤ ε / 2 * ∑ k : Fin (n + 1), bernstein n k x := by gcongr; exact S.subset_univ
      _ = ε / 2 := by rw [bernstein.probability, mul_one]
  · -- We now turn to working on `Sᶜ`: we control the difference term just using `‖f‖`,
    -- and then insert a `δ^(-2) * (x - k/n)^2` factor
    -- (which is at least one because we are not in `S`).
    calc
      ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ Sᶜ, 2 * ‖f‖ * bernstein n k x := by
        gcongr
        apply f.dist_le_two_norm
      _ = 2 * ‖f‖ * ∑ k ∈ Sᶜ, bernstein n k x := by rw [Finset.mul_sum]
      _ ≤ 2 * ‖f‖ * ∑ k ∈ Sᶜ, δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr with _ m
        conv_lhs => rw [← one_mul (bernstein _ _ _)]
        gcongr
        exact le_of_mem_S_compl m
      -- Again enlarging the sum from `Sᶜ` to all of `Fin (n+1)`
      _ ≤ 2 * ‖f‖ * ∑ k : Fin (n + 1), δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr; exact Sᶜ.subset_univ
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * ∑ k : Fin (n + 1), ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        conv_rhs =>
          rw [mul_assoc, Finset.mul_sum]
          simp only [← mul_assoc]
      -- `bernstein.variance` and `x ∈ [0,1]` gives the uniform bound
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * x * (1 - x) / n := by rw [variance npos]; ring
      _ ≤ 2 * ‖f‖ * δ ^ (-2 : ℤ) * 1 * 1 / n := by gcongr <;> unit_interval
      _ < ε / 2 := by simp only [mul_one]; exact nh
Doc
Copy
👍
👎
For any continuous function 
f
∈
C
(
[
0
,
1
]
,
R
)
f∈C([0,1],R), the sequence of Bernstein approximations 
(
B
n
(
f
)
)
n
∈
N
(B 
n
​
 (f)) 
n∈N
​
  converges uniformly to 
f
f as 
n
→
∞
n→∞, where the 
n
n-th Bernstein approximation is given by:
\[ B_n(f)(x) = \sum_{k=0}^n f\left(\frac{k}{n}\right) \binom{n}{k} x^k (1-x)^{n-k}. \]
Copy
4	
/-- A variant of the Stone-Weierstrass theorem where `X` need not be compact:
If `A` is a subalgebra of `C(X, ℝ)` which separates points, then, for any compact set `K ⊆ X`,
every real-valued continuous function on `X` is within any `ε > 0` of some element of `A` on `K`. -/
theorem exists_mem_subalgebra_near_continuous_of_isCompact_of_separatesPoints
    {X : Type*} [TopologicalSpace X] {A : Subalgebra ℝ C(X, ℝ)} (hA : A.SeparatesPoints)
    (f : C(X, ℝ)) {K : Set X} (hK : IsCompact K) {ε : ℝ} (pos : 0 < ε) :
    ∃ g ∈ A, ∀ x ∈ K, ‖(g : X → ℝ) x - f x‖ < ε := by
  let restrict_on_K : C(X, ℝ) →⋆ₐ[ℝ] C(K, ℝ) :=
    ContinuousMap.compStarAlgHom' ℝ ℝ ⟨(Subtype.val), continuous_subtype_val⟩
  --consider the subalgebra AK of functions with domain K
  let AK : Subalgebra ℝ C(K, ℝ) := Subalgebra.map (restrict_on_K) A
  have hsep : AK.SeparatesPoints := by
    intro x y hxy
    obtain ⟨_, ⟨g, hg1, hg2⟩, hg_sep⟩ := hA (Subtype.coe_ne_coe.mpr hxy)
    simp only [Set.mem_image, SetLike.mem_coe, exists_exists_and_eq_and]
    use restrict_on_K g
    refine ⟨Subalgebra.mem_map.mpr ?_,
      by simpa only [compStarAlgHom'_apply, comp_apply, coe_mk, ne_eq, restrict_on_K, hg2]⟩
    use g, hg1
    simp [AlgHom.coe_coe]
  obtain ⟨⟨gK, hgKAK⟩, hgapprox⟩ :=
    @ContinuousMap.exists_mem_subalgebra_near_continuous_of_separatesPoints _ _
    (isCompact_iff_compactSpace.mp hK) AK hsep (K.restrict f)
    (ContinuousOn.restrict (Continuous.continuousOn f.continuous)) ε pos
  obtain ⟨g, hgA, hgKAK⟩ := Subalgebra.mem_map.mp hgKAK
  use g, hgA
  intro x hxK
  have eqg : g x = gK ⟨x, hxK⟩ := by
    rw [← hgKAK]; rfl
  rw [eqg]
  exact hgapprox ⟨x, hxK⟩
Doc
Copy
👍
👎
Let 
X
X be a topological space and 
A
A a subalgebra of the space of continuous real-valued functions 
C
(
X
,
R
)
C(X,R). If 
A
A separates points, then for any compact set 
K
⊆
X
K⊆X, any continuous function 
f
 ⁣
:
X
→
R
f:X→R, and any 
ε
>
0
ε>0, there exists a function 
g
∈
A
g∈A such that for all 
x
∈
K
x∈K, 
∥
g
(
x
)
−
f
(
x
)
∥
<
ε
∥g(x)−f(x)∥<ε. This is a variant of the Stone-Weierstrass theorem where 
X
X need not be compact.
Copy
5	
definition bernsteinApproximation.δ (f : C(I, ℝ)) (ε : ℝ) (h : 0 < ε) : ℝ :=
  f.modulus (ε / 2) (half_pos h)
Doc
Copy
👍
👎
For a continuous function \( f \in C([0,1], \mathbb{R}) \) and \( \varepsilon > 0 \), the modulus of uniform continuity \( \delta(f, \varepsilon) \) is chosen such that for any \( x, y \in [0,1] \), if \( |x - y| < \delta \) then \( |f(x) - f(y)| < \varepsilon/2 \).
Copy
### exists_polynomial_

#### Query (name + statement)

```text
exists_polynomial_
theorem weierstrass_approximation (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
    (ε : ℝ) (hε : ε > 0) :
    ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε
```

#### LeanExplore (name + statement)
exists_polynomial_near_of_continuousOn
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ)
    (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
    ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
...
Show all
Docstring:
Another alternative statement of Weierstrass's theorem, for those who like epsilons, but not bundled continuous functions.

Every real-valued function ℝ → ℝ which is continuous on [a,b] can be approximated to within any ε > 0 on [a,b] by some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real-valued function 
 that is continuous on a closed interval 
 and for any 
, there exists a polynomial 
 such that for all 
, the inequality 
 holds.

Find similar
View Dependencies ▼
exists_polynomial_near_continuousMap
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ)
    (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
...
Show all
Docstring:
An alternative statement of Weierstrass' theorem, for those who like their epsilons.

Every real-valued continuous function on [a,b] is within any ε > 0 of some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real numbers 
 and 
, and any continuous real-valued function 
 defined on the closed interval 
, there exists a polynomial 
 such that for any 
, the supremum norm of the difference between 
 and the restriction of 
 to 
 is strictly less than 
.

Find similar
View Dependencies ▼
polynomialFunctions_closure_eq_top'
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem polynomialFunctions_closure_eq_top' : (polynomialFunctions I).topologicalClosure = ⊤ := by
  apply top_unique
  rintro f -
  refine mem_closure_of_tendsto (bernsteinApproximation_uniform f) <| .of_forall fun n ↦ ?_
  apply Subalgebra.sum_mem
...
Show all
Docstring:
The special case of the Weierstrass approximation theorem for the interval [0,1]. This is just a matter of unravelling definitions and using the Bernstein approximations.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem on the Unit Interval. The subalgebra of polynomial functions on the unit interval 
 is dense in the algebra of all continuous real-valued functions on 
 under the topology of uniform convergence. That is, the topological closure of the set of polynomial functions is equal to the entire space of continuous functions.

Find similar
View Dependencies ▼
polynomialFunctions_closure_eq_top
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem polynomialFunctions_closure_eq_top (a b : ℝ) :
    (polynomialFunctions (Set.Icc a b)).topologicalClosure = ⊤ := by
  rcases lt_or_ge a b with h | h
  · 
    let W : C(Set.Icc a b, ℝ) →ₐ[ℝ] C(I, ℝ) :=
...
Show all
Docstring:
The Weierstrass Approximation Theorem: polynomials functions on [a, b] ⊆ ℝ are dense in C([a,b],ℝ)

(While we could deduce this as an application of the Stone-Weierstrass theorem, our proof of that relies on the fact that abs is in the closure of polynomials on [-M, M], so we may as well get this done first.)

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any two real numbers 
 and 
, the subalgebra of polynomial functions on the closed interval 
 is dense in the algebra of continuous real-valued functions 
 with respect to the uniform topology. That is, the topological closure of the set of polynomial functions is equal to the entire space of continuous functions.

Find similar
View Dependencies ▼
ContinuousMap.exists_mem_subalgebra_near_continuous_of_separatesPoints
In: Mathlib.Topology.ContinuousMap.StoneWeierstrass

Lean Code:
theorem exists_mem_subalgebra_near_continuous_of_separatesPoints (A : Subalgebra ℝ C(X, ℝ))
    (w : A.SeparatesPoints) (f : X → ℝ) (c : Continuous f) (ε : ℝ) (pos : 0 < ε) :
    ∃ g : A, ∀ x, ‖(g : X → ℝ) x - f x‖ < ε := by
  obtain ⟨g, b⟩ := exists_mem_subalgebra_near_continuousMap_of_separatesPoints A w ⟨f, c⟩ ε pos
  use g
...
Show all
Docstring:
An alternative statement of the Stone-Weierstrass theorem, for those who like their epsilons and don't like bundled continuous functions.

If A is a subalgebra of C(X, ℝ) which separates points (and X is compact), every real-valued continuous function on X is within any ε > 0 of some element of A.

Gemini 3.0 Flash:
Stone-Weierstrass Theorem (Epsilon-Delta Form). Let 
 be a compact topological space and let 
 be a subalgebra of the algebra of continuous real-valued functions 
. If 
 separates points, then for every continuous function 
 and every 
, there exists a function 
 such that 
 for all 
.

Find similar
View Dependencies ▼
#### LeanFinder (name + statement)
Rank	Formal statement	Informal statement
1	
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ) (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
  ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
  use p
  rw [norm_lt_iff _ pos] at b
  intro x m
  exact b ⟨x, m⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any function 
f
 ⁣
:
R
→
R
f:R→R that is continuous on the closed interval 
[
a
,
b
]
[a,b], and any 
ε
>
0
ε>0, there exists a polynomial 
p
p with real coefficients such that for all 
x
∈
[
a
,
b
]
x∈[a,b], the absolute difference between 
p
(
x
)
p(x) and 
f
(
x
)
f(x) is less than 
ε
ε.
Copy
2	
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ) (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
  rw [Metric.mem_ball, dist_eq_norm] at H
  exact ⟨m, H⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any continuous function 
f
 ⁣
:
[
a
,
b
]
→
R
f:[a,b]→R, and any 
ε
>
0
ε>0, there exists a polynomial 
p
p such that the uniform norm of 
p
−
f
p−f on 
[
a
,
b
]
[a,b] is less than 
ε
ε.
Copy
3	
theorem bernsteinApproximation_uniform (f : C(I, ℝ)) : Tendsto (fun n : ℕ => bernsteinApproximation n f) atTop (𝓝 f) := by
  simp only [Metric.nhds_basis_ball.tendsto_right_iff, Metric.mem_ball, dist_eq_norm]
  intro ε h
  let δ := δ f ε h
  have nhds_zero := tendsto_const_div_atTop_nhds_zero_nat (2 * ‖f‖ * δ ^ (-2 : ℤ))
  filter_upwards [nhds_zero.eventually (gt_mem_nhds (half_pos h)), eventually_gt_atTop 0] with n nh
    npos'
  have npos : 0 < (n : ℝ) := by positivity
  -- As `[0,1]` is compact, it suffices to check the inequality pointwise.
  rw [ContinuousMap.norm_lt_iff _ h]
  intro x
  -- The idea is to split up the sum over `k` into two sets,
  -- `S`, where `x - k/n < δ`, and its complement.
  let S := S f ε h n x
  calc
    |(bernsteinApproximation n f - f) x| = |bernsteinApproximation n f x - f x| := rfl
    _ = |bernsteinApproximation n f x - f x * 1| := by rw [mul_one]
    _ = |bernsteinApproximation n f x - f x * ∑ k : Fin (n + 1), bernstein n k x| := by
      rw [bernstein.probability]
    _ = |∑ k : Fin (n + 1), (f k/ₙ - f x) * bernstein n k x| := by
      simp [bernsteinApproximation, Finset.mul_sum, sub_mul]
    _ ≤ ∑ k : Fin (n + 1), |(f k/ₙ - f x) * bernstein n k x| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ k : Fin (n + 1), |f k/ₙ - f x| * bernstein n k x := by
      simp_rw [abs_mul, abs_eq_self.mpr bernstein_nonneg]
    _ = (∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x) + ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x :=
      (S.sum_add_sum_compl _).symm
    -- We'll now deal with the terms in `S` and the terms in `Sᶜ` in separate calc blocks.
    _ < ε / 2 + ε / 2 :=
      (add_lt_add_of_le_of_lt ?_ ?_)
    _ = ε := add_halves ε
  · -- We now work on the terms in `S`: uniform continuity and `bernstein.probability`
    -- quickly give us a bound.
    calc
      ∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ S, ε / 2 * bernstein n k x := by
        gcongr with _ m
        exact le_of_lt (lt_of_mem_S m)
      _ = ε / 2 * ∑ k ∈ S, bernstein n k x := by rw [Finset.mul_sum]
      -- In this step we increase the sum over `S` back to a sum over all of `Fin (n+1)`,
      -- so that we can use `bernstein.probability`.
      _ ≤ ε / 2 * ∑ k : Fin (n + 1), bernstein n k x := by gcongr; exact S.subset_univ
      _ = ε / 2 := by rw [bernstein.probability, mul_one]
  · -- We now turn to working on `Sᶜ`: we control the difference term just using `‖f‖`,
    -- and then insert a `δ^(-2) * (x - k/n)^2` factor
    -- (which is at least one because we are not in `S`).
    calc
      ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ Sᶜ, 2 * ‖f‖ * bernstein n k x := by
        gcongr
        apply f.dist_le_two_norm
      _ = 2 * ‖f‖ * ∑ k ∈ Sᶜ, bernstein n k x := by rw [Finset.mul_sum]
      _ ≤ 2 * ‖f‖ * ∑ k ∈ Sᶜ, δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr with _ m
        conv_lhs => rw [← one_mul (bernstein _ _ _)]
        gcongr
        exact le_of_mem_S_compl m
      -- Again enlarging the sum from `Sᶜ` to all of `Fin (n+1)`
      _ ≤ 2 * ‖f‖ * ∑ k : Fin (n + 1), δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr; exact Sᶜ.subset_univ
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * ∑ k : Fin (n + 1), ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        conv_rhs =>
          rw [mul_assoc, Finset.mul_sum]
          simp only [← mul_assoc]
      -- `bernstein.variance` and `x ∈ [0,1]` gives the uniform bound
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * x * (1 - x) / n := by rw [variance npos]; ring
      _ ≤ 2 * ‖f‖ * δ ^ (-2 : ℤ) * 1 * 1 / n := by gcongr <;> unit_interval
      _ < ε / 2 := by simp only [mul_one]; exact nh
Doc
Copy
👍
👎
For any continuous function 
f
∈
C
(
[
0
,
1
]
,
R
)
f∈C([0,1],R), the sequence of Bernstein approximations 
(
B
n
(
f
)
)
n
∈
N
(B 
n
​
 (f)) 
n∈N
​
  converges uniformly to 
f
f as 
n
→
∞
n→∞, where the 
n
n-th Bernstein approximation is given by:
\[ B_n(f)(x) = \sum_{k=0}^n f\left(\frac{k}{n}\right) \binom{n}{k} x^k (1-x)^{n-k}. \]
Copy
4	
/-- A variant of the Stone-Weierstrass theorem where `X` need not be compact:
If `A` is a subalgebra of `C(X, ℝ)` which separates points, then, for any compact set `K ⊆ X`,
every real-valued continuous function on `X` is within any `ε > 0` of some element of `A` on `K`. -/
theorem exists_mem_subalgebra_near_continuous_of_isCompact_of_separatesPoints
    {X : Type*} [TopologicalSpace X] {A : Subalgebra ℝ C(X, ℝ)} (hA : A.SeparatesPoints)
    (f : C(X, ℝ)) {K : Set X} (hK : IsCompact K) {ε : ℝ} (pos : 0 < ε) :
    ∃ g ∈ A, ∀ x ∈ K, ‖(g : X → ℝ) x - f x‖ < ε := by
  let restrict_on_K : C(X, ℝ) →⋆ₐ[ℝ] C(K, ℝ) :=
    ContinuousMap.compStarAlgHom' ℝ ℝ ⟨(Subtype.val), continuous_subtype_val⟩
  --consider the subalgebra AK of functions with domain K
  let AK : Subalgebra ℝ C(K, ℝ) := Subalgebra.map (restrict_on_K) A
  have hsep : AK.SeparatesPoints := by
    intro x y hxy
    obtain ⟨_, ⟨g, hg1, hg2⟩, hg_sep⟩ := hA (Subtype.coe_ne_coe.mpr hxy)
    simp only [Set.mem_image, SetLike.mem_coe, exists_exists_and_eq_and]
    use restrict_on_K g
    refine ⟨Subalgebra.mem_map.mpr ?_,
      by simpa only [compStarAlgHom'_apply, comp_apply, coe_mk, ne_eq, restrict_on_K, hg2]⟩
    use g, hg1
    simp [AlgHom.coe_coe]
  obtain ⟨⟨gK, hgKAK⟩, hgapprox⟩ :=
    @ContinuousMap.exists_mem_subalgebra_near_continuous_of_separatesPoints _ _
    (isCompact_iff_compactSpace.mp hK) AK hsep (K.restrict f)
    (ContinuousOn.restrict (Continuous.continuousOn f.continuous)) ε pos
  obtain ⟨g, hgA, hgKAK⟩ := Subalgebra.mem_map.mp hgKAK
  use g, hgA
  intro x hxK
  have eqg : g x = gK ⟨x, hxK⟩ := by
    rw [← hgKAK]; rfl
  rw [eqg]
  exact hgapprox ⟨x, hxK⟩
Doc
Copy
👍
👎
Let 
X
X be a topological space and 
A
A a subalgebra of the space of continuous real-valued functions 
C
(
X
,
R
)
C(X,R). If 
A
A separates points, then for any compact set 
K
⊆
X
K⊆X, any continuous function 
f
 ⁣
:
X
→
R
f:X→R, and any 
ε
>
0
ε>0, there exists a function 
g
∈
A
g∈A such that for all 
x
∈
K
x∈K, 
∥
g
(
x
)
−
f
(
x
)
∥
<
ε
∥g(x)−f(x)∥<ε. This is a variant of the Stone-Weierstrass theorem where 
X
X need not be compact.
Copy
5	
definition bernsteinApproximation (n : ℕ) (f : C(I, ℝ)) : C(I, ℝ) :=
  ∑ k : Fin (n + 1), f k/ₙ • bernstein n k
Doc
Copy
👍
👎
The 
n
n-th Bernstein approximation of a continuous function 
f
∈
C
(
[
0
,
1
]
,
R
)
f∈C([0,1],R) is the continuous function on 
[
0
,
1
]
[0,1] defined by:
\[ B_n(f)(x) = \sum_{k=0}^n f\left(\frac{k}{n}\right) \cdot B_{n,k}(x) \]
where 
B
n
,
k
(
x
)
=
(
n
k
)
x
k
(
1
−
x
)
n
−
k
B 
n,k
​
 (x)=( 
k
n
​
 )x 
k
 (1−x) 
n−k
  is the Bernstein polynomial of degree 
n
n and index 
k
k.
Copy
### exists_polynomial_onic_forall_Icc_norm_lt

#### Query (name + statement)

```text
exists_polynomial_onic_forall_Icc_norm_lt
theorem weierstrass_approximation (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
    (ε : ℝ) (hε : ε > 0) :
    ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε
```

#### LeanExplore (name + statement)
taylor_mean_remainder_bound
In: Mathlib.Analysis.Calculus.Taylor

Lean Code:
theorem taylor_mean_remainder_bound {f : ℝ → E} {a b C x : ℝ} {n : ℕ} (hab : a ≤ b)
    (hf : ContDiffOn ℝ (n + 1) f (Icc a b)) (hx : x ∈ Icc a b)
    (hC : ∀ y ∈ Icc a b, ‖iteratedDerivWithin (n + 1) f (Icc a b) y‖ ≤ C) :
    ‖f x - taylorWithinEval f n (Icc a b) a x‖ ≤ C * (x - a) ^ (n + 1) / n ! := by
  rcases eq_or_lt_of_le hab with (rfl | h)
...
Show all
Docstring:
Taylor's theorem with a polynomial bound on the remainder

We assume that f is n+1-times continuously differentiable on the closed set Icc a b. The difference of f and its n-th Taylor polynomial can be estimated by C * (x - a)^(n+1) / n! where C is a bound for the n+1-th iterated derivative of f.

Gemini 3.0 Flash:
Taylor's Theorem with a Polynomial Remainder Bound. Let 
 be a function into a normed space 
 that is 
-times continuously differentiable on the closed interval 
. Suppose there exists a constant 
 such that the norm of the 
-th iterated derivative of 
 (taken within 
) is bounded by 
 for all 
. Then for any 
, the norm of the difference between 
 and its 
-th order Taylor polynomial evaluated at 
 (with base point 
) is bounded by: 
 

Find similar
View Dependencies ▼
Set.Icc
In: Mathlib.Order.Interval.Set.Defs

Lean Code:
@[to_dual self (reorder := a b)]
def Icc (a b : α) := { x | a ≤ x ∧ x ≤ b }
Show all
Docstring:
Icc a b is the left-closed right-closed interval 
.

Gemini 3.0 Flash:
Closed Interval. For any two elements 
 and 
 in a preordered set, the closed interval 
 is the set of all elements 
 such that 
 and 
.

Find similar
View Dependencies ▼
exists_polynomial_near_of_continuousOn
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ)
    (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
    ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
...
Show all
Docstring:
Another alternative statement of Weierstrass's theorem, for those who like epsilons, but not bundled continuous functions.

Every real-valued function ℝ → ℝ which is continuous on [a,b] can be approximated to within any ε > 0 on [a,b] by some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real-valued function 
 that is continuous on a closed interval 
 and for any 
, there exists a polynomial 
 such that for all 
, the inequality 
 holds.

Find similar
View Dependencies ▼
exists_polynomial_near_continuousMap
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ)
    (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
...
Show all
Docstring:
An alternative statement of Weierstrass' theorem, for those who like their epsilons.

Every real-valued continuous function on [a,b] is within any ε > 0 of some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real numbers 
 and 
, and any continuous real-valued function 
 defined on the closed interval 
, there exists a polynomial 
 such that for any 
, the supremum norm of the difference between 
 and the restriction of 
 to 
 is strictly less than 
.

Find similar
View Dependencies ▼
polynomialFunctions_closure_eq_top'
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem polynomialFunctions_closure_eq_top' : (polynomialFunctions I).topologicalClosure = ⊤ := by
  apply top_unique
  rintro f -
  refine mem_closure_of_tendsto (bernsteinApproximation_uniform f) <| .of_forall fun n ↦ ?_
  apply Subalgebra.sum_mem
...
Show all
Docstring:
The special case of the Weierstrass approximation theorem for the interval [0,1]. This is just a matter of unravelling definitions and using the Bernstein approximations.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem on the Unit Interval. The subalgebra of polynomial functions on the unit interval 
 is dense in the algebra of all continuous real-valued functions on 
 under the topology of uniform convergence. That is, the topological closure of the set of polynomial functions is equal to the entire space of continuous functions.

Find similar
View Dependencies ▼
#### LeanFinder (name + statement)
Rank	Formal statement	Informal statement
1	
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ) (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
  ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
  use p
  rw [norm_lt_iff _ pos] at b
  intro x m
  exact b ⟨x, m⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any function 
f
 ⁣
:
R
→
R
f:R→R that is continuous on the closed interval 
[
a
,
b
]
[a,b], and any 
ε
>
0
ε>0, there exists a polynomial 
p
p with real coefficients such that for all 
x
∈
[
a
,
b
]
x∈[a,b], the absolute difference between 
p
(
x
)
p(x) and 
f
(
x
)
f(x) is less than 
ε
ε.
Copy
2	
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ) (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
  rw [Metric.mem_ball, dist_eq_norm] at H
  exact ⟨m, H⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any continuous function 
f
 ⁣
:
[
a
,
b
]
→
R
f:[a,b]→R, and any 
ε
>
0
ε>0, there exists a polynomial 
p
p such that the uniform norm of 
p
−
f
p−f on 
[
a
,
b
]
[a,b] is less than 
ε
ε.
Copy
3	
theorem bernsteinApproximation_uniform (f : C(I, ℝ)) : Tendsto (fun n : ℕ => bernsteinApproximation n f) atTop (𝓝 f) := by
  simp only [Metric.nhds_basis_ball.tendsto_right_iff, Metric.mem_ball, dist_eq_norm]
  intro ε h
  let δ := δ f ε h
  have nhds_zero := tendsto_const_div_atTop_nhds_zero_nat (2 * ‖f‖ * δ ^ (-2 : ℤ))
  filter_upwards [nhds_zero.eventually (gt_mem_nhds (half_pos h)), eventually_gt_atTop 0] with n nh
    npos'
  have npos : 0 < (n : ℝ) := by positivity
  -- As `[0,1]` is compact, it suffices to check the inequality pointwise.
  rw [ContinuousMap.norm_lt_iff _ h]
  intro x
  -- The idea is to split up the sum over `k` into two sets,
  -- `S`, where `x - k/n < δ`, and its complement.
  let S := S f ε h n x
  calc
    |(bernsteinApproximation n f - f) x| = |bernsteinApproximation n f x - f x| := rfl
    _ = |bernsteinApproximation n f x - f x * 1| := by rw [mul_one]
    _ = |bernsteinApproximation n f x - f x * ∑ k : Fin (n + 1), bernstein n k x| := by
      rw [bernstein.probability]
    _ = |∑ k : Fin (n + 1), (f k/ₙ - f x) * bernstein n k x| := by
      simp [bernsteinApproximation, Finset.mul_sum, sub_mul]
    _ ≤ ∑ k : Fin (n + 1), |(f k/ₙ - f x) * bernstein n k x| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ k : Fin (n + 1), |f k/ₙ - f x| * bernstein n k x := by
      simp_rw [abs_mul, abs_eq_self.mpr bernstein_nonneg]
    _ = (∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x) + ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x :=
      (S.sum_add_sum_compl _).symm
    -- We'll now deal with the terms in `S` and the terms in `Sᶜ` in separate calc blocks.
    _ < ε / 2 + ε / 2 :=
      (add_lt_add_of_le_of_lt ?_ ?_)
    _ = ε := add_halves ε
  · -- We now work on the terms in `S`: uniform continuity and `bernstein.probability`
    -- quickly give us a bound.
    calc
      ∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ S, ε / 2 * bernstein n k x := by
        gcongr with _ m
        exact le_of_lt (lt_of_mem_S m)
      _ = ε / 2 * ∑ k ∈ S, bernstein n k x := by rw [Finset.mul_sum]
      -- In this step we increase the sum over `S` back to a sum over all of `Fin (n+1)`,
      -- so that we can use `bernstein.probability`.
      _ ≤ ε / 2 * ∑ k : Fin (n + 1), bernstein n k x := by gcongr; exact S.subset_univ
      _ = ε / 2 := by rw [bernstein.probability, mul_one]
  · -- We now turn to working on `Sᶜ`: we control the difference term just using `‖f‖`,
    -- and then insert a `δ^(-2) * (x - k/n)^2` factor
    -- (which is at least one because we are not in `S`).
    calc
      ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ Sᶜ, 2 * ‖f‖ * bernstein n k x := by
        gcongr
        apply f.dist_le_two_norm
      _ = 2 * ‖f‖ * ∑ k ∈ Sᶜ, bernstein n k x := by rw [Finset.mul_sum]
      _ ≤ 2 * ‖f‖ * ∑ k ∈ Sᶜ, δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr with _ m
        conv_lhs => rw [← one_mul (bernstein _ _ _)]
        gcongr
        exact le_of_mem_S_compl m
      -- Again enlarging the sum from `Sᶜ` to all of `Fin (n+1)`
      _ ≤ 2 * ‖f‖ * ∑ k : Fin (n + 1), δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr; exact Sᶜ.subset_univ
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * ∑ k : Fin (n + 1), ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        conv_rhs =>
          rw [mul_assoc, Finset.mul_sum]
          simp only [← mul_assoc]
      -- `bernstein.variance` and `x ∈ [0,1]` gives the uniform bound
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * x * (1 - x) / n := by rw [variance npos]; ring
      _ ≤ 2 * ‖f‖ * δ ^ (-2 : ℤ) * 1 * 1 / n := by gcongr <;> unit_interval
      _ < ε / 2 := by simp only [mul_one]; exact nh
Doc
Copy
👍
👎
For any continuous function 
f
∈
C
(
[
0
,
1
]
,
R
)
f∈C([0,1],R), the sequence of Bernstein approximations 
(
B
n
(
f
)
)
n
∈
N
(B 
n
​
 (f)) 
n∈N
​
  converges uniformly to 
f
f as 
n
→
∞
n→∞, where the 
n
n-th Bernstein approximation is given by:
\[ B_n(f)(x) = \sum_{k=0}^n f\left(\frac{k}{n}\right) \binom{n}{k} x^k (1-x)^{n-k}. \]
Copy
4	
theorem exists_taylor_mean_remainder_bound {f : ℝ → E} {a b : ℝ} {n : ℕ} (hab : a ≤ b) (hf : ContDiffOn ℝ (n + 1) f (Icc a b)) :
  ∃ C, ∀ x ∈ Icc a b, ‖f x - taylorWithinEval f n (Icc a b) a x‖ ≤ C * (x - a) ^ (n + 1) := by
  rcases eq_or_lt_of_le hab with (rfl | h)
  · refine ⟨0, fun x hx => ?_⟩
    have : x = a := by simpa [← le_antisymm_iff] using hx
    simp [← this]
  -- We estimate by the supremum of the norm of the iterated derivative
  let g : ℝ → ℝ := fun y => ‖iteratedDerivWithin (n + 1) f (Icc a b) y‖
  use SupSet.sSup (g '' Icc a b) / (n !)
  intro x hx
  rw [div_mul_eq_mul_div₀]
  refine taylor_mean_remainder_bound hab hf hx fun y => ?_
  exact (hf.continuousOn_iteratedDerivWithin rfl.le <| uniqueDiffOn_Icc h).norm.le_sSup_image_Icc
Doc
Copy
👍
👎
Let 
f
 ⁣
:
R
→
E
f:R→E be a function where 
E
E is a normed vector space over 
R
R. Given real numbers 
a
≤
b
a≤b and a natural number 
n
∈
N
n∈N, if 
f
f is 
(
n
+
1
)
(n+1)-times continuously differentiable on the closed interval 
[
a
,
b
]
[a,b], then there exists a constant 
C
≥
0
C≥0 such that for all 
x
∈
[
a
,
b
]
x∈[a,b], the difference between 
f
(
x
)
f(x) and its 
n
n-th degree Taylor polynomial centered at 
a
a is bounded by:
∥
f
(
x
)
−
T
n
(
f
)
(
a
,
x
)
∥
≤
C
(
x
−
a
)
n
+
1
∥f(x)−T 
n
​
 (f)(a,x)∥≤C(x−a) 
n+1
 

where 
T
n
(
f
)
(
a
,
x
)
T 
n
​
 (f)(a,x) denotes the Taylor polynomial of degree 
n
n evaluated at 
x
x.
Copy
5	
/-- A variant of the Stone-Weierstrass theorem where `X` need not be compact:
If `A` is a subalgebra of `C(X, ℝ)` which separates points, then, for any compact set `K ⊆ X`,
every real-valued continuous function on `X` is within any `ε > 0` of some element of `A` on `K`. -/
theorem exists_mem_subalgebra_near_continuous_of_isCompact_of_separatesPoints
    {X : Type*} [TopologicalSpace X] {A : Subalgebra ℝ C(X, ℝ)} (hA : A.SeparatesPoints)
    (f : C(X, ℝ)) {K : Set X} (hK : IsCompact K) {ε : ℝ} (pos : 0 < ε) :
    ∃ g ∈ A, ∀ x ∈ K, ‖(g : X → ℝ) x - f x‖ < ε := by
  let restrict_on_K : C(X, ℝ) →⋆ₐ[ℝ] C(K, ℝ) :=
    ContinuousMap.compStarAlgHom' ℝ ℝ ⟨(Subtype.val), continuous_subtype_val⟩
  --consider the subalgebra AK of functions with domain K
  let AK : Subalgebra ℝ C(K, ℝ) := Subalgebra.map (restrict_on_K) A
  have hsep : AK.SeparatesPoints := by
    intro x y hxy
    obtain ⟨_, ⟨g, hg1, hg2⟩, hg_sep⟩ := hA (Subtype.coe_ne_coe.mpr hxy)
    simp only [Set.mem_image, SetLike.mem_coe, exists_exists_and_eq_and]
    use restrict_on_K g
    refine ⟨Subalgebra.mem_map.mpr ?_,
      by simpa only [compStarAlgHom'_apply, comp_apply, coe_mk, ne_eq, restrict_on_K, hg2]⟩
    use g, hg1
    simp [AlgHom.coe_coe]
  obtain ⟨⟨gK, hgKAK⟩, hgapprox⟩ :=
    @ContinuousMap.exists_mem_subalgebra_near_continuous_of_separatesPoints _ _
    (isCompact_iff_compactSpace.mp hK) AK hsep (K.restrict f)
    (ContinuousOn.restrict (Continuous.continuousOn f.continuous)) ε pos
  obtain ⟨g, hgA, hgKAK⟩ := Subalgebra.mem_map.mp hgKAK
  use g, hgA
  intro x hxK
  have eqg : g x = gK ⟨x, hxK⟩ := by
    rw [← hgKAK]; rfl
  rw [eqg]
  exact hgapprox ⟨x, hxK⟩
Doc
Copy
👍
👎
Let 
X
X be a topological space and 
A
A a subalgebra of the space of continuous real-valued functions 
C
(
X
,
R
)
C(X,R). If 
A
A separates points, then for any compact set 
K
⊆
X
K⊆X, any continuous function 
f
 ⁣
:
X
→
R
f:X→R, and any 
ε
>
0
ε>0, there exists a function 
g
∈
A
g∈A such that for all 
x
∈
K
x∈K, 
∥
g
(
x
)
−
f
(
x
)
∥
<
ε
∥g(x)−f(x)∥<ε. This is a variant of the Stone-Weierstrass theorem where 
X
X need not be compact.
Copy
### exists_sup_of_bddAbove'

#### Query (name + statement)

```text
exists_sup_of_bddAbove'
theorem exists_sup_of_bddAbove {A : Set ℝ} (hne : A.Nonempty) (hbd : BddAbove A) :
    ∃ s : ℝ, IsLUB A s
```

#### LeanExplore (name + statement)
BddAbove
In: Mathlib.Order.Bounds.Defs

Lean Code:
@[to_dual ]
def BddAbove (s : Set α) :=
  (upperBounds s).Nonempty
Show all
Docstring:
A set is bounded above if there exists an upper bound.

Gemini 3.0 Flash:
Bounded Above. A set 
 is bounded above if the set of its upper bounds is non-empty; that is, there exists an element that is greater than or equal to every element in 
.

Find similar
View Dependencies ▼
Real.isLUB_sSup
In: Mathlib.Data.Real.Archimedean

Lean Code:
protected theorem isLUB_sSup (h₁ : s.Nonempty) (h₂ : BddAbove s) : IsLUB s (sSup s) := by
  simp only [sSup_def, dif_pos (And.intro h₁ h₂)]
  apply Classical.choose_spec
Gemini 3.0 Flash:
Least Upper Bound Property of the Supremum. For any nonempty set of real numbers that is bounded above, its supremum is indeed its least upper bound.

Find similar
View Dependencies ▼
Ordinal.IsNormal.map_sSup_of_bddAbove
In: Mathlib.SetTheory.Ordinal.Family

Lean Code:
@[deprecated Order.IsNormal.map_sSup (since := "2025-12-25")]
theorem IsNormal.map_sSup_of_bddAbove {f : Ordinal.{u} → Ordinal.{v}} (H : Ordinal.IsNormal f)
    {s : Set Ordinal.{u}} (hs : BddAbove s) (hn : s.Nonempty) : f (sSup s) = sSup (f '' s) :=
  Order.IsNormal.map_sSup H hn hs
Gemini 3.0 Flash:
Normal Ordinal Functions Preserve Suprema of Bounded Sets. For any normal ordinal function 
 and any nonempty, bounded-above set of ordinals 
, the function 
 preserves the supremum of 
; that is, 
.

Find similar
View Dependencies ▼
csSup_le
In: Mathlib.Order.ConditionallyCompleteLattice.Basic

Lean Code:
theorem csSup_le (h₁ : s.Nonempty) (h₂ : ∀ b ∈ s, b ≤ a) : sSup s ≤ a :=
  ConditionallyCompleteLattice.csSup_le s a h₁ h₂
Gemini 3.0 Flash:
Least Upper Bound Property. In a conditionally complete lattice, if a set 
 is nonempty and 
 is an upper bound of 
, then the supremum of 
 is less than or equal to 
.

Find similar
View Dependencies ▼
WithBot.coe_sSup'
In: Mathlib.Order.ConditionallyCompleteLattice.Basic

Lean Code:
@[norm_cast]
theorem WithBot.coe_sSup' [SupSet α] {s : Set α} (hs : s.Nonempty) (h's : BddAbove s) :
    ↑(sSup s) = (sSup ((fun (a : α) ↦ ↑a) '' s) : WithBot α) :=
  WithTop.coe_sInf' (α := αᵒᵈ) hs h's
Gemini 3.0 Flash:
Supremum of a Nonempty Bounded Set in WithBot. For any nonempty set 
 that is bounded above in a type equipped with a supremum operator, the supremum of 
 in the original type, when embedded into the type extended with a bottom element, is equal to the supremum of the image of 
 under that embedding.

Find similar
View Dependencies ▼
#### LeanFinder (name + statement)
Rank	Formal statement	Informal statement
1	
theorem Real.exists_isLUB (hne : s.Nonempty) (hbdd : BddAbove s) : ∃ x, IsLUB s x := by
  rcases hne, hbdd with ⟨⟨L, hL⟩, ⟨U, hU⟩⟩
  have : ∀ d : ℕ, BddAbove { m : ℤ | ∃ y ∈ s, (m : ℝ) ≤ y * d } := by
    cases' exists_int_gt U with k hk
    refine fun d => ⟨k * d, fun z h => ?_⟩
    rcases h with ⟨y, yS, hy⟩
    refine Int.cast_le.1 (hy.trans ?_)
    push_cast
    exact mul_le_mul_of_nonneg_right ((hU yS).trans hk.le) d.cast_nonneg
  choose f hf using fun d : ℕ =>
    Int.exists_greatest_of_bdd (this d) ⟨⌊L * d⌋, L, hL, Int.floor_le _⟩
  have hf₁ : ∀ n > 0, ∃ y ∈ s, ((f n / n : ℚ) : ℝ) ≤ y := fun n n0 =>
    let ⟨y, yS, hy⟩ := (hf n).1
    ⟨y, yS, by simpa using (div_le_iff₀ (Nat.cast_pos.2 n0 : (_ : ℝ) < _)).2 hy⟩
  have hf₂ : ∀ n > 0, ∀ y ∈ s, (y - ((n : ℕ) : ℝ)⁻¹) < (f n / n : ℚ) := by
    intro n n0 y yS
    have := (Int.sub_one_lt_floor _).trans_le (Int.cast_le.2 <| (hf n).2 _ ⟨y, yS, Int.floor_le _⟩)
    simp only [Rat.cast_div, Rat.cast_intCast, Rat.cast_natCast, gt_iff_lt]
    rwa [lt_div_iff₀ (Nat.cast_pos.2 n0 : (_ : ℝ) < _), sub_mul, inv_mul_cancel₀]
    exact ne_of_gt (Nat.cast_pos.2 n0)
  have hg : IsCauSeq abs (fun n => f n / n : ℕ → ℚ) := by
    intro ε ε0
    suffices ∀ j ≥ ⌈ε⁻¹⌉₊, ∀ k ≥ ⌈ε⁻¹⌉₊, (f j / j - f k / k : ℚ) < ε by
      refine ⟨_, fun j ij => abs_lt.2 ⟨?_, this _ ij _ le_rfl⟩⟩
      rw [neg_lt, neg_sub]
      exact this _ le_rfl _ ij
    intro j ij k ik
    replace ij := le_trans (Nat.le_ceil _) (Nat.cast_le.2 ij)
    replace ik := le_trans (Nat.le_ceil _) (Nat.cast_le.2 ik)
    have j0 := Nat.cast_pos.1 ((inv_pos.2 ε0).trans_le ij)
    have k0 := Nat.cast_pos.1 ((inv_pos.2 ε0).trans_le ik)
    rcases hf₁ _ j0 with ⟨y, yS, hy⟩
    refine lt_of_lt_of_le ((Rat.cast_lt (K := ℝ)).1 ?_) ((inv_le_comm₀ ε0 (Nat.cast_pos.2 k0)).1 ik)
    simpa using sub_lt_iff_lt_add'.2 (lt_of_le_of_lt hy <| sub_lt_iff_lt_add.1 <| hf₂ _ k0 _ yS)
  let g : CauSeq ℚ abs := ⟨fun n => f n / n, hg⟩
  refine ⟨mk g, ⟨fun x xS => ?_, fun y h => ?_⟩⟩
  · refine le_of_forall_lt_imp_le_of_dense fun z xz => ?_
    cases' exists_nat_gt (x - z)⁻¹ with K hK
    refine le_mk_of_forall_le ⟨K, fun n nK => ?_⟩
    replace xz := sub_pos.2 xz
    replace hK := hK.le.trans (Nat.cast_le.2 nK)
    have n0 : 0 < n := Nat.cast_pos.1 ((inv_pos.2 xz).trans_le hK)
    refine le_trans ?_ (hf₂ _ n0 _ xS).le
    rwa [le_sub_comm, inv_le_comm₀ (Nat.cast_pos.2 n0 : (_ : ℝ) < _) xz]
  · exact
      mk_le_of_forall_le
        ⟨1, fun n n1 =>
          let ⟨x, xS, hx⟩ := hf₁ _ n1
          le_trans hx (h xS)⟩
Doc
Copy
👍
👎
For any nonempty set 
s
s of real numbers that is bounded above, there exists a real number 
x
x which is the least upper bound (supremum) of 
s
s.
Copy
2	
theorem Real.isLUB_sSup (h₁ : s.Nonempty) (h₂ : BddAbove s) : IsLUB s (sSup s) := by
  simp only [sSup_def, dif_pos (And.intro h₁ h₂)]
  apply Classical.choose_spec
Doc
Copy
👍
👎
For any nonempty set 
s
s of real numbers that is bounded above, the supremum 
sup
⁡
s
sups is the least upper bound of 
s
s.
Copy
3	
instance Real.instSupSet : SupSet ℝ :=
  ⟨fun s => if h : s.Nonempty ∧ BddAbove s then Classical.choose (exists_isLUB h.1 h.2) else 0⟩
Doc
Copy
👍
👎
The real numbers 
R
R form a conditionally complete linear order, meaning every nonempty subset of 
R
R that is bounded above has a least upper bound (supremum) in 
R
R.
Copy
4	
theorem Real.exists_isGLB (hne : s.Nonempty) (hbdd : BddBelow s) : ∃ x, IsGLB s x := by
  have hne' : (-s).Nonempty := Set.nonempty_neg.mpr hne
  have hbdd' : BddAbove (-s) := bddAbove_neg.mpr hbdd
  use -Classical.choose (Real.exists_isLUB hne' hbdd')
  rw [← isLUB_neg]
  exact Classical.choose_spec (Real.exists_isLUB hne' hbdd')
Doc
Copy
👍
👎
For any nonempty set 
s
s of real numbers that is bounded below, there exists a real number 
x
x which is the greatest lower bound (infimum) of 
s
s.
Copy
5	
theorem Real.sSup_def (s : Set ℝ) : sSup s = if h : s.Nonempty ∧ BddAbove s then Classical.choose (exists_isLUB h.1 h.2) else 0 :=
  rfl
Doc
Copy
👍
👎
For any set 
s
s of real numbers, the supremum 
sup
⁡
(
s
)
sup(s) is defined as follows: if 
s
s is nonempty and bounded above, then 
sup
⁡
(
s
)
sup(s) is the least upper bound of 
s
s (chosen via the axiom of choice); otherwise, 
sup
⁡
(
s
)
=
0
sup(s)=0.
Copy
### card_univ

#### Query (name + statement)

```text
card_univ
theorem excedance_coexcedance_dual {n : ℕ} (π : Perm (Fin n)) :
    (excedances π).card = (coexcedances π⁻¹).card
```

#### LeanExplore (name + statement)
Fin.revOrderIso_apply
In: Mathlib.Order.Fin.Basic

Lean Code:
@[simps! apply toEquiv]
def revOrderIso : (Fin n)ᵒᵈ ≃o Fin n := ⟨OrderDual.ofDual.trans revPerm, rev_le_rev⟩
Gemini 3.0 Flash:
Order Isomorphism between the Dual of Fin n and Fin n. For any natural number 
, there exists an order isomorphism between the order dual of the set 
 and the set itself. This isomorphism is defined by the reversal permutation, which maps each index 
 to 
.

Find similar
View Dependencies ▼
Fintype.card_perm
In: Mathlib.Data.Fintype.Perm

Lean Code:
theorem Fintype.card_perm [Fintype α] : Fintype.card (Perm α) = (Fintype.card α)! :=
  Subsingleton.elim (@fintypePerm α _ _) (@Equiv.instFintype α α _ _ _ _) ▸ card_perms_of_finset _
Gemini 3.0 Flash:
Cardinality of the Symmetric Group. For any finite type 
, the number of permutations of 
 is equal to the factorial of the number of elements in 
; that is, 
.

Find similar
View Dependencies ▼
Finset.card
In: Mathlib.Data.Finset.Card

Lean Code:
def card (s : Finset α) : ℕ :=
  Multiset.card s.1
Show all
Docstring:
s.card is the number of elements of s, aka its cardinality.

The notation #s can be accessed in the Finset locale.

Gemini 3.0 Flash:
Cardinality of a Finite Set. For any finite set 
, its cardinality is defined as the number of elements contained in 
, represented as a natural number.

Find similar
View Dependencies ▼
Nat.card_fin
In: Mathlib.SetTheory.Cardinal.Finite

Lean Code:
lemma card_fin (n : ℕ) : Nat.card (Fin n) = n := by
  rw [Nat.card_eq_fintype_card, Fintype.card_fin]
Gemini 3.0 Flash:
Cardinality of Finite Sets. For any natural number 
, the cardinality of the set 
 is equal to 
.

Find similar
View Dependencies ▼
Fin.card_filter_univ_succ'
In: Mathlib.Data.Fintype.Fin

Lean Code:
theorem card_filter_univ_succ' (p : Fin (n + 1) → Prop) [DecidablePred p] :
    #{x | p x} = ite (p 0) 1 0 + #{x | p (.succ x)} := by
  rw [card_filter_univ_succ]; split_ifs <;> simp [add_comm]
Gemini 3.0 Flash:
Cardinality of a Predicate on Fin (n + 1). For any decidable predicate 
 on the set 
, the number of elements 
 that satisfy 
 is equal to the sum of a term that is 
 if 
 is true and 
 otherwise, and the number of elements 
 such that 
 is true.

Find similar
View Dependencies ▼
#### LeanFinder (name + statement)
Rank	Formal statement	Informal statement
1	
theorem Equiv.Perm.signAux_inv {n : ℕ} (f : Perm (Fin n)) : signAux f⁻¹ = signAux f :=
  prod_nbij (signBijAux f⁻¹) signBijAux_mem signBijAux_injOn signBijAux_surj fun ⟨a, b⟩ hab ↦
    if h : f⁻¹ b < f⁻¹ a then by
      simp_all [signBijAux, dif_pos h, if_neg h.not_le, apply_inv_self, apply_inv_self,
        if_neg (mem_finPairsLT.1 hab).not_le]
    else by
      simp_all [signBijAux, if_pos (le_of_not_gt h), dif_neg h, apply_inv_self, apply_inv_self,
        if_pos (mem_finPairsLT.1 hab).le]
Doc
Copy
👍
👎
For any natural number 
n
n and any permutation 
f
f of the finite set 
Fin
(
n
)
Fin(n), the sign of the inverse permutation 
f
−
1
f 
−1
  equals the sign of 
f
f, i.e., 
signAux
(
f
−
1
)
=
signAux
(
f
)
signAux(f 
−1
 )=signAux(f).
Copy
2	
theorem Finset.univ_perm_fin_succ {n : ℕ} :
  @Finset.univ (Perm <| Fin n.succ) _ =
    (Finset.univ : Finset <| Fin n.succ × Perm (Fin n)).map Equiv.Perm.decomposeFin.symm.toEmbedding :=
  (Finset.univ_map_equiv_to_embedding _).symm
Doc
Copy
👍
👎
For any natural number 
n
n, the set of all permutations of 
F
i
n
 
(
n
+
1
)
Fin(n+1) is equal to the image under the inverse decomposition map of the Cartesian product of 
F
i
n
 
(
n
+
1
)
Fin(n+1) with the set of permutations of 
F
i
n
 
n
Finn. 

More precisely, the universal finset of permutations of 
F
i
n
 
(
n
+
1
)
Fin(n+1) is obtained by applying the inverse of the decomposition equivalence to the universal finset of pairs 
(
i
,
τ
)
(i,τ) where 
i
∈
F
i
n
 
(
n
+
1
)
i∈Fin(n+1) and 
τ
τ is a permutation of 
F
i
n
 
n
Finn.
Copy
3	
theorem Fintype.card_perm [Fintype α] : Fintype.card (Perm α) = (Fintype.card α)! :=
  Subsingleton.elim (@fintypePerm α _ _) (@Equiv.instFintype α α _ _ _ _) ▸ card_perms_of_finset _
Doc
Copy
👍
👎
For any finite type 
α
α, the number of permutations of 
α
α is equal to the factorial of the cardinality of 
α
α, i.e., 
∣
Perm
(
α
)
∣
=
∣
α
∣
!
∣Perm(α)∣=∣α∣!.
Copy
4	
theorem Finset.card_inv (s : Finset α) : s⁻¹.card = s.card := card_image_of_injective _ inv_injective
Doc
Copy
👍
👎
For any finite set 
s
s of elements from a type 
α
α equipped with an inversion operation, the cardinality of the pointwise inverse set 
s
−
1
=
{
x
−
1
∣
x
∈
s
}
s 
−1
 ={x 
−1
 ∣x∈s} equals the cardinality of 
s
s, i.e., 
#
(
s
−
1
)
=
#
s
#(s 
−1
 )=#s.
Copy
5	
theorem Fintype.card_orderDual (α : Type*) [Fintype α] : Fintype.card αᵒᵈ = Fintype.card α :=
  rfl
Doc
Copy
👍
👎
For any finite type 
α
α, the cardinality of its order dual 
α
op
α 
op
  is equal to the cardinality of 
α
α, i.e., 
card
(
α
op
)
=
card
(
α
)
card(α 
op
 )=card(α).
Copy
### quotientAddGroup.quotientKerEquivOfSurjective

#### Query (name + statement)

```text
quotientAddGroup.quotientKerEquivOfSurjective
theorem kernel_subgroup_and_isomorphism {G H : Type*} [AddCommGroup G] [AddCommGroup H]
    (φ : G →+ H) :
    φ.ker = {g | φ g = 0} ∧ (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H))
```

#### LeanExplore (name + statement)
QuotientGroup.quotientKerEquivOfSurjective
In: Mathlib.GroupTheory.QuotientGroup.Basic

Lean Code:
@[to_additive ]
noncomputable def quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
  quotientKerEquivOfRightInverse φ _ hφ.hasRightInverse.choose_spec
Show all
Docstring:
The canonical isomorphism G/(ker φ) ≃* H induced by a surjection φ : G →* H.

For a computable version, see QuotientGroup.quotientKerEquivOfRightInverse.

Gemini 3.0 Flash:
First Isomorphism Theorem for Surjective Group Homomorphisms. For any surjective group homomorphism 
, there exists a canonical isomorphism between the quotient group 
 and the codomain 
. This result also holds for additive groups, providing a canonical isomorphism 
 for any surjective additive group homomorphism 
.

Find similar
View Dependencies ▼
QuotientGroup.liftEquiv
In: Mathlib.GroupTheory.QuotientGroup.Defs

Lean Code:
@[to_additive ]
noncomputable def liftEquiv {φ : G →* H} (hφ : Function.Surjective φ)
    (HN : N = φ.ker) : G ⧸ N ≃* H :=
  MulEquiv.ofBijective (QuotientGroup.lift N φ HN.le)
    ⟨by rw [← MonoidHom.ker_eq_bot_iff, ker_lift, ← HN, QuotientGroup.map_mk'_self],
...
Show all
Docstring:
A surjective group homomorphism φ : G →* H with N = ker(φ) descends (i.e. lifts) to a group isomorphism G/N ≃* H.

Gemini 3.0 Flash:
First Isomorphism Theorem for Groups. Given a surjective group homomorphism 
 and a normal subgroup 
 such that 
, there exists a unique group isomorphism between the quotient group 
 and 
 induced by 
.

Find similar
View Dependencies ▼
QuotientAddGroup.quotientKerEquivOfSurjective
In: Mathlib.GroupTheory.QuotientGroup.Basic

Lean Code:
@[to_additive ]
noncomputable def quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
Show all
Docstring:
The canonical isomorphism G/(ker φ) ≃+ H induced by a surjection φ : G →+ H. For a computable version, see QuotientAddGroup.quotientKerEquivOfRightInverse.

Gemini 3.0 Flash:
First Isomorphism Theorem for Additive Groups. For any surjective additive group homomorphism 
, there exists a canonical additive isomorphism between the quotient group 
 and the codomain 
.

Find similar
View Dependencies ▼
QuotientAddGroup.liftEquiv
In: Mathlib.GroupTheory.QuotientGroup.Defs

Lean Code:
@[to_additive ]
noncomputable def liftEquiv {φ : G →* H} (hφ : Function.Surjective φ)
Show all
Docstring:
A surjective AddGroup homomorphism φ : G →+ H with N = ker(φ) descends (i.e. lifts) to an AddGroup isomorphism G/N ≃+ H.

Gemini 3.0 Flash:
First Isomorphism Theorem for Additive Groups. Given a surjective additive group homomorphism 
 with kernel 
, there exists a unique additive group isomorphism between the quotient group 
 and the codomain 
.

Find similar
View Dependencies ▼
QuotientAddGroup.liftEquiv_mk
In: Mathlib.GroupTheory.QuotientGroup.Defs

Lean Code:
@[to_additive (attr := simp)]
theorem liftEquiv_mk {φ : G →* H} (hφ : Function.Surjective φ) (HN : N = φ.ker) (g : G) :
Gemini 3.0 Flash:
First Isomorphism Theorem for Quotients. Given a surjective group homomorphism 
 and a normal subgroup 
 such that 
, the isomorphism 
 induced by the universal property of quotients maps the coset 
 to the image 
 for any 
.

Find similar
View Dependencies ▼
#### LeanFinder (name + statement)

Rank	Formal statement	Informal statement
1	
definition QuotientGroup.quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
  quotientKerEquivOfRightInverse φ _ hφ.hasRightInverse.choose_spec
Doc
Copy
👍
👎
Given a surjective group homomorphism 
φ
:
G
→
H
φ:G→H, there is a canonical group isomorphism between the quotient group 
G
/
ker
⁡
φ
G/kerφ and 
H
H. The isomorphism maps each coset 
g
ker
⁡
φ
gkerφ to 
φ
(
g
)
φ(g).
Copy
2	
/-- The canonical isomorphism `G/(ker φ) ≃* H` induced by a surjection `φ : G →* H`.

For a `computable` version, see `QuotientGroup.quotientKerEquivOfRightInverse`.
-/
@[to_additive "The canonical isomorphism `G/(ker φ) ≃+ H` induced by a surjection `φ : G →+ H`.
For a `computable` version, see `QuotientAddGroup.quotientKerEquivOfRightInverse`."]
noncomputable def quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
  quotientKerEquivOfRightInverse φ _ hφ.hasRightInverse.choose_spec
Doc
Copy
👍
👎
Given a surjective group homomorphism 
φ
:
G
→
H
φ:G→H, there exists a canonical group isomorphism 
G
/
ker
⁡
φ
≅
H
G/kerφ≅H. This isomorphism maps each coset 
g
ker
⁡
φ
gkerφ to 
φ
(
g
)
φ(g). This result is noncomputable and relies on the existence of a right inverse for 
φ
φ.
Copy
3	
definition Con.quotientKerEquivOfSurjective (f : M →* P) (hf : Surjective f) : (ker f).Quotient ≃* P :=
  quotientKerEquivOfRightInverse _ _ hf.hasRightInverse.choose_spec
Doc
Copy
👍
👎
Given a surjective monoid homomorphism 
f
 ⁣
:
M
→
P
f:M→P, the quotient of 
M
M by the kernel congruence relation of 
f
f is isomorphic as a monoid to 
P
P via the map sending each equivalence class 
[
x
]
ker
⁡
f
[x] 
kerf
​
  to 
f
(
x
)
f(x).
Copy
4	
definition QuotientGroup.quotientKerEquivRange : G ⧸ ker φ ≃* range φ :=
  MulEquiv.ofBijective (rangeKerLift φ) ⟨rangeKerLift_injective φ, rangeKerLift_surjective φ⟩
Doc
Copy
👍
👎
The canonical isomorphism between the quotient group \( G/\ker \varphi \) and the range \( \text{range } \varphi \) of the group homomorphism \( \varphi \colon G \to H \). 

This isomorphism is constructed via the bijective homomorphism induced by \( \varphi \) on the quotient \( G/\ker \varphi \).
Copy
5	
definition Setoid.quotientKerEquivOfSurjective (hf : Surjective f) : Quotient (ker f) ≃ β :=
  quotientKerEquivOfRightInverse _ (Function.surjInv hf) (rightInverse_surjInv hf)
Doc
Copy
👍
👎
Given a surjective function 
f
:
α
→
β
f:α→β, the quotient of 
α
α by the kernel of 
f
f is in bijection with 
β
β. 

The bijection is constructed as:
- The forward map sends an equivalence class 
[
a
]
[a] to 
f
(
a
)
f(a)
- The inverse map sends 
b
∈
β
b∈β to the equivalence class 
[
f
−
1
(
b
)
]
[f 
−1
 (b)], where 
f
−
1
f 
−1
  is any right inverse of 
f
f (which exists by surjectivity)
- This satisfies 
f
(
[
a
]
)
=
b
f([a])=b if and only if 
[
a
]
=
[
f
−
1
(
b
)
]
[a]=[f 
−1
 (b)] for all 
a
∈
α
a∈α and 
b
∈
β
b∈β
Copy
## Search Scratchpad: Statement-Only Queries

### MSC-180_60_002

#### Query (statement only)

```text
theorem weierstrass_approximation (f : ℝ → ℝ) (hf : ContinuousOn f (Set.Icc 0 1))
    (ε : ℝ) (hε : ε > 0) :
    ∃ (B : Polynomial ℝ), ∀ x ∈ Set.Icc 0 1, |B.eval x - f x| ≤ ε
```

#### LeanExplore (statement only)
exists_polynomial_near_of_continuousOn
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ)
    (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
    ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
...
Show all
Docstring:
Another alternative statement of Weierstrass's theorem, for those who like epsilons, but not bundled continuous functions.

Every real-valued function ℝ → ℝ which is continuous on [a,b] can be approximated to within any ε > 0 on [a,b] by some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real-valued function 
 that is continuous on a closed interval 
 and for any 
, there exists a polynomial 
 such that for all 
, the inequality 
 holds.

Find similar
View Dependencies ▼
taylor_mean_remainder_bound
In: Mathlib.Analysis.Calculus.Taylor

Lean Code:
theorem taylor_mean_remainder_bound {f : ℝ → E} {a b C x : ℝ} {n : ℕ} (hab : a ≤ b)
    (hf : ContDiffOn ℝ (n + 1) f (Icc a b)) (hx : x ∈ Icc a b)
    (hC : ∀ y ∈ Icc a b, ‖iteratedDerivWithin (n + 1) f (Icc a b) y‖ ≤ C) :
    ‖f x - taylorWithinEval f n (Icc a b) a x‖ ≤ C * (x - a) ^ (n + 1) / n ! := by
  rcases eq_or_lt_of_le hab with (rfl | h)
...
Show all
Docstring:
Taylor's theorem with a polynomial bound on the remainder

We assume that f is n+1-times continuously differentiable on the closed set Icc a b. The difference of f and its n-th Taylor polynomial can be estimated by C * (x - a)^(n+1) / n! where C is a bound for the n+1-th iterated derivative of f.

Gemini 3.0 Flash:
Taylor's Theorem with a Polynomial Remainder Bound. Let 
 be a function into a normed space 
 that is 
-times continuously differentiable on the closed interval 
. Suppose there exists a constant 
 such that the norm of the 
-th iterated derivative of 
 (taken within 
) is bounded by 
 for all 
. Then for any 
, the norm of the difference between 
 and its 
-th order Taylor polynomial evaluated at 
 (with base point 
) is bounded by: 
 

Find similar
View Dependencies ▼
ApproximatesLinearOn
In: Mathlib.Analysis.Calculus.InverseFunctionTheorem.ApproximatesLinearOn

Lean Code:
def ApproximatesLinearOn (f : E → F) (f' : E →L[𝕜] F) (s : Set E) (c : ℝ≥0) : Prop :=
  ∀ x ∈ s, ∀ y ∈ s, ‖f x - f y - f' (x - y)‖ ≤ c * ‖x - y‖
Show all
Docstring:
We say that f approximates a continuous linear map f' on s with constant c, if ‖f x - f y - f' (x - y)‖ ≤ c * ‖x - y‖ whenever x, y ∈ s.

This predicate is defined to facilitate the splitting of the inverse function theorem into small lemmas. Some of these lemmas can be useful, e.g., to prove that the inverse function is defined on a specific set.

Gemini 3.0 Flash:
Linear Approximation on a Set. A function 
 is said to approximate a continuous linear map 
 on a set 
 with constant 
 if, for all 
, the inequality 
 holds.

Find similar
View Dependencies ▼
FDerivMeasurableAux.B
In: Mathlib.Analysis.Calculus.FDeriv.Measurable

Lean Code:
def B (f : E → F) (K : Set (E →L[𝕜] F)) (r s ε : ℝ) : Set E :=
  ⋃ L ∈ K, A f L r ε ∩ A f L s ε
Show all
Docstring:
The set B f K r s ε is the set of points x around which there exists a continuous linear map L belonging to K (a given set of continuous linear maps) that approximates well the function f (up to an error ε), simultaneously at scales r and s.

Gemini 3.0 Flash:
Simultaneous Linear Approximation Set. For a function 
, a set of continuous linear maps 
, and real parameters 
, the set 
 consists of all points 
 for which there exists some continuous linear map 
 such that 
 approximates 
 at 
 with error at most 
 at both scales 
 and 
. Formally, this is the union over all 
 of the intersection of the sets 
 and 
.

Find similar
View Dependencies ▼
exists_polynomial_near_continuousMap
In: Mathlib.Topology.ContinuousMap.Weierstrass

Lean Code:
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ)
    (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
...
Show all
Docstring:
An alternative statement of Weierstrass' theorem, for those who like their epsilons.

Every real-valued continuous function on [a,b] is within any ε > 0 of some polynomial.

Gemini 3.0 Flash:
Weierstrass Approximation Theorem. For any real numbers 
 and 
, and any continuous real-valued function 
 defined on the closed interval 
, there exists a polynomial 
 such that for any 
, the supremum norm of the difference between 
 and the restriction of 
 to 
 is strictly less than 
.

Find similar
View Dependencies ▼
#### LeanFinder (statement only)
Rank	Formal statement	Informal statement
1	
theorem exists_polynomial_near_of_continuousOn (a b : ℝ) (f : ℝ → ℝ) (c : ContinuousOn f (Set.Icc a b)) (ε : ℝ) (pos : 0 < ε) :
  ∃ p : ℝ[X], ∀ x ∈ Set.Icc a b, |p.eval x - f x| < ε := by
  let f' : C(Set.Icc a b, ℝ) := ⟨fun x => f x, continuousOn_iff_continuous_restrict.mp c⟩
  obtain ⟨p, b⟩ := exists_polynomial_near_continuousMap a b f' ε pos
  use p
  rw [norm_lt_iff _ pos] at b
  intro x m
  exact b ⟨x, m⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any function 
f
 ⁣
:
R
→
R
f:R→R that is continuous on the closed interval 
[
a
,
b
]
[a,b], and any 
ε
>
0
ε>0, there exists a polynomial 
p
p with real coefficients such that for all 
x
∈
[
a
,
b
]
x∈[a,b], the absolute difference between 
p
(
x
)
p(x) and 
f
(
x
)
f(x) is less than 
ε
ε.
Copy
2	
theorem exists_polynomial_near_continuousMap (a b : ℝ) (f : C(Set.Icc a b, ℝ)) (ε : ℝ) (pos : 0 < ε) : ∃ p : ℝ[X], ‖p.toContinuousMapOn _ - f‖ < ε := by
  have w := mem_closure_iff_frequently.mp (continuousMap_mem_polynomialFunctions_closure _ _ f)
  rw [Metric.nhds_basis_ball.frequently_iff] at w
  obtain ⟨-, H, ⟨m, ⟨-, rfl⟩⟩⟩ := w ε pos
  rw [Metric.mem_ball, dist_eq_norm] at H
  exact ⟨m, H⟩
Doc
Copy
👍
👎
For any real numbers 
a
<
b
a<b, any continuous function 
f
 ⁣
:
[
a
,
b
]
→
R
f:[a,b]→R, and any 
ε
>
0
ε>0, there exists a polynomial 
p
p such that the uniform norm of 
p
−
f
p−f on 
[
a
,
b
]
[a,b] is less than 
ε
ε.
Copy
3	
theorem bernsteinApproximation_uniform (f : C(I, ℝ)) : Tendsto (fun n : ℕ => bernsteinApproximation n f) atTop (𝓝 f) := by
  simp only [Metric.nhds_basis_ball.tendsto_right_iff, Metric.mem_ball, dist_eq_norm]
  intro ε h
  let δ := δ f ε h
  have nhds_zero := tendsto_const_div_atTop_nhds_zero_nat (2 * ‖f‖ * δ ^ (-2 : ℤ))
  filter_upwards [nhds_zero.eventually (gt_mem_nhds (half_pos h)), eventually_gt_atTop 0] with n nh
    npos'
  have npos : 0 < (n : ℝ) := by positivity
  -- As `[0,1]` is compact, it suffices to check the inequality pointwise.
  rw [ContinuousMap.norm_lt_iff _ h]
  intro x
  -- The idea is to split up the sum over `k` into two sets,
  -- `S`, where `x - k/n < δ`, and its complement.
  let S := S f ε h n x
  calc
    |(bernsteinApproximation n f - f) x| = |bernsteinApproximation n f x - f x| := rfl
    _ = |bernsteinApproximation n f x - f x * 1| := by rw [mul_one]
    _ = |bernsteinApproximation n f x - f x * ∑ k : Fin (n + 1), bernstein n k x| := by
      rw [bernstein.probability]
    _ = |∑ k : Fin (n + 1), (f k/ₙ - f x) * bernstein n k x| := by
      simp [bernsteinApproximation, Finset.mul_sum, sub_mul]
    _ ≤ ∑ k : Fin (n + 1), |(f k/ₙ - f x) * bernstein n k x| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ k : Fin (n + 1), |f k/ₙ - f x| * bernstein n k x := by
      simp_rw [abs_mul, abs_eq_self.mpr bernstein_nonneg]
    _ = (∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x) + ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x :=
      (S.sum_add_sum_compl _).symm
    -- We'll now deal with the terms in `S` and the terms in `Sᶜ` in separate calc blocks.
    _ < ε / 2 + ε / 2 :=
      (add_lt_add_of_le_of_lt ?_ ?_)
    _ = ε := add_halves ε
  · -- We now work on the terms in `S`: uniform continuity and `bernstein.probability`
    -- quickly give us a bound.
    calc
      ∑ k ∈ S, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ S, ε / 2 * bernstein n k x := by
        gcongr with _ m
        exact le_of_lt (lt_of_mem_S m)
      _ = ε / 2 * ∑ k ∈ S, bernstein n k x := by rw [Finset.mul_sum]
      -- In this step we increase the sum over `S` back to a sum over all of `Fin (n+1)`,
      -- so that we can use `bernstein.probability`.
      _ ≤ ε / 2 * ∑ k : Fin (n + 1), bernstein n k x := by gcongr; exact S.subset_univ
      _ = ε / 2 := by rw [bernstein.probability, mul_one]
  · -- We now turn to working on `Sᶜ`: we control the difference term just using `‖f‖`,
    -- and then insert a `δ^(-2) * (x - k/n)^2` factor
    -- (which is at least one because we are not in `S`).
    calc
      ∑ k ∈ Sᶜ, |f k/ₙ - f x| * bernstein n k x ≤ ∑ k ∈ Sᶜ, 2 * ‖f‖ * bernstein n k x := by
        gcongr
        apply f.dist_le_two_norm
      _ = 2 * ‖f‖ * ∑ k ∈ Sᶜ, bernstein n k x := by rw [Finset.mul_sum]
      _ ≤ 2 * ‖f‖ * ∑ k ∈ Sᶜ, δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr with _ m
        conv_lhs => rw [← one_mul (bernstein _ _ _)]
        gcongr
        exact le_of_mem_S_compl m
      -- Again enlarging the sum from `Sᶜ` to all of `Fin (n+1)`
      _ ≤ 2 * ‖f‖ * ∑ k : Fin (n + 1), δ ^ (-2 : ℤ) * ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        gcongr; exact Sᶜ.subset_univ
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * ∑ k : Fin (n + 1), ((x : ℝ) - k/ₙ) ^ 2 * bernstein n k x := by
        conv_rhs =>
          rw [mul_assoc, Finset.mul_sum]
          simp only [← mul_assoc]
      -- `bernstein.variance` and `x ∈ [0,1]` gives the uniform bound
      _ = 2 * ‖f‖ * δ ^ (-2 : ℤ) * x * (1 - x) / n := by rw [variance npos]; ring
      _ ≤ 2 * ‖f‖ * δ ^ (-2 : ℤ) * 1 * 1 / n := by gcongr <;> unit_interval
      _ < ε / 2 := by simp only [mul_one]; exact nh
Doc
Copy
👍
👎
For any continuous function 
f
∈
C
(
[
0
,
1
]
,
R
)
f∈C([0,1],R), the sequence of Bernstein approximations 
(
B
n
(
f
)
)
n
∈
N
(B 
n
​
 (f)) 
n∈N
​
  converges uniformly to 
f
f as 
n
→
∞
n→∞, where the 
n
n-th Bernstein approximation is given by:
\[ B_n(f)(x) = \sum_{k=0}^n f\left(\frac{k}{n}\right) \binom{n}{k} x^k (1-x)^{n-k}. \]
Copy
4	
definition bernsteinApproximation.δ (f : C(I, ℝ)) (ε : ℝ) (h : 0 < ε) : ℝ :=
  f.modulus (ε / 2) (half_pos h)
Doc
Copy
👍
👎
For a continuous function \( f \in C([0,1], \mathbb{R}) \) and \( \varepsilon > 0 \), the modulus of uniform continuity \( \delta(f, \varepsilon) \) is chosen such that for any \( x, y \in [0,1] \), if \( |x - y| < \delta \) then \( |f(x) - f(y)| < \varepsilon/2 \).
Copy
5	
definition bernsteinApproximation (n : ℕ) (f : C(I, ℝ)) : C(I, ℝ) :=
  ∑ k : Fin (n + 1), f k/ₙ • bernstein n k
Doc
Copy
👍
👎
The 
n
n-th Bernstein approximation of a continuous function 
f
∈
C
(
[
0
,
1
]
,
R
)
f∈C([0,1],R) is the continuous function on 
[
0
,
1
]
[0,1] defined by:
\[ B_n(f)(x) = \sum_{k=0}^n f\left(\frac{k}{n}\right) \cdot B_{n,k}(x) \]
where 
B
n
,
k
(
x
)
=
(
n
k
)
x
k
(
1
−
x
)
n
−
k
B 
n,k
​
 (x)=( 
k
n
​
 )x 
k
 (1−x) 
n−k
  is the Bernstein polynomial of degree 
n
n and index 
k
k.
Copy
### MSC-180_26_002

#### Query (statement only)

```text
theorem exists_sup_of_bddAbove {A : Set ℝ} (hne : A.Nonempty) (hbd : BddAbove A) :
    ∃ s : ℝ, IsLUB A s
```

#### LeanExplore (statement only)
isLUB_csSup
In: Mathlib.Order.ConditionallyCompleteLattice.Basic

Lean Code:
theorem isLUB_csSup (ne : s.Nonempty) (H : BddAbove s) : IsLUB s (sSup s) :=
  ⟨fun _ => le_csSup H, fun _ => csSup_le ne⟩
Gemini 3.0 Flash:
Least Upper Bound of a Conditionally Complete Set. For any nonempty set 
 that is bounded above in a conditionally complete lattice, the supremum of 
 is its least upper bound.

Find similar
View Dependencies ▼
BddAbove
In: Mathlib.Order.Bounds.Defs

Lean Code:
@[to_dual ]
def BddAbove (s : Set α) :=
  (upperBounds s).Nonempty
Show all
Docstring:
A set is bounded above if there exists an upper bound.

Gemini 3.0 Flash:
Bounded Above. A set 
 is bounded above if the set of its upper bounds is non-empty; that is, there exists an element that is greater than or equal to every element in 
.

Find similar
View Dependencies ▼
WithBot.coe_sSup'
In: Mathlib.Order.ConditionallyCompleteLattice.Basic

Lean Code:
@[norm_cast]
theorem WithBot.coe_sSup' [SupSet α] {s : Set α} (hs : s.Nonempty) (h's : BddAbove s) :
    ↑(sSup s) = (sSup ((fun (a : α) ↦ ↑a) '' s) : WithBot α) :=
  WithTop.coe_sInf' (α := αᵒᵈ) hs h's
Gemini 3.0 Flash:
Supremum of a Nonempty Bounded Set in WithBot. For any nonempty set 
 that is bounded above in a type equipped with a supremum operator, the supremum of 
 in the original type, when embedded into the type extended with a bottom element, is equal to the supremum of the image of 
 under that embedding.

Find similar
View Dependencies ▼
Int.csSup_mem
In: Mathlib.Data.Int.ConditionallyCompleteOrder

Lean Code:
theorem csSup_mem {s : Set ℤ} (h1 : s.Nonempty) (h2 : BddAbove s) : sSup s ∈ s := by
  convert (greatestOfBdd _ (Classical.choose_spec h2) h1).2.1
  exact dif_pos ⟨h1, h2⟩
Gemini 3.0 Flash:
Supremum of a Bounded Set of Integers. For any nonempty set of integers 
 that is bounded above, the supremum of 
 is an element of 
.

Find similar
View Dependencies ▼
csSup_le
In: Mathlib.Order.ConditionallyCompleteLattice.Basic

Lean Code:
theorem csSup_le (h₁ : s.Nonempty) (h₂ : ∀ b ∈ s, b ≤ a) : sSup s ≤ a :=
  ConditionallyCompleteLattice.csSup_le s a h₁ h₂
Gemini 3.0 Flash:
Least Upper Bound Property. In a conditionally complete lattice, if a set 
 is nonempty and 
 is an upper bound of 
, then the supremum of 
 is less than or equal to 
.

Find similar
View Dependencies ▼
#### LeanFinder (statement only)
Rank	Formal statement	Informal statement
1	
theorem Real.exists_isLUB (hne : s.Nonempty) (hbdd : BddAbove s) : ∃ x, IsLUB s x := by
  rcases hne, hbdd with ⟨⟨L, hL⟩, ⟨U, hU⟩⟩
  have : ∀ d : ℕ, BddAbove { m : ℤ | ∃ y ∈ s, (m : ℝ) ≤ y * d } := by
    cases' exists_int_gt U with k hk
    refine fun d => ⟨k * d, fun z h => ?_⟩
    rcases h with ⟨y, yS, hy⟩
    refine Int.cast_le.1 (hy.trans ?_)
    push_cast
    exact mul_le_mul_of_nonneg_right ((hU yS).trans hk.le) d.cast_nonneg
  choose f hf using fun d : ℕ =>
    Int.exists_greatest_of_bdd (this d) ⟨⌊L * d⌋, L, hL, Int.floor_le _⟩
  have hf₁ : ∀ n > 0, ∃ y ∈ s, ((f n / n : ℚ) : ℝ) ≤ y := fun n n0 =>
    let ⟨y, yS, hy⟩ := (hf n).1
    ⟨y, yS, by simpa using (div_le_iff₀ (Nat.cast_pos.2 n0 : (_ : ℝ) < _)).2 hy⟩
  have hf₂ : ∀ n > 0, ∀ y ∈ s, (y - ((n : ℕ) : ℝ)⁻¹) < (f n / n : ℚ) := by
    intro n n0 y yS
    have := (Int.sub_one_lt_floor _).trans_le (Int.cast_le.2 <| (hf n).2 _ ⟨y, yS, Int.floor_le _⟩)
    simp only [Rat.cast_div, Rat.cast_intCast, Rat.cast_natCast, gt_iff_lt]
    rwa [lt_div_iff₀ (Nat.cast_pos.2 n0 : (_ : ℝ) < _), sub_mul, inv_mul_cancel₀]
    exact ne_of_gt (Nat.cast_pos.2 n0)
  have hg : IsCauSeq abs (fun n => f n / n : ℕ → ℚ) := by
    intro ε ε0
    suffices ∀ j ≥ ⌈ε⁻¹⌉₊, ∀ k ≥ ⌈ε⁻¹⌉₊, (f j / j - f k / k : ℚ) < ε by
      refine ⟨_, fun j ij => abs_lt.2 ⟨?_, this _ ij _ le_rfl⟩⟩
      rw [neg_lt, neg_sub]
      exact this _ le_rfl _ ij
    intro j ij k ik
    replace ij := le_trans (Nat.le_ceil _) (Nat.cast_le.2 ij)
    replace ik := le_trans (Nat.le_ceil _) (Nat.cast_le.2 ik)
    have j0 := Nat.cast_pos.1 ((inv_pos.2 ε0).trans_le ij)
    have k0 := Nat.cast_pos.1 ((inv_pos.2 ε0).trans_le ik)
    rcases hf₁ _ j0 with ⟨y, yS, hy⟩
    refine lt_of_lt_of_le ((Rat.cast_lt (K := ℝ)).1 ?_) ((inv_le_comm₀ ε0 (Nat.cast_pos.2 k0)).1 ik)
    simpa using sub_lt_iff_lt_add'.2 (lt_of_le_of_lt hy <| sub_lt_iff_lt_add.1 <| hf₂ _ k0 _ yS)
  let g : CauSeq ℚ abs := ⟨fun n => f n / n, hg⟩
  refine ⟨mk g, ⟨fun x xS => ?_, fun y h => ?_⟩⟩
  · refine le_of_forall_lt_imp_le_of_dense fun z xz => ?_
    cases' exists_nat_gt (x - z)⁻¹ with K hK
    refine le_mk_of_forall_le ⟨K, fun n nK => ?_⟩
    replace xz := sub_pos.2 xz
    replace hK := hK.le.trans (Nat.cast_le.2 nK)
    have n0 : 0 < n := Nat.cast_pos.1 ((inv_pos.2 xz).trans_le hK)
    refine le_trans ?_ (hf₂ _ n0 _ xS).le
    rwa [le_sub_comm, inv_le_comm₀ (Nat.cast_pos.2 n0 : (_ : ℝ) < _) xz]
  · exact
      mk_le_of_forall_le
        ⟨1, fun n n1 =>
          let ⟨x, xS, hx⟩ := hf₁ _ n1
          le_trans hx (h xS)⟩
Doc
Copy
👍
👎
For any nonempty set 
s
s of real numbers that is bounded above, there exists a real number 
x
x which is the least upper bound (supremum) of 
s
s.
Copy
2	
theorem Real.isLUB_sSup (h₁ : s.Nonempty) (h₂ : BddAbove s) : IsLUB s (sSup s) := by
  simp only [sSup_def, dif_pos (And.intro h₁ h₂)]
  apply Classical.choose_spec
Doc
Copy
👍
👎
For any nonempty set 
s
s of real numbers that is bounded above, the supremum 
sup
⁡
s
sups is the least upper bound of 
s
s.
Copy
3	
instance Real.instSupSet : SupSet ℝ :=
  ⟨fun s => if h : s.Nonempty ∧ BddAbove s then Classical.choose (exists_isLUB h.1 h.2) else 0⟩
Doc
Copy
👍
👎
The real numbers 
R
R form a conditionally complete linear order, meaning every nonempty subset of 
R
R that is bounded above has a least upper bound (supremum) in 
R
R.
Copy
4	
theorem Real.exists_isGLB (hne : s.Nonempty) (hbdd : BddBelow s) : ∃ x, IsGLB s x := by
  have hne' : (-s).Nonempty := Set.nonempty_neg.mpr hne
  have hbdd' : BddAbove (-s) := bddAbove_neg.mpr hbdd
  use -Classical.choose (Real.exists_isLUB hne' hbdd')
  rw [← isLUB_neg]
  exact Classical.choose_spec (Real.exists_isLUB hne' hbdd')
Doc
Copy
👍
👎
For any nonempty set 
s
s of real numbers that is bounded below, there exists a real number 
x
x which is the greatest lower bound (infimum) of 
s
s.
Copy
5	
theorem isLUB_csSup (ne : s.Nonempty) (H : BddAbove s) : IsLUB s (sSup s) :=
  ⟨fun _ => le_csSup H, fun _ => csSup_le ne⟩
Doc
Copy
👍
👎
Let 
s
s be a nonempty subset of a conditionally complete lattice 
α
α that is bounded above. Then the supremum 
sup
⁡
s
sups is the least upper bound of 
s
s, i.e., 
sup
⁡
s
sups is an upper bound of 
s
s and for any other upper bound 
b
b of 
s
s, we have 
sup
⁡
s
≤
b
sups≤b.
Copy
### MSC-180_05_003

#### Query (statement only)

```text
theorem excedance_coexcedance_dual {n : ℕ} (π : Perm (Fin n)) :
    (excedances π).card = (coexcedances π⁻¹).card
```

#### LeanExplore (statement only)
Fin.revOrderIso_apply
In: Mathlib.Order.Fin.Basic

Lean Code:
@[simps! apply toEquiv]
def revOrderIso : (Fin n)ᵒᵈ ≃o Fin n := ⟨OrderDual.ofDual.trans revPerm, rev_le_rev⟩
Gemini 3.0 Flash:
Order Isomorphism between the Dual of Fin n and Fin n. For any natural number 
, there exists an order isomorphism between the order dual of the set 
 and the set itself. This isomorphism is defined by the reversal permutation, which maps each index 
 to 
.

Find similar
View Dependencies ▼
OrderDual
In: Mathlib.Order.OrderDual

Lean Code:
def OrderDual (α : Type*) : Type _ :=
  α
Show all
Docstring:
Type synonym to equip a type with the dual order: ≤ means ≥ and < means >. αᵒᵈ is notation for OrderDual α.

Gemini 3.0 Flash:
Order Dual. The order dual of a type, denoted 
 for a type 
, is a type that is identical to 
 in its elements but has its order relation reversed. Specifically, if 
 in the original type, then 
 in the order dual, and similarly for strict inequalities.

Find similar
View Dependencies ▼
Fintype.card_orderDual
In: Mathlib.Data.Fintype.Card

Lean Code:
@[simp]
theorem Fintype.card_orderDual (α : Type*) [Fintype α] : Fintype.card αᵒᵈ = Fintype.card α :=
  rfl
Gemini 3.0 Flash:
Cardinality of the Order Dual. For any finite type, the cardinality of its order dual is equal to the cardinality of the type itself.

Find similar
View Dependencies ▼
groupCohomology.π_map
In: Mathlib.RepresentationTheory.Homological.GroupCohomology.Functoriality

Lean Code:
@[reassoc, elementwise]
theorem π_map (n : ℕ) :
    π A n ≫ map f φ n = cocyclesMap f φ n ≫ π B n := by
  simp [map, cocyclesMap]
Gemini 3.0 Flash:
Naturality of the Projection to Group Cohomology. For any 
, the canonical projection 
 from the space of 
-cocycles to the 
-th group cohomology group is natural with respect to morphisms of group representations. Specifically, given a group homomorphism 
 and a compatible morphism of representations 
, the composition of the projection 
 for 
 and 
 with the induced map on cohomology 
 is equal to the composition of the induced map on cocycles 
 with the projection 
 for 
 and 
.

Find similar
View Dependencies ▼
ofDual_natCast
In: Mathlib.Data.Nat.Cast.Synonym

Lean Code:
@[simp]
theorem ofDual_natCast [NatCast α] (n : ℕ) : (ofDual n : α) = n :=
  rfl
Gemini 3.0 Flash:
Natural Number Coercion in the Order Dual. For any type equipped with a natural number coercion, the image of a natural number 
 under the canonical map from the order dual is equal to the coercion of 
 into that type.

Find similar
View Dependencies ▼
#### LeanFinder (statement only)
Rank	Formal statement	Informal statement
1	
theorem Equiv.Perm.signAux_inv {n : ℕ} (f : Perm (Fin n)) : signAux f⁻¹ = signAux f :=
  prod_nbij (signBijAux f⁻¹) signBijAux_mem signBijAux_injOn signBijAux_surj fun ⟨a, b⟩ hab ↦
    if h : f⁻¹ b < f⁻¹ a then by
      simp_all [signBijAux, dif_pos h, if_neg h.not_le, apply_inv_self, apply_inv_self,
        if_neg (mem_finPairsLT.1 hab).not_le]
    else by
      simp_all [signBijAux, if_pos (le_of_not_gt h), dif_neg h, apply_inv_self, apply_inv_self,
        if_pos (mem_finPairsLT.1 hab).le]
Doc
Copy
👍
👎
For any natural number 
n
n and any permutation 
f
f of the finite set 
Fin
(
n
)
Fin(n), the sign of the inverse permutation 
f
−
1
f 
−1
  equals the sign of 
f
f, i.e., 
signAux
(
f
−
1
)
=
signAux
(
f
)
signAux(f 
−1
 )=signAux(f).
Copy
2	
theorem Equiv.Perm.support_inv (σ : Perm α) : support σ⁻¹ = σ.support := by
  simp_rw [Finset.ext_iff, mem_support, not_iff_not, inv_eq_iff_eq.trans eq_comm, imp_true_iff]
Doc
Copy
👍
👎
For any permutation 
σ
σ of a type 
α
α, the support of the inverse permutation 
σ
−
1
σ 
−1
  is equal to the support of 
σ
σ. That is, 
support
(
σ
−
1
)
=
support
(
σ
)
support(σ 
−1
 )=support(σ), where 
support
(
σ
)
support(σ) is the set of elements not fixed by 
σ
σ.
Copy
3	
@[simp]
theorem map_revPerm_Ico (i j : Fin n) : (Ico i j).map revPerm.toEmbedding = Ioc j.rev i.rev := by
  simp [← coe_inj]
Doc
Copy
👍
👎
For elements 
i
i and 
j
j in 
Fin
 
n
Finn, mapping the interval 
[
i
,
j
)
[i,j) using the reverse permutation results in the interval 
(
j
rev
,
i
rev
]
(j 
rev
 ,i 
rev
 ]. Formally, 
(
Ico
 
i
 
j
)
.
map
 
revPerm.toEmbedding
=
Ioc
 
j
rev
 
i
rev
(Icoij).maprevPerm.toEmbedding=Iocj 
rev
 i 
rev
 . This uses the injectivity of the finite set to set conversion.
Copy
4	
@[simp]
theorem map_revPerm_Ioc (i j : Fin n) : (Ioc i j).map revPerm.toEmbedding = Ico j.rev i.rev := by
  simp [← coe_inj]
Doc
Copy
👍
👎
For elements 
i
i and 
j
j in 
Fin
 
n
Finn, mapping the open interval 
(
i
,
j
]
(i,j] using the reversed permutation embedding results in the interval 
[
j
rev
,
i
rev
)
[j 
rev
 ,i 
rev
 ). In symbols, 
(
i
,
j
]
.
map
(
revPerm.toEmbedding
)
=
[
j
rev
,
i
rev
)
(i,j].map(revPerm.toEmbedding)=[j 
rev
 ,i 
rev
 ). This relies on the injectivity of finite set to set conversion.
Copy
5	
theorem Fintype.card_orderDual (α : Type*) [Fintype α] : Fintype.card αᵒᵈ = Fintype.card α :=
  rfl
Doc
Copy
👍
👎
For any finite type 
α
α, the cardinality of its order dual 
α
op
α 
op
  is equal to the cardinality of 
α
α, i.e., 
card
(
α
op
)
=
card
(
α
)
card(α 
op
 )=card(α).
Copy
### MSC-180_14_001

#### Query (statement only)

```text
theorem kernel_subgroup_and_isomorphism {G H : Type*} [AddCommGroup G] [AddCommGroup H]
    (φ : G →+ H) :
    φ.ker = {g | φ g = 0} ∧ (Surjective φ → Nonempty (G ⧸ φ.ker ≃+ H))
```

#### LeanExplore (statement only)
QuotientGroup.quotientKerEquivOfSurjective
In: Mathlib.GroupTheory.QuotientGroup.Basic

Lean Code:
@[to_additive ]
noncomputable def quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
  quotientKerEquivOfRightInverse φ _ hφ.hasRightInverse.choose_spec
Show all
Docstring:
The canonical isomorphism G/(ker φ) ≃* H induced by a surjection φ : G →* H.

For a computable version, see QuotientGroup.quotientKerEquivOfRightInverse.

Gemini 3.0 Flash:
First Isomorphism Theorem for Surjective Group Homomorphisms. For any surjective group homomorphism 
, there exists a canonical isomorphism between the quotient group 
 and the codomain 
. This result also holds for additive groups, providing a canonical isomorphism 
 for any surjective additive group homomorphism 
.

Find similar
View Dependencies ▼
QuotientGroup.liftEquiv
In: Mathlib.GroupTheory.QuotientGroup.Defs

Lean Code:
@[to_additive ]
noncomputable def liftEquiv {φ : G →* H} (hφ : Function.Surjective φ)
    (HN : N = φ.ker) : G ⧸ N ≃* H :=
  MulEquiv.ofBijective (QuotientGroup.lift N φ HN.le)
    ⟨by rw [← MonoidHom.ker_eq_bot_iff, ker_lift, ← HN, QuotientGroup.map_mk'_self],
...
Show all
Docstring:
A surjective group homomorphism φ : G →* H with N = ker(φ) descends (i.e. lifts) to a group isomorphism G/N ≃* H.

Gemini 3.0 Flash:
First Isomorphism Theorem for Groups. Given a surjective group homomorphism 
 and a normal subgroup 
 such that 
, there exists a unique group isomorphism between the quotient group 
 and 
 induced by 
.

Find similar
View Dependencies ▼
QuotientAddGroup.quotientKerEquivOfSurjective
In: Mathlib.GroupTheory.QuotientGroup.Basic

Lean Code:
@[to_additive ]
noncomputable def quotientKerEquivOfSurjective (hφ : Surjective φ) : G ⧸ ker φ ≃* H :=
Show all
Docstring:
The canonical isomorphism G/(ker φ) ≃+ H induced by a surjection φ : G →+ H. For a computable version, see QuotientAddGroup.quotientKerEquivOfRightInverse.

Gemini 3.0 Flash:
First Isomorphism Theorem for Additive Groups. For any surjective additive group homomorphism 
, there exists a canonical additive isomorphism between the quotient group 
 and the codomain 
.

Find similar
View Dependencies ▼
QuotientAddGroup.liftEquiv_mk
In: Mathlib.GroupTheory.QuotientGroup.Defs

Lean Code:
@[to_additive (attr := simp)]
theorem liftEquiv_mk {φ : G →* H} (hφ : Function.Surjective φ) (HN : N = φ.ker) (g : G) :
Gemini 3.0 Flash:
First Isomorphism Theorem for Quotients. Given a surjective group homomorphism 
 and a normal subgroup 
 such that 
, the isomorphism 
 induced by the universal property of quotients maps the coset 
 to the image 
 for any 
.

Find similar
View Dependencies ▼
QuotientAddGroup.liftEquiv
In: Mathlib.GroupTheory.QuotientGroup.Defs

Lean Code:
@[to_additive ]
noncomputable def liftEquiv {φ : G →* H} (hφ : Function.Surjective φ)
Show all
Docstring:
A surjective AddGroup homomorphism φ : G →+ H with N = ker(φ) descends (i.e. lifts) to an AddGroup isomorphism G/N ≃+ H.

Gemini 3.0 Flash:
First Isomorphism Theorem for Additive Groups. Given a surjective additive group homomorphism 
 with kernel 
, there exists a unique additive group isomorphism between the quotient group 
 and the codomain 
.

Find similar
View Dependencies ▼
#### LeanFinder (statement only)
Rank	Formal statement	Informal statement
1	
definition AddCommGrp.kernelIsoKer {G H : AddCommGrp.{u}} (f : G ⟶ H) : kernel f ≅ AddCommGrp.of f.hom.ker where
  hom := ofHom
    { toFun := fun g => ⟨kernel.ι f g, ConcreteCategory.congr_hom (kernel.condition f) g⟩
      map_zero' := by
        refine Subtype.ext ?_
        simp only [Functor.comp_obj, map_zero, ZeroMemClass.coe_zero]
      map_add' := fun g g' => by
        refine Subtype.ext ?_
        simp }
  inv := kernel.lift f (ofHom (AddSubgroup.subtype f.hom.ker)) <| by ext x; exact x.2
  hom_inv_id := by
    -- Porting note (https://github.com/leanprover-community/mathlib4/pull/11041): it would be nice to do the next two steps by a single `ext`,
    -- but this will require thinking carefully about the relative priorities of `@[ext]` lemmas.
    refine equalizer.hom_ext ?_
    ext
    simp
  inv_hom_id := by
    apply AddCommGrp.ext
    rintro ⟨x, mem⟩
    refine Subtype.ext ?_
    apply ConcreteCategory.congr_hom (kernel.lift_ι f _ _)
Doc
Copy
👍
👎
Given a morphism 
f
 ⁣
:
G
→
H
f:G→H in the category of additive commutative groups, there is a canonical isomorphism between the categorical kernel of 
f
f and the group-theoretic kernel of 
f
f (viewed as an additive commutative group). 

The isomorphism consists of:
- A homomorphism from the categorical kernel to the group-theoretic kernel, sending each element 
g
g in the kernel to 
⟨
ι
f
(
g
)
,
condition
⟩
⟨ι 
f
​
 (g),condition⟩ where 
ι
f
ι 
f
​
  is the kernel inclusion and the condition verifies that 
g
g is indeed in the kernel
- An inverse homomorphism constructed via the universal property of the categorical kernel, factoring the subgroup inclusion through the kernel object

This isomorphism satisfies the naturality conditions that both compositions yield the respective identity morphisms.
Copy
2	
theorem AddCommGrp.kernelIsoKer_hom_comp_subtype {G H : AddCommGrp.{u}} (f : G ⟶ H) : (kernelIsoKer f).hom ≫ ofHom (AddSubgroup.subtype f.hom.ker) = kernel.ι f := by ext; rfl
Doc
Copy
👍
👎
For any morphism 
f
 ⁣
:
G
→
H
f:G→H in the category of additive commutative groups, the composition of the homomorphism part of the kernel isomorphism 
(
k
e
r
n
e
l
I
s
o
K
e
r
 
f
)
.
h
o
m
(kernelIsoKer f).hom with the canonical inclusion 
o
f
H
o
m
 
(
A
d
d
S
u
b
g
r
o
u
p
.
s
u
b
t
y
p
e
 
f
.
h
o
m
.
k
e
r
)
ofHom (AddSubgroup.subtype f.hom.ker) equals the kernel inclusion morphism 
ι
f
 ⁣
:
ker
⁡
(
f
)
→
G
ι 
f
​
 :ker(f)→G.

In other words, the following diagram commutes:
ker
⁡
(
f
)
→
(
k
e
r
n
e
l
I
s
o
K
e
r
 
f
)
.
h
o
m
f
.
h
o
m
.
k
e
r
→
o
f
H
o
m
 
(
A
d
d
S
u
b
g
r
o
u
p
.
s
u
b
t
y
p
e
 
f
.
h
o
m
.
k
e
r
)
G
ker(f) 
(kernelIsoKer f).hom
​
 f.hom.ker 
ofHom (AddSubgroup.subtype f.hom.ker)
​
 G

equals the kernel inclusion 
ker
⁡
(
f
)
→
ι
f
G
ker(f) 
ι 
f
​
 
​
 G.
Copy
3	
theorem AddSubgroup.ker_normedMk (S : AddSubgroup M) : S.normedMk.ker = S :=
  QuotientAddGroup.ker_mk' _
Doc
Copy
👍
👎
For any seminormed additive commutative group 
M
M and any additive subgroup 
S
⊆
M
S⊆M, the kernel of the canonical normed group homomorphism 
normedMk
:
M
→
M
⧸
S
normedMk:M→M⧸S is equal to 
S
S.
Copy
4	
definition NormedAddGroupHom.ker : AddSubgroup V₁ :=
  f.toAddMonoidHom.ker
Doc
Copy
👍
👎
The kernel of a bounded group homomorphism 
f
 ⁣
:
V
1
→
V
2
f:V 
1
​
 →V 
2
​
  between seminormed additive commutative groups is the additive subgroup of 
V
1
V 
1
​
  consisting of all elements that 
f
f maps to zero. Formally, 
ker
⁡
f
=
{
v
∈
V
1
∣
f
(
v
)
=
0
}
kerf={v∈V 
1
​
 ∣f(v)=0}.
Copy
5	
theorem AddCommGrp.kernelIsoKer_inv_comp_ι {G H : AddCommGrp.{u}} (f : G ⟶ H) : (kernelIsoKer f).inv ≫ kernel.ι f = ofHom (AddSubgroup.subtype f.hom.ker) := by
  ext
  simp [kernelIsoKer]
Doc
Copy
👍
👎
For any morphism 
f
 ⁣
:
G
→
H
f:G→H in the category of additive commutative groups, the composition of the inverse morphism of the kernel isomorphism 
(
k
e
r
n
e
l
I
s
o
K
e
r
f
)
.
i
n
v
(kernelIsoKerf).inv with the kernel inclusion 
ι
 ⁣
:
ker
⁡
(
f
)
→
G
ι:ker(f)→G equals the canonical inclusion of the group-theoretic kernel as a homomorphism of additive commutative groups, i.e.,
(
k
e
r
n
e
l
I
s
o
K
e
r
f
)
.
i
n
v
∘
ι
=
ofHom
(
AddSubgroup.subtype 
f
.
h
o
m
.
k
e
r
)
.
(kernelIsoKerf).inv∘ι=ofHom(AddSubgroup.subtype f.hom.ker).
Copy
## Structured Retrieval Worksheet: Multi-Hallucination Problems

### MSC-180_12_001

Formal statement:
```lean
 theorem polynomial_division_algorithm {F : Type*} [Field F] (f g : Polynomial F) (hg : g ≠ 0) :
    ∃ (q r : Polynomial F),
      f = g * q + r ∧
      (r = 0 ∨ r.degree < g.degree) ∧
      ∀ (q' r' : Polynomial F),
        (f = g * q' + r' ∧ (r' = 0 ∨ r'.degree < g.degree)) → q = q' ∧ r = r' := by
  sorry
```

Hallucination 1: `divModByMonic_eq_div_mod`
Expected target theorem 1: `EuclideanDomain.mod_add_div`

Hallucination 2: `modByMonic_lt_of_lt`
Expected target theorem 2: `EuclideanDomain.mod_lt`

#### Statement only
##### Query
```text
theorem polynomial_division_algorithm {F : Type*} [Field F] (f g : Polynomial F) (hg : g ≠ 0) :
    ∃ (q r : Polynomial F),
      f = g * q + r ∧
      (r = 0 ∨ r.degree < g.degree) ∧
      ∀ (q' r' : Polynomial F),
        (f = g * q' + r' ∧ (r' = 0 ∨ r'.degree < g.degree)) → q = q' ∧ r = r' := by
  sorry
```
##### LeanExplore
Polynomial.div_eq_quo_add_rem_div
In: Mathlib.RingTheory.IntegralDomain

Lean Code:
theorem div_eq_quo_add_rem_div (f : R[X]) {g : R[X]} (hg : g.Monic) :
    ∃ q r : R[X], r.degree < g.degree ∧
      (algebraMap R[X] K f) / (algebraMap R[X] K g) =
        algebraMap R[X] K q + (algebraMap R[X] K r) / (algebraMap R[X] K g) := by
  refine ⟨f /ₘ g, f %ₘ g, ?_, ?_⟩
...
Show all
Gemini 3.0 Flash:
Polynomial Division in the Field of Fractions. Given a polynomial 
 and a monic polynomial 
 over a commutative domain 
, there exist polynomials 
 and 
 in 
 such that the degree of 
 is strictly less than the degree of 
, and in the field of fractions 
 of 
, the identity 
 
 
 holds.

Find similar
View Dependencies ▼
Polynomial.div_modByMonic_unique
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
theorem div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g)
    (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by
  nontriviality R
  have h₁ : r - f %ₘ g = -g * (q - f /ₘ g) :=
    eq_of_sub_eq_zero
...
Show all
Gemini 3.0 Flash:
Uniqueness of Polynomial Division and Remainder by a Monic Polynomial. Let 
 be a monic polynomial over a ring 
. For any polynomials 
 and 
 in 
, if 
 and the degree of 
 is strictly less than the degree of 
, then 
 is the quotient of 
 divided by 
 (
) and 
 is the remainder of 
 modulo 
 (
).

Find similar
View Dependencies ▼
CategoryTheory.ShortComplex.Splitting.r_f_assoc
In: Mathlib.Algebra.Homology.ShortComplex.Exact

Lean Code:
@[reassoc]
lemma r_f (s : S.Splitting) : s.r ≫ S.f = 𝟙 _ - S.g ≫ s.s := by rw [← s.id, add_sub_cancel_right]
Gemini 3.0 Flash:
Relation between Retraction and First Morphism in a Split Short Complex. In a preadditive category, given a splitting of a short complex 
 with retraction 
 and section 
, the composition of the retraction with the first morphism satisfies 𝟙
.

Find similar
View Dependencies ▼
Polynomial.divByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def divByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).1 else 0
Show all
Docstring:
divByMonic, denoted as p /ₘ q, gives the quotient of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Division by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the quotient ₘ
 is defined as the quotient resulting from the division of 
 by 
 if 
 is monic. If 
 is not monic, the quotient is defined to be 
.

Find similar
View Dependencies ▼
Polynomial.modByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def modByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).2 else p
Show all
Docstring:
modByMonic, denoted as p %ₘ q, gives the remainder of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Remainder by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the remainder of 
 divided by 
, denoted 
, is defined as the second component of the division-with-remainder algorithm if 
 is monic; otherwise, it is defined to be 
.

Find similar
View Dependencies ▼
##### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.div_eq_quo_add_rem_div (f : R[X]) {g : R[X]} (hg : g.Monic) :
  ∃ q r : R[X],
    r.degree < g.degree ∧
      (algebraMap R[X] K f) / (algebraMap R[X] K g) =
        algebraMap R[X] K q + (algebraMap R[X] K r) / (algebraMap R[X] K g) := by
  refine ⟨f /ₘ g, f %ₘ g, ?_, ?_⟩
  · exact degree_modByMonic_lt _ hg
  · have hg' : algebraMap R[X] K g ≠ 0 :=
      -- Porting note: the proof was `by exact_mod_cast Monic.ne_zero hg`
      (map_ne_zero_iff _ (IsFractionRing.injective R[X] K)).mpr (Monic.ne_zero hg)
    field_simp [hg']
    -- Porting note: `norm_cast` was here, but does nothing.
    rw [add_comm, mul_comm, ← map_mul, ← map_add, modByMonic_add_div f hg]
Doc
Copy
👍
👎
Let 
R
R be an integral domain and 
K
K its field of fractions. For any polynomial 
f
∈
R
[
X
]
f∈R[X] and monic polynomial 
g
∈
R
[
X
]
g∈R[X], there exist polynomials 
q
,
r
∈
R
[
X
]
q,r∈R[X] with 
deg
⁡
(
r
)
<
deg
⁡
(
g
)
deg(r)<deg(g) such that the rational function 
f
g
g
f
​
  in 
K
(
X
)
K(X) can be expressed as:
\[
\frac{f}{g} = q + \frac{r}{g}
\]
where 
q
q and 
r
r are the canonical quotient and remainder polynomials from polynomial division.
Copy
2	
theorem Polynomial.div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g) (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by
  nontriviality R
  have h₁ : r - f %ₘ g = -g * (q - f /ₘ g) :=
    eq_of_sub_eq_zero
      (by
        rw [← sub_eq_zero_of_eq (h.1.trans (modByMonic_add_div f hg).symm)]
        simp [mul_add, mul_comm, sub_eq_add_neg, add_comm, add_left_comm, add_assoc])
  have h₂ : degree (r - f %ₘ g) = degree (g * (q - f /ₘ g)) := by simp [h₁]
  have h₄ : degree (r - f %ₘ g) < degree g :=
    calc
      degree (r - f %ₘ g) ≤ max (degree r) (degree (f %ₘ g)) := degree_sub_le _ _
      _ < degree g := max_lt_iff.2 ⟨h.2, degree_modByMonic_lt _ hg⟩
  have h₅ : q - f /ₘ g = 0 :=
    _root_.by_contradiction fun hqf =>
      not_le_of_gt h₄ <|
        calc
          degree g ≤ degree g + degree (q - f /ₘ g) := by
            erw [degree_eq_natDegree hg.ne_zero, degree_eq_natDegree hqf, WithBot.coe_le_coe]
            exact Nat.le_add_right _ _
          _ = degree (r - f %ₘ g) := by rw [h₂, degree_mul']; simpa [Monic.def.1 hg]
  exact ⟨Eq.symm <| eq_of_sub_eq_zero h₅, Eq.symm <| eq_of_sub_eq_zero <| by simpa [h₅] using h₁⟩
Doc
Copy
👍
👎
Let 
R
R be a ring and let 
f
,
g
∈
R
[
X
]
f,g∈R[X] be polynomials with 
g
g monic. For any polynomials 
q
,
r
∈
R
[
X
]
q,r∈R[X], if 
r
+
g
⋅
q
=
f
r+g⋅q=f and 
deg
⁡
(
r
)
<
deg
⁡
(
g
)
deg(r)<deg(g), then the quotient 
f
/
m
g
f/ 
m
​
 g equals 
q
q and the remainder 
f
%
m
g
f% 
m
​
 g equals 
r
r.
Copy
3	
definition Polynomial.divModByMonicAux : ∀ (_p : R[X]) {q : R[X]}, Monic q → R[X] × R[X] | p, q, hq =>
    letI := Classical.decEq R
    if h : degree q ≤ degree p ∧ p ≠ 0 then
      let z := C (leadingCoeff p) * X ^ (natDegree p - natDegree q)
      have _wf := div_wf_lemma h hq
      let dm := divModByMonicAux (p - q * z) hq
      ⟨z + dm.1, dm.2⟩
    else ⟨0, p⟩
  termination_by p => p
Doc
Copy
👍
👎
The auxiliary function for polynomial division by a monic polynomial. Given a polynomial 
p
p and a monic polynomial 
q
q, it returns a pair 
(
d
,
r
)
(d,r) where 
d
d is the quotient and 
r
r is the remainder when dividing 
p
p by 
q
q. The division process recursively subtracts multiples of 
q
q from 
p
p until the degree condition fails.
Copy
4	
definition Polynomial.div (p q : R[X]) :=
  C (leadingCoeff q)⁻¹ * (p /ₘ (q * C (leadingCoeff q)⁻¹))
Doc
Copy
👍
👎
The division of polynomials 
p
p and 
q
q in 
R
[
X
]
R[X] is defined as 
C
(
leadingCoeff
(
q
)
)
−
1
⋅
(
p
/
m
(
q
⋅
C
(
leadingCoeff
(
q
)
)
−
1
)
)
C(leadingCoeff(q)) 
−1
 ⋅(p/ 
m
​
 (q⋅C(leadingCoeff(q)) 
−1
 )), where 
/
m
/ 
m
​
  denotes division by a monic polynomial and 
C
C is the constant polynomial embedding. This operation computes the quotient when dividing 
p
p by 
q
q in the polynomial ring 
R
[
X
]
R[X].
Copy
5	
theorem Polynomial.natDegree_mod_lt [Field k] (p : k[X]) {q : k[X]} (hq : q.natDegree ≠ 0) : (p % q).natDegree < q.natDegree := by
  have hq' : q.leadingCoeff ≠ 0 := by
    rw [leadingCoeff_ne_zero]
    contrapose! hq
    simp [hq]
  rw [mod_def]
  refine (natDegree_modByMonic_lt p ?_ ?_).trans_le ?_
  · refine monic_mul_C_of_leadingCoeff_mul_eq_one ?_
    rw [mul_inv_eq_one₀ hq']
  · contrapose! hq
    rw [← natDegree_mul_C_eq_of_mul_eq_one ((inv_mul_eq_one₀ hq').mpr rfl)]
    simp [hq]
  · exact natDegree_mul_C_le q q.leadingCoeff⁻¹
Doc
Copy
👍
👎
Let 
k
k be a field and 
p
,
q
∈
k
[
X
]
p,q∈k[X] be polynomials such that the natural degree of 
q
q is nonzero. Then the natural degree of the remainder 
p
m
o
d
 
 
q
pmodq is strictly less than the natural degree of 
q
q, i.e.,
deg
⁡
(
p
m
o
d
 
 
q
)
<
deg
⁡
(
q
)
.
deg(pmodq)<deg(q).
Copy
#### Hallucination 1: `divModByMonic_eq_div_mod`
##### Hallucination only
###### Query
```text
divModByMonic_eq_div_mod
```
###### LeanExplore
Polynomial.divByMonic_eq_div
In: Mathlib.Algebra.Polynomial.FieldDivision

Lean Code:
theorem divByMonic_eq_div (p : R[X]) (hq : Monic q) : p /ₘ q = p / q :=
  show p /ₘ q = C (leadingCoeff q)⁻¹ * (p /ₘ (q * C (leadingCoeff q)⁻¹)) by
    simp only [Monic.def.1 hq, inv_one, C_1, one_mul, mul_one]
Gemini 3.0 Flash:
Equivalence of Polynomial Division and Division by a Monic Polynomial. For any polynomial 
 and any monic polynomial 
 over a field, the quotient obtained from the specialized division by a monic polynomial is equal to the standard polynomial quotient.

Find similar
View Dependencies ▼
Polynomial.decidableDvdMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
@[deprecated Classical.dec (since := "2026-02-07")]
def decidableDvdMonic [DecidableEq R] (p : R[X]) (hq : Monic q) : Decidable (q ∣ p) :=
  decidable_of_iff (p %ₘ q = 0) (modByMonic_eq_zero_iff_dvd hq)
Show all
Docstring:
An algorithm for deciding polynomial divisibility. Prefer Classical.dec, as the algorithm relies on %ₘ and so is noncomputable.

Gemini 3.0 Flash:
Decidability of Divisibility by a Monic Polynomial. Given a commutative ring 
 with decidable equality, for any polynomial 
 and any monic polynomial 
, it is decidable whether 
 divides 
. This is determined by checking if the remainder of 
 divided by 
 (via the modByMonic algorithm) is equal to zero.

Find similar
View Dependencies ▼
Polynomial.modByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def modByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).2 else p
Show all
Docstring:
modByMonic, denoted as p %ₘ q, gives the remainder of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Remainder by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the remainder of 
 divided by 
, denoted 
, is defined as the second component of the division-with-remainder algorithm if 
 is monic; otherwise, it is defined to be 
.

Find similar
View Dependencies ▼
Polynomial.modByMonic_eq_mod
In: Mathlib.Algebra.Polynomial.FieldDivision

Lean Code:
theorem modByMonic_eq_mod (p : R[X]) (hq : Monic q) : p %ₘ q = p % q :=
  show p %ₘ q = p %ₘ (q * C (leadingCoeff q)⁻¹) by
    simp only [Monic.def.1 hq, inv_one, mul_one, C_1]
Gemini 3.0 Flash:
Equality of Polynomial Remainder Operations for Monic Polynomials. For any polynomial 
 and any monic polynomial 
 over a field, the remainder of 
 divided by 
 using the general division algorithm is equal to the remainder obtained specifically via the division algorithm for monic polynomials.

Find similar
View Dependencies ▼
Int.ModEq
In: Mathlib.Data.Int.ModEq

Lean Code:
def Int.ModEq (n a b : ℤ) :=
  a % n = b % n
Show all
Docstring:
a ≡ b [ZMOD n] when a % n = b % n.

Gemini 3.0 Flash:
Modular Congruence of Integers. For any integers 
, 
, and 
, we say that 
 is congruent to 
 modulo 
, denoted 
, if the remainder of 
 divided by 
 is equal to the remainder of 
 divided by 
.

Find similar
View Dependencies ▼
###### LeanFinder
Rank	Formal statement	Informal statement
1	
definition Polynomial.divByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).1 else 0
Doc
Copy
👍
👎
Given polynomials 
p
p and 
q
q over a ring 
R
R, the function 
divByMonic
divByMonic computes the quotient of 
p
p divided by 
q
q when 
q
q is monic (i.e., has leading coefficient 1). If 
q
q is not monic, the function returns 0. The division is denoted by 
p
/
m
q
p/ 
m
​
 q.
Copy
2	
definition Polynomial.modByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).2 else p
Doc
Copy
👍
👎
The function modByMonic, denoted as p %ₘ q, gives the remainder when dividing the polynomial p by a monic polynomial q. If q is not monic, it returns p unchanged.
Copy
3	
theorem Polynomial.modByMonic_eq_sub_mul_div : ∀ (p : R[X]) {q : R[X]} (_hq : Monic q), p %ₘ q = p - q * (p /ₘ q) | p, q, hq =>
    letI := Classical.decEq R
    if h : degree q ≤ degree p ∧ p ≠ 0 then by
      have _wf := div_wf_lemma h hq
      have ih := modByMonic_eq_sub_mul_div
        (p - q * (C (leadingCoeff p) * X ^ (natDegree p - natDegree q))) hq
      unfold modByMonic divByMonic divModByMonicAux
      dsimp
      rw [dif_pos hq, if_pos h]
      rw [modByMonic, dif_pos hq] at ih
      refine ih.trans ?_
      unfold divByMonic
      rw [dif_pos hq, dif_pos hq, if_pos h, mul_add, sub_add_eq_sub_sub]
    else by
      unfold modByMonic divByMonic divModByMonicAux
      dsimp
      rw [dif_pos hq, if_neg h, dif_pos hq, if_neg h, mul_zero, sub_zero]
  termination_by p => p
Doc
Copy
👍
👎
For any polynomial 
p
p over a ring 
R
R and any monic polynomial 
q
q, the remainder of 
p
p divided by 
q
q satisfies 
p
%
m
q
=
p
−
q
⋅
(
p
/
m
q
)
p% 
m
​
 q=p−q⋅(p/ 
m
​
 q), where 
/
m
/ 
m
​
  denotes division by a monic polynomial and 
%
m
% 
m
​
  denotes the remainder of such division.
Copy
4	
theorem Polynomial.div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g) (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by
  nontriviality R
  have h₁ : r - f %ₘ g = -g * (q - f /ₘ g) :=
    eq_of_sub_eq_zero
      (by
        rw [← sub_eq_zero_of_eq (h.1.trans (modByMonic_add_div f hg).symm)]
        simp [mul_add, mul_comm, sub_eq_add_neg, add_comm, add_left_comm, add_assoc])
  have h₂ : degree (r - f %ₘ g) = degree (g * (q - f /ₘ g)) := by simp [h₁]
  have h₄ : degree (r - f %ₘ g) < degree g :=
    calc
      degree (r - f %ₘ g) ≤ max (degree r) (degree (f %ₘ g)) := degree_sub_le _ _
      _ < degree g := max_lt_iff.2 ⟨h.2, degree_modByMonic_lt _ hg⟩
  have h₅ : q - f /ₘ g = 0 :=
    _root_.by_contradiction fun hqf =>
      not_le_of_gt h₄ <|
        calc
          degree g ≤ degree g + degree (q - f /ₘ g) := by
            erw [degree_eq_natDegree hg.ne_zero, degree_eq_natDegree hqf, WithBot.coe_le_coe]
            exact Nat.le_add_right _ _
          _ = degree (r - f %ₘ g) := by rw [h₂, degree_mul']; simpa [Monic.def.1 hg]
  exact ⟨Eq.symm <| eq_of_sub_eq_zero h₅, Eq.symm <| eq_of_sub_eq_zero <| by simpa [h₅] using h₁⟩
Doc
Copy
👍
👎
Let 
R
R be a ring and let 
f
,
g
∈
R
[
X
]
f,g∈R[X] be polynomials with 
g
g monic. For any polynomials 
q
,
r
∈
R
[
X
]
q,r∈R[X], if 
r
+
g
⋅
q
=
f
r+g⋅q=f and 
deg
⁡
(
r
)
<
deg
⁡
(
g
)
deg(r)<deg(g), then the quotient 
f
/
m
g
f/ 
m
​
 g equals 
q
q and the remainder 
f
%
m
g
f% 
m
​
 g equals 
r
r.
Copy
5	
theorem Polynomial.modByMonic_add_div (p : R[X]) {q : R[X]} (hq : Monic q) : p %ₘ q + q * (p /ₘ q) = p :=
  eq_sub_iff_add_eq.1 (modByMonic_eq_sub_mul_div p hq)
Doc
Copy
👍
👎
For any polynomial 
p
p over a ring 
R
R and any monic polynomial 
q
q, the sum of the remainder 
p
%
m
q
p% 
m
​
 q and the product 
q
⋅
(
p
/
m
q
)
q⋅(p/ 
m
​
 q) equals 
p
p, i.e.,
p
%
m
q
+
q
⋅
(
p
/
m
q
)
=
p
.
p% 
m
​
 q+q⋅(p/ 
m
​
 q)=p.
Copy
##### Hallucination + statement
###### Query
```text
divModByMonic_eq_div_mod
theorem polynomial_division_algorithm {F : Type*} [Field F] (f g : Polynomial F) (hg : g ≠ 0) :
    ∃ (q r : Polynomial F),
      f = g * q + r ∧
      (r = 0 ∨ r.degree < g.degree) ∧
      ∀ (q' r' : Polynomial F),
        (f = g * q' + r' ∧ (r' = 0 ∨ r'.degree < g.degree)) → q = q' ∧ r = r' := by
  sorry
```
###### LeanExplore
Polynomial.div_modByMonic_unique
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
theorem div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g)
    (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by
  nontriviality R
  have h₁ : r - f %ₘ g = -g * (q - f /ₘ g) :=
    eq_of_sub_eq_zero
...
Show all
Gemini 3.0 Flash:
Uniqueness of Polynomial Division and Remainder by a Monic Polynomial. Let 
 be a monic polynomial over a ring 
. For any polynomials 
 and 
 in 
, if 
 and the degree of 
 is strictly less than the degree of 
, then 
 is the quotient of 
 divided by 
 (
) and 
 is the remainder of 
 modulo 
 (
).

Find similar
View Dependencies ▼
Polynomial.natDegree_divByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
theorem natDegree_divByMonic (f : R[X]) {g : R[X]} (hg : g.Monic) :
    natDegree (f /ₘ g) = natDegree f - natDegree g := by
  nontriviality R
  by_cases hfg : f /ₘ g = 0
  · rw [hfg, natDegree_zero]
...
Show all
Gemini 3.0 Flash:
Degree of the Quotient by a Monic Polynomial. For any polynomial 
 and any monic polynomial 
 over a ring 
, the natural degree of the quotient 
 is equal to the difference between the natural degree of 
 and the natural degree of 
, specifically 
 (where the difference is defined as 
 if 
).

Find similar
View Dependencies ▼
Polynomial.divByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def divByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).1 else 0
Show all
Docstring:
divByMonic, denoted as p /ₘ q, gives the quotient of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Division by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the quotient ₘ
 is defined as the quotient resulting from the division of 
 by 
 if 
 is monic. If 
 is not monic, the quotient is defined to be 
.

Find similar
View Dependencies ▼
Polynomial.modByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def modByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).2 else p
Show all
Docstring:
modByMonic, denoted as p %ₘ q, gives the remainder of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Remainder by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the remainder of 
 divided by 
, denoted 
, is defined as the second component of the division-with-remainder algorithm if 
 is monic; otherwise, it is defined to be 
.

Find similar
View Dependencies ▼
MonomialOrder.div_single
In: Mathlib.RingTheory.MvPolynomial.Groebner

Lean Code:
theorem div_single {b : MvPolynomial σ R}
    (hb : IsUnit (m.leadingCoeff b)) (f : MvPolynomial σ R) :
    ∃ (g : MvPolynomial σ R) (r : MvPolynomial σ R),
      f = g * b + r ∧
        (m.degree (b * g) ≼[m] m.degree f) ∧
...
Show all
Docstring:
Division by a multivariate polynomial whose leading coefficient is invertible with respect to a monomial order

Gemini 3.0 Flash:
Division of Multivariate Polynomials by a Single Divisor. Given a multivariate polynomial 
 and a divisor 
 whose leading coefficient with respect to a monomial order 
 is a unit, there exist a quotient 
 and a remainder 
 such that 
. This decomposition satisfies two conditions: first, the degree of the product 
 is less than or equal to the degree of 
 under the order 
; second, no monomial in the support of the remainder 
 is divisible by the leading monomial of 
.

Find similar
View Dependencies ▼
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.div_eq_quo_add_rem_div (f : R[X]) {g : R[X]} (hg : g.Monic) :
  ∃ q r : R[X],
    r.degree < g.degree ∧
      (algebraMap R[X] K f) / (algebraMap R[X] K g) =
        algebraMap R[X] K q + (algebraMap R[X] K r) / (algebraMap R[X] K g) := by
  refine ⟨f /ₘ g, f %ₘ g, ?_, ?_⟩
  · exact degree_modByMonic_lt _ hg
  · have hg' : algebraMap R[X] K g ≠ 0 :=
      -- Porting note: the proof was `by exact_mod_cast Monic.ne_zero hg`
      (map_ne_zero_iff _ (IsFractionRing.injective R[X] K)).mpr (Monic.ne_zero hg)
    field_simp [hg']
    -- Porting note: `norm_cast` was here, but does nothing.
    rw [add_comm, mul_comm, ← map_mul, ← map_add, modByMonic_add_div f hg]
Doc
Copy
👍
👎
Let 
R
R be an integral domain and 
K
K its field of fractions. For any polynomial 
f
∈
R
[
X
]
f∈R[X] and monic polynomial 
g
∈
R
[
X
]
g∈R[X], there exist polynomials 
q
,
r
∈
R
[
X
]
q,r∈R[X] with 
deg
⁡
(
r
)
<
deg
⁡
(
g
)
deg(r)<deg(g) such that the rational function 
f
g
g
f
​
  in 
K
(
X
)
K(X) can be expressed as:
\[
\frac{f}{g} = q + \frac{r}{g}
\]
where 
q
q and 
r
r are the canonical quotient and remainder polynomials from polynomial division.
Copy
2	
theorem Polynomial.div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g) (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by
  nontriviality R
  have h₁ : r - f %ₘ g = -g * (q - f /ₘ g) :=
    eq_of_sub_eq_zero
      (by
        rw [← sub_eq_zero_of_eq (h.1.trans (modByMonic_add_div f hg).symm)]
        simp [mul_add, mul_comm, sub_eq_add_neg, add_comm, add_left_comm, add_assoc])
  have h₂ : degree (r - f %ₘ g) = degree (g * (q - f /ₘ g)) := by simp [h₁]
  have h₄ : degree (r - f %ₘ g) < degree g :=
    calc
      degree (r - f %ₘ g) ≤ max (degree r) (degree (f %ₘ g)) := degree_sub_le _ _
      _ < degree g := max_lt_iff.2 ⟨h.2, degree_modByMonic_lt _ hg⟩
  have h₅ : q - f /ₘ g = 0 :=
    _root_.by_contradiction fun hqf =>
      not_le_of_gt h₄ <|
        calc
          degree g ≤ degree g + degree (q - f /ₘ g) := by
            erw [degree_eq_natDegree hg.ne_zero, degree_eq_natDegree hqf, WithBot.coe_le_coe]
            exact Nat.le_add_right _ _
          _ = degree (r - f %ₘ g) := by rw [h₂, degree_mul']; simpa [Monic.def.1 hg]
  exact ⟨Eq.symm <| eq_of_sub_eq_zero h₅, Eq.symm <| eq_of_sub_eq_zero <| by simpa [h₅] using h₁⟩
Doc
Copy
👍
👎
Let 
R
R be a ring and let 
f
,
g
∈
R
[
X
]
f,g∈R[X] be polynomials with 
g
g monic. For any polynomials 
q
,
r
∈
R
[
X
]
q,r∈R[X], if 
r
+
g
⋅
q
=
f
r+g⋅q=f and 
deg
⁡
(
r
)
<
deg
⁡
(
g
)
deg(r)<deg(g), then the quotient 
f
/
m
g
f/ 
m
​
 g equals 
q
q and the remainder 
f
%
m
g
f% 
m
​
 g equals 
r
r.
Copy
3	
definition Polynomial.divModByMonicAux : ∀ (_p : R[X]) {q : R[X]}, Monic q → R[X] × R[X] | p, q, hq =>
    letI := Classical.decEq R
    if h : degree q ≤ degree p ∧ p ≠ 0 then
      let z := C (leadingCoeff p) * X ^ (natDegree p - natDegree q)
      have _wf := div_wf_lemma h hq
      let dm := divModByMonicAux (p - q * z) hq
      ⟨z + dm.1, dm.2⟩
    else ⟨0, p⟩
  termination_by p => p
Doc
Copy
👍
👎
The auxiliary function for polynomial division by a monic polynomial. Given a polynomial 
p
p and a monic polynomial 
q
q, it returns a pair 
(
d
,
r
)
(d,r) where 
d
d is the quotient and 
r
r is the remainder when dividing 
p
p by 
q
q. The division process recursively subtracts multiples of 
q
q from 
p
p until the degree condition fails.
Copy
4	
definition Polynomial.divByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).1 else 0
Doc
Copy
👍
👎
Given polynomials 
p
p and 
q
q over a ring 
R
R, the function 
divByMonic
divByMonic computes the quotient of 
p
p divided by 
q
q when 
q
q is monic (i.e., has leading coefficient 1). If 
q
q is not monic, the function returns 0. The division is denoted by 
p
/
m
q
p/ 
m
​
 q.
Copy
5	
theorem Polynomial.modByMonic_eq_sub_mul_div : ∀ (p : R[X]) {q : R[X]} (_hq : Monic q), p %ₘ q = p - q * (p /ₘ q) | p, q, hq =>
    letI := Classical.decEq R
    if h : degree q ≤ degree p ∧ p ≠ 0 then by
      have _wf := div_wf_lemma h hq
      have ih := modByMonic_eq_sub_mul_div
        (p - q * (C (leadingCoeff p) * X ^ (natDegree p - natDegree q))) hq
      unfold modByMonic divByMonic divModByMonicAux
      dsimp
      rw [dif_pos hq, if_pos h]
      rw [modByMonic, dif_pos hq] at ih
      refine ih.trans ?_
      unfold divByMonic
      rw [dif_pos hq, dif_pos hq, if_pos h, mul_add, sub_add_eq_sub_sub]
    else by
      unfold modByMonic divByMonic divModByMonicAux
      dsimp
      rw [dif_pos hq, if_neg h, dif_pos hq, if_neg h, mul_zero, sub_zero]
  termination_by p => p
Doc
Copy
👍
👎
For any polynomial 
p
p over a ring 
R
R and any monic polynomial 
q
q, the remainder of 
p
p divided by 
q
q satisfies 
p
%
m
q
=
p
−
q
⋅
(
p
/
m
q
)
p% 
m
​
 q=p−q⋅(p/ 
m
​
 q), where 
/
m
/ 
m
​
  denotes division by a monic polynomial and 
%
m
% 
m
​
  denotes the remainder of such division.
Copy
#### Hallucination 2: `modByMonic_lt_of_lt`
##### Hallucination only
###### Query
```text
modByMonic_lt_of_lt
```
###### LeanExplore
Polynomial.modByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def modByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).2 else p
Show all
Docstring:
modByMonic, denoted as p %ₘ q, gives the remainder of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Remainder by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the remainder of 
 divided by 
, denoted 
, is defined as the second component of the division-with-remainder algorithm if 
 is monic; otherwise, it is defined to be 
.

Find similar
View Dependencies ▼
Polynomial.modByMonicHom
In: Mathlib.Algebra.Polynomial.RingDivision

Lean Code:
@[simps]
def modByMonicHom (q : R[X]) : R[X] →ₗ[R] R[X] where
  toFun p := p %ₘ q
  map_add' := add_modByMonic
  map_smul' := smul_modByMonic
...
Show all
Docstring:
_ %ₘ q as an R-linear map.

Gemini 3.0 Flash:
Polynomial Remainder as a Linear Map. For a fixed polynomial 
 over a commutative ring 
, the operation of taking the remainder of a polynomial 
 modulo 
 (using the monic division algorithm) defines an 
-linear map from 
 to itself.

Find similar
View Dependencies ▼
MulLeftStrictMono
In: Mathlib.Algebra.Order.Monoid.Unbundled.Defs

Lean Code:
abbrev MulLeftStrictMono [Mul M] [LT M] : Prop :=
  CovariantClass M M (· * ·) (· < ·)
Show all
Docstring:
Typeclass for monotonicity of multiplication on the left, namely b₁ < b₂ → a * b₁ < a * b₂.

You should usually not use this very granular typeclass directly, but rather a typeclass like OrderedCommGroup.

Gemini 3.0 Flash:
Strict Left Monotonicity of Multiplication. A property of a type equipped with multiplication and a less-than relation, asserting that for any elements 
, 
, and 
, if 
, then 
.

Find similar
View Dependencies ▼
Polynomial.modByMonicHom_apply
In: Mathlib.Algebra.Polynomial.RingDivision

Lean Code:
@[simps]
def modByMonicHom (q : R[X]) : R[X] →ₗ[R] R[X] where
  toFun p := p %ₘ q
Gemini 3.0 Flash:
Polynomial Remainder Linear Map. For a fixed polynomial 
 over a commutative ring 
, the map that sends any polynomial 
 to its remainder 
 (calculated via the monic division algorithm) is an 
-linear map from 
 to itself.

Find similar
View Dependencies ▼
Polynomial.mul_modByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
lemma mul_modByMonic (p₁ p₂ q : R[X]) : (p₁ * p₂) %ₘ q = (p₁ %ₘ q) * (p₂ %ₘ q) %ₘ q := by
  by_cases! h : ¬ q.Monic
  · simp [Polynomial.modByMonic_eq_of_not_monic _ h]
  apply Polynomial.modByMonic_eq_of_dvd_sub h
  have : p₁ * p₂ - p₁ %ₘ q * (p₂ %ₘ q) = (p₁ %ₘ q) * (p₂ - p₂ %ₘ q) + p₂ * (p₁ - p₁ %ₘ q) := by ring
...
Show all
Gemini 3.0 Flash:
Multiplication of Polynomials Modulo a Monic Polynomial. For any two polynomials 
 and a polynomial 
 over a commutative ring, the remainder of the product 
 divided by 
 is equal to the remainder of the product of their individual remainders 
 divided by 
, where the remainder is taken with respect to the monic division algorithm.

Find similar
View Dependencies ▼
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.degree_modByMonic_lt [Nontrivial R] : ∀ (p : R[X]) {q : R[X]} (_hq : Monic q), degree (p %ₘ q) < degree q | p, q, hq =>
    letI := Classical.decEq R
    if h : degree q ≤ degree p ∧ p ≠ 0 then by
      have _wf := div_wf_lemma ⟨h.1, h.2⟩ hq
      have :=
        degree_modByMonic_lt (p - q * (C (leadingCoeff p) * X ^ (natDegree p - natDegree q))) hq
      unfold modByMonic at this ⊢
      unfold divModByMonicAux
      dsimp
      rw [dif_pos hq] at this ⊢
      rw [if_pos h]
      exact this
    else
      Or.casesOn (not_and_or.1 h)
        (by
          unfold modByMonic divModByMonicAux
          dsimp
          rw [dif_pos hq, if_neg h]
          exact lt_of_not_ge)
        (by
          intro hp
          unfold modByMonic divModByMonicAux
          dsimp
          rw [dif_pos hq, if_neg h, Classical.not_not.1 hp]
          exact lt_of_le_of_ne bot_le (Ne.symm (mt degree_eq_bot.1 hq.ne_zero)))
  termination_by p => p
Doc
Copy
👍
👎
Let 
R
R be a nontrivial ring. For any polynomial 
p
∈
R
[
X
]
p∈R[X] and any monic polynomial 
q
∈
R
[
X
]
q∈R[X], the degree of the remainder 
p
m
o
d
 
 
q
pmodq is strictly less than the degree of 
q
q.
Copy
2	
definition Polynomial.modByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).2 else p
Doc
Copy
👍
👎
The function modByMonic, denoted as p %ₘ q, gives the remainder when dividing the polynomial p by a monic polynomial q. If q is not monic, it returns p unchanged.
Copy
3	
theorem Polynomial.degree_modByMonic_le (p : R[X]) {q : R[X]} (hq : Monic q) : degree (p %ₘ q) ≤ degree q := by
  nontriviality R
  exact (degree_modByMonic_lt _ hq).le
Doc
Copy
👍
👎
For any polynomial 
p
p over a ring 
R
R and any monic polynomial 
q
∈
R
[
X
]
q∈R[X], the degree of the remainder 
p
m
o
d
 
 
q
pmodq is less than or equal to the degree of 
q
q, i.e., 
deg
⁡
(
p
%
m
q
)
≤
deg
⁡
(
q
)
deg(p% 
m
​
 q)≤deg(q).
Copy
4	
theorem Polynomial.natDegree_modByMonic_le (p : Polynomial R) {g : Polynomial R} (hg : g.Monic) : natDegree (p %ₘ g) ≤ g.natDegree :=
  natDegree_le_natDegree (degree_modByMonic_le p hg)
Doc
Copy
👍
👎
For any polynomial 
p
p over a ring 
R
R and any monic polynomial 
g
∈
R
[
X
]
g∈R[X], the natural degree of the remainder 
p
m
o
d
 
 
g
pmodg is less than or equal to the natural degree of 
g
g, i.e., 
natDegree
(
p
%
m
g
)
≤
natDegree
(
g
)
natDegree(p% 
m
​
 g)≤natDegree(g).
Copy
5	
theorem Polynomial.natDegree_modByMonic_lt (p : R[X]) {q : R[X]} (hmq : Monic q) (hq : q ≠ 1) : natDegree (p %ₘ q) < q.natDegree := by
  by_cases hpq : p %ₘ q = 0
  · rw [hpq, natDegree_zero, Nat.pos_iff_ne_zero]
    contrapose! hq
    exact eq_one_of_monic_natDegree_zero hmq hq
  · haveI := Nontrivial.of_polynomial_ne hpq
    exact natDegree_lt_natDegree hpq (degree_modByMonic_lt p hmq)
Doc
Copy
👍
👎
Let 
R
R be a ring and let 
p
,
q
∈
R
[
X
]
p,q∈R[X] be polynomials such that 
q
q is monic and 
q
≠
1
q

=1. Then the remainder 
p
m
o
d
 
 
q
pmodq satisfies 
deg
⁡
(
p
m
o
d
 
 
q
)
<
deg
⁡
(
q
)
deg(pmodq)<deg(q), where 
deg
⁡
deg denotes the degree of a polynomial.
Copy
##### Hallucination + statement
###### Query
```text
modByMonic_lt_of_lt
theorem polynomial_division_algorithm {F : Type*} [Field F] (f g : Polynomial F) (hg : g ≠ 0) :
    ∃ (q r : Polynomial F),
      f = g * q + r ∧
      (r = 0 ∨ r.degree < g.degree) ∧
      ∀ (q' r' : Polynomial F),
        (f = g * q' + r' ∧ (r' = 0 ∨ r'.degree < g.degree)) → q = q' ∧ r = r' := by
  sorry
```
###### LeanExplore
Polynomial.div_modByMonic_unique
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
theorem div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g)
    (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by
  nontriviality R
  have h₁ : r - f %ₘ g = -g * (q - f /ₘ g) :=
    eq_of_sub_eq_zero
...
Show all
Gemini 3.0 Flash:
Uniqueness of Polynomial Division and Remainder by a Monic Polynomial. Let 
 be a monic polynomial over a ring 
. For any polynomials 
 and 
 in 
, if 
 and the degree of 
 is strictly less than the degree of 
, then 
 is the quotient of 
 divided by 
 (
) and 
 is the remainder of 
 modulo 
 (
).

Find similar
View Dependencies ▼
Polynomial.natDegree_divByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
theorem natDegree_divByMonic (f : R[X]) {g : R[X]} (hg : g.Monic) :
    natDegree (f /ₘ g) = natDegree f - natDegree g := by
  nontriviality R
  by_cases hfg : f /ₘ g = 0
  · rw [hfg, natDegree_zero]
...
Show all
Gemini 3.0 Flash:
Degree of the Quotient by a Monic Polynomial. For any polynomial 
 and any monic polynomial 
 over a ring 
, the natural degree of the quotient 
 is equal to the difference between the natural degree of 
 and the natural degree of 
, specifically 
 (where the difference is defined as 
 if 
).

Find similar
View Dependencies ▼
Polynomial.divByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def divByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).1 else 0
Show all
Docstring:
divByMonic, denoted as p /ₘ q, gives the quotient of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Division by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the quotient ₘ
 is defined as the quotient resulting from the division of 
 by 
 if 
 is monic. If 
 is not monic, the quotient is defined to be 
.

Find similar
View Dependencies ▼
MonomialOrder.div_single
In: Mathlib.RingTheory.MvPolynomial.Groebner

Lean Code:
theorem div_single {b : MvPolynomial σ R}
    (hb : IsUnit (m.leadingCoeff b)) (f : MvPolynomial σ R) :
    ∃ (g : MvPolynomial σ R) (r : MvPolynomial σ R),
      f = g * b + r ∧
        (m.degree (b * g) ≼[m] m.degree f) ∧
...
Show all
Docstring:
Division by a multivariate polynomial whose leading coefficient is invertible with respect to a monomial order

Gemini 3.0 Flash:
Division of Multivariate Polynomials by a Single Divisor. Given a multivariate polynomial 
 and a divisor 
 whose leading coefficient with respect to a monomial order 
 is a unit, there exist a quotient 
 and a remainder 
 such that 
. This decomposition satisfies two conditions: first, the degree of the product 
 is less than or equal to the degree of 
 under the order 
; second, no monomial in the support of the remainder 
 is divisible by the leading monomial of 
.

Find similar
View Dependencies ▼
Polynomial.modByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def modByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).2 else p
Show all
Docstring:
modByMonic, denoted as p %ₘ q, gives the remainder of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Remainder by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the remainder of 
 divided by 
, denoted 
, is defined as the second component of the division-with-remainder algorithm if 
 is monic; otherwise, it is defined to be 
.

Find similar
View Dependencies ▼
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g) (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by
  nontriviality R
  have h₁ : r - f %ₘ g = -g * (q - f /ₘ g) :=
    eq_of_sub_eq_zero
      (by
        rw [← sub_eq_zero_of_eq (h.1.trans (modByMonic_add_div f hg).symm)]
        simp [mul_add, mul_comm, sub_eq_add_neg, add_comm, add_left_comm, add_assoc])
  have h₂ : degree (r - f %ₘ g) = degree (g * (q - f /ₘ g)) := by simp [h₁]
  have h₄ : degree (r - f %ₘ g) < degree g :=
    calc
      degree (r - f %ₘ g) ≤ max (degree r) (degree (f %ₘ g)) := degree_sub_le _ _
      _ < degree g := max_lt_iff.2 ⟨h.2, degree_modByMonic_lt _ hg⟩
  have h₅ : q - f /ₘ g = 0 :=
    _root_.by_contradiction fun hqf =>
      not_le_of_gt h₄ <|
        calc
          degree g ≤ degree g + degree (q - f /ₘ g) := by
            erw [degree_eq_natDegree hg.ne_zero, degree_eq_natDegree hqf, WithBot.coe_le_coe]
            exact Nat.le_add_right _ _
          _ = degree (r - f %ₘ g) := by rw [h₂, degree_mul']; simpa [Monic.def.1 hg]
  exact ⟨Eq.symm <| eq_of_sub_eq_zero h₅, Eq.symm <| eq_of_sub_eq_zero <| by simpa [h₅] using h₁⟩
Doc
Copy
👍
👎
Let 
R
R be a ring and let 
f
,
g
∈
R
[
X
]
f,g∈R[X] be polynomials with 
g
g monic. For any polynomials 
q
,
r
∈
R
[
X
]
q,r∈R[X], if 
r
+
g
⋅
q
=
f
r+g⋅q=f and 
deg
⁡
(
r
)
<
deg
⁡
(
g
)
deg(r)<deg(g), then the quotient 
f
/
m
g
f/ 
m
​
 g equals 
q
q and the remainder 
f
%
m
g
f% 
m
​
 g equals 
r
r.
Copy
2	
theorem Polynomial.div_eq_quo_add_rem_div (f : R[X]) {g : R[X]} (hg : g.Monic) :
  ∃ q r : R[X],
    r.degree < g.degree ∧
      (algebraMap R[X] K f) / (algebraMap R[X] K g) =
        algebraMap R[X] K q + (algebraMap R[X] K r) / (algebraMap R[X] K g) := by
  refine ⟨f /ₘ g, f %ₘ g, ?_, ?_⟩
  · exact degree_modByMonic_lt _ hg
  · have hg' : algebraMap R[X] K g ≠ 0 :=
      -- Porting note: the proof was `by exact_mod_cast Monic.ne_zero hg`
      (map_ne_zero_iff _ (IsFractionRing.injective R[X] K)).mpr (Monic.ne_zero hg)
    field_simp [hg']
    -- Porting note: `norm_cast` was here, but does nothing.
    rw [add_comm, mul_comm, ← map_mul, ← map_add, modByMonic_add_div f hg]
Doc
Copy
👍
👎
Let 
R
R be an integral domain and 
K
K its field of fractions. For any polynomial 
f
∈
R
[
X
]
f∈R[X] and monic polynomial 
g
∈
R
[
X
]
g∈R[X], there exist polynomials 
q
,
r
∈
R
[
X
]
q,r∈R[X] with 
deg
⁡
(
r
)
<
deg
⁡
(
g
)
deg(r)<deg(g) such that the rational function 
f
g
g
f
​
  in 
K
(
X
)
K(X) can be expressed as:
\[
\frac{f}{g} = q + \frac{r}{g}
\]
where 
q
q and 
r
r are the canonical quotient and remainder polynomials from polynomial division.
Copy
3	
definition Polynomial.divModByMonicAux : ∀ (_p : R[X]) {q : R[X]}, Monic q → R[X] × R[X] | p, q, hq =>
    letI := Classical.decEq R
    if h : degree q ≤ degree p ∧ p ≠ 0 then
      let z := C (leadingCoeff p) * X ^ (natDegree p - natDegree q)
      have _wf := div_wf_lemma h hq
      let dm := divModByMonicAux (p - q * z) hq
      ⟨z + dm.1, dm.2⟩
    else ⟨0, p⟩
  termination_by p => p
Doc
Copy
👍
👎
The auxiliary function for polynomial division by a monic polynomial. Given a polynomial 
p
p and a monic polynomial 
q
q, it returns a pair 
(
d
,
r
)
(d,r) where 
d
d is the quotient and 
r
r is the remainder when dividing 
p
p by 
q
q. The division process recursively subtracts multiples of 
q
q from 
p
p until the degree condition fails.
Copy
4	
definition Polynomial.divByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).1 else 0
Doc
Copy
👍
👎
Given polynomials 
p
p and 
q
q over a ring 
R
R, the function 
divByMonic
divByMonic computes the quotient of 
p
p divided by 
q
q when 
q
q is monic (i.e., has leading coefficient 1). If 
q
q is not monic, the function returns 0. The division is denoted by 
p
/
m
q
p/ 
m
​
 q.
Copy
5	
theorem Polynomial.natDegree_mod_lt [Field k] (p : k[X]) {q : k[X]} (hq : q.natDegree ≠ 0) : (p % q).natDegree < q.natDegree := by
  have hq' : q.leadingCoeff ≠ 0 := by
    rw [leadingCoeff_ne_zero]
    contrapose! hq
    simp [hq]
  rw [mod_def]
  refine (natDegree_modByMonic_lt p ?_ ?_).trans_le ?_
  · refine monic_mul_C_of_leadingCoeff_mul_eq_one ?_
    rw [mul_inv_eq_one₀ hq']
  · contrapose! hq
    rw [← natDegree_mul_C_eq_of_mul_eq_one ((inv_mul_eq_one₀ hq').mpr rfl)]
    simp [hq]
  · exact natDegree_mul_C_le q q.leadingCoeff⁻¹
Doc
Copy
👍
👎
Let 
k
k be a field and 
p
,
q
∈
k
[
X
]
p,q∈k[X] be polynomials such that the natural degree of 
q
q is nonzero. Then the natural degree of the remainder 
p
m
o
d
 
 
q
pmodq is strictly less than the natural degree of 
q
q, i.e.,
deg
⁡
(
p
m
o
d
 
 
q
)
<
deg
⁡
(
q
)
.
deg(pmodq)<deg(q).
Copy
#### Statement + both hallucinations
##### Query
```text
divModByMonic_eq_div_mod
modByMonic_lt_of_lt
theorem polynomial_division_algorithm {F : Type*} [Field F] (f g : Polynomial F) (hg : g ≠ 0) :
    ∃ (q r : Polynomial F),
      f = g * q + r ∧
      (r = 0 ∨ r.degree < g.degree) ∧
      ∀ (q' r' : Polynomial F),
        (f = g * q' + r' ∧ (r' = 0 ∨ r'.degree < g.degree)) → q = q' ∧ r = r' := by
  sorry
```
##### LeanExplore
Polynomial.div_modByMonic_unique
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
theorem div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g)
    (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by
  nontriviality R
  have h₁ : r - f %ₘ g = -g * (q - f /ₘ g) :=
    eq_of_sub_eq_zero
...
Show all
Gemini 3.0 Flash:
Uniqueness of Polynomial Division and Remainder by a Monic Polynomial. Let 
 be a monic polynomial over a ring 
. For any polynomials 
 and 
 in 
, if 
 and the degree of 
 is strictly less than the degree of 
, then 
 is the quotient of 
 divided by 
 (
) and 
 is the remainder of 
 modulo 
 (
).

Find similar
View Dependencies ▼
Polynomial.divByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def divByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).1 else 0
Show all
Docstring:
divByMonic, denoted as p /ₘ q, gives the quotient of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Division by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the quotient ₘ
 is defined as the quotient resulting from the division of 
 by 
 if 
 is monic. If 
 is not monic, the quotient is defined to be 
.

Find similar
View Dependencies ▼
Polynomial.modByMonic
In: Mathlib.Algebra.Polynomial.Div

Lean Code:
def modByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).2 else p
Show all
Docstring:
modByMonic, denoted as p %ₘ q, gives the remainder of p by a monic polynomial q.

Gemini 3.0 Flash:
Polynomial Remainder by a Monic Polynomial. For any two polynomials 
 and 
 over a ring 
, the remainder of 
 divided by 
, denoted 
, is defined as the second component of the division-with-remainder algorithm if 
 is monic; otherwise, it is defined to be 
.

Find similar
View Dependencies ▼
Polynomial.div_eq_quo_add_rem_div
In: Mathlib.RingTheory.IntegralDomain

Lean Code:
theorem div_eq_quo_add_rem_div (f : R[X]) {g : R[X]} (hg : g.Monic) :
    ∃ q r : R[X], r.degree < g.degree ∧
      (algebraMap R[X] K f) / (algebraMap R[X] K g) =
        algebraMap R[X] K q + (algebraMap R[X] K r) / (algebraMap R[X] K g) := by
  refine ⟨f /ₘ g, f %ₘ g, ?_, ?_⟩
...
Show all
Gemini 3.0 Flash:
Polynomial Division in the Field of Fractions. Given a polynomial 
 and a monic polynomial 
 over a commutative domain 
, there exist polynomials 
 and 
 in 
 such that the degree of 
 is strictly less than the degree of 
, and in the field of fractions 
 of 
, the identity 
 
 
 holds.

Find similar
View Dependencies ▼
CategoryTheory.ShortComplex.Splitting.f_r_assoc
In: Mathlib.Algebra.Homology.ShortComplex.Exact

Lean Code:
attribute [reassoc (attr := simp)] f_r s_g
Docstring:
the condition that r is a retraction of S.f

Gemini 3.0 Flash:
Associativity of the Retraction and Section in a Split Short Complex. In a splitting of a short complex 
, the composition of the first morphism 
 with its retraction 
 (and similarly the section 
 with the second morphism 
) satisfies the associative property when composed with further morphisms in the category.

Find similar
View Dependencies ▼
##### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.div_modByMonic_unique {f g} (q r : R[X]) (hg : Monic g) (h : r + g * q = f ∧ degree r < degree g) : f /ₘ g = q ∧ f %ₘ g = r := by
  nontriviality R
  have h₁ : r - f %ₘ g = -g * (q - f /ₘ g) :=
    eq_of_sub_eq_zero
      (by
        rw [← sub_eq_zero_of_eq (h.1.trans (modByMonic_add_div f hg).symm)]
        simp [mul_add, mul_comm, sub_eq_add_neg, add_comm, add_left_comm, add_assoc])
  have h₂ : degree (r - f %ₘ g) = degree (g * (q - f /ₘ g)) := by simp [h₁]
  have h₄ : degree (r - f %ₘ g) < degree g :=
    calc
      degree (r - f %ₘ g) ≤ max (degree r) (degree (f %ₘ g)) := degree_sub_le _ _
      _ < degree g := max_lt_iff.2 ⟨h.2, degree_modByMonic_lt _ hg⟩
  have h₅ : q - f /ₘ g = 0 :=
    _root_.by_contradiction fun hqf =>
      not_le_of_gt h₄ <|
        calc
          degree g ≤ degree g + degree (q - f /ₘ g) := by
            erw [degree_eq_natDegree hg.ne_zero, degree_eq_natDegree hqf, WithBot.coe_le_coe]
            exact Nat.le_add_right _ _
          _ = degree (r - f %ₘ g) := by rw [h₂, degree_mul']; simpa [Monic.def.1 hg]
  exact ⟨Eq.symm <| eq_of_sub_eq_zero h₅, Eq.symm <| eq_of_sub_eq_zero <| by simpa [h₅] using h₁⟩
Doc
Copy
👍
👎
Let 
R
R be a ring and let 
f
,
g
∈
R
[
X
]
f,g∈R[X] be polynomials with 
g
g monic. For any polynomials 
q
,
r
∈
R
[
X
]
q,r∈R[X], if 
r
+
g
⋅
q
=
f
r+g⋅q=f and 
deg
⁡
(
r
)
<
deg
⁡
(
g
)
deg(r)<deg(g), then the quotient 
f
/
m
g
f/ 
m
​
 g equals 
q
q and the remainder 
f
%
m
g
f% 
m
​
 g equals 
r
r.
Copy
2	
theorem Polynomial.div_eq_quo_add_rem_div (f : R[X]) {g : R[X]} (hg : g.Monic) :
  ∃ q r : R[X],
    r.degree < g.degree ∧
      (algebraMap R[X] K f) / (algebraMap R[X] K g) =
        algebraMap R[X] K q + (algebraMap R[X] K r) / (algebraMap R[X] K g) := by
  refine ⟨f /ₘ g, f %ₘ g, ?_, ?_⟩
  · exact degree_modByMonic_lt _ hg
  · have hg' : algebraMap R[X] K g ≠ 0 :=
      -- Porting note: the proof was `by exact_mod_cast Monic.ne_zero hg`
      (map_ne_zero_iff _ (IsFractionRing.injective R[X] K)).mpr (Monic.ne_zero hg)
    field_simp [hg']
    -- Porting note: `norm_cast` was here, but does nothing.
    rw [add_comm, mul_comm, ← map_mul, ← map_add, modByMonic_add_div f hg]
Doc
Copy
👍
👎
Let 
R
R be an integral domain and 
K
K its field of fractions. For any polynomial 
f
∈
R
[
X
]
f∈R[X] and monic polynomial 
g
∈
R
[
X
]
g∈R[X], there exist polynomials 
q
,
r
∈
R
[
X
]
q,r∈R[X] with 
deg
⁡
(
r
)
<
deg
⁡
(
g
)
deg(r)<deg(g) such that the rational function 
f
g
g
f
​
  in 
K
(
X
)
K(X) can be expressed as:
\[
\frac{f}{g} = q + \frac{r}{g}
\]
where 
q
q and 
r
r are the canonical quotient and remainder polynomials from polynomial division.
Copy
3	
definition Polynomial.divModByMonicAux : ∀ (_p : R[X]) {q : R[X]}, Monic q → R[X] × R[X] | p, q, hq =>
    letI := Classical.decEq R
    if h : degree q ≤ degree p ∧ p ≠ 0 then
      let z := C (leadingCoeff p) * X ^ (natDegree p - natDegree q)
      have _wf := div_wf_lemma h hq
      let dm := divModByMonicAux (p - q * z) hq
      ⟨z + dm.1, dm.2⟩
    else ⟨0, p⟩
  termination_by p => p
Doc
Copy
👍
👎
The auxiliary function for polynomial division by a monic polynomial. Given a polynomial 
p
p and a monic polynomial 
q
q, it returns a pair 
(
d
,
r
)
(d,r) where 
d
d is the quotient and 
r
r is the remainder when dividing 
p
p by 
q
q. The division process recursively subtracts multiples of 
q
q from 
p
p until the degree condition fails.
Copy
4	
definition Polynomial.divByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).1 else 0
Doc
Copy
👍
👎
Given polynomials 
p
p and 
q
q over a ring 
R
R, the function 
divByMonic
divByMonic computes the quotient of 
p
p divided by 
q
q when 
q
q is monic (i.e., has leading coefficient 1). If 
q
q is not monic, the function returns 0. The division is denoted by 
p
/
m
q
p/ 
m
​
 q.
Copy
5	
definition Polynomial.modByMonic (p q : R[X]) : R[X] :=
  letI := Classical.decEq R
  if hq : Monic q then (divModByMonicAux p hq).2 else p
Doc
Copy
👍
👎
The function modByMonic, denoted as p %ₘ q, gives the remainder when dividing the polynomial p by a monic polynomial q. If q is not monic, it returns p unchanged.
Copy
### MSC-180_14_003

Formal statement:
```lean
theorem root_multiplicity_factorization_nonzero {α : Type*} [Field α] {P : Polynomial α}
    {a : α} {k : ℕ} (hP : P ≠ 0) (h : multiplicity (Polynomial.X - Polynomial.C a) P = k) :
    ∃ g : Polynomial α,
      P = (Polynomial.X - Polynomial.C a) ^ k * g ∧ Polynomial.eval a g ≠ 0 := by
  sorry
```

Hallucination 1: `pow_dvd_iff_le_multiplicity`
Expected target theorem 1: `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`

Hallucination 2: `mul_divByMonic_eq_iff_isRoot.mpr`
Expected target theorem 2: `Polynomial.dvd_iff_isRoot`

#### Statement only
##### Query
```text
theorem root_multiplicity_factorization_nonzero {α : Type*} [Field α] {P : Polynomial α}
    {a : α} {k : ℕ} (hP : P ≠ 0) (h : multiplicity (Polynomial.X - Polynomial.C a) P = k) :
    ∃ g : Polynomial α,
      P = (Polynomial.X - Polynomial.C a) ^ k * g ∧ Polynomial.eval a g ≠ 0 := by
  sorry
```
##### LeanExplore
##### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd (p : R[X]) (hp : p ≠ 0) (a : R) : ∃ q : R[X], p = (X - C a) ^ p.rootMultiplicity a * q ∧ ¬(X - C a) ∣ q := by
  classical
  rw [rootMultiplicity_eq_multiplicity, if_neg hp]
  apply (finiteMultiplicity_X_sub_C a hp).exists_eq_pow_mul_and_not_dvd
Doc
Copy
👍
👎
For any nonzero polynomial 
p
p over a ring 
R
R and any element 
a
∈
R
a∈R, there exists a polynomial 
q
q such that 
p
=
(
X
−
a
)
rootMultiplicity
(
a
,
p
)
⋅
q
p=(X−a) 
rootMultiplicity(a,p)
 ⋅q and 
(
X
−
a
)
(X−a) does not divide 
q
q.
Copy
2	
theorem pow_rootMultiplicity_not_dvd {p : R[X]} (p0 : p ≠ 0) (a : R) :
    ¬(X - C a) ^ (rootMultiplicity a p + 1) ∣ p := by rw [← rootMultiplicity_le_iff p0]
Doc
Copy
👍
👎
For a nonzero polynomial 
p
p over a ring 
R
R and an element 
a
∈
R
a∈R, the polynomial 
(
X
−
a
)
n
+
1
(X−a) 
n+1
  does not divide 
p
p, where 
n
=
rootMultiplicity
(
a
,
p
)
n=rootMultiplicity(a,p) is the root multiplicity of 
a
a in 
p
p. This means 
p
p does not have 
n
+
1
n+1 factors of 
(
X
−
a
)
(X−a). 
Copy

#### Hallucination 1: `pow_dvd_iff_le_multiplicity`
##### Hallucination only
###### Query
```text
pow_dvd_iff_le_multiplicity
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem pow_multiplicity_dvd (a b : α) : a ^ (multiplicity a b) ∣ b :=
  pow_dvd_of_le_multiplicity le_rfl
Doc
Copy
👍
👎
For any elements 
a
a and 
b
b in a commutative monoid, the power 
a
multiplicity
(
a
,
b
)
a 
multiplicity(a,b)
  divides 
b
b.
Copy
2	
theorem pow_dvd_iff_le_multiplicity {a b : α} {k : ℕ} :
    a ^ k ∣ b ↔ (k : PartENat) ≤ multiplicity a b :=
  ⟨le_multiplicity_of_pow_dvd, pow_dvd_of_le_multiplicity⟩
Doc
Copy
👍
👎
For elements 
a
a and 
b
b in a monoid 
α
α, and a natural number 
k
k, the power 
a
k
a 
k
  divides 
b
b if and only if 
k
k is less than or equal to the multiplicity of 
a
a in 
b
b, denoted as 
multiplicity
(
a
,
b
)
multiplicity(a,b). Formally, 
a
k
∣
b
↔
k
≤
multiplicity
(
a
,
b
)
a 
k
 ∣b↔k≤multiplicity(a,b).
Copy
##### Hallucination + statement
###### Query
```text
pow_dvd_iff_le_multiplicity
theorem root_multiplicity_factorization_nonzero {α : Type*} [Field α] {P : Polynomial α}
    {a : α} {k : ℕ} (hP : P ≠ 0) (h : multiplicity (Polynomial.X - Polynomial.C a) P = k) :
    ∃ g : Polynomial α,
      P = (Polynomial.X - Polynomial.C a) ^ k * g ∧ Polynomial.eval a g ≠ 0 := by
  sorry
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd (p : R[X]) (hp : p ≠ 0) (a : R) : ∃ q : R[X], p = (X - C a) ^ p.rootMultiplicity a * q ∧ ¬(X - C a) ∣ q := by
  classical
  rw [rootMultiplicity_eq_multiplicity, if_neg hp]
  apply (finiteMultiplicity_X_sub_C a hp).exists_eq_pow_mul_and_not_dvd
Doc
Copy
👍
👎
For any nonzero polynomial 
p
p over a ring 
R
R and any element 
a
∈
R
a∈R, there exists a polynomial 
q
q such that 
p
=
(
X
−
a
)
rootMultiplicity
(
a
,
p
)
⋅
q
p=(X−a) 
rootMultiplicity(a,p)
 ⋅q and 
(
X
−
a
)
(X−a) does not divide 
q
q.
Copy
2	
theorem le_rootMultiplicity_iff {p : R[X]} (p0 : p ≠ 0) {a : R} {n : ℕ} :
    n ≤ rootMultiplicity a p ↔ (X - C a) ^ n ∣ p := by
  classical
  rw [rootMultiplicity_eq_nat_find_of_nonzero p0, @Nat.le_find_iff _ (_)]
  simp_rw [Classical.not_not]
  refine ⟨fun h => ?_, fun h m hm => (pow_dvd_pow _ hm).trans h⟩
  cases' n with n
  · rw [pow_zero]
    apply one_dvd
  · exact h n n.lt_succ_self
Doc
Copy
👍
👎
For a nonzero polynomial 
p
p over a ring 
R
R, an element 
a
∈
R
a∈R, and a natural number 
n
n, the following are equivalent:
1. 
n
n is less than or equal to the root multiplicity of 
a
a in 
p
p.
2. The polynomial 
(
X
−
a
)
n
(X−a) 
n
  divides 
p
p. This means that 
p
p has at least 
n
n factors of 
(
X
−
a
)
(X−a). 
Copy
#### Hallucination 2: `mul_divByMonic_eq_iff_isRoot.mpr`
##### Hallucination only
###### Query
```text
mul_divByMonic_eq_iff_isRoot.mpr
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.mul_divByMonic_eq_iff_isRoot : (X - C a) * (p /ₘ (X - C a)) = p ↔ IsRoot p a :=
  .trans
    ⟨fun h => by rw [← h, eval_mul, eval_sub, eval_X, eval_C, sub_self, zero_mul],
    fun h => by
      conv_rhs =>
        rw [← modByMonic_add_div p (monic_X_sub_C a)]
        rw [modByMonic_X_sub_C_eq_C_eval, h, C_0, zero_add]⟩
    IsRoot.def.symm
Doc
Copy
👍
👎
For any polynomial 
p
p over a ring 
R
R and any element 
a
∈
R
a∈R, the product of the monic polynomial 
(
X
−
a
)
(X−a) and the quotient 
(
p
/
m
(
X
−
a
)
)
(p/ 
m
​
 (X−a)) equals 
p
p if and only if 
a
a is a root of 
p
p (i.e., 
p
(
a
)
=
0
p(a)=0). In other words,
(
X
−
a
)
⋅
(
p
/
m
(
X
−
a
)
)
=
p
⇔
p
(
a
)
=
0.
(X−a)⋅(p/ 
m
​
 (X−a))=p⇔p(a)=0.
Copy
2	
theorem Polynomial.mul_div_eq_iff_isRoot : (X - C a) * (p / (X - C a)) = p ↔ IsRoot p a :=
  divByMonic_eq_div p (monic_X_sub_C a) ▸ mul_divByMonic_eq_iff_isRoot
Doc
Copy
👍
👎
For any polynomial 
p
∈
R
[
X
]
p∈R[X] and any element 
a
∈
R
a∈R, the product of the linear polynomial 
(
X
−
a
)
(X−a) and the quotient polynomial 
(
p
/
(
X
−
a
)
)
(p/(X−a)) equals 
p
p if and only if 
a
a is a root of 
p
p (i.e., 
p
(
a
)
=
0
p(a)=0). In other words:
(
X
−
a
)
⋅
(
p
X
−
a
)
=
p
⇔
p
(
a
)
=
0.
(X−a)⋅( 
X−a
p
​
 )=p⇔p(a)=0.
Copy
##### Hallucination + statement
###### Query
```text
mul_divByMonic_eq_iff_isRoot.mpr
theorem root_multiplicity_factorization_nonzero {α : Type*} [Field α] {P : Polynomial α}
    {a : α} {k : ℕ} (hP : P ≠ 0) (h : multiplicity (Polynomial.X - Polynomial.C a) P = k) :
    ∃ g : Polynomial α,
      P = (Polynomial.X - Polynomial.C a) ^ k * g ∧ Polynomial.eval a g ≠ 0 := by
  sorry
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd (p : R[X]) (hp : p ≠ 0) (a : R) : ∃ q : R[X], p = (X - C a) ^ p.rootMultiplicity a * q ∧ ¬(X - C a) ∣ q := by
  classical
  rw [rootMultiplicity_eq_multiplicity, if_neg hp]
  apply (finiteMultiplicity_X_sub_C a hp).exists_eq_pow_mul_and_not_dvd
Doc
Copy
👍
👎
For any nonzero polynomial 
p
p over a ring 
R
R and any element 
a
∈
R
a∈R, there exists a polynomial 
q
q such that 
p
=
(
X
−
a
)
rootMultiplicity
(
a
,
p
)
⋅
q
p=(X−a) 
rootMultiplicity(a,p)
 ⋅q and 
(
X
−
a
)
(X−a) does not divide 
q
q.
Copy
2	
theorem Polynomial.pow_mul_divByMonic_rootMultiplicity_eq (p : R[X]) (a : R) : (X - C a) ^ rootMultiplicity a p * (p /ₘ (X - C a) ^ rootMultiplicity a p) = p := by
  have : Monic ((X - C a) ^ rootMultiplicity a p) := (monic_X_sub_C _).pow _
  conv_rhs =>
      rw [← modByMonic_add_div p this,
        (modByMonic_eq_zero_iff_dvd this).2 (pow_rootMultiplicity_dvd _ _)]
  simp
Doc
Copy
👍
👎
For any polynomial 
p
p over a ring 
R
R and any element 
a
∈
R
a∈R, the product of 
(
X
−
a
)
rootMultiplicity
(
a
,
p
)
(X−a) 
rootMultiplicity(a,p)
  and the quotient 
p
/
m
(
X
−
a
)
rootMultiplicity
(
a
,
p
)
p/ 
m
​
 (X−a) 
rootMultiplicity(a,p)
  equals 
p
p. That is,
(
X
−
a
)
n
⋅
(
p
/
m
(
X
−
a
)
n
)
=
p
(X−a) 
n
 ⋅(p/ 
m
​
 (X−a) 
n
 )=p

where 
n
=
rootMultiplicity
(
a
,
p
)
n=rootMultiplicity(a,p) is the largest natural number such that 
(
X
−
a
)
n
(X−a) 
n
  divides 
p
p.
Copy
#### Statement + both hallucinations
##### Query
```text
pow_dvd_iff_le_multiplicity
mul_divByMonic_eq_iff_isRoot.mpr
theorem root_multiplicity_factorization_nonzero {α : Type*} [Field α] {P : Polynomial α}
    {a : α} {k : ℕ} (hP : P ≠ 0) (h : multiplicity (Polynomial.X - Polynomial.C a) P = k) :
    ∃ g : Polynomial α,
      P = (Polynomial.X - Polynomial.C a) ^ k * g ∧ Polynomial.eval a g ≠ 0 := by
  sorry
```
##### LeanExplore
##### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd (p : R[X]) (hp : p ≠ 0) (a : R) : ∃ q : R[X], p = (X - C a) ^ p.rootMultiplicity a * q ∧ ¬(X - C a) ∣ q := by
  classical
  rw [rootMultiplicity_eq_multiplicity, if_neg hp]
  apply (finiteMultiplicity_X_sub_C a hp).exists_eq_pow_mul_and_not_dvd
Doc
Copy
👍
👎
For any nonzero polynomial 
p
p over a ring 
R
R and any element 
a
∈
R
a∈R, there exists a polynomial 
q
q such that 
p
=
(
X
−
a
)
rootMultiplicity
(
a
,
p
)
⋅
q
p=(X−a) 
rootMultiplicity(a,p)
 ⋅q and 
(
X
−
a
)
(X−a) does not divide 
q
q.
Copy
2	
theorem Polynomial.pow_mul_divByMonic_rootMultiplicity_eq (p : R[X]) (a : R) : (X - C a) ^ rootMultiplicity a p * (p /ₘ (X - C a) ^ rootMultiplicity a p) = p := by
  have : Monic ((X - C a) ^ rootMultiplicity a p) := (monic_X_sub_C _).pow _
  conv_rhs =>
      rw [← modByMonic_add_div p this,
        (modByMonic_eq_zero_iff_dvd this).2 (pow_rootMultiplicity_dvd _ _)]
  simp
Doc
Copy
👍
👎
For any polynomial 
p
p over a ring 
R
R and any element 
a
∈
R
a∈R, the product of 
(
X
−
a
)
rootMultiplicity
(
a
,
p
)
(X−a) 
rootMultiplicity(a,p)
  and the quotient 
p
/
m
(
X
−
a
)
rootMultiplicity
(
a
,
p
)
p/ 
m
​
 (X−a) 
rootMultiplicity(a,p)
  equals 
p
p. That is,
(
X
−
a
)
n
⋅
(
p
/
m
(
X
−
a
)
n
)
=
p
(X−a) 
n
 ⋅(p/ 
m
​
 (X−a) 
n
 )=p

where 
n
=
rootMultiplicity
(
a
,
p
)
n=rootMultiplicity(a,p) is the largest natural number such that 
(
X
−
a
)
n
(X−a) 
n
  divides 
p
p.
Copy
### MSC-180_52_002

Formal statement:
```lean
theorem diameter_achieved_by_hull_vertices {n : ℕ} {S : Set (EuclideanSpace ℝ (Fin n))}
    (h_finite : Set.Finite S) (h_nonempty : S.Nonempty) :
    ∃ x ∈ (convexHull ℝ S).extremePoints ℝ, ∃ y ∈ (convexHull ℝ S).extremePoints ℝ,
      dist x y = Metric.diam S := by
  sorry
```

Hallucination 1: `extremePoints_convexHull_of_mem`
Expected target theorem 1: `extremePoints_convexHull_subset`

Hallucination 2: `Metric.diam_convexHull`
Expected target theorem 2: `convexHull_exists_dist_ge2`

#### Statement only
##### Query
```text
theorem diameter_achieved_by_hull_vertices {n : ℕ} {S : Set (EuclideanSpace ℝ (Fin n))}
    (h_finite : Set.Finite S) (h_nonempty : S.Nonempty) :
    ∃ x ∈ (convexHull ℝ S).extremePoints ℝ, ∃ y ∈ (convexHull ℝ S).extremePoints ℝ,
      dist x y = Metric.diam S := by
  sorry
```
##### LeanExplore
##### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let 
E
E be a real normed space and 
s
⊆
E
s⊆E be a subset. The metric diameter of the convex hull of 
s
s is equal to the metric diameter of 
s
s, i.e.,
diam
(
convexHull
R
(
s
)
)
=
diam
(
s
)
.
diam(convexHull 
R
​
 (s))=diam(s).
Copy
2	
/-- Diameter of the convex hull of a set `s` equals the emetric diameter of `s`. -/
@[simp]
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let 
E
E be a real normed space and 
s
⊆
E
s⊆E be a subset. The metric diameter of the convex hull of 
s
s is equal to the metric diameter of 
s
s, i.e., 
diam
(
convexHull
R
(
s
)
)
=
diam
(
s
)
.
diam(convexHull 
R
​
 (s))=diam(s).
Copy
#### Hallucination 1: `extremePoints_convexHull_of_mem`
##### Hallucination only
###### Query
```text
extremePoints_convexHull_of_mem
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem extremePoints_convexHull_subset : (convexHull 𝕜 A).extremePoints 𝕜 ⊆ A := by
  rintro x hx
  rw [(convex_convexHull 𝕜 _).mem_extremePoints_iff_convex_diff] at hx
  by_contra h
  exact (convexHull_min (subset_diff.2 ⟨subset_convexHull 𝕜 _, disjoint_singleton_right.2 h⟩) hx.2
    hx.1).2 rfl
Doc
Copy
👍
👎
The set of extreme points of the convex hull of a set 
A
A in a vector space over a field 
K
K is a subset of 
A
A. In other words, every extreme point of 
convexHull
K
(
A
)
convexHull 
K
​
 (A) belongs to 
A
A.
Copy
2	
theorem subset_convexHull : s ⊆ convexHull 𝕜 s :=
  (convexHull 𝕜).le_closure s
Doc
Copy
👍
👎
For any set 
s
s in a 
K
K-module 
E
E, the set 
s
s is contained in its convex hull, i.e., 
s
⊆
convexHull
K
(
s
)
s⊆convexHull 
K
​
 (s).
Copy
##### Hallucination + statement
###### Query
```text
extremePoints_convexHull_of_mem
theorem diameter_achieved_by_hull_vertices {n : ℕ} {S : Set (EuclideanSpace ℝ (Fin n))}
    (h_finite : Set.Finite S) (h_nonempty : S.Nonempty) :
    ∃ x ∈ (convexHull ℝ S).extremePoints ℝ, ∃ y ∈ (convexHull ℝ S).extremePoints ℝ,
      dist x y = Metric.diam S := by
  sorry
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let $E$ be a real normed space and $s \subseteq E$ be a subset. The metric diameter of the convex hull of $s$ is equal to the metric diameter of $s$, i.e.,
$$\text{diam}(\text{convexHull}_{\mathbb{R}}(s)) = \text{diam}(s).$$
Copy
2	
/-- Diameter of the convex hull of a set `s` equals the emetric diameter of `s`. -/
@[simp]
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let $E$ be a real normed space and $s \subseteq E$ be a subset. The metric diameter of the convex hull of $s$ is equal to the metric diameter of $s$, i.e., $$\text{diam}(\text{convexHull}_{\mathbb{R}}(s)) = \text{diam}(s).$$
Copy
#### Hallucination 2: `Metric.diam_convexHull`
##### Hallucination only
###### Query
```text
Metric.diam_convexHull
```
###### LeanExplore
###### LeanFinder

Rank	Formal statement	Informal statement
1	
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let 
E
E be a real normed space and 
s
⊆
E
s⊆E be a subset. The metric diameter of the convex hull of 
s
s is equal to the metric diameter of 
s
s, i.e.,
diam
(
convexHull
R
(
s
)
)
=
diam
(
s
)
.
diam(convexHull 
R
​
 (s))=diam(s).
Copy
2	
/-- Diameter of the convex hull of a set `s` equals the emetric diameter of `s`. -/
@[simp]
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let 
E
E be a real normed space and 
s
⊆
E
s⊆E be a subset. The metric diameter of the convex hull of 
s
s is equal to the metric diameter of 
s
s, i.e., 
diam
(
convexHull
R
(
s
)
)
=
diam
(
s
)
.
diam(convexHull 
R
​
 (s))=diam(s).
Copy
##### Hallucination + statement
###### Query
```text
Metric.diam_convexHull
theorem diameter_achieved_by_hull_vertices {n : ℕ} {S : Set (EuclideanSpace ℝ (Fin n))}
    (h_finite : Set.Finite S) (h_nonempty : S.Nonempty) :
    ∃ x ∈ (convexHull ℝ S).extremePoints ℝ, ∃ y ∈ (convexHull ℝ S).extremePoints ℝ,
      dist x y = Metric.diam S := by
  sorry
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let $E$ be a real normed space and $s \subseteq E$ be a subset. The metric diameter of the convex hull of $s$ is equal to the metric diameter of $s$, i.e.,
$$\text{diam}(\text{convexHull}_{\mathbb{R}}(s)) = \text{diam}(s).$$
Copy
2	
/-- Diameter of the convex hull of a set `s` equals the emetric diameter of `s`. -/
@[simp]
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let $E$ be a real normed space and $s \subseteq E$ be a subset. The metric diameter of the convex hull of $s$ is equal to the metric diameter of $s$, i.e., $$\text{diam}(\text{convexHull}_{\mathbb{R}}(s)) = \text{diam}(s).$$
Copy
#### Statement + both hallucinations
##### Query
```text
extremePoints_convexHull_of_mem
Metric.diam_convexHull
theorem diameter_achieved_by_hull_vertices {n : ℕ} {S : Set (EuclideanSpace ℝ (Fin n))}
    (h_finite : Set.Finite S) (h_nonempty : S.Nonempty) :
    ∃ x ∈ (convexHull ℝ S).extremePoints ℝ, ∃ y ∈ (convexHull ℝ S).extremePoints ℝ,
      dist x y = Metric.diam S := by
  sorry
```
##### LeanExplore
##### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let 
E
E be a real normed space and 
s
⊆
E
s⊆E be a subset. The metric diameter of the convex hull of 
s
s is equal to the metric diameter of 
s
s, i.e.,
diam
(
convexHull
R
(
s
)
)
=
diam
(
s
)
.
diam(convexHull 
R
​
 (s))=diam(s).
Copy
2	
/-- Diameter of the convex hull of a set `s` equals the emetric diameter of `s`. -/
@[simp]
theorem convexHull_diam (s : Set E) : Metric.diam (convexHull ℝ s) = Metric.diam s := by
  simp only [Metric.diam, convexHull_ediam]
Doc
Copy
👍
👎
Let 
E
E be a real normed space and 
s
⊆
E
s⊆E be a subset. The metric diameter of the convex hull of 
s
s is equal to the metric diameter of 
s
s, i.e., 
diam
(
convexHull
R
(
s
)
)
=
diam
(
s
)
.
diam(convexHull 
R
​
 (s))=diam(s).
Copy
### MSC-180_65_003

Formal statement:
```lean
theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
  sorry
```

Hallucination 1: `Metric.lipschitzOnWith_iff_metric.mpr`
Expected target theorem 1: `Convex.lipschitzOnWith_of_nnnorm_deriv_le`

Hallucination 2: `ExistsDerivWithinAt_Icc`
Expected target theorem 2: `convex_Icc` (provisional)

#### Statement only
##### Query
```text
theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
  sorry
```
##### LeanExplore
##### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem norm_image_sub_le_of_norm_deriv_le_segment {C : ℝ} (hf : DifferentiableOn ℝ f (Icc a b)) (bound : ∀ x ∈ Ico a b, ‖derivWithin f (Icc a b) x‖ ≤ C) :
  ∀ x ∈ Icc a b, ‖f x - f a‖ ≤ C * (x - a) := by
  refine norm_image_sub_le_of_norm_deriv_le_segment' ?_ bound
  exact fun x hx => (hf x hx).hasDerivWithinAt
Doc
Copy
👍
👎
Let 
f
 ⁣
:
[
a
,
b
]
→
E
f:[a,b]→E be a differentiable function on the closed interval 
[
a
,
b
]
[a,b] with values in a normed additive commutative group 
E
E. If there exists a constant 
C
≥
0
C≥0 such that the norm of the derivative of 
f
f within 
[
a
,
b
]
[a,b] satisfies 
∥
d
e
r
i
v
W
i
t
h
i
n
 
f
 
[
a
,
b
]
 
x
∥
≤
C
∥derivWithinf[a,b]x∥≤C for all 
x
∈
[
a
,
b
)
x∈[a,b), then for every 
x
∈
[
a
,
b
]
x∈[a,b], the inequality 
∥
f
(
x
)
−
f
(
a
)
∥
≤
C
(
x
−
a
)
∥f(x)−f(a)∥≤C(x−a) holds.
Copy
2	
theorem Convex.lipschitzOnWith_of_nnnorm_deriv_le {C : ℝ≥0} (hf : ∀ x ∈ s, DifferentiableAt 𝕜 f x) (bound : ∀ x ∈ s, ‖deriv f x‖₊ ≤ C) (hs : Convex ℝ s) :
  LipschitzOnWith C f s :=
  hs.lipschitzOnWith_of_nnnorm_hasDerivWithin_le
    (fun x hx => (hf x hx).hasDerivAt.hasDerivWithinAt) bound
Doc
Copy
👍
👎
Let 
s
s be a convex subset of 
R
R and 
f
:
R
→
E
f:R→E a function differentiable at every point 
x
∈
s
x∈s. If there exists a nonnegative real constant 
C
C such that 
∥
deriv
 
f
 
x
∥
≤
C
∥derivfx∥≤C for all 
x
∈
s
x∈s, then 
f
f is Lipschitz continuous on 
s
s with Lipschitz constant 
C
C. That is, for all 
x
,
y
∈
s
x,y∈s,
\[ \|f(y) - f(x)\| \leq C \cdot |y - x|. \]
Copy
#### Hallucination 1: `Metric.lipschitzOnWith_iff_metric.mpr`
##### Hallucination only
###### Query
```text
Metric.lipschitzOnWith_iff_metric.mpr
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem lipschitzOnWith_iff_dist_le_mul [PseudoMetricSpace α] [PseudoMetricSpace β] {K : ℝ≥0} {s : Set α} {f : α → β} :
  LipschitzOnWith K f s ↔ ∀ x ∈ s, ∀ y ∈ s, dist (f x) (f y) ≤ K * dist x y := by
  simp only [LipschitzOnWith, edist_nndist, dist_nndist]
  norm_cast
Doc
Copy
👍
👎
Let 
α
α and 
β
β be pseudo-metric spaces, 
K
≥
0
K≥0 a real number, 
s
⊆
α
s⊆α a subset, and 
f
:
α
→
β
f:α→β a function. Then 
f
f is Lipschitz continuous on 
s
s with constant 
K
K if and only if for all 
x
,
y
∈
s
x,y∈s, the distance inequality 
dist
(
f
x
,
f
y
)
≤
K
⋅
dist
(
x
,
y
)
dist(fx,fy)≤K⋅dist(x,y) holds.
Copy
2	
theorem LipschitzWith.lipschitzOnWith (h : LipschitzWith K f) : LipschitzOnWith K f s :=
  fun x _ y _ => h x y
Doc
Copy
👍
👎
If a function 
f
 ⁣
:
α
→
β
f:α→β between extended pseudo-metric spaces is Lipschitz continuous with constant 
K
≥
0
K≥0 on the entire space 
α
α, then it is Lipschitz continuous with the same constant 
K
K on any subset 
s
⊆
α
s⊆α.
Copy
##### Hallucination + statement
###### Query
```text
Metric.lipschitzOnWith_iff_metric.mpr
theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
  sorry
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Convex.lipschitzOnWith_of_nnnorm_deriv_le {C : ℝ≥0} (hf : ∀ x ∈ s, DifferentiableAt 𝕜 f x) (bound : ∀ x ∈ s, ‖deriv f x‖₊ ≤ C) (hs : Convex ℝ s) :
  LipschitzOnWith C f s :=
  hs.lipschitzOnWith_of_nnnorm_hasDerivWithin_le
    (fun x hx => (hf x hx).hasDerivAt.hasDerivWithinAt) bound
Doc
Copy
👍
👎
Let 
s
s be a convex subset of 
R
R and 
f
:
R
→
E
f:R→E a function differentiable at every point 
x
∈
s
x∈s. If there exists a nonnegative real constant 
C
C such that 
∥
deriv
 
f
 
x
∥
≤
C
∥derivfx∥≤C for all 
x
∈
s
x∈s, then 
f
f is Lipschitz continuous on 
s
s with Lipschitz constant 
C
C. That is, for all 
x
,
y
∈
s
x,y∈s,
\[ \|f(y) - f(x)\| \leq C \cdot |y - x|. \]
Copy
2	
theorem norm_image_sub_le_of_norm_deriv_le_segment {C : ℝ} (hf : DifferentiableOn ℝ f (Icc a b)) (bound : ∀ x ∈ Ico a b, ‖derivWithin f (Icc a b) x‖ ≤ C) :
  ∀ x ∈ Icc a b, ‖f x - f a‖ ≤ C * (x - a) := by
  refine norm_image_sub_le_of_norm_deriv_le_segment' ?_ bound
  exact fun x hx => (hf x hx).hasDerivWithinAt
Doc
Copy
👍
👎
Let 
f
 ⁣
:
[
a
,
b
]
→
E
f:[a,b]→E be a differentiable function on the closed interval 
[
a
,
b
]
[a,b] with values in a normed additive commutative group 
E
E. If there exists a constant 
C
≥
0
C≥0 such that the norm of the derivative of 
f
f within 
[
a
,
b
]
[a,b] satisfies 
∥
d
e
r
i
v
W
i
t
h
i
n
 
f
 
[
a
,
b
]
 
x
∥
≤
C
∥derivWithinf[a,b]x∥≤C for all 
x
∈
[
a
,
b
)
x∈[a,b), then for every 
x
∈
[
a
,
b
]
x∈[a,b], the inequality 
∥
f
(
x
)
−
f
(
a
)
∥
≤
C
(
x
−
a
)
∥f(x)−f(a)∥≤C(x−a) holds.
Copy
#### Hallucination 2: `ExistsDerivWithinAt_Icc`
##### Hallucination only
###### Query
```text
ExistsDerivWithinAt_Icc
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem HasDerivAt.hasDerivWithinAt (h : HasDerivAt f f' x) : HasDerivWithinAt f f' s x :=
  HasFDerivAt.hasFDerivWithinAt h
Doc
Copy
👍
👎
If a function \( f : \mathbb{K} \to F \) has derivative \( f' \in F \) at a point \( x \in \mathbb{K} \), then \( f \) also has derivative \( f' \) at \( x \) within any subset \( s \subseteq \mathbb{K} \). Here \(\mathbb{K}\) is a normed field and \(F\) is a normed space over \(\mathbb{K}\).
Copy
2	
definition HasDerivWithinAt (f : 𝕜 → F) (f' : F) (s : Set 𝕜) (x : 𝕜) :=
  HasDerivAtFilter f f' x (𝓝[s] x)
Doc
Copy
👍
👎
A function \( f : \mathbb{K} \to F \) has derivative \( f' \in F \) at point \( x \in \mathbb{K} \) within subset \( s \subseteq \mathbb{K} \) if
\[ f(x') = f(x) + (x' - x) \cdot f' + o(x' - x) \]
as \( x' \) tends to \( x \) within \( s \). Here \( \mathbb{K} \) is a normed field and \( F \) is a normed space over \( \mathbb{K} \).
Copy
##### Hallucination + statement
###### Query
```text
ExistsDerivWithinAt_Icc
theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
  sorry
```
###### LeanExplore
###### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Convex.lipschitzOnWith_of_nnnorm_deriv_le {C : ℝ≥0} (hf : ∀ x ∈ s, DifferentiableAt 𝕜 f x) (bound : ∀ x ∈ s, ‖deriv f x‖₊ ≤ C) (hs : Convex ℝ s) :
  LipschitzOnWith C f s :=
  hs.lipschitzOnWith_of_nnnorm_hasDerivWithin_le
    (fun x hx => (hf x hx).hasDerivAt.hasDerivWithinAt) bound
Doc
Copy
👍
👎
Let 
s
s be a convex subset of 
R
R and 
f
:
R
→
E
f:R→E a function differentiable at every point 
x
∈
s
x∈s. If there exists a nonnegative real constant 
C
C such that 
∥
deriv
 
f
 
x
∥
≤
C
∥derivfx∥≤C for all 
x
∈
s
x∈s, then 
f
f is Lipschitz continuous on 
s
s with Lipschitz constant 
C
C. That is, for all 
x
,
y
∈
s
x,y∈s,
\[ \|f(y) - f(x)\| \leq C \cdot |y - x|. \]
Copy
2	
theorem norm_image_sub_le_of_norm_deriv_le_segment {C : ℝ} (hf : DifferentiableOn ℝ f (Icc a b)) (bound : ∀ x ∈ Ico a b, ‖derivWithin f (Icc a b) x‖ ≤ C) :
  ∀ x ∈ Icc a b, ‖f x - f a‖ ≤ C * (x - a) := by
  refine norm_image_sub_le_of_norm_deriv_le_segment' ?_ bound
  exact fun x hx => (hf x hx).hasDerivWithinAt
Doc
Copy
👍
👎
Let 
f
 ⁣
:
[
a
,
b
]
→
E
f:[a,b]→E be a differentiable function on the closed interval 
[
a
,
b
]
[a,b] with values in a normed additive commutative group 
E
E. If there exists a constant 
C
≥
0
C≥0 such that the norm of the derivative of 
f
f within 
[
a
,
b
]
[a,b] satisfies 
∥
d
e
r
i
v
W
i
t
h
i
n
 
f
 
[
a
,
b
]
 
x
∥
≤
C
∥derivWithinf[a,b]x∥≤C for all 
x
∈
[
a
,
b
)
x∈[a,b), then for every 
x
∈
[
a
,
b
]
x∈[a,b], the inequality 
∥
f
(
x
)
−
f
(
a
)
∥
≤
C
(
x
−
a
)
∥f(x)−f(a)∥≤C(x−a) holds.
Copy
#### Statement + both hallucinations
##### Query
```text
Metric.lipschitzOnWith_iff_metric.mpr
ExistsDerivWithinAt_Icc
theorem lipschitz_from_bounded_deriv {f : ℝ → ℝ} {a b : ℝ} {L : ℝ≥0} (hab : a ≤ b)
    (hderiv : ∀ x ∈ Icc a b, DifferentiableAt ℝ f x)
    (hbounded : ∀ x ∈ Icc a b, ‖deriv f x‖ ≤ L) :
    LipschitzOnWith L f (Icc a b) := by
  sorry
```
##### LeanExplore
##### LeanFinder
Rank	Formal statement	Informal statement
1	
theorem Convex.lipschitzOnWith_of_nnnorm_deriv_le {C : ℝ≥0} (hf : ∀ x ∈ s, DifferentiableAt 𝕜 f x) (bound : ∀ x ∈ s, ‖deriv f x‖₊ ≤ C) (hs : Convex ℝ s) :
  LipschitzOnWith C f s :=
  hs.lipschitzOnWith_of_nnnorm_hasDerivWithin_le
    (fun x hx => (hf x hx).hasDerivAt.hasDerivWithinAt) bound
Doc
Copy
👍
👎
Let $s$ be a convex subset of $\mathbb{R}$ and $f : \mathbb{R} \to E$ a function differentiable at every point $x \in s$. If there exists a nonnegative real constant $C$ such that $\|\text{deriv}\,f\,x\| \leq C$ for all $x \in s$, then $f$ is Lipschitz continuous on $s$ with Lipschitz constant $C$. That is, for all $x, y \in s$,
\[ \|f(y) - f(x)\| \leq C \cdot |y - x|. \]
Copy
2	
theorem Convex.lipschitzOnWith_of_nnnorm_derivWithin_le {C : ℝ≥0} (hs : Convex ℝ s) (hf : DifferentiableOn 𝕜 f s) (bound : ∀ x ∈ s, ‖derivWithin f s x‖₊ ≤ C) :
  LipschitzOnWith C f s :=
  hs.lipschitzOnWith_of_nnnorm_hasDerivWithin_le (fun x hx => (hf x hx).hasDerivWithinAt) bound
Doc
Copy
👍
👎
Let $s$ be a convex subset of $\mathbb{R}$, and let $f : \mathbb{R} \to E$ be a differentiable function on $s$. If there exists a nonnegative real constant $C$ such that $\|\text{derivWithin}\,f\,s\,x\| \leq C$ for all $x \in s$, then $f$ is Lipschitz continuous on $s$ with Lipschitz constant $C$. That is, for all $x, y \in s$,
\[ \|f(y) - f(x)\| \leq C \cdot |y - x|. \]
Copy