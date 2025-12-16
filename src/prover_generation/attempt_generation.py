from __future__ import annotations

import time
from typing import Dict, List, Mapping, Optional

from .generation_params import GenerationParams
from .batch_generation import generate_batch
from .prompt_config import PromptConfig
from ..lean import checking
from ..lean.http_client import LeanHTTPClient
from ..core.problem_structure import Attempt


def generate_attempts(
    configs: Mapping[str, PromptConfig],
    model,
    tokenizer,
    server_client: Optional[LeanHTTPClient],
    *,
    params: GenerationParams,
    max_attempts_per_problem: int,
    stop_on_success: bool = True,
) -> Dict[str, List[Attempt]]:
    """Generate and verify attempts for multiple prompts.

    Returns a mapping from problem key to the attempts recorded for that problem.
    When `stop_on_success=True`, attempts are truncated at the first success per problem.

    Batching policy:
    - Repeatedly build a generation batch of up to `params.micro_batch_size` prompts.
    - Prefer draining the first active problem (dict insertion order) until it can no longer fill
      the micro-batch, then top up the remaining slots by draining subsequent active problems.
    - When `stop_on_success=True`, generation may still over-sample within the current micro-batch;
      additional samples scheduled for a problem after it verifies are skipped (not recorded).
    """
    if params.micro_batch_size <= 0:
        raise ValueError("GenerationParams.micro_batch_size must be positive.")

    if max_attempts_per_problem <= 0:
        return {key: [] for key in configs}

    if not configs:
        return {}

    keys = list(configs.keys())
    attempts_by_key: Dict[str, List[Attempt]] = {key: [] for key in keys}
    prompt_by_key = {key: configs[key].build() for key in keys}
    remaining: Dict[str, int] = {key: max_attempts_per_problem for key in keys}
    solved: set[str] = set()

    while True:
        current_key: Optional[str] = None
        for key in keys:
            if remaining[key] <= 0:
                continue
            if stop_on_success and key in solved:
                continue
            current_key = key
            break

        if current_key is None:
            break

        batch_keys: List[str] = []
        batch_prompts: List[str] = []
        slots_left = params.micro_batch_size

        current_take = min(remaining[current_key], slots_left)
        if current_take > 0:
            batch_keys.extend([current_key] * current_take)
            batch_prompts.extend([prompt_by_key[current_key]] * current_take)
            remaining[current_key] -= current_take
            slots_left -= current_take

        if slots_left > 0:
            for key in keys:
                if slots_left <= 0:
                    break
                if key == current_key:
                    continue
                if remaining[key] <= 0:
                    continue
                if stop_on_success and key in solved:
                    continue

                take = min(remaining[key], slots_left)
                if take <= 0:
                    continue
                batch_keys.extend([key] * take)
                batch_prompts.extend([prompt_by_key[key]] * take)
                remaining[key] -= take
                slots_left -= take

        if not batch_prompts:
            break

        generation_start = time.time()
        raw_outputs = generate_batch(batch_prompts, model, tokenizer, params)
        generation_time = time.time() - generation_start
        if not raw_outputs:
            continue

        average_generation_time = generation_time / len(raw_outputs)
        for key, raw_output in zip(batch_keys, raw_outputs):
            if stop_on_success and key in solved:
                continue

            config = configs[key]
            parsed_proof = config.parse(raw_output)

            verification_start = time.time()
            success, message = checking.check_proof(
                parsed_proof,
                server_client,
                header=config.header(),
            )
            verification_time = time.time() - verification_start

            attempts_by_key[key].append(
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
                solved.add(key)
                remaining[key] = 0

    return attempts_by_key
