# Output Families

This directory stores generated artifacts produced by the scripts under
`rag_experiments/scripts/`.

Outputs are grouped by benchmark family first and experiment family second.

## MSC-180

- `msc180/manual/`
  Raw per-condition outputs from the older manual hint suite.
- `msc180/manual_merged/`
  Verified merged outputs built from the manual suite.
- `msc180/v2/`
  Combined outputs from the verified-20 MSC-180 v2 suite.
- `msc180/v2_nohint/`
  Raw and verified outputs for the no-hint benchmark runs. This includes base,
  the first LoRA run, and later rank sweeps such as `r64` and `r128`.
- `msc180/theorem_continuations/v3/`
  Continuation probes that cut successful MSC-180 v2 outputs immediately before
  a theorem token and ask the model to continue.
- `msc180/theorem_continuations/v4/`
  Continuation probes that add recovery logic before decoding to stabilize the
  truncation boundary.

## Debug

- `debug/`
  Local debugging artifacts produced by the continuation-fidelity harness.

## Naming

The filenames still use the historical naming convention:

- `<date>_<experiment-family>_<model-suffix>_lean4-15.json`
- verified files add `_verified.json`

The directory structure is now the primary way to tell what broad experiment
family a file belongs to. The filename records the run date and the concrete
variant inside that family.
