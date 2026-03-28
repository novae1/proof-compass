# LeanFinder Check: Statement + Full Failed Proof

Date: 2026-03-28

## Goal

Test one new LeanFinder query format that we had not yet checked manually:

- full failed proof, including the formal theorem statement

This was tested on the same four structured MSC-180 problems used in the earlier manual retrieval work.

## Setup

- Source run:
  - `rag_experiments/outputs/msc180/v2/20260301_msc180-v2_deepseekv2_7b_lean4-15_verified.json`
- Query engine:
  - public `LeanFinder`
- Retrieval depth:
  - top `5`
- Query text:
  - one representative failed `parsed_proof` per problem from the no-hint condition
- Representative attempt selection:
  - failed no-hint attempt with the strongest overlap with the previously selected hallucination targets for that problem

## Results

### `MSC-180_12_001`

- selected attempt: `0`
- query length: `646` chars
- target hallucination family:
  - `divModByMonic_eq_div_mod`
  - `modByMonic_lt_of_lt`

Top 5:
1. `Polynomial.div_modByMonic_unique`
2. `Polynomial.div_eq_quo_add_rem_div`
3. `Polynomial.natDegree_mod_lt`
4. `Polynomial.modByMonic_eq_sub_mul_div`
5. `Polynomial.divModByMonicAux`

Assessment:
- strong result
- the query recovers the same main polynomial-division family already seen in the better statement-based queries
- the full failed proof does not look better than statement-only here, but it remains highly usable

### `MSC-180_14_003`

- selected attempt: `6`
- query length: `1008` chars
- target hallucination family:
  - `pow_dvd_iff_le_multiplicity`
  - `mul_divByMonic_eq_iff_isRoot.mpr`

Top 5:
1. `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
2. `Polynomial.pow_mul_divByMonic_rootMultiplicity_eq`
3. `Polynomial.eval_divByMonic_pow_rootMultiplicity_ne_zero`
4. `le_rootMultiplicity_iff`
5. `Polynomial.le_rootMultiplicity_iff`

Assessment:
- strongest result in this check
- top 1 is exactly the main target theorem family
- top 2 and top 3 are also highly relevant local factorization lemmas
- full failed proof works very well on this problem

### `MSC-180_52_002`

- selected attempt: `2`
- query length: `977` chars
- target hallucination family:
  - `extremePoints_convexHull_of_mem`
  - `Metric.diam_convexHull`

Top 5:
1. `convexHull_exists_dist_ge2`
2. `convexHull_exists_dist_ge`
3. `convexHull_exists_dist_ge2`
4. `convexHull_diam`
5. `convexHull_ediam`

Assessment:
- mixed result
- the retrieval is still in the right geometric family
- but it collapses heavily toward convex-hull distance/diameter facts and does not recover the extreme-points theorem family well
- this matches the earlier pattern that this problem is the weakest of the four

### `MSC-180_65_003`

- selected attempt: `5`
- query length: `1058` chars
- target hallucination family:
  - `Metric.lipschitzOnWith_iff_metric.mpr`
  - `ExistsDerivWithinAt_Icc`

Top 5:
1. `Convex.lipschitzOnWith_of_nnnorm_deriv_le`
2. `norm_image_sub_le_of_norm_deriv_le_segment`
3. `Convex.lipschitzOnWith_of_nnnorm_hasDerivWithin_le`
4. `Convex.lipschitzOnWith_of_nnnorm_derivWithin_le`
5. `norm_image_sub_le_of_norm_deriv_le_segment'`

Assessment:
- strong result
- top 1 is the main expected theorem family
- top 2 through top 5 are all useful nearby derivative/Lipschitz lemmas
- full failed proof works well here

## Aggregate Conclusion

The full-failed-proof query is viable.

Across the four problems:

- strong: `MSC-180_12_001`
- very strong: `MSC-180_14_003`
- mixed: `MSC-180_52_002`
- strong: `MSC-180_65_003`

So the new query format works on `3/4` of the current structured cases.

## Comparison To Earlier Query Formats

The full failed proof does **not** clearly dominate the cleaner query formats we already tested.

What it seems to do:

- preserve the main theorem family on the strong cases
- sometimes add useful local lemmas around the main target
- still struggle on the same weak geometric case

What it does **not** show:

- a clear win over `statement only`
- a clear win over `statement + hallucination`

So the best current interpretation is:

- full failed proof is a useful backup query format
- but it should not replace the cleaner statement-based retrieval path yet

## Practical Implication

For the first iterative-RAG prototype, the primary retrieval path should still be:

- statement-only retrieval for the global anchor
- hallucination-conditioned retrieval for local additions

The full failed proof is now a plausible comparison or fallback query, not the default.
