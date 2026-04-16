#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from api_proving.model_registry import (
    MODELS,
    OPENROUTER_BASE_URL,
    OPENROUTER_REFERER,
    OPENROUTER_TITLE,
)
from prompt_hints.prompt_config import DeepSeekProverV2HintNonCoTPromptConfig
from src.core.problem_structure import Attempt, TheoremProcessor
from src.lean.checking import check_proof, check_repl_status
from src.lean.http_client import LeanHTTPClient

EXPERIMENT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SPEC_PATH = EXPERIMENT_DIR / "data" / "specs" / "20260416_proofnet_valid_nohint_smoke2_spec.json"
OUTPUT_DIR = EXPERIMENT_DIR / "outputs" / "proofnet" / "valid"
SERVER_URL = "http://localhost:1347"
TIMEOUT_SECONDS = 30
MESSAGE_NO_VERIFY = "verification skipped"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ProofNet generation through OpenRouter.")
    parser.add_argument("--spec-path", type=Path, default=DEFAULT_SPEC_PATH)
    parser.add_argument("--model-alias", required=True, choices=sorted(MODELS.keys()))
    parser.add_argument("--condition-label", default="nohint-smoke2")
    parser.add_argument("--attempts-per-problem", type=int, default=2)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--max-problems", type=int)
    parser.add_argument("--skip-verification", action="store_true")
    parser.add_argument("--output-name")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_keys() -> dict[str, Any]:
    keys_path = ROOT / "keys.json"
    if not keys_path.exists():
        raise FileNotFoundError(f"Missing keys.json at {keys_path}")
    data = json.loads(keys_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("keys.json must be a JSON object")
    return data


def _build_processors(spec: dict[str, Any]) -> list[tuple[str, TheoremProcessor]]:
    problems = spec.get("problems")
    if not isinstance(problems, dict):
        raise TypeError("Spec must contain a 'problems' object.")

    processors: list[tuple[str, TheoremProcessor]] = []
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
        processors.append(
            (
                key,
                TheoremProcessor(
                    formal_statement=formal_statement,
                    header=header,
                    informal_statement=theorem_hint or None,
                ),
            )
        )
    return processors


def _strip_leading_import_lines(text: str) -> str:
    lines = text.splitlines()
    idx = 0
    while idx < len(lines):
        stripped = lines[idx].lstrip()
        if not stripped or stripped.startswith("import "):
            idx += 1
            continue
        break
    return "\n".join(lines[idx:]).strip()


def _format_raw_output(prompt: str, content: str) -> str:
    return f"=== PROMPT ===\n{prompt}\n\n=== OUTPUT ===\n{content}"


def _normalize_problem_key(problem_key: str) -> str:
    return problem_key.replace("/", "_")


def _output_name(condition_label: str, model_slug: str, custom_name: str | None) -> str:
    if custom_name:
        return custom_name
    date_prefix = datetime.now().strftime("%Y%m%d")
    condition_slug = condition_label.replace("/", "-").replace("_", "-")
    return f"{date_prefix}_proofnet-valid_{condition_slug}_{model_slug}.json"


def _build_openrouter_client(api_key: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)


def _chat_completion(
    client: OpenAI,
    *,
    model_id: str,
    prompt: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
    disable_reasoning: bool,
) -> tuple[str, float]:
    request_kwargs: dict[str, Any] = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": False,
        "extra_headers": {
            "HTTP-Referer": OPENROUTER_REFERER,
            "X-OpenRouter-Title": OPENROUTER_TITLE,
        },
    }
    if disable_reasoning:
        request_kwargs["extra_body"] = {"reasoning": {"enabled": False}}

    last_exc: Exception | None = None
    for attempt_idx in range(4):
        start = time.time()
        try:
            response = client.chat.completions.create(**request_kwargs)
            elapsed = time.time() - start
            content = response.choices[0].message.content or ""
            return content, elapsed
        except Exception as exc:  # API error surface varies by provider
            last_exc = exc
            if disable_reasoning and attempt_idx == 0:
                request_kwargs.pop("extra_body", None)
                continue
            message = str(exc)
            if "429" in message or "rate limit" in message.lower():
                time.sleep(10 * (attempt_idx + 1))
                continue
            if attempt_idx < 3:
                time.sleep(3 * (attempt_idx + 1))
                continue
            break
    raise RuntimeError(f"OpenRouter request failed for {model_id}: {last_exc}")


