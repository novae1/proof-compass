#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Iterable

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.problem_structure import Attempt, TheoremProcessor
from src.prover_generation.prompt_config import _extract_last_theorem_block
from prompt_hints.prompt_config import DeepSeekProverV2HintPromptConfig

SPEC_DIR = Path(__file__).resolve().parent

SPEC_FILES = {
    "proving-with-given-theorem": SPEC_DIR / "proving-with-given-theorem_spec.json",
    "proving-with-hints": SPEC_DIR / "proving-with-hints_spec.json",
    "proving-no-hint": SPEC_DIR / "proving-no-hint_spec.json",
}

PROVIDERS = {
    "moonshot": {
        "base_url": "https://api.moonshot.ai/v1",
        "model": "kimi-k2.5",
        "key_field": "moonshot",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-reasoner",
        "key_field": "deepseek",
    },
}

DATE_PREFIX = "20260204"
ATTEMPTS_PER_PROBLEM = 4
MAX_TOKENS = 8000
MESSAGE_NO_VERIFY = "Server client is None"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_keys() -> dict:
    keys_path = ROOT / "keys.json"
    if not keys_path.exists():
        raise FileNotFoundError(f"Missing keys.json at {keys_path}")
    data = json.loads(keys_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("keys.json must be a JSON object")
    return data


def _build_processors(spec: dict) -> dict[str, TheoremProcessor]:
    problems = spec.get("problems")
    if not isinstance(problems, dict):
        raise TypeError("Spec must contain a 'problems' object.")

    processors: dict[str, TheoremProcessor] = {}
    for key, entry in problems.items():
        if not isinstance(entry, dict):
            raise TypeError(f"Problem '{key}' must be a JSON object.")

        header = str(entry.get("header", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        theorem_hint = str(entry.get("theorem_hint", "")).strip()

        if not header:
            raise ValueError(f"Problem '{key}' is missing a non-empty header.")
        if not formal_statement:
            raise ValueError(f"Problem '{key}' is missing a non-empty formal_statement.")

        processors[key] = TheoremProcessor(
            formal_statement=formal_statement,
            header=header,
            informal_statement=theorem_hint or None,
        )

    return processors


def _stream_chat_completion(client: OpenAI, model: str, prompt: str) -> tuple[str, str, float]:
    start = time.time()
    reasoning_chunks: list[str] = []
    content_chunks: list[str] = []

    stream = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=MAX_TOKENS,
        stream=True,
    )

    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if hasattr(delta, "reasoning_content"):
            reasoning = getattr(delta, "reasoning_content")
            if reasoning:
                reasoning_chunks.append(reasoning)
        if delta.content:
            content_chunks.append(delta.content)

    elapsed = time.time() - start
    return "".join(reasoning_chunks), "".join(content_chunks), elapsed


def _format_raw_output(prompt: str, reasoning: str, content: str) -> str:
    return (
        "=== PROMPT ===\n"
        f"{prompt}\n\n"
        "=== REASONING ===\n"
        f"{reasoning}\n\n"
        "=== OUTPUT ===\n"
        f"{content}"
    )


def _run_spec(
    spec_path: Path,
    output_path: Path,
    client: OpenAI,
    model: str,
) -> None:
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec not found at {spec_path}")

    spec = _load_json(spec_path)
    processors = _build_processors(spec)

    output: dict[str, object] = {}
    for key, processor in processors.items():
        print(key)
        prompt = DeepSeekProverV2HintPromptConfig.build(
            header=processor.header,
            informal_statement=processor.informal_statement,
            formal_statement=processor.formal_statement,
        )

        for _ in range(ATTEMPTS_PER_PROBLEM):
            reasoning, content, elapsed = _stream_chat_completion(client, model, prompt)
            raw_output = _format_raw_output(prompt, reasoning, content)
            parsed_proof = _extract_last_theorem_block(content)
            attempt = Attempt(
                success=False,
                raw_output=raw_output,
                parsed_proof=parsed_proof,
                message=MESSAGE_NO_VERIFY,
                generation_time=elapsed,
                verification_time=0.0,
            )
            processor.add_attempt(attempt)

        output[key] = processor.to_dict()
        _save_json(output, output_path)

    print(f"Wrote attempts to {output_path}")


def main() -> int:
    keys = _load_keys()

    for provider, cfg in PROVIDERS.items():
        key_field = cfg["key_field"]
        api_key = keys.get(key_field)
        if not api_key:
            raise ValueError(f"Missing API key for '{provider}' in keys.json")

        client = OpenAI(api_key=api_key, base_url=cfg["base_url"])
        model = cfg["model"]

        for spec_name, spec_path in SPEC_FILES.items():
            output_name = f"{DATE_PREFIX}_{spec_name}_{provider}.json"
            output_path = SPEC_DIR / output_name
            _run_spec(spec_path, output_path, client, model)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
