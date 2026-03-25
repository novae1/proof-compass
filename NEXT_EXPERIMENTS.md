# Next Experiments

This file lists the current best next experiments in rank order. The aim is to
keep the option set finite and explicit.

## 1. Summarize Theorem-Guidance / Prompt-Hint Results

Hypothesis:
- retrieval-style theorem guidance already contains positive signal that has not yet been synthesized.

Expected signal:
- either it already beats no-hint baselines in useful ways, or it fails in a pattern that clarifies what iterative RAG should do next.

Cost / difficulty:
- low
- mostly analysis and summarization work on existing artifacts

Relevant files:
- `prompt_hints/outputs/README.md`
- `theorem_guidance/outputs/README.md`
- `prompt_hints/outputs/`
- `theorem_guidance/outputs/`

## 2. Define An MSC-180 Theorem-Grounding Benchmark Layer

Hypothesis:
- the missing skill is theorem grounding under weak context, and MSC-180 already contains enough metadata to measure that directly.

Expected signal:
- separates theorem selection from full proof construction, which should make future interventions easier to evaluate.

Cost / difficulty:
- low to medium
- benchmark design and script work, no GPU required

Relevant files:
- `rag_experiments/data/benchmarks/msc180/MSC-180.json`
- `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`

## 3. Build A Small Contamination-Safe Theorem-Grounding Dataset

Hypothesis:
- a targeted dataset for theorem shortlist prediction and hinted continuation will transfer better than generic standalone theorem-block SFT.

Expected signal:
- either theorem-name grounding improves directly, or we falsify the targeted-objective idea quickly with a small run.

Cost / difficulty:
- medium
- requires dataset design, holdout policy, and likely a new trainer/input format

Relevant files:
- `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`
- `mathlib_fine_tuning/scripts/build_tactic_sft_dataset.py`

## 4. Try A Retrieval-First Baseline Before Another Fine-Tune

Hypothesis:
- retrieval or iterative theorem guidance will help more than another blind LoRA sweep.

Expected signal:
- positive gains here would justify prioritizing RAG / theorem-guidance methods in parallel with fine-tuning.

Cost / difficulty:
- medium
- likely new prompt/run scripts, but no new training required initially

Relevant files:
- `prompt_hints/README.md`
- `theorem_guidance/README.md`
- `rag_experiments/README.md`
- `continuation_recovery/reports/FINDINGS.md`

## 5. Run The MiniF2F / mathd Regression Check

Hypothesis:
- the LoRA regressions may extend beyond MSC-180 no-hint.

Expected signal:
- tells us whether the current failure is narrowly benchmark-specific or a broader capability drop.

Cost / difficulty:
- medium
- new evaluation plumbing needed for the V2-style models and prompts

Relevant files:
- `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`
- `src/benchmarks/mathd_variants/`

## 6. Only Then: Run The Smallest New Training Experiment

Hypothesis:
- a small retrieval-aware or theorem-grounding-aware fine-tune can recover some transfer without repeating the earlier collapse.

Expected signal:
- a quick test of whether the new objective changes theorem-name behavior in the right direction.

Cost / difficulty:
- high relative to the CPU-only work above
- should wait until the benchmark and dataset designs are explicit

Relevant files:
- `mathlib_fine_tuning/README.md`
- `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`
