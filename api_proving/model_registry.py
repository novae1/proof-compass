from __future__ import annotations

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_REFERER = "https://github.com/nicolas/proof-compass"
OPENROUTER_TITLE = "proof-compass api_proving"

MODELS: dict[str, dict[str, object]] = {
    "deepseek-v3.2": {
        "model_id": "deepseek/deepseek-v3.2",
        "slug": "deepseek-v3.2",
        "free": False,
        "disable_reasoning": True,
    },
    "nemotron-120b-free": {
        "model_id": "nvidia/nemotron-3-super-120b-a12b:free",
        "slug": "nemotron-120b-free",
        "free": True,
        "disable_reasoning": False,
    },
    "step-3.5-flash-free": {
        "model_id": "stepfun/step-3.5-flash:free",
        "slug": "step-3.5-flash-free",
        "free": True,
        "disable_reasoning": True,
    },
    "qwen3.6-plus-free": {
        "model_id": "qwen/qwen3.6-plus:free",
        "slug": "qwen3.6-plus-free",
        "free": True,
        "disable_reasoning": True,
    },
    "gemma-4-31b-free": {
        "model_id": "google/gemma-4-31b-it:free",
        "slug": "gemma-4-31b-free",
        "free": True,
        "disable_reasoning": True,
    },
    "gemma-4-26b-a4b-free": {
        "model_id": "google/gemma-4-26b-a4b-it:free",
        "slug": "gemma-4-26b-a4b-free",
        "free": True,
        "disable_reasoning": True,
    },
    "gpt-oss-120b-free": {
        "model_id": "openai/gpt-oss-120b:free",
        "slug": "gpt-oss-120b-free",
        "free": True,
        "disable_reasoning": True,
    },
}

FREE_MODEL_ALIASES = [
    "nemotron-120b-free",
    "step-3.5-flash-free",
    "qwen3.6-plus-free",
    "gemma-4-31b-free",
    "gemma-4-26b-a4b-free",
    "gpt-oss-120b-free",
]
