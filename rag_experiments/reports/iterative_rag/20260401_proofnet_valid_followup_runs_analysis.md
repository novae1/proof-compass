# ProofNet-valid Follow-up Run Analysis

This note compares the five new follow-up runs against the relevant existing ProofNet-valid baselines.

## Subsets

- `N`: no-hint pass2 trigger set
  - source: `rag_experiments/data/specs/20260331_proofnet_valid_nohint_iterative_pass2_spec.json`
  - size: `58`
- `R`: statement-RAG-top2 pass2 trigger set
  - source: `rag_experiments/data/specs/20260331_proofnet_valid_statement_rag_top2_iterative_pass2_spec.json`
  - size: `50`
- `S`: solved-or-triggered follow-up set for the statement-RAG-top4 run
  - source: `rag_experiments/data/specs/20260401_proofnet_valid_statement_rag_top4_followup_spec.json`
  - size: `122`

The new verified runs are:

- `rag_experiments/outputs/proofnet/valid/20260401_proofnet-valid_nohint-trigger-subset_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260401_proofnet-valid_statement-rag-top2-trigger-subset_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260401_proofnet-valid_statement-rag-top4-followup_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260401_proofnet-valid_nohint-attempt-rag-top4_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260401_proofnet-valid_statement-rag-top2-attempt-rag-top4_base_deepseekv2_7b_lean4-15_verified.json`

The relevant older baselines are:

- `rag_experiments/outputs/proofnet/valid/20260331_proofnet-valid_nohint_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260331_proofnet-valid_statement-rag-top2_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260401_proofnet-valid_nohint-pass2_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260401_proofnet-valid_statement-rag-top2-pass2_base_deepseekv2_7b_lean4-15_verified.json`

Hallucination metrics below use the filtered theorem-like metric:

- unresolved `unknown identifier` / `unknown constant`
- minimum name length `>= 7`

## Headline

The follow-up runs do not overturn the main result.

- The iterative hallucination-conditioned pass2 still beats the matched-compute control in both branches.
- Whole-attempt top4 retrieval is competitive with pass2 and reduces hallucinations even more sharply.
- Statement-RAG-top4 on the broader solved-or-triggered subset adds some new solved problems, but only modestly improves over the best first-pass union while losing some previously solved problems.

## Matched-Compute Controls on `N`

`N` contains the `58` problems that triggered the no-hint pass2.

### Performance

- first 4 no-hint attempts on `N`
  - `0/232` successful attempts
  - `0/58` solved problems
- extra 4 no-hint attempts on `N`
  - `4/232`
  - `4/58`
- combined 8 no-hint attempts on `N`
  - `4/464`
  - `4/58`
- no-hint pass2 on `N`
  - `6/232`
  - `6/58`
- no-hint whole-attempt-top4 on `N`
  - `7/232`
  - `5/58`

### Hallucination rates

- extra 4 no-hint attempts on `N`
  - failed-attempt hallucination rate: `96/228 = 42.1%`
  - failed-problem hallucination rate: `42/54 = 77.8%`
- no-hint pass2 on `N`
  - failed-attempt hallucination rate: `80/226 = 35.4%`
  - failed-problem hallucination rate: `32/52 = 61.5%`
- no-hint whole-attempt-top4 on `N`
  - failed-attempt hallucination rate: `55/225 = 24.4%`
  - failed-problem hallucination rate: `25/53 = 47.2%`

### Solved-problem overlap

Extra 4 no-hint attempts solve:

- `exercise_23_4`
- `exercise_38_6`
- `exercise_4_4_7`
- `exercise_9_1_6`

No-hint pass2 solves:

- `exercise_27_4`
- `exercise_2_4_36`
- `exercise_32_1`
- `exercise_38_6`
- `exercise_3_2_21a`
- `exercise_9_4_11`

Shared:

- `exercise_38_6`

No-hint whole-attempt-top4 solves:

- `exercise_27_4`
- `exercise_2_24`
- `exercise_32_1`
- `exercise_3_2_21a`
- `exercise_4_5_25`

Compared to no-hint pass2:

- whole-attempt-top4 only:
  - `exercise_2_24`
  - `exercise_4_5_25`
- pass2 only:
  - `exercise_2_4_36`
  - `exercise_38_6`
  - `exercise_9_4_11`
- shared:
  - `exercise_27_4`
  - `exercise_32_1`
  - `exercise_3_2_21a`

### Interpretation

- Pass2 still beats the matched-compute no-hint control: `6` solved versus `4`.
- The whole-attempt-top4 variant is roughly competitive on solve count and stronger on hallucination suppression than pass2.
- The solved-problem overlap is only partial, so pass2 and whole-attempt retrieval are not solving the same exact cases.

## Matched-Compute Controls on `R`

`R` contains the `50` problems that triggered the statement-RAG-top2 pass2.

### Performance

- first 4 statement-RAG-top2 attempts on `R`
  - `0/200` successful attempts
  - `0/50` solved problems
- extra 4 statement-RAG-top2 attempts on `R`
  - `4/200`
  - `3/50`
- combined 8 statement-RAG-top2 attempts on `R`
  - `4/400`
  - `3/50`
- statement-RAG-top2 pass2 on `R`
  - `4/200`
  - `4/50`
- statement-RAG-top2 whole-attempt-top4 on `R`
  - `5/200`
  - `4/50`

