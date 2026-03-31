#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path("rag_experiments/outputs")


@dataclass
class PairResult:
    raw_path: Path
    verified_path: Path | None
    status: str
    detail: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate raw/verified JSON pairs by checking that matching attempts "
            "have the same raw_output strings."
        )
    )
    parser.add_argument(
        "roots",
        nargs="*",
        type=Path,
        default=[DEFAULT_ROOT],
        help="Directories to scan recursively for JSON outputs.",
    )
    parser.add_argument(
        "--check-parsed-proof",
        action="store_true",
        help="Also require parsed_proof to match for every attempt.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full results as JSON.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Expected JSON object at {path}, got {type(data).__name__}")
    return data


def find_raw_files(roots: list[Path]) -> list[Path]:
    raw_files: list[Path] = []
    for root in roots:
        if root.is_file():
            candidates = [root]
        else:
            candidates = sorted(root.rglob("*.json"))
        for path in candidates:
            if path.name.endswith("_verified.json"):
                continue
            raw_files.append(path)
    return sorted(set(raw_files))


def expected_verified_path(raw_path: Path) -> Path:
    return raw_path.with_name(f"{raw_path.stem}_verified.json")


def compare_pair(raw_path: Path, verified_path: Path, check_parsed_proof: bool) -> PairResult:
    raw_payload = load_json(raw_path)
    verified_payload = load_json(verified_path)

    raw_keys = list(raw_payload.keys())
    verified_keys = list(verified_payload.keys())

    if set(raw_keys) != set(verified_keys):
        raw_only = sorted(set(raw_keys) - set(verified_keys))
        verified_only = sorted(set(verified_keys) - set(raw_keys))
        detail = (
            f"problem-key mismatch; raw_only={raw_only[:3]} verified_only={verified_only[:3]}"
        )
        return PairResult(raw_path, verified_path, "mismatch", detail)

    for key in raw_keys:
        raw_entry = raw_payload.get(key)
        verified_entry = verified_payload.get(key)
        if not isinstance(raw_entry, dict) or not isinstance(verified_entry, dict):
            return PairResult(
                raw_path,
                verified_path,
                "mismatch",
                f"{key}: entry type mismatch",
            )

        raw_attempts = raw_entry.get("attempts", [])
        verified_attempts = verified_entry.get("attempts", [])
        if not isinstance(raw_attempts, list) or not isinstance(verified_attempts, list):
            return PairResult(
                raw_path,
                verified_path,
                "mismatch",
                f"{key}: attempts is not a list in one of the files",
            )
        if len(raw_attempts) != len(verified_attempts):
            return PairResult(
                raw_path,
                verified_path,
                "mismatch",
                f"{key}: attempt-count mismatch ({len(raw_attempts)} vs {len(verified_attempts)})",
            )

        for idx, (raw_attempt, verified_attempt) in enumerate(
            zip(raw_attempts, verified_attempts), start=1
        ):
            if not isinstance(raw_attempt, dict) or not isinstance(verified_attempt, dict):
                return PairResult(
                    raw_path,
                    verified_path,
                    "mismatch",
                    f"{key} attempt {idx}: attempt type mismatch",
                )

            raw_output = str(raw_attempt.get("raw_output", ""))
            verified_output = str(verified_attempt.get("raw_output", ""))
            if raw_output != verified_output:
                return PairResult(
                    raw_path,
                    verified_path,
                    "mismatch",
                    f"{key} attempt {idx}: raw_output mismatch",
                )

            if check_parsed_proof:
                raw_proof = str(raw_attempt.get("parsed_proof", ""))
                verified_proof = str(verified_attempt.get("parsed_proof", ""))
                if raw_proof != verified_proof:
                    return PairResult(
                        raw_path,
                        verified_path,
                        "mismatch",
                        f"{key} attempt {idx}: parsed_proof mismatch",
                    )

    return PairResult(raw_path, verified_path, "match")


def main() -> int:
    args = parse_args()
    raw_files = find_raw_files(args.roots)
    results: list[PairResult] = []

    for raw_path in raw_files:
        verified_path = expected_verified_path(raw_path)
        if not verified_path.exists():
            results.append(
                PairResult(raw_path, None, "missing_verified", "no matching _verified.json file")
            )
            continue
        results.append(compare_pair(raw_path, verified_path, args.check_parsed_proof))

    if args.json:
        payload = [
            {
                "raw_path": str(result.raw_path),
                "verified_path": str(result.verified_path) if result.verified_path else None,
                "status": result.status,
                "detail": result.detail,
            }
            for result in results
        ]
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    matches = [r for r in results if r.status == "match"]
    missing = [r for r in results if r.status == "missing_verified"]
    mismatches = [r for r in results if r.status == "mismatch"]

    print(f"Scanned raw files: {len(results)}")
    print(f"Matching raw/verified pairs: {len(matches)}")
    print(f"Missing verified pair: {len(missing)}")
    print(f"Mismatched pairs: {len(mismatches)}")

    if matches:
        print("\nSafe raw-file deletion candidates:")
        for result in matches:
            print(f"- {result.raw_path}")

    if missing:
        print("\nMissing verified pair:")
        for result in missing:
            print(f"- {result.raw_path}")

    if mismatches:
        print("\nMismatched pairs:")
        for result in mismatches:
            print(f"- {result.raw_path} :: {result.detail}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
