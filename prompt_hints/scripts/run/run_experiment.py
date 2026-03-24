#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from src.core.problem_structure import TheoremProcessor
from src.prover_generation.artifacts import load_artifacts
from src.prover_generation.generation_params import GenerationParams
from src.prover_generation.theorem_proving import generate_attempts
from prompt_hints.prompt_config import DeepSeekProverV2HintPromptConfig

HINTS_DIR = Path(__file__).resolve().parents[2]
SPEC_PATH = HINTS_DIR / "data" / "specs" / "experiment_spec.json"
OUTPUT_PATH = HINTS_DIR / "outputs" / "experiments" / "attempts.json"

MODEL_ID = "deepseek-ai/DeepSeek-Prover-V2-7B"
ATTEMPTS_PER_PROBLEM = 4
MICRO_BATCH_SIZE = 4
TEMPERATURE = 1.0
TOP_P = 0.95
MAX_NEW_TOKENS = 8000
STOP_ON_SUCCESS = False


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run prompt-hint experiment.")
    parser.add_argument("--spec", type=Path, default=SPEC_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--model-id", default=MODEL_ID)
    parser.add_argument("--attempts", type=int, default=ATTEMPTS_PER_PROBLEM)
    parser.add_argument("--micro-batch-size", type=int, default=MICRO_BATCH_SIZE)
    parser.add_argument("--temperature", type=float, default=TEMPERATURE)
    parser.add_argument("--top-p", type=float, default=TOP_P)
    parser.add_argument("--max-new-tokens", type=int, default=MAX_NEW_TOKENS)
    parser.add_argument("--stop-on-success", action="store_true", default=STOP_ON_SUCCESS)
    return parser.parse_args()


def _build_processors(spec: dict) -> dict[str, TheoremProcessor]:
    problems = spec.get("problems")
    if not isinstance(problems, dict):
        raise TypeError("Spec must contain a 'problems' object.")

    processors: dict[str, TheoremProcessor] = {}
    for key, entry in problems.items():
        if not isinstance(entry, dict):
            raise TypeError(f"Problem '{key}' must be a JSON object.")

        header = str(entry.get("header", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        theorem_hint = str(entry.get("theorem_hint", "")).strip()

        if not header:
            raise ValueError(f"Problem '{key}' is missing a non-empty header.")
        if not formal_statement:
            raise ValueError(f"Problem '{key}' is missing a non-empty formal_statement.")

        processors[key] = TheoremProcessor(
            formal_statement=formal_statement,
            header=header,
            informal_statement=theorem_hint or None,
        )

    return processors


def main() -> int:
    args = _parse_args()
    if not args.spec.exists():
        raise FileNotFoundError(f"Spec not found at {args.spec}")

    spec = _load_json(args.spec)
    processors = _build_processors(spec)

    model, tokenizer = load_artifacts(args.model_id)
    params = GenerationParams(
        micro_batch_size=args.micro_batch_size,
        temperature=args.temperature,
        top_p=args.top_p,
        max_new_tokens=args.max_new_tokens,
    )

    output: dict[str, object] = {}
    for key, processor in processors.items():
        print(key)
        attempts = generate_attempts(
            processor,
            DeepSeekProverV2HintPromptConfig,
            model,
            tokenizer,
            server_client=None,
            params=params,
            max_attempts=args.attempts,
            stop_on_success=args.stop_on_success,
        )
        for attempt in attempts:
            processor.add_attempt(attempt)

        output[key] = processor.to_dict()
        _save_json(output, args.output)

    print(f"Wrote attempts to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
