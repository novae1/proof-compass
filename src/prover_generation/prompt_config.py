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


def _normalize_formal_statement_without_sorry(formal_statement: str) -> str:
    trimmed = formal_statement.strip()
    needle = ":= by"
    idx = trimmed.rfind(needle)
    if idx != -1:
        return trimmed[: idx + len(needle)].rstrip() + "\n"
    return trimmed


_LEAN4_BLOCK_RE = re.compile(r"```lean4\s*(.*?)```", re.DOTALL)


def _extract_last_theorem_block(raw_output: str) -> str:
    matches = list(_LEAN4_BLOCK_RE.finditer(raw_output))
    if not matches:
        return ""

    block = matches[-1].group(1)
    lines = block.splitlines()
    last_idx = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("theorem "):
            last_idx = idx

    if last_idx is None:
        return ""

    return "\n".join(lines[last_idx:]).strip()


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
        return _extract_last_theorem_block(str(raw_output))


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


class KiminaProverPromptConfig(PromptConfig):
    """Prompt configuration that matches the Kimina-Prover example format."""

    @staticmethod
    def build(
        header: str,
        informal_statement: Optional[str],
        formal_statement: str,
    ) -> str:
        prompt = "Think about and solve the following problem step by step in Lean 4."
        normalized_formal_statement = _normalize_formal_statement_without_sorry(formal_statement)
        
        if informal_statement:
            normalized_informal_statement = _normalize_informal_statement(informal_statement)
            prompt += f"\n# Problem:{informal_statement}"
            normalized_formal_statement = normalized_informal_statement + "\n" + normalized_formal_statement

        prompt += f"\n# Formal statement:\n```lean4\n{header.strip()}\n\n{normalized_formal_statement}```\n"
        return prompt

    @staticmethod
    def parse(raw_output: str) -> str:
        """Not yet implemented."""
        return raw_output
