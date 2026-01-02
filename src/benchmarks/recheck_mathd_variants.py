#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.lean.http_client import LeanHTTPClient
from src.lean.checking import check_proof

INPUT_PATH = ROOT / "experiments/mathd_runs/checkpoint.json"
OUTPUT_PATH = ROOT / "experiments/mathd_runs/checkpoint_verified.json"
SERVER_URL = "http://localhost:1347"
TIMEOUT_SECONDS = 20
FALLBACK_HEADER = "set_option maxHeartbeats 0"


def _load_checkpoint(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_checkpoint(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _strip_imports(text: str) -> str:
    lines = text.splitlines()
    return "\n".join(
        line for line in lines if not line.lstrip().startswith("import ")
    )


def _split_header_and_theorem(text: str) -> tuple[str, str]:
    cleaned = _strip_imports(text).strip()
    lines = cleaned.splitlines()

    start_idx = None
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("/--") or stripped.startswith("theorem "):
            start_idx = idx
            break

    if start_idx is None:
        return FALLBACK_HEADER, cleaned

    header_lines = []
    for line in lines[:start_idx]:
        stripped = line.lstrip()
        if stripped.startswith("set_option ") or stripped.startswith("open "):
            header_lines.append(line)

    header = "\n".join(header_lines).strip()
    if not header:
        header = FALLBACK_HEADER

    theorem = "\n".join(lines[start_idx:]).strip()
    return header, theorem


def recheck_attempts(payload: dict, server_url: str, output_path: Path) -> dict:
    client = LeanHTTPClient(server_url)

    for problem_id, variants in payload.items():
        print(problem_id)
        _ = problem_id
        for variant_name, processor in variants.items():
            _ = variant_name
            attempts = processor.get("attempts", [])
            for attempt in attempts:
                proof = attempt.get("parsed_proof", "")
                header, theorem = _split_header_and_theorem(proof)
                start = time.time()
                success, message = check_proof(
                    theorem,
                    client,
                    timeout=TIMEOUT_SECONDS,
                    ignore_sorries=False,
                    header=header,
                )
                attempt["success"] = success
                attempt["message"] = message
                attempt["verification_time"] = time.time() - start

        _save_checkpoint(payload, output_path)

    return payload


def main() -> int:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Checkpoint not found at {INPUT_PATH}.")

    payload = _load_checkpoint(INPUT_PATH)
    updated = recheck_attempts(payload, SERVER_URL, OUTPUT_PATH)
    _save_checkpoint(updated, OUTPUT_PATH)
    print(f"Wrote verified checkpoint to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