### Hallucination rates

- extra 4 statement-RAG-top2 attempts on `R`
  - failed-attempt hallucination rate: `77/196 = 39.3%`
  - failed-problem hallucination rate: `37/47 = 78.7%`
- statement-RAG-top2 pass2 on `R`
  - failed-attempt hallucination rate: `67/196 = 34.2%`
  - failed-problem hallucination rate: `30/46 = 65.2%`
- statement-RAG-top2 whole-attempt-top4 on `R`
  - failed-attempt hallucination rate: `53/195 = 27.2%`
  - failed-problem hallucination rate: `28/46 = 60.9%`

### Solved-problem overlap

Extra 4 statement-RAG-top2 attempts solve:

- `exercise_13_4_10`
- `exercise_1_26`
- `exercise_9_4_11`

Statement-RAG-top2 pass2 solves:

- `exercise_13_4_10`
- `exercise_2_5_30`
- `exercise_32_1`
- `exercise_3_2_21a`

Shared:

- `exercise_13_4_10`

Statement-RAG-top2 whole-attempt-top4 solves:

- `exercise_13_4_10`
- `exercise_23_2`
- `exercise_3_1_22b`
- `exercise_3_2_21a`

Compared to statement-RAG-top2 pass2:

- whole-attempt-top4 only:
  - `exercise_23_2`
  - `exercise_3_1_22b`
- pass2 only:
  - `exercise_2_5_30`
  - `exercise_32_1`
- shared:
  - `exercise_13_4_10`
  - `exercise_3_2_21a`

### Interpretation

- Pass2 still beats the matched-compute statement-RAG-top2 control: `4` solved versus `3`.
- Whole-attempt-top4 matches pass2 on solved problems and slightly improves attempt-level success.
- Whole-attempt-top4 also drives hallucination rates lower than pass2 on the same subset.

## Statement-RAG-Top4 on `S`

`S` contains the `122`-problem solved-or-triggered follow-up set.

### Performance

- no-hint pass1 on `S`
  - `155/488` successful attempts
  - `47/122` solved problems
- statement-RAG-top2 pass1 on `S`
  - `156/488`
  - `47/122`
- first-pass solved union on `S`
  - `52/122` solved problems
- statement-RAG-top4 on `S`
  - `284/976`
  - `53/122`

### Hallucination rates

- no-hint pass1 on `S`
  - failed-attempt hallucination rate: `119/333 = 35.7%`
  - failed-problem hallucination rate: `58/75 = 77.3%`
- statement-RAG-top2 pass1 on `S`
  - failed-attempt hallucination rate: `103/332 = 31.0%`
  - failed-problem hallucination rate: `50/75 = 66.7%`
- statement-RAG-top4 on `S`
  - failed-attempt hallucination rate: `162/692 = 23.4%`
  - failed-problem hallucination rate: `45/69 = 65.2%`

### Solved-problem overlap vs first-pass union

First-pass solved union on `S` has `52` solved problems.

Statement-RAG-top4 solves `53`.

Newly solved by top4:

- `exercise_13_4_10`
- `exercise_23_2`
- `exercise_26_11`
- `exercise_32_1`
- `exercise_4_4_7`
- `exercise_4_6_3`
- `exercise_9_4_11`

Solved by the first-pass union but not by top4:

- `exercise_11_4_8`
- `exercise_2_1_5`
- `exercise_2_9_2`
- `exercise_3_5_6`
- `exercise_4_5_25`
- `exercise_9_4_2b`

### Interpretation

- Top4 retrieval does not dominate the existing first-pass union.
- It adds `7` new solved problems on `S`, but loses `6` that were already solved by the top2/no-hint first-pass union.
- So the net solved-problem gain is only `+1`, despite running `8` attempts/problem.
- At the same time, top4 substantially reduces theorem-like hallucination rates on `S`.

## Main Takeaways

### 1. Pass2 still survives the matched-compute control

This is the strongest result from the follow-up runs.

- On `N`, pass2 solves `6/58` versus `4/58` for 8 no-hint attempts.
- On `R`, pass2 solves `4/50` versus `3/50` for 8 statement-RAG-top2 attempts.

So the pass2 gains are not explained away by simply sampling 4 more times.

### 2. Whole-attempt top4 retrieval is the most interesting competitor

It does not clearly beat pass2 on solved-problem count, but it is strong enough to matter:

- on `N`: `5/58` solved, versus `6/58` for pass2
- on `R`: `4/50` solved, matching pass2

More importantly, whole-attempt top4 produces the lowest hallucination rates among the follow-up methods on both trigger sets.

This suggests that direct retrieval from the hallucination-bearing attempt text is a serious alternative to the current statement-plus-hallucination construction.

### 3. Generic top4 statement retrieval is not an obvious answer

The broader statement-RAG-top4 run on `S`:

- reduces hallucination rates
- adds some new solves
- but also loses several first-pass solved problems

So increasing the generic theorem budget is not a clean fix.

### 4. The paper story is getting sharper

The emerging story is not:

- “more generic RAG solves theorem proving”

It is closer to:

- generic statement-only retrieval has limited effect on theorem-name hallucinations
- hallucination-aware retrieval helps more
- whole-attempt retrieval may help even more on the hallucination metric
- but the end-to-end solve gains are still modest and selective

That is a narrower claim, but it is more defensible.
