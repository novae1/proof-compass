#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from prompt_hints.prompt_config import DeepSeekProverV2HintNonCoTPromptConfig
from transformers import AutoTokenizer


MODEL_ID = "deepseek-ai/DeepSeek-Prover-V2-7B"
MODEL_PATH = ROOT / "models" / MODEL_ID
BOS_MARKER = "<｜begin▁of▁sentence｜>"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract assistant-only completion suffixes from stored raw_output payloads."
    )
    parser.add_argument("input_json", type=Path)
    parser.add_argument("--max-examples", type=int, default=3)
    return parser.parse_args()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_entries(payload: Any):
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, dict) and "attempts" in value:
                yield key, value


def _build_prompt(entry: dict[str, Any]) -> str:
    header = str(entry.get("header") or "").strip()
    formal_statement = str(entry.get("formal_statement") or "").strip()
    informal_statement = entry.get("informal_statement")
    if informal_statement is None:
        informal_statement = entry.get("theorem_hint")
    hint = str(informal_statement).strip() or None
    return DeepSeekProverV2HintNonCoTPromptConfig.build(
        header=header,
        informal_statement=hint,
        formal_statement=formal_statement,
    )


def _render_prompt(tokenizer, prompt: str) -> str:
    return str(
        tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )
    )


def _extract_completion(raw_output: str, rendered_prompt: str) -> dict[str, str | bool]:
    normalized_prompt = rendered_prompt.removeprefix(BOS_MARKER)
    if raw_output.startswith(normalized_prompt):
        return {
            "matched": True,
            "completion": raw_output[len(normalized_prompt) :].lstrip(),
            "mode": "prefix",
        }

    assistant_marker = "<｜Assistant｜>"
    if assistant_marker in raw_output:
        idx = raw_output.rfind(assistant_marker)
        return {
            "matched": False,
            "completion": raw_output[idx + len(assistant_marker) :].lstrip(),
            "mode": "assistant_marker_fallback",
        }

    return {
        "matched": False,
        "completion": raw_output,
        "mode": "raw_output_fallback",
    }


def main() -> int:
    args = parse_args()
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model tokenizer path not found: {MODEL_PATH}")

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH), trust_remote_code=True)
    payload = _load_json(args.input_json)

    examples: list[dict[str, Any]] = []
    for key, entry in _iter_entries(payload):
        attempts = entry.get("attempts")
        if not isinstance(attempts, list) or not attempts:
            continue

        prompt = _build_prompt(entry)
        rendered_prompt = _render_prompt(tokenizer, prompt)

        for attempt_index, attempt in enumerate(attempts):
            raw_output = str(attempt.get("raw_output") or "")
            if not raw_output.strip():
                continue
            extracted = _extract_completion(raw_output, rendered_prompt)
            examples.append(
                {
                    "key": key,
                    "attempt_index": attempt_index,
                    "prompt_prefix_matched": extracted["matched"],
                    "extraction_mode": extracted["mode"],
                    "completion": extracted["completion"],
                }
            )
            if len(examples) >= args.max_examples:
                print(json.dumps(examples, indent=2, ensure_ascii=False))
                return 0

    print(json.dumps(examples, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
