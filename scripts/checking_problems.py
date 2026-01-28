#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.lean.http_client import LeanHTTPClient
from src.lean.checking import check_proof

SERVER_URL = "http://localhost:1347"
TIMEOUT_SECONDS = 20
IGNORE_SORRIES = False


def _load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Expected JSON object at {path}, got {type(data).__name__}.")
    return data


def _save_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify attempts JSON produced by proof-compass runs."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Repo-root-relative path to attempts JSON",
    )
    parser.add_argument(
        "output",
        type=Path,
        help="Repo-root-relative path for verified JSON",
    )
    return parser.parse_args()


def _resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        raise ValueError(f"Paths must be repo-root-relative, got absolute: {path}")
    if not str(path):
        raise ValueError("Path must be non-empty.")
    return ROOT / path


def verify_attempts(payload: dict, output_path: Path) -> dict:
    client = LeanHTTPClient(SERVER_URL)
    total = len(payload)

    for idx, problem_key in enumerate(payload, start=1):
        print(f"[{idx}/{total}] {problem_key}")
        processor = payload[problem_key]
        if not isinstance(processor, dict):
            raise TypeError(f"Problem '{problem_key}' must be a JSON object.")

        header = str(processor.get("header", "")).rstrip()
        attempts = processor.get("attempts", [])
        if not isinstance(attempts, list):
            raise TypeError(f"Attempts for '{problem_key}' must be a list.")

        for attempt in attempts:
            if not isinstance(attempt, dict):
                raise TypeError(f"Attempt in '{problem_key}' must be a JSON object.")
            proof = attempt.get("parsed_proof", "")
            start = time.time()
            success, message = check_proof(
                proof,
                client,
                timeout=TIMEOUT_SECONDS,
                ignore_sorries=IGNORE_SORRIES,
                header="",
            )
            attempt["success"] = success
            attempt["message"] = message
            attempt["verification_time"] = time.time() - start

        _save_json(payload, output_path)

    return payload


def main() -> int:
    args = _parse_args()
    input_path = _resolve_repo_path(args.input)
    output_path = _resolve_repo_path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(f"Input not found at {input_path}")

    payload = _load_json(input_path)
    verify_attempts(payload, output_path)
    print(f"Wrote verified attempts to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
