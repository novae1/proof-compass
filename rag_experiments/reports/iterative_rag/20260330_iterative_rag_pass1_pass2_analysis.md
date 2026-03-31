# Iterative RAG Pass 1 / Pass 2 Analysis

## Scope
This note summarizes the first uncontaminated MSC-180 no-hint iterative-RAG runs built from the committed specs:

- `rag_experiments/data/specs/20260330_msc180_nohint_iterative_rag_pass1_spec.json`
- `rag_experiments/data/specs/20260330_msc180_nohint_iterative_rag_pass2_spec.json`

Compared runs:
- base no-hint: `rag_experiments/outputs/msc180/v2_nohint/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json`
- pass1 statement-only retrieval: `rag_experiments/outputs/msc180/v2_nohint/20260330_msc180-v2-nohint_iterative-rag-pass1_base_deepseekv2_7b_lean4-15_verified.json`
- pass2 statement + hallucination-derived retrieval: `rag_experiments/outputs/msc180/v2_nohint/20260330_msc180-v2-nohint_iterative-rag-pass2_base_deepseekv2_7b_lean4-15_verified.json`

Detailed pairwise comparison artifacts:
- `finetuning_analysis/20260330_msc180_nohint_iterative_rag_pass1_vs_base.md`
- `finetuning_analysis/20260330_msc180_nohint_iterative_rag_pass2_vs_base.md`
- `finetuning_analysis/20260330_msc180_nohint_iterative_rag_pass2_vs_pass1.md`

## Headline
| run | successful attempts | solved problems | attempts with `unknown` |
| --- | --- | --- | --- |
| base | `77/400` | `6/20` | `111/400` |
| pass1 | `92/400` | `9/20` | `130/400` |
| pass2 | `87/400` | `11/20` | `86/400` |

Key deltas:
- pass1 vs base:
  - successful attempts: `+15`
  - solved problems: `+3`
  - attempts with `unknown`: `+19`
  - total `unknown` occurrences: `-4`
- pass2 vs base:
  - successful attempts: `+10`
  - solved problems: `+5`
  - attempts with `unknown`: `-25`
  - total `unknown` occurrences: `-66`
- pass2 vs pass1:
  - successful attempts: `-5`
  - solved problems: `+2`
  - attempts with `unknown`: `-44`
  - total `unknown` occurrences: `-62`

## Main conclusions

### 1. Statement-only retrieval is already strong
The missing ablation turned out to matter a lot.

Pass1 alone improves substantially over the no-hint baseline:
- `77/400 -> 92/400` successful attempts
- `6/20 -> 9/20` solved problems

This means a large fraction of the gain does not require hallucination-conditioned retrieval at all. The theorem statement by itself is already a strong retrieval seed.

### 2. Hallucination-conditioned additions still matter
Pass2 does not dominate pass1 on attempt pass rate, but it does improve the metrics that are most closely aligned with theorem grounding:
- `9/20 -> 11/20` solved problems
- `130/400 -> 86/400` attempts with `unknown`

So the hallucination-derived extra theorems appear to help the model solve a broader set of problems and reduce unresolved-name failures, even though they also introduce some distraction on attempt-rich problems.

### 3. Pass1 and pass2 optimize different things
Current picture:
- pass1 is better for raw attempt pass rate
- pass2 is better for solved-problem coverage and unknown-name reduction

That is a meaningful tradeoff, not noise.

## Low-count wins caveat
The problem-level headline `9/20 -> 11/20` is real, but not all newly solved problems should be treated as equally strong evidence.

Pass2-only solved problems:
- `no-hint/MSC-180_14_003`: `0/20 -> 1/20`
- `no-hint/MSC-180_60_002`: `0/20 -> 1/20`
- `no-hint/MSC-180_90_001`: `0/20 -> 2/20`

Pass1-only solved problem:
- `no-hint/MSC-180_28_003`: `1/20 -> 0/20`

So the low-count tail needs qualitative inspection:
- some of these wins are probably real improvements in theorem grounding
- some are likely just sampling luck

The rest of this note distinguishes those cases explicitly.

## Problem-level pattern

