# Empirical Evidence

This file is a concise index of the strongest empirical results in the repo.
Each item gives the claim, one key metric, and the canonical source.

## Fine-Tuning Regressions

- Fine-tuning on the standalone Mathlib theorem-block dataset hurt MSC-180 v2 no-hint badly.
  Key metric: base `77/400` attempts and `6/20` solved problems vs LoRA `4/400` and `2/20`.
  Source: `finetuning_analysis/reports/msc180_nohint/msc180_nohint_base_vs_lora_20260313.md`

- The main regression is theorem-name grounding, not a small drop in overall quality.
  Key metric: attempts with `unknown` rose from `111/400` to `258/400` in the base vs LoRA comparison.
  Source: `finetuning_analysis/reports/msc180_nohint/msc180_nohint_base_vs_lora_20260313.md`

- Increasing LoRA rank did not fix the problem.
  Key metric: `r=16` `4/400`, `r=64` `1/400`, `r=128` `2/400` on MSC-180 v2 no-hint.
  Source: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`

- Higher-rank LoRA runs produced more unresolved-name burden, not less.
  Key metric: unknown occurrences = base `196`, `r=16` `347`, `r=64` `357`, `r=128` `448`.
  Source: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`

## Nature Of The Failure

- The rank-sweep failure is semantic, not textual.
  Key metric: all three LoRA runs kept about `20/20` unique parsed proofs per problem and theorem-name match rate `1.0`.
  Source: `finetuning_analysis/reports/multi_rank/multi_rank_output_structure_analysis_20260324.md`

- The hallucinations are often theorem-adjacent rather than random garbage.
  Key metric: each LoRA run produced many exact-short, normalized, or near matches to real Mathlib names, but still a large `no_convincing_theorem_match` bucket.
  Source: `finetuning_analysis/reports/multi_rank/multi_rank_hallucination_analysis_20260324.md`

- Higher rank changed the hallucinations more than it reduced them.
  Key metric: Jaccard overlap of distinct unknown-name sets stayed very low: `0.0378` (`r16` vs `r64`), `0.0362` (`r16` vs `r128`), `0.0478` (`r64` vs `r128`).
  Source: `finetuning_analysis/reports/multi_rank/multi_rank_hallucination_analysis_20260324.md`

## Benchmark And Contamination Guardrails

- There is no exact normalized statement overlap across the benchmark pairs checked so far.
  Key metric: `0` exact overlaps for MSC-180 vs miniF2F valid, MSC-180 v2 A vs mathd-valid, MSC-180 v2 A vs AMC-valid, and miniF2F valid vs miniF2F test.
  Source: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`

- MSC-180 already contains theorem-link metadata and is suitable for theorem-grounding evaluation.
  Key metric: `178/180` MSC-180 problems have non-empty `related_theorems`.
  Source: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`

- The source-corpus contamination audit is still incomplete.
  Key metric: `mathlib_fine_tuning/data/raw/mathlib_standalone_theorems_validated.jsonl` is not present locally, so exact source-corpus-vs-benchmark overlap has not yet been recomputed in the current repo state.
  Source: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`

## Continuation Recovery

- Raw-text continuation recovery is viable under the pinned environment.
  Key metric: `adaptive_lexical_first` reached prefix/oracle continuation recovery `0.940` on the greedy medium sweep.
  Source: `continuation_recovery/reports/FINDINGS.md`

- The continuation-recovery path substantially reduced residual theorem-name hallucination evidence in the v4 rerun.
  Key metric: on the real v4 rerun, hallucinated `57/760`, but those `57` attempts reduce to `9` slots and `3` unique first identifiers, mostly boundary fragments rather than broad theorem-name failures.
  Source: `continuation_recovery/reports/FINDINGS.md`

## Retrieval / Theorem-Guidance Workflows

- The repo already contains multiple theorem-guided experiment families that are structurally ready for follow-up analysis.
  Key metric: durable output families exist under `prompt_hints/outputs/proving_variants/` and `theorem_guidance/outputs/`.
  Source: `prompt_hints/README.md`, `prompt_hints/outputs/README.md`, `theorem_guidance/README.md`, `theorem_guidance/outputs/README.md`

- There is currently no single canonical aggregate report for the theorem-guidance / prompt-hint results.
  Key metric: the workflows have durable outputs and specs, but no top-level synthesis analogous to the MSC-180 no-hint LoRA analyses.
  Source: `prompt_hints/README.md`, `theorem_guidance/README.md`
