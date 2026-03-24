# MSC-180 No-Hint Comparison

## Scope
- baseline: `rag_experiments/outputs/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json`
- candidate: `rag_experiments/outputs/20260323_msc180-v2-nohint_lora_r64_deepseekv2_7b_lean4-15_verified.json`

Labels:
- baseline: `base`
- candidate: `r64`

## Headline
- base: `77/400` successful attempts, `6/20` problems solved
- r64: `1/400` successful attempts, `1/20` problems solved

Delta:
- successful attempts: `-76`
- problems solved: `-5`
- attempts with unknown: `+157`
- total unknown occurrences: `+163`

## Metrics
### base
- attempt pass rate: `19.25%`
- problem pass rate: `30.00%`
- attempts with unknown: `111/400` (`27.75%`)
- unknown among failed attempts: `34.37%`

### r64
- attempt pass rate: `0.25%`
- problem pass rate: `5.00%`
- attempts with unknown: `268/400` (`67.00%`)
- unknown among failed attempts: `67.17%`

## Improved Problems
- none

## Regressed Problems
- `no-hint/MSC-180_26_002`: `19/20 -> 0/20`
- `no-hint/MSC-180_20_001`: `19/20 -> 1/20`
- `no-hint/MSC-180_12_003`: `16/20 -> 0/20`
- `no-hint/MSC-180_14_001`: `14/20 -> 0/20`
- `no-hint/MSC-180_68_002`: `6/20 -> 0/20`
- `no-hint/MSC-180_28_003`: `3/20 -> 0/20`

## Unchanged Problems
- `14` problems unchanged
