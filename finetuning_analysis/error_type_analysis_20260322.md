# Error Type Analysis: Base vs LoRA (`2026-03-22`)

## Scope
This report compares verifier error distributions for:
- `rag_experiments/outputs/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/20260313_msc180-v2-nohint_lora_deepseekv2_7b_lean4-15_verified.json`

It complements the hallucination analysis by asking a narrower question:
- did non-unknown error causes also increase,
- or is the regression concentrated in unknown-name failures?

Counting policy:
- only verifier messages with `severity = error` are counted;
- warnings and info messages are excluded;
- errors are bucketed heuristically by the first line of each Lean error message.

Machine-readable artifacts:
- `finetuning_analysis/_error_type_inventory_20260322.json`
- `finetuning_analysis/error_type_analysis_20260322.json`

## Headline Conclusion
The regression is not a broad increase across every Lean error type.

The main shift is still unknown-name failure.

In fact, if we exclude all failed attempts that contain any unknown-name error:
- Base has `214` non-unknown-only failures.
- LoRA has `139` non-unknown-only failures.

So non-unknown-only failures actually go down in absolute count. The LoRA collapse is mostly caused by the jump in unknown-name attempts.

## Overall Failure Totals
Base:
- `77/400` successful attempts
- `323` failed attempts
- `109` failed attempts containing at least one unknown-name error
- `214` failed attempts with no unknown-name error

LoRA:
- `4/400` successful attempts
- `396` failed attempts
- `257` failed attempts containing at least one unknown-name error
- `139` failed attempts with no unknown-name error

This is the key split. The LoRA run adds `148` extra unknown-name failures while simultaneously having fewer non-unknown-only failures.

## All Error Occurrences
Top categories by total error occurrences:

### Base
- `automation_no_progress`: `288`
- `unknown_name`: `192`
- `unsolved_goals`: `147`
- `type_mismatch`: `142`
- `rewrite_failed`: `57`
- `field_error`: `55`

### LoRA
- `unknown_name`: `346`
- `field_error`: `120`
- `type_mismatch`: `104`
- `shape_or_induction_error`: `103`
- `rewrite_failed`: `96`
- `unsolved_goals`: `57`

So some non-unknown categories do rise in raw occurrence count, especially:
- `field_error`
- `rewrite_failed`
- `shape_or_induction_error`

But that raw rise is mostly attached to the much larger pool of unknown-name failures.

## What Happens After Removing Unknown-Name Failures
Looking only at failed attempts with no unknown-name error:

### Base (`214` attempts)
Most common first error categories:
- `automation_no_progress`: `76`
- `type_mismatch`: `34`
- `unsolved_goals`: `34`
- `rewrite_failed`: `21`
- `calc_error`: `15`

### LoRA (`139` attempts)
Most common first error categories:
- `type_mismatch`: `41`
- `rewrite_failed`: `22`
- `field_error`: `21`
- `synthesis_error`: `13`
- `other`: `11`
- `shape_or_induction_error`: `10`

This is the main non-unknown shift:
- Base non-unknown failures are dominated by automation not closing goals.
- LoRA non-unknown failures shift toward structural Lean errors: type mismatches, rewrite failures, field notation failures, and rcases/constructor shape errors.

## Unknown-Name Failures and Their Downstream Effects
Among attempts that already contain an unknown-name error, the most common co-occurring categories are:

### Base
- `automation_no_progress`: `35`
- `unsolved_goals`: `30`
- `shape_or_induction_error`: `18`
- `rewrite_failed`: `17`
- `type_mismatch`: `15`

### LoRA
- `shape_or_induction_error`: `73`
- `rewrite_failed`: `58`
- `goal_state_error`: `44`
- `unsolved_goals`: `36`
- `field_error`: `23`
- `type_mismatch`: `23`

This shows the downstream effect clearly. In the LoRA run, once the model chooses a bad theorem name, the rest of the proof often degrades into:
- rewrite failures,
- rcases/constructor failures,
- and field/goal-state errors.

So these categories did increase, but often as consequences of the initial unknown-name choice rather than independent primary failures.

## Representative Non-Unknown LoRA Failures
The residual non-unknown failure pool is still worth understanding.

### `type_mismatch`
Example: `MSC-180_05_003`, attempt `11`
- the proof tries `Finset.card_congr` with a shape that does not fit the goal;
- Lean reports `function expected at` and `type mismatch`.

### `rewrite_failed`
Example: `MSC-180_05_003`, attempt `17`
- the proof uses `conv_lhs` plus a rewrite that does not match;
- Lean reports `tactic 'rewrite' failed` and then `no goals to be solved`.

### `field_error`
Example: `MSC-180_08_002`, attempt `2`
- the proof tries things like `h₆.symm` and `h₈.ge` on hypotheses that are not fields of a structure in the required way;
- Lean reports `invalid field 'symm'` and `invalid field notation`.

### `shape_or_induction_error`
Example: `MSC-180_08_001`, attempt `11`
- the proof uses an `obtain` pattern on a target that is not an inductive witness of the expected shape;
- Lean reports an `rcases tactic failed` error.

### `synthesis_error`
Example: `MSC-180_05_003`, attempt `3`
- the proof leaves metavariables around `Fintype.card_congr ?_`;
- Lean reports `typeclass instance problem is stuck`.

### `parser_error`
Example: `MSC-180_05_003`, attempt `4`
- the proof contains malformed structure syntax;
- Lean reports `unexpected token ';'; expected '}'`.

These are real regressions in proof construction quality, but they are secondary in scale compared to the unknown-name explosion.

## Practical Interpretation
There are two different stories in the data:

1. **Main regression**
   - Unknown-name failures rise massively.
   - This remains the dominant explanation for the benchmark collapse.

2. **Residual non-unknown shift**
   - Among failures without unknown names, the LoRA model is less dominated by automation failures and more dominated by direct structural Lean errors.
   - That is consistent with a model that tries to write more explicit proof terms/tactic scripts and gets their local structure wrong.

So yes, some other error causes do change, but they do not look like the primary reason performance collapsed.

## Working Conclusion
The answer to the motivating question is:
- **No**, other error causes did not simply all go up together.
- **Yes**, some non-unknown categories such as rewrite, field, and shape errors become more prominent.
- But the benchmark regression is still mainly a name-grounding failure, with those other errors often appearing as downstream fallout once the wrong lemma name is chosen.
