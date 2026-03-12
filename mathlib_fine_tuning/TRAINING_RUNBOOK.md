# Training Runbook

## Prerequisites

Run from the repo root.

```bash
python3.12 -m venv pc
source pc/bin/activate
pip install -r requirements.txt
```

Required local paths:

- `mathlib_fine_tuning/processed/deepseek_noncot_tactic_1024_train.jsonl`
- `mathlib_fine_tuning/processed/deepseek_noncot_tactic_1024_valid.jsonl`
- `models/deepseek-ai/DeepSeek-Prover-V2-7B`

## Smoke Test

This uses the script's built-in smoke defaults:

- `256` train examples
- `64` valid examples
- `20` max steps

```bash
python mathlib_fine_tuning/train_tactic_sft.py \
  --smoke \
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_smoke
```

If VRAM is tighter, reduce only batch size:

```bash
python mathlib_fine_tuning/train_tactic_sft.py \
  --smoke \
  --per-device-train-batch-size 1 \
  --per-device-eval-batch-size 1 \
  --gradient-accumulation-steps 8 \
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_smoke
```

## Full Training

```bash
python mathlib_fine_tuning/train_tactic_sft.py \
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_v1
```

If you want to set batch size explicitly:

```bash
python mathlib_fine_tuning/train_tactic_sft.py \
  --per-device-train-batch-size 2 \
  --per-device-eval-batch-size 2 \
  --gradient-accumulation-steps 8 \
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_v1
```

## Outputs

The script saves only final artifacts, not intermediate checkpoints.

Inside `--output-dir` you should get:

- final LoRA adapter
- `train_config.json`
- `train_metrics.json`
- `eval_metrics.json`

## Progress

`transformers.Trainer` prints the standard tqdm progress bar during training.
That includes step progress and an ETA-like remaining-time estimate.
