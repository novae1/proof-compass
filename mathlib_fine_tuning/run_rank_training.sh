#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

exec bash "$ROOT/mathlib_fine_tuning/scripts/run_rank_training.sh" "$@"
