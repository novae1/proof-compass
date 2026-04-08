# Transfer Subset 5% Eval100: REPL Verification And Syntactic Similarity

This note analyzes the two held-out `100`-example inference files:

- `mathlib_fine_tuning/analysis/transfer_subset_5pct_eval100/base_inference.json`
- `mathlib_fine_tuning/analysis/transfer_subset_5pct_eval100/lora_inference.json`

It supplements the already-committed string-match and loss metrics with:

- Lean REPL verification
- syntactic-nearness metrics based on normalized edit similarity

## Existing committed metrics

From the inference and eval artifacts:

| model | eval loss | exact match | normalized exact match |
|---|---:|---:|---:|
| base | `0.6925` | `0/100` | `0/100` |
| LoRA | `0.3074` | `4/100` | `4/100` |

Relevant files:

- `mathlib_fine_tuning/analysis/transfer_subset_5pct_eval100/base_eval.json`
- `mathlib_fine_tuning/analysis/transfer_subset_5pct_eval100/lora_eval.json`
- `mathlib_fine_tuning/analysis/transfer_subset_5pct_eval100/base_inference.json`
- `mathlib_fine_tuning/analysis/transfer_subset_5pct_eval100/lora_inference.json`

## REPL verification setup

The inference files do not contain full standalone Lean files. Each example stores:

- a prompt with the header/context and a theorem stub ending in `sorry`
- a generated theorem/lemma completion

The prompt is missing the original trailing `end ...` lines, so direct prompt+completion verification is unsafe.

Instead, for each example:

1. match the prompt back to the original row in `mathlib_fine_tuning/data/raw/mathlib_theorems_validated_tactic.jsonl`
2. recover the full original `standalone_lean`
3. replace the original theorem body with the generated theorem body
4. strip leading `import ...` lines to match the current REPL workflow
5. verify with the local Flask-backed Lean REPL

The reconstruction was manually spot-checked before running bulk verification.

The exact-match LoRA examples at indices `41`, `54`, `66`, and `72` were inspected. For indices `54` and `72`, the reconstructed file exactly matches the original source file and verifies. For indices `41` and `66`, the reconstructed file also exactly matches the original source file, but both fail under the current stripped-import REPL path with `expected token`, so those two failures are not reconstruction bugs.

Generated verification artifacts:

- `mathlib_fine_tuning/analysis/transfer_subset_5pct_eval100/base_repl_verification.json`
- `mathlib_fine_tuning/analysis/transfer_subset_5pct_eval100/lora_repl_verification.json`

## REPL verification results

| model | REPL verified | verified rate | exact-and-verified |
|---|---:|---:|---:|
| base | `32/100` | `0.32` | `0/100` |
| LoRA | `13/100` | `0.13` | `2/100` |

This reverses the story suggested by the string-match metrics:

- the LoRA model is closer to the gold strings
- but the base model produces more Lean-verifiable proofs on this held-out slice

## Syntactic-nearness metrics

To measure "close syntactic match" more meaningfully than exact equality, normalized Levenshtein similarity was computed:

- once on the full completion
- once on the proof body only, after splitting at the outer `:=`

Important note:

- `header_exact_count = 100/100` for both models, because both models generally copy the theorem statement/header from the prompt
- so the proof-body-only metrics are more informative

### Summary

| metric | base | LoRA |
|---|---:|---:|
| exact match | `0/100` | `4/100` |
| normalized exact match | `0/100` | `4/100` |
| header exact | `100/100` | `100/100` |
| body exact | `0/100` | `4/100` |
| mean full similarity | `0.490` | `0.612` |
| median full similarity | `0.480` | `0.643` |
| mean body similarity | `0.235` | `0.341` |
| median body similarity | `0.212` | `0.281` |

### Threshold counts: full completion similarity

| threshold | base | LoRA |
|---|---:|---:|
| `>= 0.95` | `1` | `6` |
| `>= 0.90` | `1` | `9` |
| `>= 0.75` | `9` | `32` |
| `>= 0.50` | `48` | `69` |

### Threshold counts: proof-body similarity

| threshold | base | LoRA |
|---|---:|---:|
| `>= 0.95` | `0` | `4` |
| `>= 0.90` | `1` | `4` |
| `>= 0.75` | `1` | `5` |
| `>= 0.50` | `5` | `19` |

## Interpretation

The held-out transfer experiment now has a split outcome:

- **string similarity favors LoRA**
- **formal verification favors the base model**

More concretely:

- the LoRA model produces completions that are often much closer to the gold proof text
- but those completions more often fail Lean checking, especially on:
  - rewrite failures
  - unsolved goals
  - typeclass / synthesis failures
  - parser-level issues in a few cases

The base model is less similar to the gold proofs but still verifies more often.

## Main conclusion

On this `100`-example held-out slice:

- the LoRA adapter clearly improves syntactic closeness to the target proofs
- but that does **not** translate into better Lean-verifiable performance
- under REPL verification, the base model is stronger: `32/100` vs `13/100`

So for this experiment, exact or near-exact string metrics are not reliable proxies for theorem-proving quality.
