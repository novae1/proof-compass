from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional

from ..lean.http_client import LeanHTTPClient
from ..core.problem_structure import TheoremProcessor
from ..core.theorem_proving import synthesize_proof_attempts_many
from ..prover_generation.generation_params import GenerationParams


Benchmark = Mapping[str, Mapping[str, Any]]


def build_processors(benchmark: Benchmark) -> dict[str, TheoremProcessor]:
    """Instantiate processors for each problem in the benchmark."""
    processors: dict[str, TheoremProcessor] = {}
    for name, problem in benchmark.items():
        try:
            formal_statement = problem["formal_statement"]
        except KeyError as exc:
            raise KeyError(f"Benchmark problem '{name}' is missing 'formal_statement'.") from exc

        header = problem.get("header")
        if not header or not str(header).strip():
            raise KeyError(f"Benchmark problem '{name}' is missing a non-empty 'header'.")

        processors[name] = TheoremProcessor(
            formal_statement=formal_statement,
            header=str(header),
            informal_statement=problem.get("informal_statement"),
            nl_proof=problem.get("nl_proof"),
        )

    return processors


def save_processors(processors: Mapping[str, TheoremProcessor], path: Path | str) -> None:
    """Persist processors to disk as JSON using their serialized form."""
    payload = {name: processor.to_dict() for name, processor in processors.items()}
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n")


def solve_benchmark(
    benchmark: Benchmark,
    *,
    model,
    tokenizer,
    server_client: Optional[LeanHTTPClient],
    num_attempts: int,
    model_id: str,
    generation_params: GenerationParams,
    checkpoint_path: Path | str,
) -> dict[str, TheoremProcessor]:
    """Solve every problem in the benchmark and checkpoint once at the end."""
    processors = build_processors(benchmark)

    synthesize_proof_attempts_many(
        processors=processors,
        model=model,
        tokenizer=tokenizer,
        server_client=server_client,
        model_id=model_id,
        max_attempts_per_problem=num_attempts,
        generation_params=generation_params,
    )
    save_processors(processors, checkpoint_path)

    return processors