### Pass1 biggest wins over base
- `no-hint/MSC-180_08_001`: `0/20 -> 19/20`
- `no-hint/MSC-180_08_002`: `0/20 -> 6/20`
- `no-hint/MSC-180_52_002`: `0/20 -> 5/20`

### Pass2 biggest wins over pass1
- `no-hint/MSC-180_14_001`: `11/20 -> 19/20`
- `no-hint/MSC-180_26_002`: `16/20 -> 18/20`
- `no-hint/MSC-180_90_001`: `0/20 -> 2/20`
- `no-hint/MSC-180_14_003`: `0/20 -> 1/20`
- `no-hint/MSC-180_60_002`: `0/20 -> 1/20`

### Main regressions to inspect
Pass1 vs base:
- `no-hint/MSC-180_12_003`: `16/20 -> 11/20`
- `no-hint/MSC-180_14_001`: `14/20 -> 11/20`
- `no-hint/MSC-180_26_002`: `19/20 -> 16/20`

Pass2 vs pass1:
- `no-hint/MSC-180_08_001`: `19/20 -> 9/20`
- `no-hint/MSC-180_12_003`: `11/20 -> 7/20`
- `no-hint/MSC-180_52_002`: `5/20 -> 3/20`

These regressions are consistent with a likely tradeoff:
- extra retrieved theorems can improve grounding and coverage
- but too much or slightly off-target context can still distract the model on problems where statement-only retrieval was already enough

## Qualitative inspection of changed problems

### Robust pass2 win: `MSC-180_14_001`
This is the clearest high-confidence pass2 improvement.

Counts:
- pass1: `11/20`
- pass2: `19/20`

Hallucination behavior:
- pass1 had `8` attempts with filtered unresolved theorem names
- pass2 had `1`

The key difference is the added hallucination-derived context:
- pass1 only had weak statement anchors
- pass2 added:
  - `QuotientGroup.quotientKerEquivOfSurjective`
  - `QuotientGroup.quotientKerEquivRange`

The successful pass2 proofs use exactly the quotient-kernel equivalence family that the hallucination analysis pointed to. This looks like a genuine win for the hallucination-conditioned step, not luck.

### Ambiguous pass2 gain: `MSC-180_26_002`
Counts:
- pass1: `16/20`
- pass2: `18/20`

But this is not evidence for the hallucination-conditioned step, because pass1 and pass2 had the same theorem context here:
- `Real.exists_isLUB`
- `Real.isLUB_sSup`

There were no hallucination-derived additions for this problem. So the `+2` is almost certainly sampling variance, not a pass2 mechanism effect.

### Low-count but plausible pass2 win: `MSC-180_14_003`
Counts:
- base: `0/20`
- pass1: `0/20`
- pass2: `1/20`

Hallucination behavior:
- base: `4` attempts with filtered unresolved names, `17` filtered occurrences
- pass1: `16` attempts with filtered unresolved names, `27` occurrences
- pass2: `8` attempts with filtered unresolved names, `18` occurrences

Qualitatively:
- pass1 often hallucinated local divisibility/multiplicity lemmas such as `mul_dvd_of_dvd_of_dvd`
- pass2 cut those unknown-name failures roughly in half
- the one successful pass2 attempt produced a proof in the right theorem family: power divisibility, root multiplicity, and evaluation-at-root non-vanishing

This is still only `1/20`, so it is not decisive. But unlike a pure lucky sample, the failure distribution also improved in the expected direction. This is suggestive evidence that hallucination-conditioned retrieval helped.

### Low-count and mixed: `MSC-180_60_002`
Counts:
- base: `0/20`
- pass1: `0/20`
- pass2: `1/20`

Hallucination behavior:
- base: `18` attempts with filtered unresolved names
- pass1: `7`
- pass2: `0`

This is the clearest example where retrieval changed the failure mode:
- base was dominated by fake polynomial-approximation names
- pass1 reduced that sharply
- pass2 removed it entirely

However, the interpretation is still mixed:
- pass1 already had the correct main theorem, `exists_polynomial_near_of_continuousOn`
- many pass1 failures were no longer hallucination failures but `linarith` failures while trying to convert `< ε` into `≤ ε`
- the pass2 success is a short proof using the same core theorem family

So pass2 clearly improved grounding, but the additional theorem context may not be the whole reason it finally solved one sample. This is encouraging, but not yet strong causal evidence for the hallucination step itself.

