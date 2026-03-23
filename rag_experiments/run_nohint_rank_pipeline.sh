#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

usage() {
  cat <<'EOF'
Usage:
  rag_experiments/run_nohint_rank_pipeline.sh <rank> [options]

Runs the full MSC-180 no-hint pipeline for a LoRA adapter:
1. generation
2. verification
3. standard MSC-180 analysis
4. pairwise comparison against base
5. pairwise comparison against r16
6. pairwise error-type analysis against base
7. pairwise error-type analysis against r16

Options:
  --adapter-dir PATH            Override adapter directory.
  --date-prefix YYYYMMDD        Prefix for generated output names. Default: today.
  --attempts-per-problem N      Default: 20
  --micro-batch-size N          Default: 10
  --max-problems N              Optional cap for smoke/debug runs.
  --temperature X               Default: 1.0
  --top-p X                     Default: 0.95
  --max-new-tokens N            Default: 7000

Examples:
  rag_experiments/run_nohint_rank_pipeline.sh 64
  rag_experiments/run_nohint_rank_pipeline.sh 128 --date-prefix 20260323

Prerequisite:
  Keep the Lean verifier server running in another terminal:
    python3 src/lean/flask_server.py
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

DATE_PREFIX="$(date +%Y%m%d)"
ATTEMPTS=20
MICRO_BATCH=10
TEMPERATURE=1.0
TOP_P=0.95
MAX_NEW_TOKENS=7000
MAX_PROBLEMS=""
ADAPTER_DIR="$ROOT/mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_r${RANK}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --adapter-dir)
      ADAPTER_DIR="$2"
      shift 2
      ;;
    --date-prefix)
      DATE_PREFIX="$2"
      shift 2
      ;;
    --attempts-per-problem)
      ATTEMPTS="$2"
      shift 2
      ;;
    --micro-batch-size)
      MICRO_BATCH="$2"
      shift 2
      ;;
    --max-problems)
      MAX_PROBLEMS="$2"
      shift 2
      ;;
    --temperature)
      TEMPERATURE="$2"
      shift 2
      ;;
    --top-p)
      TOP_P="$2"
      shift 2
      ;;
    --max-new-tokens)
      MAX_NEW_TOKENS="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ! -d "$ADAPTER_DIR" ]]; then
  echo "Adapter directory not found: $ADAPTER_DIR" >&2
  exit 1
fi

VARIANT="lora_r${RANK}"
RAW_NAME="${DATE_PREFIX}_msc180-v2-nohint_${VARIANT}_deepseekv2_7b_lean4-15.json"
VERIFIED_NAME="${DATE_PREFIX}_msc180-v2-nohint_${VARIANT}_deepseekv2_7b_lean4-15_verified.json"
RAW_PATH="rag_experiments/outputs/${RAW_NAME}"
VERIFIED_PATH="rag_experiments/outputs/${VERIFIED_NAME}"

BASE_VERIFIED="rag_experiments/outputs/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json"
R16_VERIFIED="rag_experiments/outputs/20260313_msc180-v2-nohint_lora_deepseekv2_7b_lean4-15_verified.json"

echo "Generating ${RAW_PATH}"
GEN_ARGS=(
  --adapter-dir "$ADAPTER_DIR"
  --attempts-per-problem "$ATTEMPTS"
  --micro-batch-size "$MICRO_BATCH"
  --temperature "$TEMPERATURE"
  --top-p "$TOP_P"
  --max-new-tokens "$MAX_NEW_TOKENS"
  --output-name "$RAW_NAME"
)
if [[ -n "$MAX_PROBLEMS" ]]; then
  GEN_ARGS+=(--max-problems "$MAX_PROBLEMS")
fi
python3 "$ROOT/rag_experiments/run_msc180_v2_nohint.py" "${GEN_ARGS[@]}"

echo "Verifying ${RAW_PATH}"
python3 "$ROOT/scripts/checking_problems.py" "$RAW_PATH" "$VERIFIED_PATH"

echo "Analyzing ${VERIFIED_PATH}"
python3 "$ROOT/rag_experiments/analyze_msc180_v2_results.py" "$ROOT/$VERIFIED_PATH"

echo "Comparing against base"
python3 "$ROOT/finetuning_analysis/compare_nohint_runs.py" \
  --baseline "$ROOT/$BASE_VERIFIED" \
  --candidate "$ROOT/$VERIFIED_PATH" \
  --baseline-label base \
  --candidate-label "$VARIANT" \
  --output-prefix "$ROOT/finetuning_analysis/${DATE_PREFIX}_msc180_nohint_${VARIANT}_vs_base"

echo "Comparing against r16"
python3 "$ROOT/finetuning_analysis/compare_nohint_runs.py" \
  --baseline "$ROOT/$R16_VERIFIED" \
  --candidate "$ROOT/$VERIFIED_PATH" \
  --baseline-label r16 \
  --candidate-label "$VARIANT" \
  --output-prefix "$ROOT/finetuning_analysis/${DATE_PREFIX}_msc180_nohint_${VARIANT}_vs_r16"

echo "Analyzing error types against base"
python3 "$ROOT/finetuning_analysis/analyze_error_types.py" \
  --baseline "$ROOT/$BASE_VERIFIED" \
  --candidate "$ROOT/$VERIFIED_PATH" \
  --baseline-label base \
  --candidate-label "$VARIANT" \
  --output-prefix "$ROOT/finetuning_analysis/${DATE_PREFIX}_error_types_${VARIANT}_vs_base"

echo "Analyzing error types against r16"
python3 "$ROOT/finetuning_analysis/analyze_error_types.py" \
  --baseline "$ROOT/$R16_VERIFIED" \
  --candidate "$ROOT/$VERIFIED_PATH" \
  --baseline-label r16 \
  --candidate-label "$VARIANT" \
  --output-prefix "$ROOT/finetuning_analysis/${DATE_PREFIX}_error_types_${VARIANT}_vs_r16"

echo "Done:"
echo "  raw:      $RAW_PATH"
echo "  verified: $VERIFIED_PATH"
