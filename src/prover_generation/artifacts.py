from __future__ import annotations

from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _model_path(model_id: str) -> Path:
    model_id = model_id.strip().strip("/")
    if not model_id:
        raise ValueError("model_id must be non-empty (e.g. 'org/model-name').")
    return _project_root() / "models" / model_id


def load_artifacts(model_id: str):
    """Load a model/tokenizer from `models/<model_id>` using HuggingFace Transformers."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA device required for generation but was not found.")

    source_path = _model_path(model_id)
    if not source_path.exists():
        raise FileNotFoundError(
            f"Model files for '{model_id}' were not found at '{source_path}'. "
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
