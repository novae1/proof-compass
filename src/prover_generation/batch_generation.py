from __future__ import annotations
import torch
from transformers import PreTrainedModel, PreTrainedTokenizerBase
from .generation_params import GenerationParams


def _ensure_pad_token(tokenizer: PreTrainedTokenizerBase) -> int:
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return tokenizer.pad_token_id


def generate_batch(
    prompts: list[str],
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizerBase,
    params: GenerationParams,
) -> list[str]:
    """Generate one sample per prompt using HuggingFace Transformers."""
    if not prompts:
        return []
    
    pad_token_id = _ensure_pad_token(tokenizer)
    target_device = torch.device("cuda")
    chat_inputs = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=True,
            add_generation_prompt=True,
        )
        for prompt in prompts
    ]

    encoded = tokenizer.pad(
        {"input_ids": chat_inputs},
        return_tensors="pt",
        padding=True,
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

    generations: list[str] = []
    for idx in range(outputs.size(0)):
        generations.append(tokenizer.decode(outputs[idx], skip_special_tokens=True).strip())

    return generations
