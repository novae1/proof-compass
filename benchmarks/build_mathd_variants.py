#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.benchmarks.benchmark_runner import DEFAULT_HEADER

MINIF2F_PATH = Path("benchmarks/processed/miniF2F_valid.json")
OUTPUT_PATH = Path("benchmarks/processed/miniF2F_mathd_variants.json")
MODEL_ID = "deepseek-ai/DeepSeek-Prover-V1.5-RL"
WRONG_PROOF = "The value of 1 plus 1 is 2."


def build_mathd_variants(
    *,
    minif2f_path: Path,
    output_path: Path,
    model_id: str,
    wrong_proof: str,
) -> None:
    payload = json.loads(minif2f_path.read_text(encoding="utf-8"))
    benchmark: dict[str, dict[str, object]] = {}

    for name in sorted(payload):
        if not name.startswith("mathd_"):
            continue

        problem = payload[name]
        formal_statement = problem["formal_statement"]
        informal_statement = problem.get("informal_statement", "")

        benchmark[name] = {
            "formal_statement": formal_statement,
            "informal_statement": informal_statement,
            "header": DEFAULT_HEADER,
            "variants": {
                "cot": {
                    "model_id": model_id,
                    "nl_proof": None,
                },
                "noncot": {
                    "model_id": model_id,
                    "nl_proof": None,
                },
                "wrong_proof": {
                    "model_id": model_id,
                    "nl_proof": wrong_proof,
                },
            },
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(benchmark, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    build_mathd_variants(
        minif2f_path=MINIF2F_PATH,
        output_path=OUTPUT_PATH,
        model_id=MODEL_ID,
        wrong_proof=WRONG_PROOF,
    )
    print(f"Wrote mathd variants benchmark to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
