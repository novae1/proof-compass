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
from src.prover_generation.theorem_proving import generate_attempts
from prompt_hints.prompt_config import DeepSeekProverV2HintPromptConfig, GoedelHintPromptConfig

WORKFLOW_DIR = Path(__file__).resolve().parents[2]
SPEC_DIR = WORKFLOW_DIR / "data" / "specs"
OUTPUT_ROOT = WORKFLOW_DIR / "outputs"

SPEC_FILES = {
    "newstuff-with-hints": SPEC_DIR / "proving-with-given-theorem-newstuff_spec.json",
    "newstuff-no-hint": SPEC_DIR / "proving-with-given-theorem-newstuff-no-hint_spec.json",
}

MODEL_CONFIGS = {
    "deepseek": {
        "model_id": "deepseek-ai/DeepSeek-Prover-V2-7B",
        "prompt_config": DeepSeekProverV2HintPromptConfig,
        "suffix": "deepseekv2_7b",
    },
    "goedel": {
        "model_id": "Goedel-LM/Goedel-Prover-V2-8B",
        "prompt_config": GoedelHintPromptConfig,
        "suffix": "goedelv2_8b",
    },
}

DATE_PREFIX = "20260205"

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


def _run_spec(
    spec_path: Path,
    output_path: Path,
    model,
    tokenizer,
    prompt_config,
    params: GenerationParams,
) -> None:
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec not found at {spec_path}")

    spec = _load_json(spec_path)
    processors = _build_processors(spec)

    output: dict[str, object] = {}
    for key, processor in processors.items():
        print(key)
        attempts = generate_attempts(
            processor,
            prompt_config,
            model,
            tokenizer,
            server_client=None,
            params=params,
            max_attempts=ATTEMPTS_PER_PROBLEM,
            stop_on_success=STOP_ON_SUCCESS,
        )
        for attempt in attempts:
            processor.add_attempt(attempt)
        output[key] = processor.to_dict()
        _save_json(output, output_path)

    print(f"Wrote attempts to {output_path}")


def _output_dir_for_spec(spec_name: str) -> Path:
    if spec_name.endswith("no-hint"):
        return OUTPUT_ROOT / "no_hint"
    return OUTPUT_ROOT / "with_hints"


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 run_local_tasks.py <deepseek|goedel>")

    mode = sys.argv[1].strip().lower()
    cfg = MODEL_CONFIGS.get(mode)
    if not cfg:
        raise SystemExit("Mode must be one of: deepseek, goedel")

    params = GenerationParams(
        micro_batch_size=MICRO_BATCH_SIZE,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_new_tokens=MAX_NEW_TOKENS,
    )

    model, tokenizer = load_artifacts(cfg["model_id"])
    prompt_config = cfg["prompt_config"]
    suffix = cfg["suffix"]

    for spec_name, spec_path in SPEC_FILES.items():
        output_name = f"{DATE_PREFIX}_{spec_name}_{suffix}.json"
        output_path = _output_dir_for_spec(spec_name) / output_name
        _run_spec(spec_path, output_path, model, tokenizer, prompt_config, params)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
