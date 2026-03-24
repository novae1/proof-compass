# Error Type Comparison

## Scope
- baseline: `rag_experiments/outputs/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json`
- candidate: `rag_experiments/outputs/20260323_msc180-v2-nohint_lora_r64_deepseekv2_7b_lean4-15_verified.json`

Labels:
- baseline: `base`
- candidate: `r64`

## Headline
- base: `323` failed attempts, `214` non-unknown-only failures
- r64: `399` failed attempts, `133` non-unknown-only failures

Unknown-related split:
- base: `unknown_only=14`, `unknown_plus_other=95`
- r64: `unknown_only=25`, `unknown_plus_other=241`

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

### r64
- `unknown_name`: `354`
- `rewrite_failed`: `127`
- `type_mismatch`: `115`
- `shape_or_induction_error`: `109`
- `unsolved_goals`: `82`
- `field_error`: `81`
- `goal_state_error`: `67`
- `synthesis_error`: `50`

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

### r64
- `type_mismatch`: `30`
- `rewrite_failed`: `19`
- `field_error`: `17`
- `other`: `17`
- `synthesis_error`: `17`
- `automation_no_progress`: `12`
- `shape_or_induction_error`: `7`
- `parser_error`: `6`

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

### r64
- `rewrite_failed`: `76`
- `shape_or_induction_error`: `75`
- `goal_state_error`: `49`
- `unsolved_goals`: `49`
- `type_mismatch`: `33`
- `field_error`: `22`
- `automation_no_progress`: `15`
- `synthesis_error`: `14`
