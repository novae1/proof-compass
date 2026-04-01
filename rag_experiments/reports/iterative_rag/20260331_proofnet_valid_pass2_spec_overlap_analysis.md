# ProofNet-valid Pass2 Spec Overlap Analysis

## Scope
- baseline no-hint verified run:
  - `rag_experiments/outputs/proofnet/valid/20260331_proofnet-valid_nohint_base_deepseekv2_7b_lean4-15_verified.json`
- statement-only RAG verified run:
  - `rag_experiments/outputs/proofnet/valid/20260331_proofnet-valid_statement-rag-top2_base_deepseekv2_7b_lean4-15_verified.json`
- comparison summary:
  - `finetuning_analysis/20260331_proofnet_valid_statement_rag_top2_vs_nohint.md`
- no-hint pass2 spec:
  - `rag_experiments/data/specs/20260331_proofnet_valid_nohint_iterative_pass2_spec.json`
- statement-RAG-top2 pass2 spec:
  - `rag_experiments/data/specs/20260331_proofnet_valid_statement_rag_top2_iterative_pass2_spec.json`

## Trigger Rule
Both pass2 specs were built only for problems that are:
- unsolved in the source run
- and contain at least one filtered theorem-like hallucination

Filtered hallucinations use the same rule as earlier:
- unresolved theorem-like names from `unknown identifier` / `unknown constant`
- minimum name length `>= 7`

Both pass2 builders start from the same statement-only LeanFinder top-`2` anchors and then add up to `2` hallucination-conditioned theorem statements:
- `1` hallucination:
  - query `statement + hallucination`
  - add top `2` distinct theorem/lemma results not already in the base top-`2`
- `2+` hallucinations:
  - rank by attempt frequency, then occurrences
  - keep top `2`
  - add top `1` distinct theorem/lemma result for each

So every pass2 prompt contains at most `4` theorem statements.

## ProofNet-valid Headline
The first ProofNet-valid development comparison was:
- no-hint
- statement-only RAG top-`2`
- `4` attempts per problem

Headline result:
- no-hint: `155/740` successful attempts, `47/185` solved problems
- statement-RAG-top2: `156/740` successful attempts, `47/185` solved problems

So statement-only RAG did **not** improve solved-problem count on this run.

However, it did reduce unresolved-name burden:
- attempts with `unknown`: `122 -> 108`
- total `unknown` occurrences: `158 -> 134`

The solved sets were not identical:
- overlap: `42`
- no-hint only: `5`
- statement-RAG-top2 only: `5`

So theorem hints changed behavior meaningfully, but the gains and regressions canceled at the solved-problem level.

## Hallucination Prevalence
Using filtered theorem-like hallucinations:

No-hint:
- problems with at least one hallucination: `63/185` = `34.1%`
- failed attempts with at least one hallucination: `119/585` = `20.3%`
- failed problems with at least one hallucination: `58/138` = `42.0%`

Statement-RAG-top2:
- problems with at least one hallucination: `52/185` = `28.1%`
- failed attempts with at least one hallucination: `103/584` = `17.6%`
- failed problems with at least one hallucination: `50/138` = `36.2%`

This is enough to justify a targeted pass2 on a nontrivial subset of ProofNet-valid, but it also shows that theorem hallucination is not the dominant failure mode overall.

## Pass2 Trigger Sets
The trigger sets differ substantially.

No-hint pass2:
- triggered problems: `58`

Statement-RAG-top2 pass2:
- triggered problems: `50`

Overlap:
- shared triggered problems: `31`
- no-hint-only triggered problems: `27`
- statement-RAG-top2-only triggered problems: `19`

This already implies the two pass2 specs are not redundant.

## Hallucination Overlap Before Spec Construction
Among the `36` problems where both first-pass configurations hallucinated at all:
- any overlap in the full distinct hallucination sets: `10/36`
- any overlap in the top-`2` hallucination sets: `9/36`
- exact top-`1` match: `6/36`
- exact top-`2` set match: `4/36`

So even before theorem selection, the two branches are usually not hallucinating the same names for the same problem.

This matters because the pass2 added theorems are driven by those hallucinations.

## Final Theorem-Set Overlap
On the `31` shared triggered problems, the final theorem sets overlap a lot:
- exact final theorem-set match: `12/31`
- average final-set Jaccard: `0.693`
- median final-set Jaccard: `0.6`

But this number is inflated by the shared statement-only top-`2` anchors.

### Added-Theorem Overlap Only
The more informative comparison is to ignore the shared base top-`2` and compare only the hallucination-conditioned additions.

On the `31` shared triggered problems:
- exact added-theorem-set match: `12/31`
- any added-theorem overlap: `22/31`
- average added-set Jaccard: `0.5`
- median added-set Jaccard: `0.333`
- disjoint added-theorem sets: `9/31`

Distribution of added-theorem intersection size:
- `0`: `9`
- `1`: `11`
- `2`: `11`

So the two pass2 specs often converge to similar added theorem families, but not always.

## Interpretation
There are three distinct effects:

1. Different trigger sets
- the no-hint and statement-RAG-top2 runs do not trigger on the same subset of ProofNet-valid

2. Different hallucination signals
- even when the same problem triggers in both branches, the hallucinated theorem names often differ

3. Partial convergence in retrieved additions
- despite those differences, the final added theorem sets often overlap
- but they are still disjoint on `9/31` shared triggered problems

So the correct conclusion is:
- the two pass2 specs are **not duplicates**
- but they are also **not independent**
- they share the same statement-only base anchors and sometimes converge on the same local theorem family

## Practical Consequence
It is worth running both pass2 branches:
- no-hint -> pass2
- statement-RAG-top2 -> pass2

Reason:
- the triggered subsets differ materially
- and on shared triggered problems the added theorem sets are only partially aligned

If either branch shows a real gain, that result will not automatically imply the other branch would behave the same way.

## Representative Shared-Problem Cases
Exact added-theorem-set match examples:
- `exercise_13_5a`
- `exercise_1_18a`
- `exercise_1_26`
- `exercise_22_2b`
- `exercise_2_5_44`

Partial-overlap examples:
- `exercise_13_8b`
- `exercise_23_2`
- `exercise_2_11_22`
- `exercise_2_4_16b`
- `exercise_30_13`

Disjoint added-theorem-set example:
- `exercise_23_4`

So there is no single blanket statement like “the two pass2 specs are basically the same” or “the two pass2 specs are unrelated.” The reality is in between, with substantial but incomplete convergence.
