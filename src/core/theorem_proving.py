from __future__ import annotations

from typing import Mapping, Optional

from .problem_structure import TheoremProcessor
from ..lean.http_client import LeanHTTPClient
from ..prover_generation.attempt_generation import generate_attempts
from ..prover_generation.generation_params import GenerationParams
from ..prover_generation.prompt_factory import make_prompt_config


def synthesize_proof_attempts_many(
    processors: Mapping[str, TheoremProcessor],
    model,
    tokenizer,
    server_client: Optional[LeanHTTPClient],
    *,
    model_id: str,
    max_attempts_per_problem: int,
    generation_params: GenerationParams,
    stop_on_success: bool = True,
) -> None:
    """Generate proof attempts for many processors and attach them in-place."""
    if max_attempts_per_problem <= 0:
        return

    if generation_params.micro_batch_size <= 0:
        raise ValueError("GenerationParams.micro_batch_size must be positive.")

    configs = {
        key: make_prompt_config(
            model_id,
            formal_statement=processor.formal_statement,
            header=processor.header,
            informal_statement=processor.informal_statement,
            nl_proof=processor.nl_proof,
        )
        for key, processor in processors.items()
    }

    attempts_by_key = generate_attempts(
        configs,
        model,
        tokenizer,
        server_client,
        params=generation_params,
        max_attempts_per_problem=max_attempts_per_problem,
        stop_on_success=stop_on_success,
    )

    for key, attempts in attempts_by_key.items():
        processor = processors[key]
        for attempt in attempts:
            processor.add_attempt(attempt)
