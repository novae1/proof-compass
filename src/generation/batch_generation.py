from __future__ import annotations

from typing import List

import torch
from transformers import PreTrainedModel, PreTrainedTokenizerBase

from .generation_params import GenerationParams


def _ensure_pad_token(tokenizer: PreTrainedTokenizerBase) -> int:
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer.pad_token_id


def generate_batch(
    prompt: str,
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    params: GenerationParams,
) -> List[str]:
    """Generate multiple samples from a single prompt using HuggingFace Transformers."""
    if params.batch_size <= 0:
        raise ValueError("batch_size must be positive")

    if tokenizer is None:
        raise ValueError("tokenizer is required for batch generation")

    formatted_prompt = prompt
    if hasattr(tokenizer, "apply_chat_template"):
        formatted_prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )

    prompts = [formatted_prompt] * params.batch_size

    pad_token_id = _ensure_pad_token(tokenizer)
    target_device = torch.device("cuda")

    encoded = tokenizer(
        prompts,
        return_tensors="pt",
        padding=True,
        truncation=True,
    )
    inputs = {k: v.to(target_device) for k, v in encoded.items()}

    outputs = model.generate(
        **inputs,
        do_sample=True,
        temperature=params.temperature,
        top_p=params.top_p,
        max_new_tokens=params.max_new_tokens,
        pad_token_id=pad_token_id,
    )

    generations: List[str] = []
    for idx in range(outputs.size(0)):
        generations.append(tokenizer.decode(outputs[idx], skip_special_tokens=True).strip())

    return generations
