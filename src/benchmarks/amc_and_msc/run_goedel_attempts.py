#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.core.problem_structure import TheoremProcessor
from src.prover_generation.artifacts import load_artifacts
from src.prover_generation.generation_params import GenerationParams
from src.prover_generation.prompt_config import GoedelPromptConfig
from src.prover_generation.theorem_proving import generate_attempts

INPUT_PATH = ROOT / "experiments" / "amc_and_msc" / "filtered_problems.json"
OUTPUT_PATH = ROOT / "experiments" / "amc_and_msc" / "attempts.json"

MODEL_ID = "Goedel-LM/Goedel-Prover-V2-8B"
TEMPERATURE = 1.0
TOP_P = 0.95
MAX_NEW_TOKENS = 14000
MAX_ATTEMPTS_PER_PROBLEM = 4
MICRO_BATCH_SIZE = 4
STOP_ON_SUCCESS = False


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _load_problems(path: Path) -> dict[str, dict[str, str]]:
    data = _load_json(path)
    if not isinstance(data, dict):
        raise TypeError("Filtered problems JSON must be an object.")
    return data


def main() -> int:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing input at {INPUT_PATH}")

    problems = _load_problems(INPUT_PATH)
    model, tokenizer = load_artifacts(MODEL_ID)
    params = GenerationParams(
        micro_batch_size=MICRO_BATCH_SIZE,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_new_tokens=MAX_NEW_TOKENS,
    )

    output: dict[str, object] = {}
    for problem_key in problems:
        entry = problems[problem_key]
        header = str(entry.get("header", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        if not header or not formal_statement:
            raise ValueError(f"Problem '{problem_key}' is missing header/formal_statement.")

        print(problem_key)
        processor = TheoremProcessor(
            formal_statement=formal_statement,
            header=header,
        )
        attempts = generate_attempts(
            processor,
            GoedelPromptConfig,
            model,
            tokenizer,
            server_client=None,
            params=params,
            max_attempts=MAX_ATTEMPTS_PER_PROBLEM,
            stop_on_success=STOP_ON_SUCCESS,
        )
        for attempt in attempts:
            processor.add_attempt(attempt)

        output[problem_key] = processor.to_dict()
        _save_json(output, OUTPUT_PATH)

    print(f"Wrote attempts to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
