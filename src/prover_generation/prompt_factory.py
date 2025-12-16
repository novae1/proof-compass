from __future__ import annotations

from typing import Optional

from .prompt_config import DefaultPromptConfig, PromptConfig


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
    _ = model_id
    return DefaultPromptConfig(
        formal_statement=formal_statement,
        header_text=header,
        informal_statement=informal_statement,
        nl_proof=nl_proof,
    )