def _build_verifier(skip_verification: bool) -> LeanHTTPClient | None:
    if skip_verification:
        return None
    client = LeanHTTPClient(SERVER_URL)
    success, message = check_repl_status(client)
    if not success:
        raise RuntimeError(f"Lean server unavailable: {message}")
    return client


def main() -> int:
    args = parse_args()
    if not args.spec_path.exists():
        raise FileNotFoundError(f"Spec not found: {args.spec_path}")
    if args.attempts_per_problem <= 0:
        raise ValueError("--attempts-per-problem must be positive.")

    keys = _load_keys()
    api_key = keys.get("openrouter")
    if not api_key:
        raise ValueError("Missing 'openrouter' API key in keys.json")

    model_cfg = MODELS[args.model_alias]
    model_id = str(model_cfg["model_id"])
    model_slug = str(model_cfg["slug"])
    disable_reasoning = bool(model_cfg.get("disable_reasoning", False))

    client = _build_openrouter_client(str(api_key))
    verifier = _build_verifier(args.skip_verification)

    spec = _load_json(args.spec_path)
    processors = _build_processors(spec)
    if args.max_problems is not None:
        processors = processors[: max(args.max_problems, 0)]

    output_path = OUTPUT_DIR / _output_name(args.condition_label, model_slug, args.output_name)
    if output_path.exists():
        loaded = _load_json(output_path)
        if not isinstance(loaded, dict):
            raise TypeError(f"Existing output must be a JSON object: {output_path}")
        payload: dict[str, Any] = loaded
        print(f"Resuming existing output: {output_path} ({len(payload)} entries)")
    else:
        payload = {}

    for key, processor in processors:
        merged_key = f"{args.condition_label}/{_normalize_problem_key(key)}"
        existing = payload.get(merged_key)
        existing_attempts: list[object] = []
        if isinstance(existing, dict):
            prior_attempts = existing.get("attempts")
            if isinstance(prior_attempts, list):
                existing_attempts = prior_attempts
        if len(existing_attempts) >= args.attempts_per_problem:
            print(f"[{model_slug}] {key} (skip: already {len(existing_attempts)}/{args.attempts_per_problem})")
            continue

        prompt = DeepSeekProverV2HintNonCoTPromptConfig.build(
            processor.header,
            processor.informal_statement,
            processor.formal_statement,
        )
        header = _strip_leading_import_lines(processor.header)

        print(f"[{model_slug}] {key} ({len(existing_attempts)}/{args.attempts_per_problem} done)")
        for attempt_idx in range(len(existing_attempts), args.attempts_per_problem):
            content, generation_time = _chat_completion(
                client,
                model_id=model_id,
                prompt=prompt,
                temperature=args.temperature,
                top_p=args.top_p,
                max_tokens=args.max_tokens,
                disable_reasoning=disable_reasoning,
            )
            raw_output = _format_raw_output(prompt, content)
            parsed_proof = DeepSeekProverV2HintNonCoTPromptConfig.parse(raw_output)
            if verifier is None:
                success = False
                message: Any = MESSAGE_NO_VERIFY
                verification_time = 0.0
            else:
                verify_start = time.time()
                success, message = check_proof(
                    parsed_proof,
                    verifier,
                    timeout=TIMEOUT_SECONDS,
                    ignore_sorries=False,
                    header=header,
                )
                verification_time = time.time() - verify_start

            processor.add_attempt(
                Attempt(
                    success=success,
                    raw_output=raw_output,
                    parsed_proof=parsed_proof,
                    message=message,
                    generation_time=generation_time,
                    verification_time=verification_time,
                )
            )
            print(
                f"  attempt {attempt_idx + 1}/{args.attempts_per_problem}: "
                f"success={success} gen={generation_time:.1f}s verify={verification_time:.1f}s"
            )
            entry = processor.to_dict()
            if existing_attempts:
                entry["attempts"] = [*existing_attempts, *entry.get("attempts", [])]
            payload[merged_key] = entry
            _save_json(payload, output_path)

    print(f"Wrote attempts to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
