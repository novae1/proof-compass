# Error Type Comparison

## Scope
- baseline: `rag_experiments/outputs/20260313_msc180-v2-nohint_lora_deepseekv2_7b_lean4-15_verified.json`
- candidate: `rag_experiments/outputs/20260323_msc180-v2-nohint_lora_r128_deepseekv2_7b_lean4-15_verified.json`

Labels:
- baseline: `r16`
- candidate: `r128`

## Headline
- r16: `396` failed attempts, `139` non-unknown-only failures
- r128: `398` failed attempts, `121` non-unknown-only failures

Unknown-related split:
- r16: `unknown_only=32`, `unknown_plus_other=225`
- r128: `unknown_only=39`, `unknown_plus_other=238`

## Top Error Occurrences
### r16
- `unknown_name`: `346`
- `field_error`: `120`
- `type_mismatch`: `104`
- `shape_or_induction_error`: `103`
- `rewrite_failed`: `96`
- `unsolved_goals`: `57`
- `goal_state_error`: `55`
- `synthesis_error`: `31`

### r128
- `unknown_name`: `440`
- `type_mismatch`: `135`
- `field_error`: `130`
- `rewrite_failed`: `121`
- `shape_or_induction_error`: `101`
- `unsolved_goals`: `80`
- `goal_state_error`: `62`
- `other`: `56`

## First Error Category Among Non-Unknown-Only Failures
### r16
- `type_mismatch`: `41`
- `rewrite_failed`: `22`
- `field_error`: `21`
- `synthesis_error`: `13`
- `other`: `11`
- `shape_or_induction_error`: `10`
- `automation_no_progress`: `6`
- `parser_error`: `6`

### r128
- `rewrite_failed`: `29`
- `type_mismatch`: `26`
- `field_error`: `18`
- `other`: `12`
- `parser_error`: `11`
- `synthesis_error`: `11`
- `shape_or_induction_error`: `5`
- `automation_no_progress`: `4`

## Categories Co-Occurring With Unknown Names
### r16
- `shape_or_induction_error`: `73`
- `rewrite_failed`: `58`
- `goal_state_error`: `44`
- `unsolved_goals`: `36`
- `field_error`: `23`
- `type_mismatch`: `23`
- `automation_no_progress`: `14`
- `parser_error`: `13`

### r128
- `shape_or_induction_error`: `79`
- `rewrite_failed`: `55`
- `type_mismatch`: `52`
- `unsolved_goals`: `49`
- `goal_state_error`: `47`
- `other`: `25`
- `field_error`: `22`
- `automation_no_progress`: `21`
