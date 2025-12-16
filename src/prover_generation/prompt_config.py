from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Optional

class PromptConfig:
    """Recipe for building and parsing prompts for proof generation."""

    def build(self) -> str:
        raise NotImplementedError

    def parse(self, raw_output: str) -> str:
        return raw_output.strip()

    def header(self) -> str:
        raise NotImplementedError


Parser = Callable[[str], str]


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
