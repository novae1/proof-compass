# LeanFinder Top-2 Analysis For Multi-Hallucination MSC-180 Cases

## Purpose
This note summarizes the manual retrieval study recorded in:
- `rag_experiments/reports/iterative_rag/20260327_msc180_v2_hallucination_casebook.md`

The goal of the study was not to score search engines in the abstract. The goal was to test a specific idea:
- when a small Lean prover hallucinates a Mathlib theorem name,
- can we query a theorem search engine with that hallucinated name, optionally combined with the problem statement,
- and recover useful real theorems that do roughly what the hallucination was trying to do?

This pass uses:
- `4` MSC-180 problems
- `2` hallucinations per problem
- `LeanFinder` only
- top-`2` results only

The top-`2` restriction matters. It is a more realistic proxy for a future retrieval loop than top-`5`, because we probably do not want to inject a long list of theorem candidates into the model context.

## Problems Covered
The study used these four problems:
- `MSC-180_12_001`
- `MSC-180_14_003`
- `MSC-180_52_002`
- `MSC-180_65_003`

These were chosen because they contain multiple theorem-like hallucinations and are better suited than the original seed cases for testing whether different hallucinations can retrieve different theorem families.

## Aggregate Conclusion
The overall pattern is clear.

1. The formal statement is doing most of the heavy lifting.
- `statement only` retrieval is already strong on all `4` problems.
- In several cases it returns the main useful theorem family immediately.

2. Hallucinations still carry useful local signal.
- `hallucination only` is less stable, but when it works it often preserves theorem intent that the full statement washes out.
- This is especially visible when two hallucinations in the same proof are trying to express different subfacts.

3. The best single query mode is usually `hallucination + statement`.
- It keeps the global relevance of the statement.
- It often rescues weak hallucinations.
- It still preserves some of the local signal from the hallucinated theorem name.

4. `statement + both hallucinations` is usually good, but not obviously better.
- It tends to collapse toward the dominant theorem family for the whole problem.
- That is useful for getting a strong global theorem into context.
- It is less useful if the goal is to preserve distinct intent from different hallucinations.

Compressed to one sentence:
- the statement gives the search engine the global problem, the hallucination gives it local intent, and the most promising deployment-style query is one hallucination plus the statement with top-`2` retrieval.

## Configuration-Level Findings

### `statement only`
This is the strongest baseline.

What it does well:
- retrieves globally relevant theorem families
- often returns the main proof-driving theorem in top-`2`
- is robust across all `4` problems

Representative top-`2` results:
- `MSC-180_12_001`:
  - `Polynomial.div_eq_quo_add_rem_div`
  - `Polynomial.div_modByMonic_unique`
