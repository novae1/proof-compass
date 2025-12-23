from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional
import textwrap

class PromptConfig:
    """Recipe for building and parsing prompts for proof generation."""

    def build(self) -> str:
        raise NotImplementedError

    def parse(self, raw_output: str) -> str:
        return raw_output.strip()

    def header(self) -> str:
        raise NotImplementedError


Parser = Callable[[str], str]

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


def _format_nl_proof_block(nl_proof: str) -> str:
    proof = nl_proof.strip("\n")
    lines = proof.splitlines() if proof else [""]
    indented = "\n".join(f"  {line}" if line else "  " for line in lines)
    return f"  /-\n{indented}\n  -/"


@dataclass(frozen=True)
class DefaultPromptConfig(PromptConfig):
    """Default prompting strategy (easy to replace later)."""

    formal_statement: str
    header_text: str
    informal_statement: Optional[str] = None
    nl_proof: Optional[str] = None
    parser: Optional[Parser] = None

    _LEAN_BLOCK_PATTERN = re.compile(r"```lean4\s*(.*?)\s*```", re.DOTALL)

    def header(self) -> str:
        return self.header_text

    def build(self) -> str:
        statement = self.formal_statement.strip()
        if statement and not statement.endswith("sorry"):
            statement = f"{statement}\n  sorry"

        nl_proof = (self.nl_proof or "").strip()
        proof_block = f"\n\nThe English proof is as follows:\n```text\n{nl_proof}\n```" if nl_proof else ""

        return (
            "Complete the following Lean 4 code:\n\n"
            "```lean4\n"
            f"{self.header_text}\n\n{statement}\n"
            "```\n"
            f"{proof_block}\n\n"
            "Before producing the Lean 4 code to formally prove the given theorem, "
            "provide a detailed proof plan outlining the main proof steps and strategies."
        ).strip()

    def parse(self, raw_output: str) -> str:
        if self.parser is not None:
            return self.parser(raw_output)
        matches = self._LEAN_BLOCK_PATTERN.findall(raw_output)
        if matches:
            return matches[-1].strip()
        return raw_output.strip()


@dataclass(frozen=True)
class GoedelPromptConfig(PromptConfig):
    """Prompt configuration that matches `experiments/testing_goedel.py` exactly."""

    formal_statement: str
    header_text: str
    nl_proof: Optional[str] = None
    parser: Optional[Parser] = None

    _LEAN_BLOCK_PATTERN = re.compile(r"```lean4\s*(.*?)\s*```", re.DOTALL)

    _NO_NL_TEMPLATE = """
Complete the following Lean 4 code:

```lean4
{}```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.
""".strip()

    def header(self) -> str:
        return self.header_text

    def build(self) -> str:
        theorem = self.formal_statement
        nl_proof = (self.nl_proof or "").strip()

        if not nl_proof:
            lean_block = f"{self.header_text}\n\n{theorem}"
            return self._NO_NL_TEMPLATE.format(lean_block)

        # Matches `build_goedel_prompt` in `experiments/testing_goedel.py`.
        return textwrap.dedent(
            f"""\
Your goal is to implement the following theorem, using Lean 4 and the mathlib library:

```lean4
{self.header_text}


{theorem}
```

The English proof is as follows:
```text
{nl_proof}
```

Complete the following Lean 4 code:

```lean4
{self.header_text}

{theorem}
```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof."""
        )

    def parse(self, raw_output: str) -> str:
        if self.parser is not None:
            return self.parser(raw_output)
        matches = self._LEAN_BLOCK_PATTERN.findall(raw_output)
        if matches:
            return matches[-1].strip()
        return raw_output.strip()


@dataclass(frozen=True)
class DeepSeekProverCotPromptConfig(PromptConfig):
    """Prompt configuration for DeepSeek Prover v1.5 RL (COT)."""

    formal_statement: str
    header_text: str
    informal_statement: Optional[str] = None
    nl_proof: Optional[str] = None
    parser: Optional[Parser] = None

    _LEAN_BLOCK_PATTERN = re.compile(r"```lean4\s*(.*?)\s*```", re.DOTALL)
    _PREFIX = "Complete the following Lean 4 code with explanatory comments preceding each line of code:\n\n```lean4\n"

    def header(self) -> str:
        return self.header_text

    def build(self) -> str:
        header = self.header_text.strip()
        statement = _normalize_formal_statement(self.formal_statement)
        doc_comment = _normalize_doc_comment(self.informal_statement)

        body_parts = [header, ""]
        if doc_comment:
            body_parts.append(doc_comment)
        body_parts.append(statement)
        body = "\n".join(body_parts).rstrip()

        if self.nl_proof:
            body = f"{body}\n{_format_nl_proof_block(self.nl_proof)}"

        return f"{self._PREFIX}{body}"

    def parse(self, raw_output: str) -> str:
        if self.parser is not None:
            return self.parser(raw_output)
        matches = self._LEAN_BLOCK_PATTERN.findall(raw_output)
        if matches:
            return matches[-1].strip()
        return raw_output.strip()


@dataclass(frozen=True)
class DeepSeekProverNonCotPromptConfig(PromptConfig):
    """Prompt configuration for DeepSeek Prover v1.5 RL (non-COT)."""

    formal_statement: str
    header_text: str
    informal_statement: Optional[str] = None
    parser: Optional[Parser] = None

    _LEAN_BLOCK_PATTERN = re.compile(r"```lean4\s*(.*?)\s*```", re.DOTALL)
    _PREFIX = "Complete the following Lean 4 code:\n\n```lean4\n"

    def header(self) -> str:
        return self.header_text

    def build(self) -> str:
        header = self.header_text.strip()
        statement = _normalize_formal_statement(self.formal_statement)
        doc_comment = _normalize_doc_comment(self.informal_statement)

        body_parts = [header, ""]
        if doc_comment:
            body_parts.append(doc_comment)
        body_parts.append(statement)
        body = "\n".join(body_parts).rstrip()

        return f"{self._PREFIX}{body}"

    def parse(self, raw_output: str) -> str:
        if self.parser is not None:
            return self.parser(raw_output)
        matches = self._LEAN_BLOCK_PATTERN.findall(raw_output)
        if matches:
            return matches[-1].strip()
        return raw_output.strip()
