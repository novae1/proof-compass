# Mathlib Fine-Tuning

This folder contains the training workflow for the tactic-only Mathlib SFT runs.

Its role is to own:

- the source corpus used to build the SFT dataset
- the processed train/valid files used for training
- the training entry points and wrappers
- the saved LoRA run artifacts

This is not the folder for benchmark generations or benchmark-side analysis.
Those live elsewhere:

- benchmark outputs in `rag_experiments/outputs/`
- derived evaluation analysis in `finetuning_analysis/`

## Layout

- `TRAINING_RUNBOOK.md`
  - operational instructions for training and evaluation

- `data/raw/`
  - source corpus for dataset construction

- `data/processed/`
  - processed train/valid JSONL files and validation summaries

- `scripts/`
  - training and dataset entry points owned by this workflow

- `runs/`
  - saved LoRA training artifacts and metrics

## Conventions

- `runs/` is the canonical home for training outputs.
- `data/processed/` is the canonical home for retained SFT datasets.
- `scripts/` holds the canonical workflow entry points.

## Compatibility

Legacy root-level entry points are still present:

- `mathlib_fine_tuning/build_tactic_sft_dataset.py`
- `mathlib_fine_tuning/inspect_tactic_sft_dataset.py`
- `mathlib_fine_tuning/train_tactic_sft.py`
- `mathlib_fine_tuning/validate_tactic_sft_dataset.py`
- `mathlib_fine_tuning/run_rank_training.sh`

These are thin wrappers that forward into `scripts/`.
They should remain until external callers and older notes stop depending on them.
