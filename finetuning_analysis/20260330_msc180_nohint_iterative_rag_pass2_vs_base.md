# MSC-180 No-Hint Comparison

## Scope
- baseline: `rag_experiments/outputs/msc180/v2_nohint/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json`
- candidate: `rag_experiments/outputs/msc180/v2_nohint/20260330_msc180-v2-nohint_iterative-rag-pass2_base_deepseekv2_7b_lean4-15_verified.json`

Labels:
- baseline: `base`
- candidate: `iterative_rag_pass2`

## Headline
- base: `77/400` successful attempts, `6/20` problems solved
- iterative_rag_pass2: `87/400` successful attempts, `11/20` problems solved

Delta:
- successful attempts: `+10`
- problems solved: `+5`
- attempts with unknown: `-25`
- total unknown occurrences: `-66`

## Metrics
### base
- attempt pass rate: `19.25%`
- problem pass rate: `30.00%`
- attempts with unknown: `111/400` (`27.75%`)
- unknown among failed attempts: `34.37%`

### iterative_rag_pass2
- attempt pass rate: `21.75%`
- problem pass rate: `55.00%`
- attempts with unknown: `86/400` (`21.50%`)
- unknown among failed attempts: `27.48%`

## Improved Problems
- `no-hint/MSC-180_08_001`: `0/20 -> 9/20`
- `no-hint/MSC-180_08_002`: `0/20 -> 5/20`
- `no-hint/MSC-180_14_001`: `14/20 -> 19/20`
- `no-hint/MSC-180_52_002`: `0/20 -> 3/20`
- `no-hint/MSC-180_90_001`: `0/20 -> 2/20`
- `no-hint/MSC-180_14_003`: `0/20 -> 1/20`
- `no-hint/MSC-180_60_002`: `0/20 -> 1/20`

## Regressed Problems
- `no-hint/MSC-180_12_003`: `16/20 -> 7/20`
- `no-hint/MSC-180_28_003`: `3/20 -> 0/20`
- `no-hint/MSC-180_68_002`: `6/20 -> 3/20`
- `no-hint/MSC-180_26_002`: `19/20 -> 18/20`

## Unchanged Problems
- `9` problems unchanged
