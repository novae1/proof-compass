# RAG Experiments

This folder owns benchmark-oriented experiment workflows built on top of the
shared code in `src/`.

It contains:

- benchmark input data used by these experiments
- experiment specs derived from those benchmarks
- runnable scripts for generation, verification-oriented pipelines, and analysis
- generated benchmark outputs
- a small amount of workflow-specific documentation

It does not contain:

- reusable library code; that belongs in `src/`
- fine-tuning datasets or adapter weights; those belong in `mathlib_fine_tuning/`
- post-hoc benchmark comparison reports; those belong in `finetuning_analysis/`

## Layout

- `data/benchmarks/`
  Benchmark source assets used to build or inspect experiment specs. For now the
  main benchmark here is MSC-180.
- `data/indexes/`
  Stable reference indexes used by the experiment scripts, such as theorem-name
  indexes for continuation probes.
- `data/specs/`
  Experiment-specific JSON specs consumed by the runners.
- `scripts/run/`
  Canonical entry points that generate new outputs.
- `scripts/analyze/`
  Canonical analyzers for benchmark outputs and continuation probes.
- `scripts/tools/`
  Helpers that build specs, print prompts, merge outputs, or run local debugging
  harnesses.
- `outputs/`
  Durable generated artifacts. Files are grouped first by benchmark family and
  then by experiment family.

Temporary root-level wrappers remain in place only to preserve older command
paths while the rest of the repo is migrated.

## MSC-180 Families

The current file naming already encodes several experiment families. The
subfolders make that structure explicit:

- `outputs/msc180/manual/`
  Raw per-condition runs from the earlier manual hint suite.
- `outputs/msc180/manual_merged/`
  Verified merged outputs from the manual suite.
- `outputs/msc180/v2/`
  The later unified A/B/C benchmark suite over the verified-20 MSC-180 slice.
- `outputs/msc180/v2_nohint/`
  The no-hint variant used for base vs LoRA comparisons, including rank sweeps.
- `outputs/msc180/theorem_continuations/v3/`
  The first theorem-continuation probe family, built by cutting successful v2
  outputs immediately before a theorem occurrence.
- `outputs/msc180/theorem_continuations/v4/`
  The continuation family with recovery logic around tokenization boundaries.

The labels `v2`, `v3`, and `v4` are historical experiment names, not model
versions.

## Notes

- `CONTINUATION_ENV.md` documents the environment expectations for continuation
  experiments.
- `msc180_verified20_v2_plan.md` is a historical planning document for the
  verified-20 v2 benchmark design.
- `outputs/README.md` explains what the current output families mean.
