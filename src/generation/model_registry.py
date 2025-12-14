from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"

MODEL_REGISTRY: Dict[str, Dict[str, object]] = {
    "Goedel-LM/Goedel-Prover-V2-8B": {
        "subdir": "Goedel-Prover-V2-8B",
    },
    "deepseek-ai/DeepSeek-Prover-V1.5-RL": {
        "subdir": "DeepSeek-Prover-V1.5-RL",
    },
    "deepseek-ai/DeepSeek-Prover-V2-7B": {
        "subdir": "DeepSeek-Prover-V2-7B",
    },
}


def supported_model_ids() -> Iterable[str]:
    return MODEL_REGISTRY.keys()

def allow_patterns(model_id: str) -> Optional[Sequence[str]]:
    """Optional allowlist for Hugging Face snapshot downloads.

    Returning `None` means "download the full repository snapshot".
    """
    # Currently we do not restrict which files are pulled for any supported model.
    if model_id not in MODEL_REGISTRY:
        raise ValueError(f"Unsupported model_id '{model_id}'.")
    return None


def model_path(model_id: str) -> Path:
    try:
        subdir = MODEL_REGISTRY[model_id]["subdir"]
    except KeyError as exc:
        raise ValueError(f"Unsupported model_id '{model_id}'.") from exc
    return MODELS_DIR / str(subdir)
