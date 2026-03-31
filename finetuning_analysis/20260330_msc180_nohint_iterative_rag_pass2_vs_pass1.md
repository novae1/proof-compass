# MSC-180 No-Hint Comparison

## Scope
- baseline: `rag_experiments/outputs/msc180/v2_nohint/20260330_msc180-v2-nohint_iterative-rag-pass1_base_deepseekv2_7b_lean4-15_verified.json`
- candidate: `rag_experiments/outputs/msc180/v2_nohint/20260330_msc180-v2-nohint_iterative-rag-pass2_base_deepseekv2_7b_lean4-15_verified.json`

Labels:
- baseline: `iterative_rag_pass1`
- candidate: `iterative_rag_pass2`

## Headline
- iterative_rag_pass1: `92/400` successful attempts, `9/20` problems solved
- iterative_rag_pass2: `87/400` successful attempts, `11/20` problems solved

Delta:
- successful attempts: `-5`
- problems solved: `+2`
- attempts with unknown: `-44`
- total unknown occurrences: `-62`

## Metrics
### iterative_rag_pass1
- attempt pass rate: `23.00%`
- problem pass rate: `45.00%`
- attempts with unknown: `130/400` (`32.50%`)
- unknown among failed attempts: `42.21%`

### iterative_rag_pass2
- attempt pass rate: `21.75%`
- problem pass rate: `55.00%`
- attempts with unknown: `86/400` (`21.50%`)
- unknown among failed attempts: `27.48%`

## Improved Problems
- `no-hint/MSC-180_14_001`: `11/20 -> 19/20`
- `no-hint/MSC-180_26_002`: `16/20 -> 18/20`
- `no-hint/MSC-180_90_001`: `0/20 -> 2/20`
- `no-hint/MSC-180_14_003`: `0/20 -> 1/20`
- `no-hint/MSC-180_20_001`: `18/20 -> 19/20`
- `no-hint/MSC-180_60_002`: `0/20 -> 1/20`

## Regressed Problems
- `no-hint/MSC-180_08_001`: `19/20 -> 9/20`
- `no-hint/MSC-180_12_003`: `11/20 -> 7/20`
- `no-hint/MSC-180_52_002`: `5/20 -> 3/20`
- `no-hint/MSC-180_68_002`: `5/20 -> 3/20`
- `no-hint/MSC-180_08_002`: `6/20 -> 5/20`
- `no-hint/MSC-180_28_003`: `1/20 -> 0/20`

## Unchanged Problems
- `8` problems unchanged
