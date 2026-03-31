# MSC-180 No-Hint Comparison

## Scope
- baseline: `rag_experiments/outputs/msc180/v2_nohint/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json`
- candidate: `rag_experiments/outputs/msc180/v2_nohint/20260330_msc180-v2-nohint_iterative-rag-pass1_base_deepseekv2_7b_lean4-15_verified.json`

Labels:
- baseline: `base`
- candidate: `iterative_rag_pass1`

## Headline
- base: `77/400` successful attempts, `6/20` problems solved
- iterative_rag_pass1: `92/400` successful attempts, `9/20` problems solved

Delta:
- successful attempts: `+15`
- problems solved: `+3`
- attempts with unknown: `+19`
- total unknown occurrences: `-4`

## Metrics
### base
- attempt pass rate: `19.25%`
- problem pass rate: `30.00%`
- attempts with unknown: `111/400` (`27.75%`)
- unknown among failed attempts: `34.37%`

### iterative_rag_pass1
- attempt pass rate: `23.00%`
- problem pass rate: `45.00%`
- attempts with unknown: `130/400` (`32.50%`)
- unknown among failed attempts: `42.21%`

## Improved Problems
- `no-hint/MSC-180_08_001`: `0/20 -> 19/20`
- `no-hint/MSC-180_08_002`: `0/20 -> 6/20`
- `no-hint/MSC-180_52_002`: `0/20 -> 5/20`

## Regressed Problems
- `no-hint/MSC-180_12_003`: `16/20 -> 11/20`
- `no-hint/MSC-180_14_001`: `14/20 -> 11/20`
- `no-hint/MSC-180_26_002`: `19/20 -> 16/20`
- `no-hint/MSC-180_28_003`: `3/20 -> 1/20`
- `no-hint/MSC-180_20_001`: `19/20 -> 18/20`
- `no-hint/MSC-180_68_002`: `6/20 -> 5/20`

## Unchanged Problems
- `11` problems unchanged
