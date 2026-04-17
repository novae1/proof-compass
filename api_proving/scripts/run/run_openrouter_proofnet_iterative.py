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
from api_proving.retrieval import LeanFinderClient, build_hint_block, top_results
from prompt_hints.prompt_config import (
    DeepSeekProverV2HintNonCoTPromptConfig,
    DeepSeekProverV2HintPromptConfig,
)
from src.core.problem_structure import Attempt
from src.lean.checking import check_proof, check_repl_status
from src.lean.http_client import LeanHTTPClient

EXPERIMENT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_NOHINT_SPEC = (
    EXPERIMENT_DIR / "data" / "specs" / "20260417_proofnet_valid_trigger_union_nohint_spec.json"
)
OUTPUT_DIR = EXPERIMENT_DIR / "outputs" / "proofnet" / "valid"
SERVER_URL = "http://localhost:1347"
TIMEOUT_SECONDS = 30
MESSAGE_NO_VERIFY = "verification skipped"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run ProofNet-valid API proving on the trigger-union subset. Supports no-hint and "
            "iterative whole-attempt retrieval."
        )
    )
    parser.add_argument("--model-alias", default="deepseek-v3.2", choices=sorted(MODELS.keys()))
    parser.add_argument(
        "--condition",
        required=True,
        choices=["nohint", "iterative-attempt-rag-top4"],
    )
    parser.add_argument("--nohint-spec", type=Path, default=DEFAULT_NOHINT_SPEC)
    parser.add_argument("--attempts-per-problem", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--prompt-style", choices=["cot", "noncot"], default="cot")
    parser.add_argument("--search-topk", type=int, default=8)
    parser.add_argument("--final-theorem-budget", type=int, default=4)
    parser.add_argument("--cache-path", type=Path, help="LeanFinder cache path override.")
    parser.add_argument("--request-delay-s", type=float, default=0.35)
    parser.add_argument("--max-problems", type=int)
    parser.add_argument(
        "--problem-key",
        action="append",
        default=[],
        help="Optional exact ProofNet problem key to include. Can be repeated.",
    )
    parser.add_argument("--skip-verification", action="store_true")
    parser.add_argument("--stop-on-success", action="store_true")
    parser.add_argument("--output-name")
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected JSON object at {path}")
    return payload


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


def _problem_items(spec_path: Path) -> list[tuple[str, dict[str, Any]]]:
    payload = _load_json(spec_path)
    problems = payload.get("problems")
    if not isinstance(problems, dict):
        raise TypeError(f"Spec must contain a 'problems' object: {spec_path}")
    return sorted((key, value) for key, value in problems.items() if isinstance(value, dict))


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


def _output_name(condition: str, model_slug: str, custom_name: str | None) -> str:
    if custom_name:
        return custom_name
    date_prefix = datetime.now().strftime("%Y%m%d")
    condition_slug = condition.replace("/", "-").replace("_", "-")
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
        "timeout": 180,
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
        except Exception as exc:
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


def _prompt_adapter(prompt_style: str):
    if prompt_style == "cot":
        return DeepSeekProverV2HintPromptConfig
    return DeepSeekProverV2HintNonCoTPromptConfig


def _ensure_entry(payload: dict[str, Any], key: str, *, header: str, formal_statement: str) -> dict[str, Any]:
    entry = payload.get(key)
    if not isinstance(entry, dict):
        entry = {
            "header": header,
            "formal_statement": formal_statement,
            "informal_statement": None,
            "attempts": [],
            "retrieval_log": [],
        }
        payload[key] = entry
    entry.setdefault("header", header)
    entry.setdefault("formal_statement", formal_statement)
    entry.setdefault("informal_statement", None)
    entry.setdefault("attempts", [])
    entry.setdefault("retrieval_log", [])
    return entry


def _attempt_query_text(attempt: dict[str, Any]) -> str:
    text = str(attempt.get("parsed_proof") or "").strip()
    if text:
        return text
    text = str(attempt.get("raw_output") or "").strip()
    if text:
        return text
    raise ValueError("Attempt is missing both parsed_proof and raw_output.")


def _cached_probe(client: LeanFinderClient, query: str, k: int) -> bool:
    cache_key = json.dumps({"query": query.strip(), "k": k}, ensure_ascii=False, sort_keys=True)
    return cache_key in client._cache


def main() -> int:
    args = parse_args()
    if args.attempts_per_problem <= 0:
        raise ValueError("--attempts-per-problem must be positive.")
    if args.final_theorem_budget <= 0:
        raise ValueError("--final-theorem-budget must be positive.")
    if not args.nohint_spec.exists():
        raise FileNotFoundError(f"No-hint spec not found: {args.nohint_spec}")

    keys = _load_keys()
    api_key = keys.get("openrouter")
    if not api_key:
        raise ValueError("Missing 'openrouter' API key in keys.json")

    model_cfg = MODELS[args.model_alias]
    model_id = str(model_cfg["model_id"])
    model_slug = str(model_cfg["slug"])
    disable_reasoning = bool(model_cfg.get("disable_reasoning", False))

    prompt_cfg = _prompt_adapter(args.prompt_style)
    client = _build_openrouter_client(str(api_key))
    verifier = _build_verifier(args.skip_verification)
    leanfinder = None
    if args.condition == "iterative-attempt-rag-top4":
        leanfinder = LeanFinderClient(cache_path=args.cache_path)

    nohint_items = _problem_items(args.nohint_spec)
    problem_items = nohint_items
    if args.problem_key:
        wanted = set(args.problem_key)
        problem_items = [(key, entry) for key, entry in problem_items if key in wanted]
    if args.max_problems is not None:
        problem_items = problem_items[: max(args.max_problems, 0)]
    if not problem_items:
        raise ValueError("No ProofNet problems matched the requested filters.")

    output_path = OUTPUT_DIR / _output_name(args.condition, model_slug, args.output_name)
    if output_path.exists():
        loaded = _load_json(output_path)
        if not isinstance(loaded, dict):
            raise TypeError(f"Existing output must be a JSON object: {output_path}")
        payload: dict[str, Any] = loaded
        print(f"Resuming existing output: {output_path} ({len(payload)} entries)")
    else:
        payload = {}

    total = len(problem_items)
    for index, (problem_key, base_entry) in enumerate(problem_items, start=1):
        header = str(base_entry.get("header", "")).strip()
        formal_statement = str(base_entry.get("formal_statement", "")).strip()
        if not header or not formal_statement:
            raise ValueError(f"Problem {problem_key} is missing header/formal_statement.")
        merged_key = f"{args.condition}/{_normalize_problem_key(problem_key)}"
        output_entry = _ensure_entry(payload, merged_key, header=header, formal_statement=formal_statement)
        attempts = output_entry["attempts"]
        retrieval_log = output_entry["retrieval_log"]
        if not isinstance(attempts, list) or not isinstance(retrieval_log, list):
            raise TypeError(f"Corrupt output entry for {merged_key}")

        if args.stop_on_success and any(
            isinstance(attempt, dict) and bool(attempt.get("success")) for attempt in attempts
        ):
            print(f"[{args.condition} {index}/{total}] {problem_key} (skip: already solved)")
            continue
        if len(attempts) >= args.attempts_per_problem:
            print(
                f"[{args.condition} {index}/{total}] {problem_key} "
                f"(skip: already {len(attempts)}/{args.attempts_per_problem})"
            )
            continue

        verify_header = _strip_leading_import_lines(header)
        print(
            f"[{args.condition} {index}/{total}] {problem_key} "
            f"({len(attempts)}/{args.attempts_per_problem} done)"
        )

        while len(attempts) < args.attempts_per_problem:
            theorem_hint = ""
            retrieval_row: dict[str, Any] | None = None
            if args.condition == "iterative-attempt-rag-top4" and attempts:
                previous_attempt = attempts[-1]
                if not isinstance(previous_attempt, dict):
                    raise TypeError(f"Attempt payload for {merged_key} is not a JSON object.")
                if bool(previous_attempt.get("success")):
                    break
                query = _attempt_query_text(previous_attempt)
                assert leanfinder is not None
                was_cached = _cached_probe(leanfinder, query, args.search_topk)
                results = leanfinder.retrieve(query, k=args.search_topk)
                selected = top_results(results, limit=args.final_theorem_budget)
                theorem_hint = build_hint_block(selected)
                retrieval_row = {
                    "from_attempt_index": len(attempts) - 1,
                    "query_chars": len(query),
                    "query_preview": query[:500],
                    "results": results,
                    "selected_results": selected,
                }
                retrieval_log.append(retrieval_row)
                if not was_cached and args.request_delay_s > 0:
                    time.sleep(args.request_delay_s)

            prompt = prompt_cfg.build(header, theorem_hint or None, formal_statement)
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
            parsed_proof = prompt_cfg.parse(raw_output)

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
                    header=verify_header,
                )
                verification_time = time.time() - verify_start

            attempts.append(
                Attempt(
                    success=bool(success),
                    raw_output=raw_output,
                    parsed_proof=parsed_proof,
                    message=message,
                    generation_time=generation_time,
                    verification_time=verification_time,
                ).to_dict()
            )
            output_entry["informal_statement"] = theorem_hint or None
            output_entry["attempts"] = attempts
            output_entry["retrieval_log"] = retrieval_log
            payload[merged_key] = output_entry
            _save_json(payload, output_path)

            selected_count = 0
            if retrieval_row is not None:
                selected_count = len(retrieval_row.get("selected_results", []))
            print(
                f"  attempt {len(attempts)}/{args.attempts_per_problem}: "
                f"success={success} gen={generation_time:.1f}s verify={verification_time:.1f}s "
                f"hint_theorems={selected_count if theorem_hint else 0}"
            )
            if args.condition == "iterative-attempt-rag-top4" and bool(success):
                break
            if args.stop_on_success and bool(success):
                break

    print(f"Wrote attempts to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
