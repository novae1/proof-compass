from __future__ import annotations

from typing import Optional

from src.prover_generation.prompt_config import (
    PromptConfig,
    _extract_last_theorem_block,
    _normalize_formal_statement,
)


class DeepSeekProverV2HintPromptConfig(PromptConfig):
    """Prompt config that injects a single Mathlib theorem hint after the target statement."""

    @staticmethod
    def build(
        header: str,
        informal_statement: Optional[str],
        formal_statement: str,
    ) -> str:
        prompt = f"""
Complete the following Lean 4 code:

```lean4
{header.strip()}"""

        normalized_formal_statement = _normalize_formal_statement(formal_statement)
        prompt += f"""\n{normalized_formal_statement}
```
"""

        hint = (informal_statement or "").strip()
        if hint:
            prompt += f"""
The following Mathlib statement can be used in your formal proof. It is already part of Mathlib; do not try to prove or restate it in your output.

```lean4
{hint}
```
"""

        prompt += """
Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.
"""
        return prompt.strip()

    @staticmethod
    def parse(raw_output: str) -> str:
        return _extract_last_theorem_block(str(raw_output))
