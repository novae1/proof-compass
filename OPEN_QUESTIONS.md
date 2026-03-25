# Open Questions

This file tracks live research questions only. Resolved questions should move to
`EMPIRICAL_EVIDENCE.md` or the relevant canonical report.

## Highest Priority

1. Can theorem grounding be improved without repeating the standalone-proof SFT mistake?
   Why it matters: the current evidence says objective mismatch, not LoRA rank, is the main failure.
   Main sources: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`, `finetuning_analysis/reports/multi_rank/multi_rank_hallucination_analysis_20260324.md`

2. How much can retrieval or theorem guidance recover on MSC-180 before any new fine-tuning?
   Why it matters: theorem grounding looks like the missing skill, and retrieval may attack that directly.
   Main sources: `prompt_hints/README.md`, `theorem_guidance/README.md`, `continuation_recovery/reports/FINDINGS.md`

3. What is the smallest contamination-safe dataset that teaches the right skill?
   Why it matters: the next dataset should target theorem selection/use under weak context, not generic theorem-block imitation.
   Main sources: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`

## Important But Secondary

4. Did the LoRA runs also degrade broader theorem proving outside MSC-180 no-hint?
   Why it matters: a miniF2F/mathd regression check would tell us whether the failure is narrow or general.
   Main sources: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`

5. What secondary benchmark family should complement MSC-180?
   Why it matters: MSC-180 is the right place to debug the current failure, but it should not be the only benchmark family.
   Current candidates: ProofNet or a small self-contained Mathlib domain slice.
   Main sources: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`

6. How much of the continuation-recovery machinery should be reused in future retrieval or iterative-RAG pipelines?
   Why it matters: the continuation work already solved a real boundary problem and may transfer to iterative proof construction.
   Main sources: `continuation_recovery/reports/FINDINGS.md`, `continuation_recovery/reports/PROGRESS.md`

## Evidence Gaps

7. What do the theorem-guidance / prompt-hint runs actually achieve in aggregate?
   Why it matters: those workflows may already contain useful positive signal, but they are not yet summarized in one canonical report.
   Main sources: `prompt_hints/outputs/README.md`, `theorem_guidance/outputs/README.md`

8. What exact source-corpus overlap exists between the original SFT source JSONL and the current evaluation benchmarks?
   Why it matters: this is a guardrail for future dataset design, even if it is probably not the main explanation for the current failure.
   Main sources: `finetuning_analysis/reports/reviews/20260325_finetuning_postmortem_and_next_steps.md`
