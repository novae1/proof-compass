#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

CHECKPOINT_PATH = Path("experiments/mathd_runs/checkpoint.json")


def _load_checkpoint(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _accumulate_attempts(payload: dict) -> Dict[str, Tuple[int, int]]:
    counts: Dict[str, Tuple[int, int]] = {}

    for problem_id, variants in payload.items():
        _ = problem_id
        for variant_name, processor in variants.items():
            attempts = processor.get("attempts", [])
            successes = sum(1 for attempt in attempts if attempt.get("success"))
            total = len(attempts)
            if variant_name in counts:
                prev_successes, prev_total = counts[variant_name]
                counts[variant_name] = (prev_successes + successes, prev_total + total)
            else:
                counts[variant_name] = (successes, total)

    return counts


def main() -> int:
    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError(
            f"Checkpoint not found at {CHECKPOINT_PATH}. Run the benchmark first."
        )

    payload = _load_checkpoint(CHECKPOINT_PATH)
    counts = _accumulate_attempts(payload)
    if not counts:
        print("No attempts found in checkpoint.")
        return 0

    print(f"Checkpoint: {CHECKPOINT_PATH}")
    for variant_name in sorted(counts):
        successes, total = counts[variant_name]
        rate = (successes / total) if total else 0.0
        print(f"{variant_name}: {successes}/{total} = {rate:.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
