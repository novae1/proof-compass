from __future__ import annotations

from typing import Optional

from .prompt_config import (
    DeepSeekProverCotPromptConfig,
    DeepSeekProverNonCotPromptConfig,
    DefaultPromptConfig,
    GoedelPromptConfig,
    PromptConfig,
)


def make_prompt_config(
    model_id: str,
    *,
    formal_statement: str,
    header: str,
    informal_statement: Optional[str],
    nl_proof: Optional[str],
) -> PromptConfig:
    """Build the prompt configuration for a theorem/model pair.

    For now this defaults to a single prompt style; model-specific prompting can be added later.
    """
    _ = informal_statement
    if model_id == "deepseek-prover-v15-cot":
        return DeepSeekProverCotPromptConfig(
            formal_statement=formal_statement,
            header_text=header,
            informal_statement=informal_statement,
            nl_proof=nl_proof,
        )
    if model_id == "deepseek-prover-v15-noncot":
        return DeepSeekProverNonCotPromptConfig(
            formal_statement=formal_statement,
            header_text=header,
            informal_statement=informal_statement,
        )
    if "Goedel" in model_id:
        return GoedelPromptConfig(
            formal_statement=formal_statement,
            header_text=header,
            nl_proof=nl_proof,
        )

    return DefaultPromptConfig(
        formal_statement=formal_statement,
        header_text=header,
        informal_statement=informal_statement,
        nl_proof=nl_proof,
    )
