from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional

from ..verification.http_client import LeanHTTPClient
from ..core.problem_structure import TheoremProcessor
from ..core.theorem_proving import synthesize_proof_attempts
from ..generation.generation_params import GenerationParams


Benchmark = Mapping[str, Mapping[str, Any]]


def build_processors(benchmark: Benchmark) -> dict[str, TheoremProcessor]:
    """Instantiate processors for each problem in the benchmark."""
    processors: dict[str, TheoremProcessor] = {}
    for name, problem in benchmark.items():
        try:
            formal_statement = problem["formal_statement"]
        except KeyError as exc:
            raise KeyError(f"Benchmark problem '{name}' is missing 'formal_statement'.") from exc

        processors[name] = TheoremProcessor(
            formal_statement=formal_statement,
            header=problem.get("header"),
            informal_statement=problem.get("informal_statement"),
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
    generation_params: GenerationParams,
    checkpoint_path: Path | str,
) -> dict[str, TheoremProcessor]:
    """Solve every problem in the benchmark and checkpoint after each one."""
    processors = build_processors(benchmark)

    i = 0
    for processor in processors.values():
        
        i += 1
        synthesize_proof_attempts(
            processor=processor,
            model=model,
            tokenizer=tokenizer,
            server_client=server_client,
            num_attempts=num_attempts,
            generation_params=generation_params,
        )
        save_processors(processors, checkpoint_path)
        print(i)

    return processors
