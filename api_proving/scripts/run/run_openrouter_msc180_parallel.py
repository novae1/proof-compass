#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from api_proving.model_registry import MODELS


EXPERIMENT_DIR = Path(__file__).resolve().parents[2]
RUNNER_PATH = EXPERIMENT_DIR / "scripts" / "run" / "run_openrouter_msc180.py"
OUTPUT_DIR = EXPERIMENT_DIR / "outputs" / "msc180" / "verified20"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run MSC-180 API proving in parallel using one shard per problem. Workers reuse the "
            "single-problem runner, stop on first solve, and merge shard outputs into the canonical file."
        )
    )
    parser.add_argument("--model-alias", default="deepseek-v3.2", choices=sorted(MODELS.keys()))
    parser.add_argument(
        "--condition",
        required=True,
        choices=["basic-rag-top4", "iterative-attempt-rag-top4", "nohint"],
    )
    parser.add_argument("--attempts-per-problem", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--prompt-style", choices=["cot", "noncot"], default="cot")
    parser.add_argument("--search-topk", type=int, default=8)
    parser.add_argument("--final-theorem-budget", type=int, default=4)
    parser.add_argument("--cache-path", type=Path)
    parser.add_argument("--request-delay-s", type=float, default=0.35)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--output-name", required=True)
    parser.add_argument(
        "--force-problems",
        action="append",
        default=[],
        help="Optional exact MSC-180 problem key to force-run even if already solved.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected JSON object at {path}")
    return payload


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize_problem_key(problem_key: str) -> str:
    return problem_key.replace("/", "_")


def combined_output_path(output_name: str) -> Path:
    return OUTPUT_DIR / output_name


def shard_output_name(condition: str, problem_key: str, output_name: str) -> str:
    stem = Path(output_name).stem
    suffix = Path(output_name).suffix or ".json"
    return f"shards/{condition}/{stem}__{normalize_problem_key(problem_key)}{suffix}"


def list_problem_keys() -> list[str]:
    spec_path = EXPERIMENT_DIR / "data" / "specs" / "20260416_msc180_verified20_nohint_spec.json"
    payload = load_json(spec_path)
    problems = payload.get("problems")
    if not isinstance(problems, dict):
        raise TypeError("MSC-180 nohint spec is missing a 'problems' object.")
    return sorted(problems.keys())


def merged_key(condition: str, problem_key: str) -> str:
    return f"{condition}/{normalize_problem_key(problem_key)}"


def is_solved(entry: dict[str, Any] | None) -> bool:
    if not isinstance(entry, dict):
        return False
    attempts = entry.get("attempts")
    if not isinstance(attempts, list):
        return False
    return any(bool(attempt.get("success")) for attempt in attempts if isinstance(attempt, dict))


def seed_shard_if_needed(
    *,
    combined_payload: dict[str, Any],
    condition: str,
    problem_key: str,
    shard_path: Path,
) -> None:
    if shard_path.exists():
        return
    key = merged_key(condition, problem_key)
    entry = combined_payload.get(key)
    if not isinstance(entry, dict):
        return
    save_json(shard_path, {key: entry})


def run_worker(
    *,
    python_bin: str,
    args: argparse.Namespace,
    problem_key: str,
    shard_name: str,
) -> tuple[str, int]:
    cmd = [
        python_bin,
        str(RUNNER_PATH),
        "--model-alias",
        args.model_alias,
        "--condition",
        args.condition,
        "--attempts-per-problem",
        str(args.attempts_per_problem),
        "--temperature",
        str(args.temperature),
        "--top-p",
        str(args.top_p),
        "--max-tokens",
        str(args.max_tokens),
        "--prompt-style",
        args.prompt_style,
        "--search-topk",
        str(args.search_topk),
        "--final-theorem-budget",
        str(args.final_theorem_budget),
        "--request-delay-s",
        str(args.request_delay_s),
        "--problem-key",
        problem_key,
        "--stop-on-success",
        "--output-name",
        shard_name,
    ]
    if args.cache_path is not None:
        cmd.extend(["--cache-path", str(args.cache_path)])
    completed = subprocess.run(cmd, cwd=str(ROOT), check=False)
    return problem_key, int(completed.returncode)


def merge_shards(
    *,
    output_path: Path,
    condition: str,
    problem_keys: list[str],
    combined_payload: dict[str, Any],
) -> dict[str, Any]:
    merged = dict(combined_payload)
    for problem_key in problem_keys:
        shard_path = OUTPUT_DIR / shard_output_name(condition, problem_key, output_path.name)
        if not shard_path.exists():
            continue
        shard_payload = load_json(shard_path)
        key = merged_key(condition, problem_key)
        entry = shard_payload.get(key)
        if isinstance(entry, dict):
            merged[key] = entry
    save_json(output_path, merged)
    return merged


def main() -> int:
    args = parse_args()
    if args.max_workers <= 0:
        raise ValueError("--max-workers must be positive.")

    output_path = combined_output_path(args.output_name)
    if output_path.exists():
        combined_payload = load_json(output_path)
        if not isinstance(combined_payload, dict):
            raise TypeError(f"Existing output must be a JSON object: {output_path}")
        print(f"Loaded existing output: {output_path} ({len(combined_payload)} entries)")
    else:
        combined_payload = {}

    all_problem_keys = list_problem_keys()
    forced = set(args.force_problems)
    selected_problem_keys = all_problem_keys
    if forced:
        selected_problem_keys = [problem_key for problem_key in all_problem_keys if problem_key in forced]
        missing = sorted(forced - set(selected_problem_keys))
        if missing:
            raise ValueError(f"Unknown MSC-180 problem keys in --force-problems: {missing}")

    todo: list[str] = []
    skipped = 0
    for problem_key in selected_problem_keys:
        key = merged_key(args.condition, problem_key)
        if problem_key not in forced and is_solved(combined_payload.get(key)):
            skipped += 1
            continue
        todo.append(problem_key)

    print(f"condition: {args.condition}")
    print(f"total problems: {len(selected_problem_keys)}")
    print(f"already solved/skipped: {skipped}")
    print(f"workers to launch: {len(todo)}")

    candidate_bins = [
        str(ROOT / ".venv" / "bin" / "python"),
        sys.executable,
        shutil.which("python3"),
        shutil.which("python"),
    ]
    python_bin = None
    for candidate in candidate_bins:
        if candidate and Path(candidate).exists():
            python_bin = candidate
            break
    if python_bin is None:
        raise FileNotFoundError("Could not locate a Python interpreter for worker processes.")

    for problem_key in todo:
        shard_path = OUTPUT_DIR / shard_output_name(args.condition, problem_key, args.output_name)
        seed_shard_if_needed(
            combined_payload=combined_payload,
            condition=args.condition,
            problem_key=problem_key,
            shard_path=shard_path,
        )

    failures: list[tuple[str, int]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        future_map = {
            pool.submit(
                run_worker,
                python_bin=python_bin,
                args=args,
                problem_key=problem_key,
                shard_name=shard_output_name(args.condition, problem_key, args.output_name),
            ): problem_key
            for problem_key in todo
        }
        for future in concurrent.futures.as_completed(future_map):
            problem_key = future_map[future]
            try:
                finished_problem_key, returncode = future.result()
            except Exception:
                failures.append((problem_key, -1))
                continue
            if returncode != 0:
                failures.append((finished_problem_key, returncode))

    merged_payload = merge_shards(
        output_path=output_path,
        condition=args.condition,
        problem_keys=todo,
        combined_payload=combined_payload,
    )

    solved = sum(
        1 for key in selected_problem_keys if is_solved(merged_payload.get(merged_key(args.condition, key)))
    )
    print(f"merged output: {output_path}")
    print(f"solved after merge: {solved}/{len(selected_problem_keys)}")
    if failures:
        print("failed workers:")
        for problem_key, returncode in failures:
            print(f"  - {problem_key}: rc={returncode}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