### Low-count and probably luck: `MSC-180_90_001`
Counts:
- base: `0/20`
- pass1: `0/20`
- pass2: `2/20`

Hallucination behavior:
- base: `2` attempts with filtered unresolved names
- pass1: `1`
- pass2: `0`

But the successful pass2 proofs are just direct uses of `convex_ball`, which was already present in pass1. The extra pass2 theorem `Seminorm.convex_ball` was not needed in the successful proofs.

This means the `2/20` improvement is promising but weak evidence. It could easily be sampling luck rather than a real advantage from hallucination-conditioned retrieval.

### Low-count pass1-only case: `MSC-180_28_003`
Counts:
- base: `3/20`
- pass1: `1/20`
- pass2: `0/20`

This should be interpreted symmetrically with the pass2 low-count wins: the single pass1 success is not strong evidence for pass1 superiority here.

Both pass1 and pass2 were still dominated by outer-measure hallucinations:
- pass1: `9` attempts with filtered unresolved names
- pass2: `9`

So this problem remains unresolved and should not carry much weight in either direction.

### Clear pass2 regression: `MSC-180_08_001`
Counts:
- base: `0/20`
- pass1: `19/20`
- pass2: `9/20`

Hallucination behavior:
- base: `12` attempts with filtered unresolved names
- pass1: `1`
- pass2: `11`

This is a strong negative example for the hallucination-conditioned step.

Pass1 already had the right theorem pair:
- `ext_of_adjoin_eq_top`
- `AlgHom.ext_of_adjoin_eq_top`

Its successful proofs were extremely clean:
- `apply AlgHom.ext_of_adjoin_eq_top hgen`

Pass2 added more related declarations:
- `ext_of_eq_adjoin`
- `AlgHom.adjoin_ext`

After that, the model frequently switched to the unresolved unqualified name:
- `ext_of_adjoin_eq_top`

So pass2 did not merely add noise. It appears to have pushed the model toward a more ambiguous local theorem family and increased namespace confusion.

### Clear pass2 regression: `MSC-180_12_003`
Counts:
- base: `16/20`
- pass1: `11/20`
- pass2: `7/20`

Hallucination behavior:
- base: `2` attempts with filtered unresolved names
- pass1: `0`
- pass2: `8`

This is another strong negative example.

Pass1 already had a clean hint pair:
- `maximal_ideal_iff_isField_quotient`
- `Ideal.Quotient.maximal_ideal_iff_isField_quotient`

Pass2 added:
- `Ideal.Quotient.maximal_of_isField`
- `isField_iff_maximalIdeal_eq`

After that, the model started hallucinating the wrong nearby quotient/field lemmas:
- `Ideal.Quotient.isField_iff_isField_quotient.mpr`
- `Ideal.Quotient.isField_iff_isEmpty.mpr`

So here the hallucination-conditioned additions very likely made the retrieval context worse by over-expanding an already adequate theorem family.

### Mixed case: `MSC-180_52_002`
Counts:
- base: `0/20`
- pass1: `5/20`
- pass2: `3/20`

Hallucination behavior:
- base: `4` attempts with filtered unresolved names
- pass1: `8`
- pass2: `0`

This case is interesting because pass2 clearly improved grounding but still regressed on success count.

Pass1 failures often included extreme-point theorem hallucinations. Pass2 eliminated hallucinations entirely, but the failure mode shifted to:
- `exact?` failures
- `Proof contains sorries`
- one collision where `convexHull_exists_dist_ge2` was treated as already declared

So pass2 made the model more grounded, but not more successful overall. This is evidence that theorem-name hallucination reduction and final proof success are related but not identical objectives.

## Per-problem hallucination analysis
The aggregate drop in unknown-name failures is real, but it is not uniform across problems.

Primary hallucination metric used in the table below:
- `hall att` = attempts with at least one filtered unresolved theorem-like identifier

Secondary intensity metric:
- `hall occ` = total filtered unresolved theorem-like name occurrences across all 20 attempts

