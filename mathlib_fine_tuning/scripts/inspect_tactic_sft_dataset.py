#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUMMARY = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "deepseek_noncot_tactic_1024_summary.json"
DEFAULT_TRAIN = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "deepseek_noncot_tactic_1024_train.jsonl"
DEFAULT_VALID = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "deepseek_noncot_tactic_1024_valid.jsonl"


def _read_examples(path: Path, limit: int) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if idx >= limit:
                break
            rows.append(json.loads(line))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--train", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument("--valid", type=Path, default=DEFAULT_VALID)
    parser.add_argument("--examples", type=int, default=2)
    args = parser.parse_args()

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    print("summary")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    for label, path in [("train", args.train), ("valid", args.valid)]:
        examples = _read_examples(path, args.examples)
        print(f"\n{label}_examples path={path.relative_to(ROOT)} count={len(examples)}")
        for idx, row in enumerate(examples, start=1):
            print(f"\n[{label} example {idx}] token_count={row['token_count']}")
            print("-- prompt --")
            print(row["prompt"][:2500])
            print("-- completion --")
            print(row["completion"][:2500])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
