#!/usr/bin/env python3
"""
Run ProofNet-valid generations without verification.

Scope:
- Uses a spec JSON under `rag_experiments/data/specs/`
- Uses the non-CoT DeepSeek V2 prompt config
- Generates attempts only; verification is a separate step

Typical usage:
- No hint:
    python3 rag_experiments/run_proofnet_valid.py \
      --spec-path rag_experiments/data/specs/20260331_proofnet_valid_nohint_spec.json \
      --condition-label no-hint

- Statement-only RAG:
    python3 rag_experiments/run_proofnet_valid.py \
      --spec-path rag_experiments/data/specs/20260331_proofnet_valid_statement_rag_top2_spec.json \
      --condition-label statement-rag-top2
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from prompt_hints.prompt_config import DeepSeekProverV2HintNonCoTPromptConfig
from src.core.problem_structure import Attempt, TheoremProcessor


EXPERIMENT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SPEC_PATH = EXPERIMENT_DIR / "data" / "specs" / "20260331_proofnet_valid_nohint_spec.json"
OUTPUT_DIR = EXPERIMENT_DIR / "outputs" / "proofnet" / "valid"

DATE_PREFIX = "20260331"
MODEL_ID = "deepseek-ai/DeepSeek-Prover-V2-7B"
MODEL_SUFFIX = "deepseekv2_7b"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate ProofNet-valid attempts without verification."
    )
    parser.add_argument(
        "--spec-path",
        type=Path,
        default=DEFAULT_SPEC_PATH,
        help="Path to the ProofNet-valid spec.",
    )
    parser.add_argument(
        "--condition-label",
        default="no-hint",
        help="Prefix stored in output keys, e.g. no-hint or statement-rag-top2.",
    )
    parser.add_argument(
        "--attempts-per-problem",
        type=int,
        default=4,
        help="Number of generations to sample for each problem.",
    )
    parser.add_argument(
        "--micro-batch-size",
        type=int,
        default=5,
        help="How many prompts to send per generate() call.",
    )
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-new-tokens", type=int, default=7000)
    parser.add_argument(
        "--adapter-dir",
        type=Path,
        help="Optional PEFT adapter directory. If omitted, runs the base model.",
    )
    parser.add_argument(
        "--output-name",
        help="Optional output filename inside rag_experiments/outputs/proofnet/valid.",
    )
    parser.add_argument(
        "--max-problems",
        type=int,
        help="Optional cap for debug runs.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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


def _load_model_and_tokenizer(adapter_dir: Path | None):
    from src.prover_generation.artifacts import load_artifacts

    model, tokenizer = load_artifacts(MODEL_ID)
    if adapter_dir is None:
        return model, tokenizer

    try:
        from peft import PeftModel
    except ImportError as exc:
        raise ImportError("peft is required when --adapter-dir is provided.") from exc

    if not adapter_dir.exists():
        raise FileNotFoundError(f"Adapter directory not found: {adapter_dir}")

    model = PeftModel.from_pretrained(model, str(adapter_dir))
    return model, tokenizer


def _output_name(condition_label: str, adapter_dir: Path | None, custom_name: str | None) -> str:
    if custom_name:
        return custom_name
    variant = "lora" if adapter_dir else "base"
    condition_slug = condition_label.replace("/", "-").replace("_", "-")
    return f"{DATE_PREFIX}_proofnet-valid_{condition_slug}_{variant}_{MODEL_SUFFIX}_lean4-15.json"


def _normalize_problem_key(problem_key: str) -> str:
    return problem_key.replace("/", "_")


def _count_completed_problems(payload: dict[str, Any], attempts_per_problem: int) -> int:
    completed = 0
    for entry in payload.values():
        if not isinstance(entry, dict):
            continue
        attempts = entry.get("attempts")
        if isinstance(attempts, list) and len(attempts) >= attempts_per_problem:
            completed += 1
    return completed


def _sum_generation_seconds(payload: dict[str, Any]) -> float:
    total = 0.0
    for entry in payload.values():
        if not isinstance(entry, dict):
            continue
        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            continue
        for attempt in attempts:
            if isinstance(attempt, dict):
                try:
                    total += float(attempt.get("generation_time", 0.0) or 0.0)
                except (TypeError, ValueError):
                    continue
    return total


def _format_duration(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _progress_line(
    *,
    condition_label: str,
    key: str,
    existing_count: int,
    attempts_per_problem: int,
    remaining: int,
    completed_problems: int,
    total_problems: int,
    estimated_elapsed_s: float,
) -> str:
    completed_fraction = completed_problems / total_problems if total_problems else 0.0
    completed_pct = completed_fraction * 100.0
    if completed_fraction > 0:
        projected_total_s = estimated_elapsed_s / completed_fraction
        eta_s = max(0.0, projected_total_s - estimated_elapsed_s)
        eta_text = _format_duration(eta_s)
    else:
        eta_text = "unknown"
    return (
        f"[{condition_label}] {key} "
        f"({existing_count}/{attempts_per_problem} done, generating {remaining}) | "
        f"completed problems: {completed_problems}/{total_problems} ({completed_pct:.1f}%) | "
        f"elapsed≈{_format_duration(estimated_elapsed_s)} | eta≈{eta_text}"
    )


def main() -> int:
    args = parse_args()
    if not args.spec_path.exists():
        raise FileNotFoundError(f"Spec not found: {args.spec_path}")
    if args.attempts_per_problem <= 0:
        raise ValueError("--attempts-per-problem must be positive.")
    if args.micro_batch_size <= 0:
        raise ValueError("--micro-batch-size must be positive.")

    spec = _load_json(args.spec_path)
    processors = _build_processors(spec)
    if args.max_problems is not None:
        processors = processors[: max(args.max_problems, 0)]
    total_problems = len(processors)

    output_path = OUTPUT_DIR / _output_name(args.condition_label, args.adapter_dir, args.output_name)
    if output_path.exists():
        loaded = _load_json(output_path)
        if not isinstance(loaded, dict):
            raise TypeError(f"Existing output must be a JSON object: {output_path}")
        output_payload: dict[str, Any] = loaded
        print(f"Resuming existing output: {output_path} ({len(output_payload)} entries)")
    else:
        output_payload = {}

    from src.prover_generation.batch_generation import generate_batch
    from src.prover_generation.generation_params import GenerationParams

    params = GenerationParams(
        micro_batch_size=args.micro_batch_size,
        temperature=args.temperature,
        top_p=args.top_p,
        max_new_tokens=args.max_new_tokens,
    )

    model, tokenizer = _load_model_and_tokenizer(args.adapter_dir)

    for key, processor in processors:
        merged_key = f"{args.condition_label}/{_normalize_problem_key(key)}"
        existing = output_payload.get(merged_key)
        existing_attempts: list[object] = []
        if isinstance(existing, dict):
            prior_attempts = existing.get("attempts")
            if isinstance(prior_attempts, list):
                existing_attempts = prior_attempts

        existing_count = len(existing_attempts)
        if existing_count >= args.attempts_per_problem:
            print(f"[{args.condition_label}] {key} (skip: already {existing_count}/{args.attempts_per_problem})")
            continue

        completed_problems = _count_completed_problems(output_payload, args.attempts_per_problem)
        estimated_elapsed_s = _sum_generation_seconds(output_payload)

        remaining = args.attempts_per_problem - existing_count
        print(
            _progress_line(
                condition_label=args.condition_label,
                key=key,
                existing_count=existing_count,
                attempts_per_problem=args.attempts_per_problem,
                remaining=remaining,
                completed_problems=completed_problems,
                total_problems=total_problems,
                estimated_elapsed_s=estimated_elapsed_s,
            )
        )

        prompt = DeepSeekProverV2HintNonCoTPromptConfig.build(
            processor.header,
            processor.informal_statement,
            processor.formal_statement,
        )

        while remaining > 0:
            batch_size = min(params.micro_batch_size, remaining)
            remaining -= batch_size
            batch_prompts = [prompt] * batch_size

            generation_start = time.time()
            raw_outputs = generate_batch(batch_prompts, model, tokenizer, params)
            generation_time = time.time() - generation_start
            if not raw_outputs:
                continue

            average_generation_time = generation_time / len(raw_outputs)
            for raw_output in raw_outputs:
                parsed_proof = DeepSeekProverV2HintNonCoTPromptConfig.parse(raw_output)
                processor.add_attempt(
                    Attempt(
                        success=False,
                        raw_output=raw_output,
                        parsed_proof=parsed_proof,
                        message="verification skipped",
                        generation_time=average_generation_time,
                        verification_time=0.0,
                    )
                )

        entry = processor.to_dict()
        if existing_attempts:
            entry["attempts"] = [*existing_attempts, *entry.get("attempts", [])]
        output_payload[merged_key] = entry
        _save_json(output_payload, output_path)

    print(f"Wrote combined attempts to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
