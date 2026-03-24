# Training Runbook

## Prerequisites

Run from the repo root.

```bash
python3.12 -m venv pc
source pc/bin/activate
pip install -r requirements.txt
```

Required local paths:

- `mathlib_fine_tuning/data/processed/deepseek_noncot_tactic_1024_train.jsonl`
- `mathlib_fine_tuning/data/processed/deepseek_noncot_tactic_1024_valid.jsonl`
- `models/deepseek-ai/DeepSeek-Prover-V2-7B`

## Smoke Test

This uses the script's built-in smoke defaults:

- `256` train examples
- `64` valid examples
- `20` max steps

Current trainer behavior:

- training uses ordinary shuffled batches
- it does not group long sequences together by length

This is intentionally simpler and reduces the risk of late OOM failures from
long-sequence buckets, at the cost of somewhat lower throughput from padding.

Recommended starting point for an RTX PRO 6000 Blackwell Workstation:

```bash
python mathlib_fine_tuning/scripts/train_tactic_sft.py \
  --smoke \
  --per-device-train-batch-size 12 \
  --per-device-eval-batch-size 12 \
  --gradient-accumulation-steps 1 \
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_smoke
```

If you want to probe extra headroom on `r=64`, try:

```bash
python mathlib_fine_tuning/scripts/train_tactic_sft.py \
  --smoke \
  --per-device-train-batch-size 14 \
  --per-device-eval-batch-size 14 \
  --gradient-accumulation-steps 1 \
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_smoke
```

If you still hit CUDA OOM, fall back to:

```bash
python mathlib_fine_tuning/scripts/train_tactic_sft.py \
  --smoke \
  --per-device-train-batch-size 8 \
  --per-device-eval-batch-size 8 \
  --gradient-accumulation-steps 1 \
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_smoke
```

Optional allocator setting if CUDA reports fragmentation:

```bash
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
```

## Full Training

Recommended starting point for an RTX PRO 6000 Blackwell Workstation:

```bash
python mathlib_fine_tuning/scripts/train_tactic_sft.py \
  --per-device-train-batch-size 12 \
  --per-device-eval-batch-size 12 \
  --gradient-accumulation-steps 1 \
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_v1
```

If an `r=64` smoke run is clearly comfortable and you want to reduce wall-clock time, try:

```bash
python mathlib_fine_tuning/scripts/train_tactic_sft.py \
  --per-device-train-batch-size 14 \
  --per-device-eval-batch-size 14 \
  --gradient-accumulation-steps 1 \
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_v1
```

For the current `r=64` / `r=128` ablation, prefer keeping both runs on the same configuration:

- `--per-device-train-batch-size 12`
- `--per-device-eval-batch-size 12`
- `--gradient-accumulation-steps 1`

That keeps the comparison clean and should fit comfortably on the PRO 6000.

## Outputs

The script saves only final artifacts, not intermediate checkpoints.

Inside `--output-dir` you should get:

- final LoRA adapter
- `train_config.json`
- `train_metrics.json`
- `eval_metrics.json`

The smoke run also saves its own final adapter and metrics.
It does not affect the full training run as long as the smoke and full runs use different `--output-dir` values.

## Progress

`transformers.Trainer` prints the standard tqdm progress bar during training.
That includes step progress and an ETA-like remaining-time estimate.

## Rank Sweeps

Use the rank wrapper to keep output naming consistent while still allowing
hardware-specific overrides.

`r=64`
```bash
mathlib_fine_tuning/scripts/run_rank_training.sh 64
```

`r=128`
```bash
mathlib_fine_tuning/scripts/run_rank_training.sh 128
```

Recommended commands for the PRO 6000:

`r=64`
```bash
mathlib_fine_tuning/scripts/run_rank_training.sh 64 \
  --per-device-train-batch-size 12 \
  --per-device-eval-batch-size 12 \
  --gradient-accumulation-steps 1
```

`r=128`
```bash
mathlib_fine_tuning/scripts/run_rank_training.sh 128 \
  --per-device-train-batch-size 12 \
  --per-device-eval-batch-size 12 \
  --gradient-accumulation-steps 1
```

If `r=64` has clear headroom, you can test:
```bash
mathlib_fine_tuning/scripts/run_rank_training.sh 64 \
  --per-device-train-batch-size 14 \
  --per-device-eval-batch-size 14 \
  --gradient-accumulation-steps 1
```

The wrapper sets:
- `--lora-r <rank>`
- `--lora-alpha <2 * rank>`
- `--output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_r<rank>`
- standard defaults for the current PRO 6000 runs:
  - `--per-device-train-batch-size 12`
  - `--per-device-eval-batch-size 12`
  - `--gradient-accumulation-steps 1`
  - `--seed 42`

## No-Hint Benchmark Pipeline

Keep the Lean verifier server running in another terminal:

```bash
python3 src/lean/flask_server.py
```

Then run the full no-hint pipeline for a trained rank:
- generation
- verification
- standard MSC-180 summary
- comparison against base
- comparison against `r=16`
- error-type comparison against base
- error-type comparison against `r=16`

`r=64`
```bash
rag_experiments/run_nohint_rank_pipeline.sh 64
```

`r=128`
```bash
rag_experiments/run_nohint_rank_pipeline.sh 128
```

Recommended starting point for inference on the PRO 6000:
```bash
rag_experiments/run_nohint_rank_pipeline.sh 64 \
  --date-prefix 20260323 \
  --attempts-per-problem 20 \
  --micro-batch-size 10
```

Use the same `--micro-batch-size 10` setting for `r=128` first. If generation OOMs or slows down badly due to long outputs, fall back to `5`.

This pipeline writes:
- raw attempts under `rag_experiments/outputs/`
- verified attempts under `rag_experiments/outputs/`
- pairwise summaries under `finetuning_analysis/reports/msc180_nohint/`
