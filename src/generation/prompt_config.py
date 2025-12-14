from __future__ import annotations
import re
from typing import Callable, Optional

# This remains a module-level constant.
DEFAULT_HEADER = """import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat

"""

# Define the type alias for clarity.
Parser = Callable[[str], str]

class PromptConfig:
    """A self-contained recipe for generating and parsing Lean proofs."""

    def __init__(
        self,
        *,
        formal_statement: str,
        header: str,
        informal_statement: Optional[str] = None,
        parser: Optional[Parser] = None,
    ):
        self._formal_statement = formal_statement
        self._header = header
        self._informal_statement = informal_statement

        # Parser modifies model outputs into lean-verifiable format
        self.parser: Parser = parser if parser is not None else (lambda raw_output: raw_output)

    def build(self) -> str:
        """Construct the prompt fed to the language model."""
        raise NotImplementedError("PromptConfig.build() must be implemented by subclasses.")

    def header(self) -> str:
        """Returns the header text."""
        return self._header or DEFAULT_HEADER


class DSPV2PromptConfig(PromptConfig):
    """Prompt configuration tailored for DeepSeek-Prover v2 style prompting."""

    PROMPT_TEMPLATE = """Complete the following Lean 4 code:

```lean4
{}
```

Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.
""".strip()

    _LEAN_BLOCK_PATTERN = re.compile(r"```lean4\s*(.*?)\s*```", re.DOTALL)

    def __init__(
        self,
        *,
        formal_statement: str,
        header: str,
        cot: Optional[str] = None,
        informal_statement: Optional[str] = None,
    ):
        super().__init__(
            formal_statement=formal_statement,
            header=header,
            informal_statement=informal_statement,
            parser=self._parse_model_output,
        )
        self._cot = cot

    def build(self) -> str:
        """Render the prompt using the DeepSeek-Prover v2 template."""
        header_block = self.header().strip()

        informal_block = ""
        if self._informal_statement:
            informal_text = self._informal_statement.strip()
            if informal_text:
                single_line = " ".join(informal_text.splitlines())
                informal_block = f"/-- {single_line}-/"

        statement_block = self._formal_statement.strip()
        if not statement_block.endswith("sorry"):
            statement_block = f"{statement_block}\n  sorry"

        body_parts = [part for part in (informal_block, statement_block) if part]
        body_code = "\n".join(body_parts)

        if header_block:
            lean_code = f"{header_block}\n\n{body_code}" if body_code else header_block
        else:
            lean_code = body_code

        prompt = self.PROMPT_TEMPLATE.format(lean_code)

        if self._cot:
            cot_block = self._cot.strip()
            if cot_block:
                prompt = f"{prompt}\n\n{cot_block}"

        return prompt

    @staticmethod
    def _parse_model_output(raw_output: str) -> str:
        matches = DSPV2PromptConfig._LEAN_BLOCK_PATTERN.findall(raw_output)
        if not matches:
            return raw_output.strip()
        return matches[-1].strip()
