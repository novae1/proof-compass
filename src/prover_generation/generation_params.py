from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class GenerationParams:
    """Sampling settings used during generation.

    `micro_batch_size` controls how many prompts are sent in a single `model.generate` call.
    """

    micro_batch_size: int
    temperature: float = 1.0
    top_p: float = 0.95
    max_new_tokens: int = 8192

    def with_micro_batch_size(self, micro_batch_size: int) -> GenerationParams:
        return replace(self, micro_batch_size=micro_batch_size)
