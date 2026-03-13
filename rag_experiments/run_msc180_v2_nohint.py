#!/usr/bin/env python3
"""
Run MSC-180 v2 no-hint generations without verification.

Scope:
- Uses only `rag_experiments/specs/msc180_v2_A_spec.json`
- Uses the non-CoT no-hint prompt config
- Generates attempts only; verification is skipped on purpose

Defaults:
- 20 generations per problem
- micro-batch size 5
- temperature 1.0
- top-p 0.95
- max-new-tokens 7000

Model modes:
- Base model:
    python3 rag_experiments/run_msc180_v2_nohint.py
- Base + LoRA adapter:
    python3 rag_experiments/run_msc180_v2_nohint.py \
      --adapter-dir mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_v1

Default output files:
- Base:
    rag_experiments/outputs/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15.json
- LoRA:
    rag_experiments/outputs/20260313_msc180-v2-nohint_lora_deepseekv2_7b_lean4-15.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prompt_hints.prompt_config import DeepSeekProverV2HintNonCoTPromptConfig
from src.core.problem_structure import Attempt, TheoremProcessor
from src.prover_generation.artifacts import load_artifacts
from src.prover_generation.batch_generation import generate_batch
from src.prover_generation.generation_params import GenerationParams


EXPERIMENT_DIR = Path(__file__).resolve().parent
SPEC_PATH = EXPERIMENT_DIR / "specs" / "msc180_v2_A_spec.json"
OUTPUT_DIR = EXPERIMENT_DIR / "outputs"

DATE_PREFIX = "20260313"
MODEL_ID = "deepseek-ai/DeepSeek-Prover-V2-7B"
MODEL_SUFFIX = "deepseekv2_7b"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate MSC-180 v2 no-hint attempts without verification."
    )
    parser.add_argument(
        "--spec-path",
        type=Path,
        default=SPEC_PATH,
        help="Path to the no-hint MSC-180 v2 spec.",
    )
    parser.add_argument(
        "--attempts-per-problem",
        type=int,
        default=20,
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
        help="Optional output filename inside rag_experiments/outputs.",
    )
    parser.add_argument(
        "--max-problems",
        type=int,
        help="Optional cap for smoke/debug runs.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _build_processors(spec: dict) -> list[tuple[str, TheoremProcessor]]:
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


def _normalize_problem_key(problem_key: str) -> str:
    return problem_key.replace("/", "_")


def _load_model_and_tokenizer(adapter_dir: Path | None):
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


def _output_name(adapter_dir: Path | None, custom_name: str | None) -> str:
    if custom_name:
        return custom_name
    variant = "lora" if adapter_dir else "base"
    return f"{DATE_PREFIX}_msc180-v2-nohint_{variant}_{MODEL_SUFFIX}_lean4-15.json"


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

    params = GenerationParams(
        micro_batch_size=args.micro_batch_size,
        temperature=args.temperature,
        top_p=args.top_p,
        max_new_tokens=args.max_new_tokens,
    )

    output_path = OUTPUT_DIR / _output_name(args.adapter_dir, args.output_name)
    if output_path.exists():
        loaded = _load_json(output_path)
        if not isinstance(loaded, dict):
            raise TypeError(f"Existing output must be a JSON object: {output_path}")
        output_payload: dict[str, object] = loaded
        print(f"Resuming existing output: {output_path} ({len(output_payload)} entries)")
    else:
        output_payload = {}

    model, tokenizer = _load_model_and_tokenizer(args.adapter_dir)

    for key, processor in processors:
        merged_key = f"no-hint/{_normalize_problem_key(key)}"
        existing = output_payload.get(merged_key)
        existing_attempts: list[object] = []
        if isinstance(existing, dict):
            prior_attempts = existing.get("attempts")
            if isinstance(prior_attempts, list):
                existing_attempts = prior_attempts

        existing_count = len(existing_attempts)
        if existing_count >= args.attempts_per_problem:
            print(f"[no-hint] {key} (skip: already {existing_count}/{args.attempts_per_problem})")
            continue

        remaining = args.attempts_per_problem - existing_count
        print(f"[no-hint] {key} ({existing_count}/{args.attempts_per_problem} done, generating {remaining})")

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
