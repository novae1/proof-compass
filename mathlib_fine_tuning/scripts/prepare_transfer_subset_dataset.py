#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_TRAIN = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "deepseek_noncot_tactic_1024_train.jsonl"
DEFAULT_SOURCE_VALID = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "deepseek_noncot_tactic_1024_valid.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "transfer_subset_5pct"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-train-path", type=Path, default=DEFAULT_SOURCE_TRAIN)
    parser.add_argument("--source-valid-path", type=Path, default=DEFAULT_SOURCE_VALID)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--train-percent", type=float, default=5.0)
    parser.add_argument("--eval-size", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    if not (0 < args.train_percent <= 100):
        raise ValueError("--train-percent must be in (0, 100].")

    train_rows = _read_jsonl(args.source_train_path)
    valid_rows = _read_jsonl(args.source_valid_path)

    train_size = max(1, round(len(train_rows) * (args.train_percent / 100.0)))
    if args.eval_size > len(valid_rows):
        raise ValueError(f"--eval-size={args.eval_size} exceeds available valid rows={len(valid_rows)}")

    rng = random.Random(args.seed)
    selected_train = rng.sample(train_rows, train_size)
    selected_valid = rng.sample(valid_rows, args.eval_size)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_path = args.output_dir / "train.jsonl"
    valid_path = args.output_dir / "valid.jsonl"
    summary_path = args.output_dir / "summary.json"

    _write_jsonl(train_path, selected_train)
    _write_jsonl(valid_path, selected_valid)

    summary = {
        "source_train_path": str(args.source_train_path.relative_to(ROOT)),
        "source_valid_path": str(args.source_valid_path.relative_to(ROOT)),
        "output_dir": str(args.output_dir.relative_to(ROOT)),
        "train_percent": args.train_percent,
        "eval_size": args.eval_size,
        "seed": args.seed,
        "train_rows": len(selected_train),
        "valid_rows": len(selected_valid),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote train={train_path.relative_to(ROOT)}")
    print(f"wrote valid={valid_path.relative_to(ROOT)}")
    print(f"wrote summary={summary_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