## Per-problem table
| problem | base pass | pass1 pass | pass2 pass | base hall att | pass1 hall att | pass2 hall att | base hall occ | pass1 hall occ | pass2 hall occ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MSC-180_05_003 | `0/20` | `0/20` | `0/20` | `15/20` | `8/20` | `14/20` | `17` | `9` | `14` |
| MSC-180_08_001 | `0/20` | `19/20` | `9/20` | `12/20` | `1/20` | `11/20` | `13` | `1` | `11` |
| MSC-180_08_002 | `0/20` | `6/20` | `5/20` | `4/20` | `1/20` | `1/20` | `8` | `2` | `2` |
| MSC-180_08_003 | `0/20` | `0/20` | `0/20` | `0/20` | `0/20` | `0/20` | `0` | `0` | `0` |
| MSC-180_12_001 | `0/20` | `0/20` | `0/20` | `10/20` | `19/20` | `16/20` | `18` | `44` | `27` |
| MSC-180_12_002 | `0/20` | `0/20` | `0/20` | `0/20` | `1/20` | `2/20` | `0` | `1` | `4` |
| MSC-180_12_003 | `16/20` | `11/20` | `7/20` | `2/20` | `0/20` | `8/20` | `2` | `0` | `8` |
| MSC-180_14_001 | `14/20` | `11/20` | `19/20` | `6/20` | `8/20` | `1/20` | `6` | `8` | `1` |
| MSC-180_14_003 | `0/20` | `0/20` | `1/20` | `4/20` | `16/20` | `8/20` | `17` | `27` | `18` |
| MSC-180_15_003 | `0/20` | `0/20` | `0/20` | `8/20` | `12/20` | `9/20` | `13` | `14` | `16` |
| MSC-180_20_001 | `19/20` | `18/20` | `19/20` | `0/20` | `0/20` | `0/20` | `0` | `0` | `0` |
| MSC-180_26_002 | `19/20` | `16/20` | `18/20` | `0/20` | `0/20` | `0/20` | `0` | `0` | `0` |
| MSC-180_28_003 | `3/20` | `1/20` | `0/20` | `7/20` | `9/20` | `9/20` | `16` | `11` | `11` |
| MSC-180_40_003 | `0/20` | `0/20` | `0/20` | `3/20` | `18/20` | `0/20` | `3` | `26` | `0` |
| MSC-180_52_002 | `0/20` | `5/20` | `3/20` | `4/20` | `8/20` | `0/20` | `5` | `9` | `0` |
| MSC-180_60_002 | `0/20` | `0/20` | `1/20` | `18/20` | `7/20` | `0/20` | `18` | `7` | `0` |
| MSC-180_65_001 | `0/20` | `0/20` | `0/20` | `0/20` | `0/20` | `0/20` | `0` | `0` | `0` |
| MSC-180_65_003 | `0/20` | `0/20` | `0/20` | `6/20` | `17/20` | `2/20` | `9` | `17` | `2` |
| MSC-180_68_002 | `6/20` | `5/20` | `3/20` | `0/20` | `0/20` | `0/20` | `0` | `0` | `0` |
| MSC-180_90_001 | `0/20` | `0/20` | `2/20` | `2/20` | `1/20` | `0/20` | `2` | `1` | `0` |

## Error taxonomy beyond hallucinations
Theorem hallucination is only one failure mode. For failed attempts, the current report groups messages into these coarse buckets:

- `hallucination`: `unknown identifier` / `unknown constant`
- `unsolved_goals`: Lean reaches a partial proof state but leaves goals open
- `type_mismatch`: includes `type mismatch` and `application type mismatch`
- `calc_issue`: malformed or ill-typed `calc` chains
- `finishing_failure`: local proof-completion failures such as `linarith failed`, `exact?` failure, `aesop` failure, `rewrite` failure, and failed `simp`
- `invalid_field_notation`
- `sorries`
- `other`

### Aggregate failed-attempt buckets
| subset | run | failed attempts | hallucination | unsolved_goals | type_mismatch | calc_issue | finishing_failure | invalid_field_notation | sorries | other |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all problems | base | `323` | `109` | `57` | `42` | `20` | `62` | `9` | `0` | `24` |
| all problems | pass1 | `308` | `129` | `41` | `25` | `11` | `45` | `10` | `0` | `47` |
| all problems | pass2 | `313` | `86` | `76` | `39` | `13` | `53` | `6` | `3` | `37` |
| changed problems only | base | `128` | `59` | `13` | `7` | `16` | `26` | `4` | `0` | `3` |
| changed problems only | pass1 | `117` | `50` | `14` | `10` | `9` | `22` | `6` | `0` | `6` |
| changed problems only | pass2 | `120` | `38` | `14` | `9` | `13` | `35` | `3` | `3` | `5` |

