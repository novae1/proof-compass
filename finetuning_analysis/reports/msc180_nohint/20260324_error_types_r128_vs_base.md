# Error Type Comparison

## Scope
- baseline: `rag_experiments/outputs/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json`
- candidate: `rag_experiments/outputs/20260323_msc180-v2-nohint_lora_r128_deepseekv2_7b_lean4-15_verified.json`

Labels:
- baseline: `base`
- candidate: `r128`

## Headline
- base: `323` failed attempts, `214` non-unknown-only failures
- r128: `398` failed attempts, `121` non-unknown-only failures

Unknown-related split:
- base: `unknown_only=14`, `unknown_plus_other=95`
- r128: `unknown_only=39`, `unknown_plus_other=238`

## Top Error Occurrences
### base
- `automation_no_progress`: `288`
- `unknown_name`: `192`
- `unsolved_goals`: `147`
- `type_mismatch`: `142`
- `rewrite_failed`: `57`
- `field_error`: `55`
- `other`: `36`
- `synthesis_error`: `35`

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
### base
- `automation_no_progress`: `76`
- `type_mismatch`: `34`
- `unsolved_goals`: `34`
- `rewrite_failed`: `21`
- `calc_error`: `15`
- `other`: `10`
- `field_error`: `9`
- `synthesis_error`: `8`

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
### base
- `automation_no_progress`: `35`
- `unsolved_goals`: `30`
- `shape_or_induction_error`: `18`
- `rewrite_failed`: `17`
- `type_mismatch`: `15`
- `goal_state_error`: `13`
- `field_error`: `6`
- `other`: `6`

### r128
- `shape_or_induction_error`: `79`
- `rewrite_failed`: `55`
- `type_mismatch`: `52`
- `unsolved_goals`: `49`
- `goal_state_error`: `47`
- `other`: `25`
- `field_error`: `22`
- `automation_no_progress`: `21`
