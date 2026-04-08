#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "deepseek_noncot_tactic_1024_train.jsonl"
DEFAULT_OUTPUT_DIR = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "memorization_100"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-train-path", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--sample-size", type=int, default=100)
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
    rows = _read_jsonl(args.source_train_path)
    if args.sample_size > len(rows):
        raise ValueError(
            f"sample_size={args.sample_size} exceeds available rows={len(rows)} in {args.source_train_path}"
        )

    rng = random.Random(args.seed)
    selected = rng.sample(rows, args.sample_size)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    train_path = args.output_dir / "train.jsonl"
    valid_path = args.output_dir / "valid.jsonl"
    summary_path = args.output_dir / "summary.json"

    _write_jsonl(train_path, selected)
    _write_jsonl(valid_path, selected)

    summary = {
        "source_train_path": str(args.source_train_path.relative_to(ROOT)),
        "output_dir": str(args.output_dir.relative_to(ROOT)),
        "sample_size": args.sample_size,
        "seed": args.seed,
        "train_rows": len(selected),
        "valid_rows": len(selected),
        "evaluation_policy": "in_sample_memorization",
        "notes": [
            "train.jsonl and valid.jsonl intentionally contain the same rows",
            "this dataset is for the 100-example memorization experiment only",
        ],
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"wrote train={train_path.relative_to(ROOT)}")
    print(f"wrote valid={valid_path.relative_to(ROOT)}")
    print(f"wrote summary={summary_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
