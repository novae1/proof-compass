from __future__ import annotations

import re
import textwrap
from typing import Optional


class PromptConfig:
    """Stateless recipe for building and parsing prompts."""

    @staticmethod
    def build(
        header: str,
        informal_statement: Optional[str],
        formal_statement: str,
    ) -> str:
        raise NotImplementedError

    @staticmethod
    def parse(raw_output: str) -> str:
        return raw_output.strip()


_DOC_COMMENT_START = "/--"
_DOC_COMMENT_END = "-/"


def _normalize_informal_statement(informal_statement: Optional[str]) -> str:
    if not informal_statement:
        return ""
    stripped = informal_statement.strip()
    if stripped.startswith(_DOC_COMMENT_START) and stripped.endswith(_DOC_COMMENT_END):
        return stripped
    return f"{_DOC_COMMENT_START} {stripped}{_DOC_COMMENT_END}"


def _normalize_formal_statement(formal_statement: str) -> str:
    trimmed = formal_statement.strip()
    needle = ":= by"
    idx = trimmed.rfind(needle)
    if idx != -1:
        return trimmed[: idx + len(needle)].rstrip() + "\n  sorry"
    return trimmed


class GoedelPromptConfig(PromptConfig):
    """Prompt configuration that matches `experiments/testing_goedel.py`."""

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
        prompt += f"""\n\n\n{normalized_formal_statement}```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.
"""
        return prompt.strip()

    @staticmethod
    def parse(raw_output: str) -> str:
        """Not yet implemented."""
        return raw_output


class DeepSeekProverV2CoTPromptConfig(PromptConfig):
    """Prompt configuration for the DeepSeek-Prover-V2-7B model in CoT mode."""

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
        
        if informal_statement:
            normalized_informal_statement = _normalize_informal_statement(informal_statement)
            prompt += f"\n\n{normalized_informal_statement}"

        normalized_formal_statement = _normalize_formal_statement(formal_statement)
        prompt += f"""\n{normalized_formal_statement}
```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.
"""
        return prompt.strip()

    @staticmethod
    def parse(raw_output: str) -> str:
        """Not yet implemented."""
        return raw_output