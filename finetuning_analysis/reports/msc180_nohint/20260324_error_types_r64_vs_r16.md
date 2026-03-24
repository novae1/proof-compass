# Error Type Comparison

## Scope
- baseline: `rag_experiments/outputs/20260313_msc180-v2-nohint_lora_deepseekv2_7b_lean4-15_verified.json`
- candidate: `rag_experiments/outputs/20260323_msc180-v2-nohint_lora_r64_deepseekv2_7b_lean4-15_verified.json`

Labels:
- baseline: `r16`
- candidate: `r64`

## Headline
- r16: `396` failed attempts, `139` non-unknown-only failures
- r64: `399` failed attempts, `133` non-unknown-only failures

Unknown-related split:
- r16: `unknown_only=32`, `unknown_plus_other=225`
- r64: `unknown_only=25`, `unknown_plus_other=241`

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
### r16
- `type_mismatch`: `41`
- `rewrite_failed`: `22`
- `field_error`: `21`
- `synthesis_error`: `13`
- `other`: `11`
- `shape_or_induction_error`: `10`
- `automation_no_progress`: `6`
- `parser_error`: `6`

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
### r16
- `shape_or_induction_error`: `73`
- `rewrite_failed`: `58`
- `goal_state_error`: `44`
- `unsolved_goals`: `36`
- `field_error`: `23`
- `type_mismatch`: `23`
- `automation_no_progress`: `14`
- `parser_error`: `13`

### r64
- `rewrite_failed`: `76`
- `shape_or_induction_error`: `75`
- `goal_state_error`: `49`
- `unsolved_goals`: `49`
- `type_mismatch`: `33`
- `field_error`: `22`
- `automation_no_progress`: `15`
- `synthesis_error`: `14`
