# Experiments

This folder is an archival umbrella for older or side experiment families.
It does not represent one active workflow in the same way as:

- `mathlib_fine_tuning/`
- `rag_experiments/`
- `finetuning_analysis/`
- `prompt_hints/`
- `theorem_guidance/`

## Why This Folder Does Not Follow The Standard Layout

Most workflow folders in this repo now use a standard internal layout such as:

- `README.md`
- `data/`
- `scripts/`
- `outputs/`
- `reports/`
- `runs/`

`experiments/` does not follow that pattern because it is not one workflow. It is a mixed container for:

- benchmark-specific artifact subfolders
- prototype scripts
- parked datasets
- historical one-off experiments

Some of its subfolders are still referenced directly by scripts under `src/`, so reorganizing the whole tree mechanically would create unnecessary breakage.

## Current Contents

### `amc_and_msc/`
A benchmark artifact area for AMC and MSC-style runs.

Contains:
- `filtered_problems.json`: input problem set used by the AMC/MSC benchmark scripts
- dated verified attempt JSONs for different models and Lean versions
- `20260114_count_successes.csv`: a simple summary table over those runs

This subfolder is still used by scripts under `src/benchmarks/amc_and_msc/`.

### `mathd_runs/`
Stored outputs for the mathd variants benchmark.

Contains:
- `checkpoint.json`: raw checkpoint output
- `checkpoint_verified.json`: verified version of the checkpoint output

This subfolder is still used by scripts under `src/benchmarks/mathd_variants/`.

### `aime/`
A small data-only subfolder.

Contains:
- `aime_informal_problems.json`: generated informal AIME problem/proof material

### Root-level scripts
These are older prototype or utility scripts, not one coherent pipeline.

- `aime_proofs.py`: generates informal AIME proof data from miniF2F AIME problems
- `generating_informal_proofs.py`: helper code for natural-language proof generation and summarization via API
- `exploring_lean.py`: one-off Lean Explore API inspection script
- `testing_goedel.py`: prompt and generation prototype for Goedel models

### Root-level data files
- `miniF2F_mathd_variants.json`: historical benchmark data snapshot; the current active processed version lives under `benchmarks/processed/`

### Package marker
- `__init__.py`: exists only to support relative imports among the root-level prototype scripts

## Practical Rule

Use this folder for:
- historical experiments that are still worth keeping
- small prototype code that does not yet deserve its own workflow folder

Do not use this folder for:
- new mainline benchmark workflows
- new training workflows
- new post-hoc analysis pipelines

If one subfamily becomes active again, it should be migrated on its own rather than forcing the entire `experiments/` umbrella into the standard layout.
