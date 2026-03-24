#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPERIMENT_DIR = Path(__file__).resolve().parents[2]
INPUT_DIR = EXPERIMENT_DIR / "outputs" / "msc180" / "manual"
OUTPUT_DIR = EXPERIMENT_DIR / "outputs" / "msc180" / "manual_merged"

DATE_PREFIX_DEFAULT = "20260213"
MODEL_SUFFIX_DEFAULT = "deepseekv2_7b"
LEAN_TAG = "lean4-15"

CONDITION_TO_GROUP = [
    ("A", "no-hint"),
    ("B-main", "single-hint"),
    ("B-all", "multi-hint"),
    ("C-main", "single-hint-and-example"),
    ("C-all", "multi-hint-and-example"),
]


def _load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Expected JSON object at {path}, got {type(data).__name__}.")
    return data


def _save_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _normalize_problem_key(problem_key: str) -> str:
    # Example: MSC-180/65_001 -> MSC-180_65_001
    return problem_key.replace("/", "_")


def _assert_verified_entry(source: Path, problem_key: str, entry: dict) -> None:
    if not isinstance(entry, dict):
        raise TypeError(f"Problem '{problem_key}' in {source} must be a JSON object.")

    attempts = entry.get("attempts")
    if not isinstance(attempts, list):
        raise TypeError(f"Problem '{problem_key}' in {source} must contain an 'attempts' list.")

    for idx, attempt in enumerate(attempts):
        if not isinstance(attempt, dict):
            raise TypeError(
                f"Attempt index {idx} of '{problem_key}' in {source} must be a JSON object."
            )
        missing = [k for k in ("success", "message", "verification_time") if k not in attempt]
        if missing:
            raise ValueError(
                f"Attempt index {idx} of '{problem_key}' in {source} is not verified "
                f"(missing {missing}). Run scripts/checking_problems.py first."
            )


def _build_input_filename(date_prefix: str, condition: str, model_suffix: str) -> str:
    return f"{date_prefix}_msc180-manual-{condition}_{model_suffix}_{LEAN_TAG}_verified.json"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge verified MSC-180 manual hint outputs into one grouped JSON."
    )
    parser.add_argument(
        "--date-prefix",
        default=DATE_PREFIX_DEFAULT,
        help=f"Date prefix used in filenames (default: {DATE_PREFIX_DEFAULT}).",
    )
    parser.add_argument(
        "--model-suffix",
        default=MODEL_SUFFIX_DEFAULT,
        help=f"Model suffix used in filenames (default: {MODEL_SUFFIX_DEFAULT}).",
    )
    parser.add_argument(
        "--output-name",
        default=None,
        help=(
            "Output filename inside rag_experiments/outputs/msc180/manual_merged. "
            "Defaults to <date>_msc180-manual-merged_<model>_lean4-15_verified.json."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    output_name = (
        args.output_name
        or f"{args.date_prefix}_msc180-manual-merged_{args.model_suffix}_{LEAN_TAG}_verified.json"
    )
    output_path = OUTPUT_DIR / output_name

    merged: dict[str, dict] = {}

    for condition, group in CONDITION_TO_GROUP:
        input_name = _build_input_filename(args.date_prefix, condition, args.model_suffix)
        input_path = INPUT_DIR / input_name
        if not input_path.exists():
            raise FileNotFoundError(f"Missing input file: {input_path}")

        payload = _load_json(input_path)
        for problem_key in sorted(payload):
            entry = payload[problem_key]
            _assert_verified_entry(input_path, problem_key, entry)
            normalized_problem = _normalize_problem_key(problem_key)
            merged_key = f"{group}/{normalized_problem}"
            if merged_key in merged:
                raise ValueError(f"Duplicate merged key '{merged_key}' from {input_path}.")
            merged[merged_key] = entry

    _save_json(merged, output_path)
    print(f"Wrote merged verified JSON to {output_path}")
    print(f"Total merged entries: {len(merged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
