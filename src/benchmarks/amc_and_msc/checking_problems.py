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
from src.prover_generation.prompt_config import DeepSeekProverV2CoTPromptConfig, KiminaProverPromptConfig

INPUT_PATH = ROOT / "experiments" / "amc_and_msc" / "20260106_attempts_goedelv2_verified_lean4_26.json"
OUTPUT_PATH = ROOT / "experiments" / "amc_and_msc" / "20260113_attempts_goedel_v2_verified_lean4_15.json"
SERVER_URL = "http://localhost:1347"
TIMEOUT_SECONDS = 20
IGNORE_SORRIES = False


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _strip_imports(text: str) -> str:
    lines = text.splitlines()
    return "\n".join(
        line for line in lines if not line.lstrip().startswith("import ")
    )


def verify_attempts(payload: dict, server_url: str) -> dict:
    client = LeanHTTPClient(server_url)
    total = len(payload)

    for idx, problem_key in enumerate(payload, start=1):
        print(f"[{idx}/{total}] {problem_key}")
        processor = payload[problem_key]
        header = _strip_imports(str(processor.get("header", ""))).strip()

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
            attempt["parsed_proof"] = proof

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
