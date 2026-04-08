# Mathlib Fine-Tuning Analysis

This directory contains lightweight analysis artifacts copied out of ignored
`mathlib_fine_tuning/runs/` directories so they can be committed without
including LoRA weights or trainer state.

## Memorization Test

Experiment:
- Model: `deepseek-ai/DeepSeek-Prover-V2-7B`
- Train set: 100 tactic-style Mathlib examples
- Eval set: the same 100 examples
- LoRA: `r=16`, `alpha=32`, dropout `0.05`
- Training schedule: 30 total epochs

Key results:
- Final eval loss: `0.00014271335385274142`
- Greedy pass@1 exact match on the 100 train examples: `100 / 100`
- Greedy pass@1 normalized match on the 100 train examples: `100 / 100`

Artifacts:
- `memorization_100/lora_eval_metrics.json`
- `memorization_100/lora_inference.json`

## Held-Out Transfer Test

Experiment:
- Train set: 2,789 examples (5% of tactic-style Mathlib train split)
- Eval set: 100 held-out examples from the tactic-style Mathlib valid split
- LoRA: `r=16`, `alpha=32`, dropout `0.05`
- Training schedule: 2 epochs

Key results:
- Base eval loss before training: `0.6925109028816223`
- Fine-tuned eval loss after training: `0.3073683977127075`
- Base greedy pass@1 exact match on held-out eval: `0 / 100`
- Fine-tuned greedy pass@1 exact match on held-out eval: `4 / 100`

Artifacts:
- `transfer_subset_5pct_eval100/base_eval.json`
- `transfer_subset_5pct_eval100/lora_eval.json`
- `transfer_subset_5pct_eval100/base_inference.json`
- `transfer_subset_5pct_eval100/lora_inference.json`
- `transfer_subset_5pct_eval100/base_repl_verification.json`
- `transfer_subset_5pct_eval100/lora_repl_verification.json`
- `20260408_transfer_subset_5pct_eval100_repl_and_similarity_analysis.md`

Post-hoc note:
- Lean REPL verification on reconstructed standalone files gives a different result from the string-match analysis.
- On this held-out `100`-example slice, the base model verifies more often than the LoRA model: `32/100` vs `13/100`.
- The LoRA model is still syntactically closer to the gold proofs on normalized edit-similarity metrics.

Notes:
- No model weights are included here.
- We intentionally did not copy ignored checkpoint directories or optimizer
  state.
- We also did not save a base-model inference run for the memorization test,
  because that was not needed to answer the memorization question.
