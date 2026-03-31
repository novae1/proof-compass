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
