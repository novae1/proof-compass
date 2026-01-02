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


def _normalize_doc_comment(informal_statement: Optional[str]) -> str:
    if not informal_statement:
        return ""
    stripped = informal_statement.strip()
    if stripped.startswith(_DOC_COMMENT_START) and stripped.endswith(_DOC_COMMENT_END):
        return stripped
    return f"{_DOC_COMMENT_START} {stripped} {_DOC_COMMENT_END}"


def _normalize_formal_statement(statement: str) -> str:
    trimmed = statement.strip()
    match = re.search(r":=\s*by\b", trimmed)
    if match:
        return trimmed[: match.end()].rstrip()
    return trimmed


class GoedelPromptConfig(PromptConfig):
    """Prompt configuration that matches `experiments/testing_goedel.py`."""

    _LEAN_BLOCK_PATTERN = re.compile(r"```lean4\s*(.*?)\s*```", re.DOTALL)

    _TEMPLATE = """
Your goal is to implement the following theorem, using Lean 4 and the mathlib library:

```lean4
{header}


{theorem}
```

Complete the following Lean 4 code:

```lean4
{header}

{theorem}
```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.
""".strip()

    @staticmethod
    def build(
        header: str,
        informal_statement: Optional[str],
        formal_statement: str,
    ) -> str:
        _ = informal_statement
        prompt = GoedelPromptConfig._TEMPLATE.format(
            header=header,
            theorem=formal_statement,
        )
        return textwrap.dedent(prompt)

    @staticmethod
    def parse(raw_output: str) -> str:
        matches = GoedelPromptConfig._LEAN_BLOCK_PATTERN.findall(raw_output)
        if matches:
            return matches[-1].strip()
        return raw_output.strip()


class DeepSeekProverCotPromptConfig(PromptConfig):
    """Prompt configuration for DeepSeek Prover v1.5 RL (COT)."""

    _LEAN_BLOCK_PATTERN = re.compile(r"```lean4\s*(.*?)\s*```", re.DOTALL)
    _PREFIX = (
        "Complete the following Lean 4 code with explanatory comments preceding each line of code:\n\n```lean4\n"
    )

    @staticmethod
    def build(
        header: str,
        informal_statement: Optional[str],
        formal_statement: str,
    ) -> str:
        header = header.strip()
        statement = _normalize_formal_statement(formal_statement)
        doc_comment = _normalize_doc_comment(informal_statement)

        body_parts = [header, ""]
        if doc_comment:
            body_parts.append(doc_comment)
        body_parts.append(statement)
        body = "\n".join(body_parts).rstrip()

        return f"{DeepSeekProverCotPromptConfig._PREFIX}{body}"

    @staticmethod
    def parse(raw_output: str) -> str:
        matches = DeepSeekProverCotPromptConfig._LEAN_BLOCK_PATTERN.findall(raw_output)
        if matches:
            return matches[-1].strip()
        return raw_output.strip()


class DeepSeekProverNonCotPromptConfig(PromptConfig):
    """Prompt configuration for DeepSeek Prover v1.5 RL (non-COT)."""

    _LEAN_BLOCK_PATTERN = re.compile(r"```lean4\s*(.*?)\s*```", re.DOTALL)
    _PREFIX = "Complete the following Lean 4 code:\n\n```lean4\n"

    @staticmethod
    def build(
        header: str,
        informal_statement: Optional[str],
        formal_statement: str,
    ) -> str:
        header = header.strip()
        statement = _normalize_formal_statement(formal_statement)
        doc_comment = _normalize_doc_comment(informal_statement)

        body_parts = [header, ""]
        if doc_comment:
            body_parts.append(doc_comment)
        body_parts.append(statement)
        body = "\n".join(body_parts).rstrip()

        return f"{DeepSeekProverNonCotPromptConfig._PREFIX}{body}"

    @staticmethod
    def parse(raw_output: str) -> str:
        matches = DeepSeekProverNonCotPromptConfig._LEAN_BLOCK_PATTERN.findall(raw_output)
        if matches:
            return matches[-1].strip()
        return raw_output.strip()
