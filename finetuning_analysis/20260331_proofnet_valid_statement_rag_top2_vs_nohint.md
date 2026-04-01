# Verified Run Comparison

## Scope
- baseline: `rag_experiments/outputs/proofnet/valid/20260331_proofnet-valid_nohint_base_deepseekv2_7b_lean4-15_verified.json`
- candidate: `rag_experiments/outputs/proofnet/valid/20260331_proofnet-valid_statement-rag-top2_base_deepseekv2_7b_lean4-15_verified.json`

Labels:
- baseline: `nohint`
- candidate: `statement_rag_top2`

## Headline
- nohint: `155/740` successful attempts, `47/185` problems solved
- statement_rag_top2: `156/740` successful attempts, `47/185` problems solved

Delta:
- successful attempts: `+1`
- problems solved: `+0`
- attempts with unknown: `-14`
- total unknown occurrences: `-24`

## Metrics
### nohint
- attempt pass rate: `20.95%`
- problem pass rate: `25.41%`
- attempts with unknown: `122/740` (`16.49%`)
- unknown among failed attempts: `20.85%`

### statement_rag_top2
- attempt pass rate: `21.08%`
- problem pass rate: `25.41%`
- attempts with unknown: `108/740` (`14.59%`)
- unknown among failed attempts: `18.49%`

## Improved Problems
- `exercise_1_11a`: `0/4 -> 4/4`
- `exercise_10_7_10`: `1/4 -> 4/4`
- `exercise_13_1`: `0/4 -> 2/4`
- `exercise_2_24`: `0/4 -> 2/4`
- `exercise_11_4_6b`: `1/4 -> 2/4`
- `exercise_16_4`: `3/4 -> 4/4`
- `exercise_1_1_22a`: `3/4 -> 4/4`
- `exercise_1_1_25`: `3/4 -> 4/4`
- `exercise_2_9_2`: `0/4 -> 1/4`
- `exercise_3_5`: `2/4 -> 3/4`
- `exercise_4_5_25`: `0/4 -> 1/4`
- `exercise_7_1_11`: `2/4 -> 3/4`

## Regressed Problems
- `exercise_3_1_22b`: `4/4 -> 0/4`
- `exercise_4_4a`: `4/4 -> 1/4`
- `exercise_1_13`: `3/4 -> 1/4`
- `exercise_10_4_6`: `3/4 -> 2/4`
- `exercise_11_4_8`: `1/4 -> 0/4`
- `exercise_2_1_5`: `4/4 -> 3/4`
- `exercise_2_21`: `4/4 -> 3/4`
- `exercise_2_5_30`: `1/4 -> 0/4`
- `exercise_3_5_6`: `1/4 -> 0/4`
- `exercise_4_4_6a`: `4/4 -> 3/4`
- `exercise_4_5_16__2`: `4/4 -> 3/4`
- `exercise_9_4_2b`: `1/4 -> 0/4`

## Unchanged Problems
- `161` problems unchanged
