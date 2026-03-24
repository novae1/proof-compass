# Prompt Hints

This workflow contains the earlier prompt-hint experiments built around injecting
Mathlib theorem context into Lean proof prompts.

It includes:

- prompt builders used by multiple workflows
- a small set of prompt-hint experiment specs
- local and API runner entry points
- durable output artifacts from those prompt variants

It does not include:

- reusable proving infrastructure; that belongs in `src/`
- fine-tuning data or weights; that belongs in `mathlib_fine_tuning/`
- MSC-180 benchmark runs; those live in `rag_experiments/`

## Layout

- `prompt_config.py`
  Shared prompt builders used both here and by other workflows. It remains at
  the workflow root intentionally for now.
- `data/specs/`
  JSON specs for the main prompt-hints workflow.
- `scripts/run/`
  Canonical runners for local and API-backed prompt-hints experiments.
- `scripts/tools/`
  Prompt inspection helpers.
- `outputs/experiments/`
  General experiment outputs such as `attempts.json`.
- `outputs/tasks/`
  Task-split outputs such as `task1_attempts.json` and `task2_attempts.json`.
- `outputs/proving_variants/`
  Dated runs for the no-hint / theorem-guided / multi-hint prompt variants.

`runners/` and `tools/` remain as compatibility wrapper paths while the rest of
the repo migrates to the canonical `scripts/...` layout.

## Related Workflow

The old `newstuff_suite/` has been promoted into the separate top-level
workflow `theorem_guidance/`. That experiment family was distinct enough to
justify its own folder.
