from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable, Dict, Optional, Tuple

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase

from .prompt_config import PromptConfig, DSPV2PromptConfig
from .model_registry import model_path

PromptConfigBuilder = Callable[[str, str, Optional[str], Optional[str]], PromptConfig]


def _build_dspv2_prompt_config(
    formal_statement: str,
    header: str,
    informal_statement: Optional[str],
    cot: Optional[str],
) -> PromptConfig:
    return DSPV2PromptConfig(
        formal_statement=formal_statement,
        header=header,
        informal_statement=informal_statement,
        cot=cot,
    )


PROMPT_CONFIG_BUILDERS: Dict[str, PromptConfigBuilder] = {
    "deepseek-ai/DeepSeek-Prover-V2-7B": _build_dspv2_prompt_config,
    #"Goedel-LM/Goedel-Prover-V2-8B": _build_dspv2_prompt_config,
    #"deepseek-ai/DeepSeek-Prover-V1.5-RL": _build_dspv2_prompt_config,
}


@dataclass(frozen=True)
class GenerationParams:
    """All configuration needed to sample proofs from the language model."""

    batch_size: int
    model_id: str
    temperature: float = 1.0
    top_p: float = 0.95
    max_new_tokens: int = 8192

    def with_batch_size(self, batch_size: int) -> GenerationParams:
        """Clone the configuration with a different batch size."""
        return replace(self, batch_size=batch_size)

    def make_prompt_config(
        self,
        *,
        formal_statement: str,
        header: str,
        informal_statement: Optional[str],
        cot: Optional[str],
    ) -> PromptConfig:
        """Create the prompt configuration associated with this generation profile."""
        try:
            builder = PROMPT_CONFIG_BUILDERS[self.model_id]
        except KeyError as exc:
            raise ValueError(f"Unsupported model_id '{self.model_id}'.") from exc
        return builder(
            formal_statement=formal_statement,
            header=header,
            informal_statement=informal_statement,
            cot=cot,
        )

    def load_artifacts(self) -> Tuple[PreTrainedModel, PreTrainedTokenizerBase]:
        """Instantiate model and tokenizer using HuggingFace Transformers."""
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA device required for generation but was not found.")

        source_path = model_path(self.model_id)
        if not source_path.exists():
            raise FileNotFoundError(
                f"Model files for '{self.model_id}' were not found at '{source_path}'. "
                "Run scripts/download_model.py to fetch them."
            )
        source_str = str(source_path)

        tokenizer = AutoTokenizer.from_pretrained(source_str, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            source_str,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
        )
        return model, tokenizer
