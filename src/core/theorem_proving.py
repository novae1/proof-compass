from __future__ import annotations

import time
from typing import Optional

from .problem_structure import Attempt, TheoremProcessor
from ..lean import checking
from ..lean.http_client import LeanHTTPClient
from ..prover_generation.batch_generation import generate_batch
from ..prover_generation.generation_params import GenerationParams
from ..prover_generation.prompt_config import PromptConfig


def generate_attempts(
    processor: TheoremProcessor,
    prompt_config: type[PromptConfig],
    model,
    tokenizer,
    server_client: Optional[LeanHTTPClient],
    *,
    params: GenerationParams,
    max_attempts: int,
    stop_on_success: bool = True,
) -> list[Attempt]:
    """Generate and verify attempts for a single processor."""
    if params.micro_batch_size <= 0:
        raise ValueError("GenerationParams.micro_batch_size must be positive.")

    if max_attempts <= 0:
        return []

    prompt = prompt_config.build(
        processor.header,
        processor.informal_statement,
        processor.formal_statement,
    )

    remaining = max_attempts
    attempts: list[Attempt] = []
    solved = False

    while remaining > 0:
        batch_size = min(params.micro_batch_size, remaining)
        remaining -= batch_size

        batch_prompts = [prompt] * batch_size
        generation_start = time.time()
        raw_outputs = generate_batch(batch_prompts, model, tokenizer, params)
        generation_time = time.time() - generation_start
        if not raw_outputs:
            continue

        average_generation_time = generation_time / len(raw_outputs)
        for raw_output in raw_outputs:
            if stop_on_success and solved:
                continue

            parsed_proof = prompt_config.parse(raw_output)

            verification_start = time.time()
            success, message = checking.check_proof(
                parsed_proof,
                server_client,
                header=processor.header,
            )
            verification_time = time.time() - verification_start

            attempts.append(
                Attempt(
                    success=success,
                    raw_output=raw_output,
                    parsed_proof=parsed_proof,
                    message=message,
                    generation_time=average_generation_time,
                    verification_time=verification_time,
                )
            )

            if stop_on_success and success:
                solved = True
                remaining = 0
                break

    return attempts


def synthesize_proof_attempts(
    processors: dict[str, TheoremProcessor],
    model,
    tokenizer,
    server_client: Optional[LeanHTTPClient],
    *,
    prompt_config: type[PromptConfig],
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

    _ = model_id

    for key, processor in processors.items():
        _ = key
        attempts = generate_attempts(
            processor,
            prompt_config,
            model,
            tokenizer,
            server_client,
            params=generation_params,
            max_attempts=max_attempts_per_problem,
            stop_on_success=stop_on_success,
        )
        for attempt in attempts:
            processor.add_attempt(attempt)
