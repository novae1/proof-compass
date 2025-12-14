from typing import List, Optional

from .problem_structure import TheoremProcessor, Attempt
from ..verification.http_client import LeanHTTPClient
from ..generation import attempt_generation
from ..generation.generation_params import GenerationParams


def synthesize_proof_attempts(
    processor: TheoremProcessor,
    model,
    tokenizer,
    server_client: Optional[LeanHTTPClient],
    *,
    num_attempts: int,
    generation_params: GenerationParams,
    # Note: The way cot is passed may change in the future.
    cot: str = "",
) -> None:
    """Generate proof attempts for the given processor and capture the results."""
    if num_attempts <= 0:
        return
    if generation_params.batch_size <= 0:
        raise ValueError("GenerationParams.batch_size must be positive.")

    config = generation_params.make_prompt_config(
        formal_statement=processor.formal_statement,
        header=processor.header,
        cot=cot,
        informal_statement=processor.informal_statement,
    )

    for i in range(0, num_attempts, generation_params.batch_size):
        current_batch_size = min(generation_params.batch_size, num_attempts - i)
        batch_params = (
            generation_params
            if current_batch_size == generation_params.batch_size
            else generation_params.with_batch_size(current_batch_size)
        )

        new_attempts: List[Attempt] = attempt_generation.generate_attempts_batch(
            config,
            model,
            tokenizer,
            server_client,
            params=batch_params,
        )

        for attempt in new_attempts:
            processor.add_attempt(attempt)