- `MSC-180_14_003`:
  - `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
  - `pow_rootMultiplicity_not_dvd`
- `MSC-180_52_002`:
  - `convexHull_diam`
- `MSC-180_65_003`:
  - `norm_image_sub_le_of_norm_deriv_le_segment`
  - `Convex.lipschitzOnWith_of_nnnorm_deriv_le`

Interpretation:
- if we only care about giving the model a small amount of useful context, statement-only retrieval is already viable.
- it is not enough, by itself, to tell us what a specific hallucinated theorem was trying to do.

### `hallucination only`
This is the best mode for preserving distinct theorem intent, but it is not stable enough to use alone.

What it does well:
- separates different hallucinations in the same problem
- often recovers a local theorem family close to the hallucination

What it does poorly:
- sometimes returns infrastructure rather than the theorem we want
- sometimes locks onto surface-form similarity rather than proof relevance

Representative top-`2` results:
- `MSC-180_12_001`
  - `divModByMonic_eq_div_mod`:
    - `Polynomial.divByMonic`
    - `Polynomial.modByMonic`
  - `modByMonic_lt_of_lt`:
    - `Polynomial.degree_modByMonic_lt`
    - `Polynomial.modByMonic`
- `MSC-180_14_003`
  - `pow_dvd_iff_le_multiplicity`:
    - `pow_multiplicity_dvd`
    - `pow_dvd_iff_le_multiplicity`
  - `mul_divByMonic_eq_iff_isRoot.mpr`:
    - `Polynomial.mul_divByMonic_eq_iff_isRoot`
    - `Polynomial.mul_div_eq_iff_isRoot`
- `MSC-180_52_002`
  - `extremePoints_convexHull_of_mem`:
    - `extremePoints_convexHull_subset`
    - `subset_convexHull`
  - `Metric.diam_convexHull`:
    - `convexHull_diam`
- `MSC-180_65_003`
  - `Metric.lipschitzOnWith_iff_metric.mpr`:
    - `lipschitzOnWith_iff_dist_le_mul`
    - `LipschitzWith.lipschitzOnWith`
  - `ExistsDerivWithinAt_Icc`:
    - `HasDerivAt.hasDerivWithinAt`
    - `HasDerivWithinAt`

Interpretation:
- this is useful evidence that different hallucinations can really point to different theorem families.
- but it is also the configuration most likely to return something too local or too infrastructural.

### `hallucination + statement`
This is the best compromise.

What it does well:
- stabilizes weak hallucinations
- preserves more local signal than statement-only
- usually returns a useful theorem family in top-`2`

Representative top-`2` results:
- `MSC-180_12_001`
  - `divModByMonic_eq_div_mod + statement`:
    - `Polynomial.div_eq_quo_add_rem_div`
    - `Polynomial.div_modByMonic_unique`
  - `modByMonic_lt_of_lt + statement`:
    - `Polynomial.div_modByMonic_unique`
    - `Polynomial.div_eq_quo_add_rem_div`
- `MSC-180_14_003`
  - `pow_dvd_iff_le_multiplicity + statement`:
    - `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
    - `le_rootMultiplicity_iff`
  - `mul_divByMonic_eq_iff_isRoot.mpr + statement`:
    - `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
    - `Polynomial.pow_mul_divByMonic_rootMultiplicity_eq`
- `MSC-180_52_002`
  - `extremePoints_convexHull_of_mem + statement`:
    - `convexHull_diam`
  - `Metric.diam_convexHull + statement`:
    - `convexHull_diam`
- `MSC-180_65_003`
  - `Metric.lipschitzOnWith_iff_metric.mpr + statement`:
    - `Convex.lipschitzOnWith_of_nnnorm_deriv_le`
    - `norm_image_sub_le_of_norm_deriv_le_segment`
  - `ExistsDerivWithinAt_Icc + statement`:
    - `Convex.lipschitzOnWith_of_nnnorm_deriv_le`
    - `norm_image_sub_le_of_norm_deriv_le_segment`

Interpretation:
- this is the strongest single configuration for a first prototype.
- it does not always preserve theorem distinctness as well as hallucination-only, but it is much more robust.

### `statement + both hallucinations`
This is strong as a global reranker, but not clearly better than the best single-hallucination query.

Representative top-`2` results:
- `MSC-180_12_001`:
  - `Polynomial.div_modByMonic_unique`
  - `Polynomial.div_eq_quo_add_rem_div`
- `MSC-180_14_003`:
  - `Polynomial.exists_eq_pow_rootMultiplicity_mul_and_not_dvd`
  - `Polynomial.pow_mul_divByMonic_rootMultiplicity_eq`
- `MSC-180_52_002`:
  - `convexHull_diam`
- `MSC-180_65_003`:
  - `Convex.lipschitzOnWith_of_nnnorm_deriv_le`
  - `Convex.lipschitzOnWith_of_nnnorm_derivWithin_le`

Interpretation:
- useful if we want one globally relevant top-`2` bundle
- less useful if we care which hallucination expressed which missing theorem need

## What The Results Say About The Iterative-RAG Idea
These results support the core idea.

The manual study suggests that the following loop is worth implementing:
1. run the model on a problem
2. detect theorem-like unresolved identifiers in the failed proof
3. query theorem search using the formal statement plus one hallucinated theorem name
4. retrieve top-`2` candidate theorems
5. retry the model once with those theorem statements in context

Why the idea looks viable:
- statement-only retrieval already finds useful global theorem families
- hallucination-only retrieval sometimes isolates the specific subfact the model was groping toward
- combining the statement with a hallucination is usually strong enough to make top-`2` retrieval useful

What the results do **not** support:
- using hallucination-only retrieval as the main intervention
- feeding the model large top-`5` bundles by default
- assuming the search engine should recover a theorem whose name is lexically similar to the hallucination and nothing else

The important reframing is:
- we are not trying to recover the exact theorem the model "meant" in a purely lexical sense
- we are trying to recover a real theorem that serves the same proof role

That is exactly what the stronger cases show.

## Strongest And Weakest Cases
### Strongest
- `MSC-180_14_003`
- `MSC-180_12_001`
- `MSC-180_65_003`

These give the clearest evidence that:
- different hallucinations can correspond to different theorem families
- statement-containing queries can recover useful top-`2` theorems

### Weakest
- `MSC-180_52_002`

This case is still informative, but it behaves differently:
- once the statement is present, retrieval collapses onto `convexHull_diam`
- the two hallucinations do not produce a clean two-theorem decomposition like the other strong cases

This suggests we should not overfit the prototype to one difficult geometry case.

## Immediate Next Steps

### 1. Implement the smallest retrieval prototype
Use:
- query mode: `hallucination + statement`
- backend: `LeanFinder`
- retrieval budget: top-`2`
- intervention: retry once with retrieved theorem statements only

This is the most justified next step from the current evidence.

### 2. Compare against a statement-only baseline
The prototype should not assume hallucinations are necessary.

Minimal comparison:
- retry with statement-only top-`2`
- retry with hallucination+statement top-`2`

This will tell us whether the hallucinated name actually adds enough signal to be worth the extra machinery.

### 3. Try the full failed proof as a query
This is worth testing.

Rationale:
- the failed proof contains more local structure than the theorem statement alone
- it may help LeanFinder recover theorem families tied to the attempted tactic sequence

Risk:
- the failed proof may add too much noise
- the hallucinated name may dominate the query in bad ways

So this should be a controlled comparison, not the default first implementation.

### 4. Improve query formatting for LeanFinder
This is also worth testing.

Current queries are plain concatenation.
That is fine for an initial pass, but the next manual study should try a slightly more structured format, for example:
- statement context
- target hallucinated theorem name
- short instruction such as "find theorems similar to this name in the context of this statement"

We do not yet know whether LeanFinder benefits from this formatting, but it is cheap to test.

### 5. Add a short local snippet around the hallucination
This is your `2.5` idea.

Rationale:
- the line where the hallucination was used may be more informative than the theorem header alone
- it can tell search what proof role the theorem is supposed to play

Example of what to include later:
- the hallucinated theorem name
- one or two lines around its use
- the theorem statement

This is probably more valuable than adding the entire failed proof immediately.

### 6. Retrieve separately for each hallucination instead of merging them upfront
The current results suggest this matters.

Why:
- different hallucinations sometimes point to different theorem families
- combining all hallucinations into one query can collapse the ranking toward one dominant global theorem family

So the first prototype should likely:
- retrieve top-`2` for each hallucination separately
- optionally deduplicate and rerank before retrying

### 7. Replace or deprioritize `MSC-180_52_002` in the next manual study
If we want a cleaner diagnostic set, the first three-problem evaluation set should probably be:
- `MSC-180_12_001`
- `MSC-180_14_003`
- `MSC-180_65_003`

Those are the strongest evidence-bearing cases from this pass.

## Suggested First Prototype Rule
If we implement a minimal version next, the rule I would use is:

1. extract theorem-like unresolved identifiers from the failed proof
2. for each hallucination, run `LeanFinder` on:
   - the hallucination
   - plus the formal statement
3. keep top-`2` theorems
4. deduplicate across hallucinations
5. retry once with a short theorem block containing those retrieved statements

Fallback:
- if no theorem-like hallucination is extracted cleanly, use statement-only top-`2`

This is the smallest implementation consistent with the current evidence.

## Final Conclusion
The manual `LeanFinder top-2` study is already strong enough to justify a first iterative-RAG prototype.

The main empirical lesson is not that hallucinations alone are enough.
The main lesson is:
- statement retrieval gives global relevance
- hallucinations provide local proof intent
- combining them is a realistic way to recover useful theorems in a small retrieval budget

So the current evidence supports building a first loop around:
- one hallucination at a time
- plus the formal statement
- with top-`2` retrieved theorems
- and a single retry.
