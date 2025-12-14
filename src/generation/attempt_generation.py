import time
from typing import List, Optional

from ..verification import checking
from .generation_params import GenerationParams
from .batch_generation import generate_batch
from ..verification.http_client import LeanHTTPClient
from ..core.problem_structure import Attempt
from .prompt_config import PromptConfig


def generate_attempts_batch(
    config: PromptConfig,
    model,
    tokenizer,
    server_client: Optional[LeanHTTPClient],
    *,
    params: GenerationParams,
) -> List[Attempt]:
    """Generate a batch of proof attempts and verify them sequentially."""
    if params.batch_size <= 0:
        return []

    prompt = config.build()

    generation_start = time.time()
    raw_outputs = generate_batch(prompt, model, tokenizer, params)
    generation_time = time.time() - generation_start

    if not raw_outputs:
        return []

    parsed_proofs = [config.parser(output) for output in raw_outputs]
    average_generation_time = generation_time / len(parsed_proofs)

    attempts: List[Attempt] = []
    # Zip the raw and parsed outputs to handle them in pairs.
    for raw_output, parsed_proof in zip(raw_outputs, parsed_proofs):
        verification_start = time.time()
        success, message = checking.check_proof(
            parsed_proof,
            server_client,
            header=config.header(),
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

        if success:
            break

    return attempts
