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
from prompt_hints.prompt_config import (
    DeepSeekProverV2HintPromptConfig,
    DeepSeekProverV2HintWithUsagePromptConfig,
)

EXPERIMENT_DIR = Path(__file__).resolve().parents[2]
SPEC_DIR = EXPERIMENT_DIR / "data" / "specs"
OUTPUT_DIR = EXPERIMENT_DIR / "outputs" / "msc180" / "manual"

SPEC_FILES = [
    ("A", SPEC_DIR / "msc180_manual_A_spec.json"),
    ("B-main", SPEC_DIR / "msc180_manual_B_main_spec.json"),
    ("B-all", SPEC_DIR / "msc180_manual_B_all_spec.json"),
    ("C-main", SPEC_DIR / "msc180_manual_C_main_spec.json"),
    ("C-all", SPEC_DIR / "msc180_manual_C_all_spec.json"),
]

MODEL_CONFIGS = {
    "deepseek": {
        "model_id": "deepseek-ai/DeepSeek-Prover-V2-7B",
        "suffix": "deepseekv2_7b",
        "micro_batch_size": 4,
    },
    "goedel": {
        "model_id": "Goedel-LM/Goedel-Prover-V2-8B",
        "suffix": "goedelv2_8b",
        "micro_batch_size": 4,
    },
}

DATE_PREFIX = "20260213"

ATTEMPTS_PER_PROBLEM = 4
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


def _prompt_config_for_condition(condition: str):
    if condition in {"C-main", "C-all"}:
        return DeepSeekProverV2HintWithUsagePromptConfig
    return DeepSeekProverV2HintPromptConfig


def _run_spec(
    condition: str,
    spec_path: Path,
    output_path: Path,
    model,
    tokenizer,
    params: GenerationParams,
) -> None:
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec not found at {spec_path}")

    prompt_config = _prompt_config_for_condition(condition)
    spec = _load_json(spec_path)
    processors = _build_processors(spec)

    output: dict[str, object] = {}
    for key, processor in processors.items():
        print(f"[{condition}] {key}")
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


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 run_msc180_manual_suite.py <deepseek|goedel>")

    mode = sys.argv[1].strip().lower()
    cfg = MODEL_CONFIGS.get(mode)
    if not cfg:
        raise SystemExit("Mode must be one of: deepseek, goedel")

    params = GenerationParams(
        micro_batch_size=cfg["micro_batch_size"],
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_new_tokens=MAX_NEW_TOKENS,
    )

    model, tokenizer = load_artifacts(cfg["model_id"])
    suffix = cfg["suffix"]

    for condition, spec_path in SPEC_FILES:
        output_name = f"{DATE_PREFIX}_msc180-manual-{condition}_{suffix}_lean4-15.json"
        output_path = OUTPUT_DIR / output_name
        _run_spec(condition, spec_path, output_path, model, tokenizer, params)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
