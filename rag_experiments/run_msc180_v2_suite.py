#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.problem_structure import TheoremProcessor
from src.prover_generation.artifacts import load_artifacts
from src.prover_generation.generation_params import GenerationParams
from src.prover_generation.theorem_proving import generate_attempts
from prompt_hints.prompt_config import DeepSeekProverV2HintPromptConfig


EXPERIMENT_DIR = Path(__file__).resolve().parent
SPEC_DIR = EXPERIMENT_DIR / "specs"
OUTPUT_DIR = EXPERIMENT_DIR / "outputs"

SPEC_FILES = [
    ("A", "no-hint", SPEC_DIR / "msc180_v2_A_spec.json"),
    ("B", "theorem-statements", SPEC_DIR / "msc180_v2_B_spec.json"),
    ("C", "theorem-statements-and-examples", SPEC_DIR / "msc180_v2_C_spec.json"),
]

MODEL_CONFIGS = {
    "deepseek": {
        "model_id": "deepseek-ai/DeepSeek-Prover-V2-7B",
        "suffix": "deepseekv2_7b",
        "micro_batch_size": 4,
    }
}

DATE_PREFIX = "20260217"

ATTEMPTS_PER_PROBLEM = 8
TEMPERATURE = 1.0
TOP_P = 0.95
MAX_NEW_TOKENS = 7000
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


def _normalize_problem_key(problem_key: str) -> str:
    return problem_key.replace("/", "_")


def _run_spec(
    *,
    condition_tag: str,
    group_prefix: str,
    spec_path: Path,
    output_path: Path,
    output_payload: dict[str, object],
    model,
    tokenizer,
    params: GenerationParams,
) -> None:
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec not found at {spec_path}")

    spec = _load_json(spec_path)
    processors = _build_processors(spec)

    for key, processor in processors.items():
        merged_key = f"{group_prefix}/{_normalize_problem_key(key)}"
        existing = output_payload.get(merged_key)
        existing_attempts: list[object] = []
        if isinstance(existing, dict):
            prior_attempts = existing.get("attempts")
            if isinstance(prior_attempts, list):
                existing_attempts = prior_attempts

        existing_count = len(existing_attempts)
        if existing_count >= ATTEMPTS_PER_PROBLEM:
            print(f"[{condition_tag}] {key} (skip: already {existing_count}/{ATTEMPTS_PER_PROBLEM})")
            continue

        remaining = ATTEMPTS_PER_PROBLEM - existing_count
        print(f"[{condition_tag}] {key} ({existing_count}/{ATTEMPTS_PER_PROBLEM} done, generating {remaining})")
        attempts = generate_attempts(
            processor,
            DeepSeekProverV2HintPromptConfig,
            model,
            tokenizer,
            server_client=None,
            params=params,
            max_attempts=remaining,
            stop_on_success=STOP_ON_SUCCESS,
        )
        for attempt in attempts:
            processor.add_attempt(attempt)

        entry = processor.to_dict()
        if existing_attempts:
            entry["attempts"] = [*existing_attempts, *entry.get("attempts", [])]
        output_payload[merged_key] = entry
        _save_json(output_payload, output_path)

    print(f"Updated combined output at {output_path}")


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 run_msc180_v2_suite.py <deepseek>")

    mode = sys.argv[1].strip().lower()
    cfg = MODEL_CONFIGS.get(mode)
    if not cfg:
        raise SystemExit("Mode must be: deepseek")

    params = GenerationParams(
        micro_batch_size=cfg["micro_batch_size"],
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_new_tokens=MAX_NEW_TOKENS,
    )

    model, tokenizer = load_artifacts(cfg["model_id"])
    suffix = cfg["suffix"]

    output_name = f"{DATE_PREFIX}_msc180-v2_{suffix}_lean4-15.json"
    output_path = OUTPUT_DIR / output_name
    if output_path.exists():
        loaded = _load_json(output_path)
        if not isinstance(loaded, dict):
            raise TypeError(f"Existing output must be a JSON object: {output_path}")
        output_payload: dict[str, object] = loaded
        print(f"Resuming existing output: {output_path} ({len(output_payload)} entries)")
    else:
        output_payload = {}

    for condition_tag, group_prefix, spec_path in SPEC_FILES:
        _run_spec(
            condition_tag=condition_tag,
            group_prefix=group_prefix,
            spec_path=spec_path,
            output_path=output_path,
            output_payload=output_payload,
            model=model,
            tokenizer=tokenizer,
            params=params,
        )

    print(f"Wrote combined attempts to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
