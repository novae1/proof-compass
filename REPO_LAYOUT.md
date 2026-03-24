# Repo Layout

This document defines the target directory layout for non-core workflows in this repository.

It is a layout target, not a claim that every folder already follows it perfectly.
Some scripts still reference legacy paths, and some helper modules still live at workflow root.

## Core Folders

These are the stable repo foundations and should remain mostly unchanged:

- `src/`
  - reusable library code
- `benchmarks/`
  - benchmark source assets and processed benchmark datasets
- `scripts/`
  - repo-wide utility scripts
- `models/`
  - locally downloaded model snapshots

## Standard Workflow Layout

For workflow-specific directories, the default structure should be:

```text
<workflow>/
  README.md
  data/
  scripts/
  outputs/
  reports/
  runs/
```

Not every workflow needs every subfolder, but this is the default shape.

## Folder Meanings

- `README.md`
  - short workflow-specific explanation
  - should describe what the workflow does, what its subfolders mean, and where new artifacts should go

- `data/`
  - inputs or reference artifacts owned by the workflow
  - examples:
    - specs
    - theorem indexes
    - processed datasets
    - curated problem subsets
  - not for model generations
  - not for training checkpoints

- `scripts/`
  - workflow-specific entry points
  - examples:
    - run scripts
    - analyzers
    - conversion tools
  - reusable shared code should live in `src/`, not here

- `outputs/`
  - direct outputs of generation or verification runs
  - examples:
    - raw generations
    - verified generations
    - continuation-probe outputs

- `reports/`
  - derived analysis artifacts
  - examples:
    - Markdown summaries
    - machine-readable comparison JSONs
    - failure reviews
  - if a file exists to summarize or interpret outputs, it belongs here

- `runs/`
  - training-run artifacts
  - examples:
    - adapter weights
    - training metrics
    - eval metrics
    - run configs

## Recurring Subfolders

These are common nested patterns that should be reused when helpful.

### `data/specs/`

Use for formal experiment specs or benchmark slice definitions.

Examples:
- MSC-180 subset specs
- prompt experiment specs

### `data/indexes/`

Use for lookup tables and reference indices.

Examples:
- theorem-name indexes
- declaration lookup tables

### `data/processed/`

Use for processed datasets derived from a raw source corpus.

Examples:
- train/valid JSONL files
- processed benchmark JSON files

### `outputs/<family>/`

Use when one workflow contains multiple experiment families.

Examples:
- `outputs/msc180_v2/`
- `outputs/msc180_v2_nohint/`
- `outputs/continuations/`

The same experiment-family subtree should usually be mirrored under `reports/`.

### `reports/<family>/`

Use for analyses corresponding to an experiment family under `outputs/<family>/`.

This mirroring should happen at the family level, not necessarily as a strict one-file-to-one-file pairing.

Good:
- `outputs/msc180_v2_nohint/...`
- `reports/msc180_v2_nohint/...`

Not required:
- every raw output file having exactly one matching report file

### `scripts/run/`

Use for scripts that produce outputs or training runs.

### `scripts/analyze/`

Use for scripts that summarize or compare outputs.

### `scripts/verify/`

Use for scripts that perform Lean checking or other validation.

### `scripts/tools/`

Use for maintenance and conversion helpers.

Examples:
- exporting attempts to Lean files
- merging output JSONs
- prompt inspection helpers

## Current Exceptions

These are allowed temporarily and should not block layout cleanup.

- Small workflow-local helper modules may remain at workflow root for now.
  - Example: prompt-specific helper modules that may eventually move into `src/`

- Existing scripts may still point at legacy paths.
  - Path updates should be handled in a separate migration step after the target layout is agreed on.

- `__init__.py` and `__pycache__/` do not define architecture and should be ignored when evaluating layout quality.

## Migration Rule

Do not move files just to match the layout unless the corresponding scripts and references are updated in a controlled pass.

The intended sequence is:

1. define target layout
2. identify exceptions and path dependencies
3. move files by workflow
4. update scripts and docs
5. verify end-to-end commands still work
