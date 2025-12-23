#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.problem_structure import TheoremProcessor
from src.core.theorem_proving import synthesize_proof_attempts_many
from src.lean.http_client import LeanHTTPClient
from src.prover_generation.artifacts import load_artifacts
from src.prover_generation.generation_params import GenerationParams


Benchmark = Mapping[str, Mapping[str, object]]

BENCHMARK_PATH = Path("benchmarks/processed/miniF2F_mathd_variants.json")
CHECKPOINT_PATH = Path("experiments/mathd_runs/checkpoint.json")
ATTEMPTS_PER_VARIANT = 4
MICRO_BATCH_SIZE = 6
TEMPERATURE = 1.0
TOP_P = 0.95
MAX_NEW_TOKENS = 2048
SERVER_URL = ""
MODEL_ID = "deepseek-ai/DeepSeek-Prover-V1.5-RL"
COT_PROMPT_ID = "deepseek-prover-v15-cot"
NONCOT_PROMPT_ID = "deepseek-prover-v15-noncot"


def _load_benchmark(path: Path) -> Benchmark:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_processors(
    benchmark: Benchmark,
) -> tuple[dict[str, dict[str, TheoremProcessor]], dict[str, dict[str, TheoremProcessor]]]:
    processors_by_problem: dict[str, dict[str, TheoremProcessor]] = {}
    processors_by_style: dict[str, dict[str, TheoremProcessor]] = {"cot": {}, "noncot": {}}

    for problem_id in sorted(benchmark):
        item = benchmark[problem_id]
        formal_statement = item["formal_statement"]
        header = item["header"]
        informal_statement = item.get("informal_statement")
        variants = item.get("variants")
        if not variants:
            raise KeyError(f"Problem '{problem_id}' is missing variants.")

        processors_by_problem[problem_id] = {}
        for variant_name, variant in variants.items():
            _ = variant.get("model_id")
            nl_proof = variant.get("nl_proof")
            processor = TheoremProcessor(
                formal_statement=formal_statement,
                header=header,
                informal_statement=informal_statement,
                nl_proof=nl_proof,
            )
            processors_by_problem[problem_id][variant_name] = processor
            style = "noncot" if variant_name == "noncot" else "cot"
            processors_by_style.setdefault(style, {})[
                f"{problem_id}/{variant_name}"
            ] = processor

    return processors_by_problem, processors_by_style


def _save_nested_processors(
    processors_by_problem: Mapping[str, Mapping[str, TheoremProcessor]],
    path: Path,
) -> None:
    payload: dict[str, dict[str, object]] = {}
    for problem_id, variants in processors_by_problem.items():
        payload[problem_id] = {
            variant_name: processor.to_dict() for variant_name, processor in variants.items()
        }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_mathd_variants(
    *,
    benchmark_path: Path,
    checkpoint_path: Path,
    attempts_per_variant: int,
    generation_params: GenerationParams,
    server_url: str,
) -> None:
    benchmark = _load_benchmark(benchmark_path)
    processors_by_problem, processors_by_style = _build_processors(benchmark)

    if not processors_by_style.get("cot") and not processors_by_style.get("noncot"):
        raise ValueError("No variants were found to run.")

    server_client = LeanHTTPClient(server_url) if server_url else None

    model, tokenizer = load_artifacts(MODEL_ID)

    for round_idx in range(attempts_per_variant):
        cot_processors = processors_by_style.get("cot", {})
        if cot_processors:
            synthesize_proof_attempts_many(
                processors=cot_processors,
                model=model,
                tokenizer=tokenizer,
                server_client=server_client,
                model_id=COT_PROMPT_ID,
                max_attempts_per_problem=1,
                generation_params=generation_params,
                stop_on_success=False,
            )
        noncot_processors = processors_by_style.get("noncot", {})
        if noncot_processors:
            synthesize_proof_attempts_many(
                processors=noncot_processors,
                model=model,
                tokenizer=tokenizer,
                server_client=server_client,
                model_id=NONCOT_PROMPT_ID,
                max_attempts_per_problem=1,
                generation_params=generation_params,
                stop_on_success=False,
            )
        _save_nested_processors(processors_by_problem, checkpoint_path)
        print(
            f"checkpointed round {round_idx + 1}/{attempts_per_variant} -> {checkpoint_path}"
        )


def main() -> int:
    params = GenerationParams(
        micro_batch_size=MICRO_BATCH_SIZE,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_new_tokens=MAX_NEW_TOKENS,
    )
    run_mathd_variants(
        benchmark_path=BENCHMARK_PATH,
        checkpoint_path=CHECKPOINT_PATH,
        attempts_per_variant=ATTEMPTS_PER_VARIANT,
        generation_params=params,
        server_url=SERVER_URL,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
