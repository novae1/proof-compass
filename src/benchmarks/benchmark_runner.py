from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Optional

from ..lean.http_client import LeanHTTPClient
from ..core.problem_structure import TheoremProcessor
from ..core.theorem_proving import synthesize_proof_attempts_many
from ..prover_generation.generation_params import GenerationParams


Benchmark = Mapping[str, Mapping[str, Any]]

DEFAULT_HEADER = """import Mathlib
import Aesop

set_option maxHeartbeats 0

open BigOperators Real Nat Topology Rat
"""


def build_processors(benchmark: Benchmark) -> dict[str, TheoremProcessor]:
    """Instantiate processors for each problem in the benchmark."""
    processors: dict[str, TheoremProcessor] = {}
    for name, problem in benchmark.items():
        try:
            formal_statement = problem["formal_statement"]
        except KeyError as exc:
            raise KeyError(f"Benchmark problem '{name}' is missing 'formal_statement'.") from exc

        header = problem.get("header")
        if not header or not str(header).strip():
            raise KeyError(f"Benchmark problem '{name}' is missing a non-empty 'header'.")

        processors[name] = TheoremProcessor(
            formal_statement=formal_statement,
            header=str(header),
            informal_statement=problem.get("informal_statement"),
            nl_proof=problem.get("nl_proof"),
        )

    return processors


def save_processors(processors: Mapping[str, TheoremProcessor], path: Path | str) -> None:
    """Persist processors to disk as JSON using their serialized form."""
    payload = {name: processor.to_dict() for name, processor in processors.items()}
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n")


def solve_benchmark(
    benchmark: Benchmark,
    *,
    model,
    tokenizer,
    server_client: Optional[LeanHTTPClient],
    num_attempts: int,
    model_id: str,
    generation_params: GenerationParams,
    checkpoint_path: Path | str,
) -> dict[str, TheoremProcessor]:
    """Solve every problem in the benchmark and checkpoint once at the end."""
    processors = build_processors(benchmark)

    synthesize_proof_attempts_many(
        processors=processors,
        model=model,
        tokenizer=tokenizer,
        server_client=server_client,
        model_id=model_id,
        max_attempts_per_problem=num_attempts,
        generation_params=generation_params,
    )
    save_processors(processors, checkpoint_path)

    return processors


def _ensure_sorry_stub(statement: str) -> str:
    trimmed = statement.rstrip()
    if not trimmed.endswith("sorry"):
        return f"{trimmed}\n  sorry"
    return trimmed


def _save_nested_processors(
    processors_by_problem: Mapping[str, Mapping[str, TheoremProcessor]],
    path: Path | str,
) -> None:
    payload: dict[str, dict[str, object]] = {}
    for problem_id, variants in processors_by_problem.items():
        payload[problem_id] = {variant: processor.to_dict() for variant, processor in variants.items()}

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n")


def run_aime_informal_experiment(
    *,
    model,
    tokenizer,
    model_id: str,
    attempts_per_variant: int,
    generation_params: GenerationParams,
    checkpoint_path: Path | str,
    aime_path: Path | str = "aime_informal_problems.json",
    minif2f_path: Path | str = "benchmarks/processed/miniF2F_valid.json",
) -> Mapping[str, Mapping[str, TheoremProcessor]]:
    """Generate attempts for AIME problems with NL proof variants and checkpoint each round.

    Builds 5 variants per problem:
    - no_nl
    - proof1_full / proof1_summary
    - proof2_full / proof2_summary

    Verification is intentionally stubbed by using a dummy `LeanHTTPClient`.
    """
    aime = json.loads(Path(aime_path).read_text(encoding="utf-8"))
    minif2f = json.loads(Path(minif2f_path).read_text(encoding="utf-8"))

    processors_by_problem: dict[str, dict[str, TheoremProcessor]] = {}
    for problem_id, item in aime.items():
        if problem_id not in minif2f:
            raise KeyError(f"Problem '{problem_id}' was not found in '{minif2f_path}'.")

        theorem = _ensure_sorry_stub(minif2f[problem_id]["formal_statement"])
        informal_statement = item.get("informal_statement")

        proofs = item.get("proofs", [])
        if not isinstance(proofs, list) or len(proofs) != 2:
            raise ValueError(f"Problem '{problem_id}' must contain exactly 2 proofs.")

        variants: dict[str, TheoremProcessor] = {}
        variants["no_nl"] = TheoremProcessor(
            formal_statement=theorem,
            header=DEFAULT_HEADER,
            informal_statement=informal_statement,
            nl_proof=None,
        )

        for idx, proof in enumerate(proofs, start=1):
            nl_proof = proof.get("nl_proof")
            proof_summary = proof.get("proof_summary")
            variants[f"proof{idx}_full"] = TheoremProcessor(
                formal_statement=theorem,
                header=DEFAULT_HEADER,
                informal_statement=informal_statement,
                nl_proof=nl_proof,
            )
            variants[f"proof{idx}_summary"] = TheoremProcessor(
                formal_statement=theorem,
                header=DEFAULT_HEADER,
                informal_statement=informal_statement,
                nl_proof=proof_summary,
            )

        processors_by_problem[problem_id] = variants

    flat_processors: dict[str, TheoremProcessor] = {}
    for problem_id, variants in processors_by_problem.items():
        for variant_name, processor in variants.items():
            flat_processors[f"{problem_id}/{variant_name}"] = processor

    dummy_client = LeanHTTPClient("")

    for round_idx in range(attempts_per_variant):
        synthesize_proof_attempts_many(
            processors=flat_processors,
            model=model,
            tokenizer=tokenizer,
            server_client=dummy_client,
            model_id=model_id,
            max_attempts_per_problem=1,
            generation_params=generation_params,
            stop_on_success=False,
        )
        _save_nested_processors(processors_by_problem, checkpoint_path)
        print(f"checkpointed round {round_idx + 1}/{attempts_per_variant} -> {checkpoint_path}")

    return processors_by_problem


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    aime_parser = subparsers.add_parser("aime")
    aime_parser.add_argument("--model-id", required=True)
    aime_parser.add_argument("--attempts-per-variant", type=int, default=1)
    aime_parser.add_argument("--micro-batch-size", type=int, default=8)
    aime_parser.add_argument("--temperature", type=float, default=1.0)
    aime_parser.add_argument("--top-p", type=float, default=0.95)
    aime_parser.add_argument("--max-new-tokens", type=int, default=8192)
    aime_parser.add_argument("--checkpoint-path", default="experiments/aime_runs/checkpoint.json")
    aime_parser.add_argument("--aime-path", default="aime_informal_problems.json")
    aime_parser.add_argument("--minif2f-path", default="benchmarks/processed/miniF2F_valid.json")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if args.command == "aime":
        from ..prover_generation.artifacts import load_artifacts

        model, tokenizer = load_artifacts(args.model_id)
        params = GenerationParams(
            micro_batch_size=args.micro_batch_size,
            temperature=args.temperature,
            top_p=args.top_p,
            max_new_tokens=args.max_new_tokens,
        )
        run_aime_informal_experiment(
            model=model,
            tokenizer=tokenizer,
            model_id=args.model_id,
            attempts_per_variant=args.attempts_per_variant,
            generation_params=params,
            checkpoint_path=args.checkpoint_path,
            aime_path=args.aime_path,
            minif2f_path=args.minif2f_path,
        )
        return 0

    raise AssertionError(f"Unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