Interpretation:
- pass2 reduces hallucination failures substantially, both overall and on the changed-problem subset
- many of those failures do not disappear; they shift into `unsolved_goals` and `finishing_failure`
- this supports the current view that theorem grounding improves before full proof completion does

### Dominant error buckets on changed problems
| problem | base dominant errors | pass1 dominant errors | pass2 dominant errors |
| --- | --- | --- | --- |
| MSC-180_14_001 | `hallucination:6` | `hallucination:8`, `invalid_field_notation:1` | `hallucination:1` |
| MSC-180_14_003 | `unsolved_goals:10`, `hallucination:4`, `finishing_failure:2` | `hallucination:16`, `unsolved_goals:2`, `finishing_failure:1` | `hallucination:8`, `unsolved_goals:6`, `finishing_failure:4` |
| MSC-180_60_002 | `hallucination:18`, `invalid_field_notation:1`, `other:1` | `finishing_failure:9`, `hallucination:7`, `type_mismatch:3` | `finishing_failure:15`, `type_mismatch:3`, `hallucination:1` |
| MSC-180_90_001 | `calc_issue:16`, `hallucination:2`, `finishing_failure:1` | `unsolved_goals:10`, `calc_issue:9`, `hallucination:1` | `calc_issue:13`, `unsolved_goals:3`, `invalid_field_notation:1` |
| MSC-180_28_003 | `finishing_failure:9`, `hallucination:7`, `type_mismatch:1` | `hallucination:9`, `finishing_failure:8`, `unsolved_goals:2` | `hallucination:9`, `finishing_failure:5`, `unsolved_goals:5` |
| MSC-180_08_001 | `hallucination:15`, `type_mismatch:4`, `unsolved_goals:1` | `hallucination:1` | `hallucination:11` |
| MSC-180_12_003 | `hallucination:2`, `invalid_field_notation:2` | `other:5`, `invalid_field_notation:4` | `hallucination:8`, `other:2`, `type_mismatch:2` |
| MSC-180_52_002 | `finishing_failure:14`, `hallucination:5`, `unsolved_goals:1` | `hallucination:8`, `finishing_failure:4`, `type_mismatch:3` | `finishing_failure:11`, `sorries:3`, `other:2` |

Problems where pass2 clearly reduced hallucination pressure:
- `MSC-180_14_001`: `8 -> 1` attempts with filtered unresolved names
- `MSC-180_14_003`: `16 -> 8`
- `MSC-180_60_002`: `7 -> 0`
- `MSC-180_90_001`: `1 -> 0`
- `MSC-180_52_002`: `8 -> 0`

Problems where pass2 made hallucinations worse:
- `MSC-180_08_001`: `1 -> 11`
- `MSC-180_12_003`: `0 -> 8`

Problems where pass2 did not change the hallucination load materially:
- `MSC-180_28_003`: `9 -> 9`

This supports a more precise version of the current hypothesis:
- hallucination-conditioned retrieval is useful when the model is already stuck on a real missing theorem family
- but if statement-only retrieval already gives a clean anchor, extra related theorems can cause namespace confusion and increase hallucinations again

## What this changes
Before the pass1 run, it was tempting to attribute most of the improvement to hallucination-driven retrieval. That would have been wrong.

The more defensible conclusion is:
- statement-only RAG already gives a large gain over base
- hallucination-conditioned additions provide extra value mainly through coverage and error-type reduction
- the iterative-RAG idea remains promising, but the hallucination-conditioned step should be treated as a targeted augmentation, not as the sole source of improvement

## Practical next steps
1. Inspect the pass2 regressions against pass1, especially `MSC-180_08_001` and `MSC-180_12_003`.
2. Test a smaller pass2 theorem budget, e.g. cap at `3` theorems total instead of `4`.
3. Keep pass1 as the clean uncontaminated baseline for all future iterative-RAG comparisons.
