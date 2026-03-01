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


_LEAN4_OPEN_RE = re.compile(r"```lean4\b", re.IGNORECASE)
_FENCE_CLOSE_RE = re.compile(r"(?m)^[ \t]*```[ \t]*$")


def _iter_lean4_blocks(raw_output: str) -> list[str]:
    blocks: list[str] = []
    for open_match in _LEAN4_OPEN_RE.finditer(raw_output):
        block_start = open_match.end()
        close_match = _FENCE_CLOSE_RE.search(raw_output, block_start)
        if close_match:
            blocks.append(raw_output[block_start:close_match.start()])
        else:
            blocks.append(raw_output[block_start:])
    return blocks


def _extract_theorem_from_text(text: str) -> str:
    lines = text.splitlines()
    theorem_starts: list[int] = []
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("theorem "):
            theorem_starts.append(idx)

    if not theorem_starts:
        return ""

    segments: list[str] = []
    for i, start in enumerate(theorem_starts):
        end = theorem_starts[i + 1] if i + 1 < len(theorem_starts) else len(lines)
        segment = "\n".join(lines[start:end]).strip()
        if segment:
            segments.append(segment)

    if not segments:
        return ""

    with_body = [segment for segment in segments if ":= by" in segment]
    if with_body:
        return with_body[-1]
    return segments[-1]


def _extract_last_theorem_block(raw_output: str) -> str:
    blocks = _iter_lean4_blocks(raw_output)
    if blocks:
        with_body: list[str] = []
        fallback: list[str] = []
        for block in blocks:
            theorem = _extract_theorem_from_text(block)
            if not theorem:
                continue
            fallback.append(theorem)
            if ":= by" in theorem:
                with_body.append(theorem)
        if with_body:
            return with_body[-1]
        if fallback:
            return fallback[-1]

    # Fallback for generations that do not use fenced code blocks.
    return _extract_theorem_from_text(raw_output)


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
        return _extract_last_theorem_block(str(raw_output))


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
        return _extract_last_theorem_block(str(raw_output))
