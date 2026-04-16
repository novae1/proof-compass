#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from api_proving.model_registry import FREE_MODEL_ALIASES

SCRIPT = Path(__file__).resolve().parent / "run_openrouter_proofnet.py"
DEFAULT_SPEC = ROOT / "api_proving" / "data" / "specs" / "20260416_proofnet_valid_nohint_smoke2_spec.json"
DEFAULT_PYTHON = ROOT / ".venv" / "bin" / "python"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the OpenRouter ProofNet smoke run.")
    parser.add_argument("--spec-path", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--condition-label", default="nohint-smoke2")
    parser.add_argument("--attempts-per-problem", type=int, default=2)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--top-p", type=float, default=0.95)
    parser.add_argument("--max-tokens", type=int, default=4000)
    parser.add_argument("--max-problems", type=int)
    parser.add_argument("--max-parallel-models", type=int, default=4)
    parser.add_argument("--skip-verification", action="store_true")
    return parser.parse_args()


def _build_command(args: argparse.Namespace, model_alias: str) -> list[str]:
    cmd = [
        str(DEFAULT_PYTHON if DEFAULT_PYTHON.exists() else Path(sys.executable)),
        str(SCRIPT),
        "--spec-path",
        str(args.spec_path),
        "--model-alias",
        model_alias,
        "--condition-label",
        args.condition_label,
        "--attempts-per-problem",
        str(args.attempts_per_problem),
        "--temperature",
        str(args.temperature),
        "--top-p",
        str(args.top_p),
        "--max-tokens",
        str(args.max_tokens),
    ]
    if args.max_problems is not None:
        cmd.extend(["--max-problems", str(args.max_problems)])
    if args.skip_verification:
        cmd.append("--skip-verification")
    return cmd


def main() -> int:
    args = parse_args()
    if args.max_parallel_models <= 0:
        raise ValueError("--max-parallel-models must be positive.")

    pending = list(FREE_MODEL_ALIASES)
    running: list[tuple[str, subprocess.Popen[str]]] = []
    failures: list[str] = []

    while pending or running:
        while pending and len(running) < args.max_parallel_models:
            alias = pending.pop(0)
            cmd = _build_command(args, alias)
            print(f"Starting {alias}")
            proc = subprocess.Popen(cmd, cwd=ROOT)
            running.append((alias, proc))
            time.sleep(1.5)

        next_running: list[tuple[str, subprocess.Popen[str]]] = []
        for alias, proc in running:
            returncode = proc.poll()
            if returncode is None:
                next_running.append((alias, proc))
                continue
            if returncode != 0:
                failures.append(alias)
                print(f"FAILED {alias} (exit {returncode})")
            else:
                print(f"Finished {alias}")
        running = next_running
        if running:
            time.sleep(2)

    if failures:
        print(f"Smoke run completed with failures: {', '.join(failures)}")
        return 1
    print("Smoke run completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
