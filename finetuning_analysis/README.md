# Finetuning Analysis

This folder holds derived analysis for fine-tuning experiments and their downstream benchmark results.

Its role is to sit between:

- training artifacts in `mathlib_fine_tuning/`
- benchmark outputs in `rag_experiments/outputs/`

and record what those runs mean.

This is not the place for raw model generations or LoRA weights. It is the place for:

- comparisons between runs
- error-type breakdowns
- hallucination studies
- higher-level postmortem notes

The goal is to keep the reasoning around fine-tuning outcomes in one place so later experiment cycles can build on prior conclusions instead of re-deriving them from raw JSON outputs.

## Layout

- `scripts/analyze/`
  - analysis entry points owned by this workflow
  - these scripts read benchmark outputs and produce summaries or reports

- `reports/msc180_nohint/`
  - reports tied to MSC-180 no-hint evaluation
  - includes both human-readable Markdown and machine-readable JSON summaries

- `reports/multi_rank/`
  - analyses that compare multiple LoRA ranks or examine cross-run structural behavior

- `reports/reviews/`
  - longer-form interpretive documents and postmortems

- `data/inventories/`
  - supporting extracted inventories used to build reports
  - these are backing artifacts rather than the main analysis deliverables

## What Belongs Here

Good fits for this folder:

- benchmark comparison summaries
- failure analyses
- hallucination inventories
- structured report JSON that mirrors a Markdown report
- review notes that explain what likely happened and why

Bad fits for this folder:

- raw generation outputs
- verified attempt JSON produced directly by benchmark runs
- training checkpoints or adapter weights
- general-purpose reusable code that belongs in `src/`

## Naming Conventions

Most files are date-prefixed so the analysis remains tied to a specific experiment wave.

Typical patterns:

- `<date>_msc180_nohint_<candidate>_vs_<baseline>.md`
- `<date>_msc180_nohint_<candidate>_vs_<baseline>.json`
- `<date>_error_types_<candidate>_vs_<baseline>.md`
- `<date>_error_types_<candidate>_vs_<baseline>.json`

Conventions:

- Markdown files are the primary human-readable reports.
- JSON files next to those reports are machine-readable summaries of the same analysis.
- Files under `data/inventories/` are support artifacts and often use more descriptive names rather than report-style naming.

## Relationship To Other Folders

- `mathlib_fine_tuning/`
  - owns training code, processed SFT data, and run artifacts

- `rag_experiments/outputs/`
  - owns raw and verified benchmark outputs

- `finetuning_analysis/`
  - owns interpretation, comparison, and diagnosis derived from those outputs

This separation is intentional: if a file is the direct product of a run, it should usually live elsewhere; if it explains the meaning of that run, it belongs here.

## Compatibility

Some callers outside `finetuning_analysis/` still reference the legacy wrapper paths:

- `finetuning_analysis/compare_nohint_runs.py`
- `finetuning_analysis/analyze_error_types.py`

Those files are thin compatibility entry points that forward into `scripts/analyze/`.
They should remain until external references are updated.
