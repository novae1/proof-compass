#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  mathlib_fine_tuning/run_rank_training.sh <rank> [extra train_tactic_sft.py args...]

Examples:
  mathlib_fine_tuning/run_rank_training.sh 64
  mathlib_fine_tuning/run_rank_training.sh 128 \
    --per-device-train-batch-size 8 \
    --per-device-eval-batch-size 8 \
    --gradient-accumulation-steps 2

Defaults added by this wrapper:
  --lora-r <rank>
  --lora-alpha <2 * rank>
  --output-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_r<rank>
  --per-device-train-batch-size 12
  --per-device-eval-batch-size 12
  --gradient-accumulation-steps 1
  --seed 42

Any extra arguments are passed through to train_tactic_sft.py and can override
these defaults by appearing later on the command line.
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 0
fi

RANK="$1"
shift

if [[ ! "$RANK" =~ ^[0-9]+$ ]]; then
  echo "Rank must be a positive integer, got: $RANK" >&2
  exit 1
fi

ALPHA=$((RANK * 2))
OUTPUT_DIR="$ROOT/mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_r${RANK}"

exec python3 "$ROOT/mathlib_fine_tuning/train_tactic_sft.py" \
  --lora-r "$RANK" \
  --lora-alpha "$ALPHA" \
  --output-dir "$OUTPUT_DIR" \
  --per-device-train-batch-size 12 \
  --per-device-eval-batch-size 12 \
  --gradient-accumulation-steps 1 \
  --seed 42 \
  "$@"
