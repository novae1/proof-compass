#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.lean.http_client import LeanHTTPClient
from src.lean.checking import check_proof

INPUT_PATH = ROOT / "experiments" / "amc_and_msc" / "attempts_extracted.json"
OUTPUT_PATH = ROOT / "experiments" / "amc_and_msc" / "attempts_verified.json"
SERVER_URL = "http://localhost:1347"
TIMEOUT_SECONDS = 20
IGNORE_SORRIES = False


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def verify_attempts(payload: dict, server_url: str) -> dict:
    client = LeanHTTPClient(server_url)
    total = len(payload)

    for idx, problem_key in enumerate(sorted(payload), start=1):
        print(f"[{idx}/{total}] {problem_key}")
        processor = payload[problem_key]
        header = str(processor.get("header", "")).strip()
        if not header:
            raise ValueError(f"Problem '{problem_key}' is missing a header.")

        attempts = processor.get("attempts", [])
        for attempt in attempts:
            proof = attempt.get("parsed_proof", "")
            start = time.time()
            success, message = check_proof(
                proof,
                client,
                timeout=TIMEOUT_SECONDS,
                ignore_sorries=IGNORE_SORRIES,
                header=header,
            )
            attempt["success"] = success
            attempt["message"] = message
            attempt["verification_time"] = time.time() - start

    return payload


def main() -> int:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing input at {INPUT_PATH}")

    payload = _load_json(INPUT_PATH)
    updated = verify_attempts(payload, SERVER_URL)
    _save_json(updated, OUTPUT_PATH)
    print(f"Wrote verified attempts to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
