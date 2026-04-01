#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from extract_hallucinations import summarize


DEFAULT_BASE_NOHINT = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260331_proofnet-valid_nohint_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_PASS2_NOHINT = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260401_proofnet-valid_nohint-pass2_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_BASE_RAG = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260331_proofnet-valid_statement-rag-top2_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_PASS2_RAG = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260401_proofnet-valid_statement-rag-top2-pass2_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_SPEC_NOHINT = Path(
    "rag_experiments/data/specs/20260331_proofnet_valid_nohint_iterative_pass2_spec.json"
)
DEFAULT_SPEC_RAG = Path(
    "rag_experiments/data/specs/"
    "20260331_proofnet_valid_statement_rag_top2_iterative_pass2_spec.json"
)
DEFAULT_OUTPUT = Path(
    "rag_experiments/reports/iterative_rag/"
    "20260401_proofnet_valid_pass2_hallucination_metrics.png"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Plot triggered-subset hallucination metrics for ProofNet-valid "
            "pass1 versus pass2 runs."
        )
    )
    parser.add_argument("--base-nohint", type=Path, default=DEFAULT_BASE_NOHINT)
    parser.add_argument("--pass2-nohint", type=Path, default=DEFAULT_PASS2_NOHINT)
    parser.add_argument("--base-rag", type=Path, default=DEFAULT_BASE_RAG)
    parser.add_argument("--pass2-rag", type=Path, default=DEFAULT_PASS2_RAG)
    parser.add_argument("--spec-nohint", type=Path, default=DEFAULT_SPEC_NOHINT)
    parser.add_argument("--spec-rag", type=Path, default=DEFAULT_SPEC_RAG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected JSON object at {path}")
    return payload


def canonical_problem_key(problem_key: str) -> str:
    if "/" in problem_key:
        return problem_key.split("/", 1)[1]
    return problem_key


def build_key_map(payload: dict[str, Any]) -> dict[str, str]:
    return {canonical_problem_key(problem_key): problem_key for problem_key in payload}


def subset_metrics(
    run_payload: dict[str, Any],
    summary: dict[str, Any],
    canonical_keys: set[str],
) -> dict[str, float | int]:
    key_map = build_key_map(run_payload)
    failed_attempts = 0
    failed_attempts_with_hall = 0
    hall_occurrences = 0
    failed_problems = 0
    failed_problems_with_hall = 0

    for canonical_key in canonical_keys:
        actual_key = key_map[canonical_key]
        attempts = run_payload[actual_key]["attempts"]
        problem_summary = summary["problems"][actual_key]
        solved = any(bool(attempt.get("success")) for attempt in attempts)
        problem_has_hall = problem_summary["attempts_with_filtered_unresolved_name"] > 0
        hall_occurrences += int(problem_summary["filtered_unresolved_name_occurrences"])

        if not solved:
            failed_problems += 1
            if problem_has_hall:
                failed_problems_with_hall += 1

        for attempt_row in problem_summary["attempt_rows"]:
            if attempt_row["success"]:
                continue
            failed_attempts += 1
            if attempt_row["filtered_names"]:
                failed_attempts_with_hall += 1

    return {
        "failed_attempts": failed_attempts,
        "failed_attempts_with_hall": failed_attempts_with_hall,
        "failed_problems": failed_problems,
        "failed_problems_with_hall": failed_problems_with_hall,
        "hall_occurrences": hall_occurrences,
        "failed_attempt_hall_rate": (
            100.0 * failed_attempts_with_hall / failed_attempts if failed_attempts else 0.0
        ),
        "failed_problem_hall_rate": (
            100.0 * failed_problems_with_hall / failed_problems if failed_problems else 0.0
        ),
        "hall_occurrences_per_100_failed_attempts": (
            100.0 * hall_occurrences / failed_attempts if failed_attempts else 0.0
        ),
    }


def annotate_bars(ax: plt.Axes, bars: list[Any], fmt: str) -> None:
    for bar in bars:
        height = float(bar.get_height())
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 1.2,
            fmt.format(height),
            ha="center",
            va="bottom",
            fontsize=9,
        )


def main() -> int:
    args = parse_args()

    base_nohint_payload = load_json(args.base_nohint)
    pass2_nohint_payload = load_json(args.pass2_nohint)
    base_rag_payload = load_json(args.base_rag)
    pass2_rag_payload = load_json(args.pass2_rag)

    spec_nohint = load_json(args.spec_nohint)["problems"]
    spec_rag = load_json(args.spec_rag)["problems"]

    base_nohint_summary = summarize(args.base_nohint, min_name_length=7, top=20)
    pass2_nohint_summary = summarize(args.pass2_nohint, min_name_length=7, top=20)
    base_rag_summary = summarize(args.base_rag, min_name_length=7, top=20)
    pass2_rag_summary = summarize(args.pass2_rag, min_name_length=7, top=20)

    triggered_nohint = set(spec_nohint.keys())
    triggered_rag = set(spec_rag.keys())

    metrics = {
        "NoHint Pass1": subset_metrics(
            base_nohint_payload, base_nohint_summary, triggered_nohint
        ),
        "NoHint Pass2": subset_metrics(
            pass2_nohint_payload, pass2_nohint_summary, triggered_nohint
        ),
        "RAG Pass1": subset_metrics(base_rag_payload, base_rag_summary, triggered_rag),
        "RAG Pass2": subset_metrics(pass2_rag_payload, pass2_rag_summary, triggered_rag),
    }

    labels = list(metrics.keys())
    positions = [0.0, 1.0, 3.0, 4.0]
    colors = ["#c46b48", "#f0b37e", "#2d6a8e", "#7fc8d4"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), constrained_layout=True)

    panels = [
        (
            "failed_attempt_hall_rate",
            "% Failed Attempts With Hallucination",
            "{:.1f}%",
            (0, 60),
        ),
        (
            "failed_problem_hall_rate",
            "% Failed Problems With Hallucination",
            "{:.1f}%",
            (0, 105),
        ),
        (
            "hall_occurrences_per_100_failed_attempts",
            "Hallucination Occurrences Per 100 Failed Attempts",
            "{:.1f}",
            (0, 70),
        ),
    ]

    for ax, (metric_key, title, value_fmt, ylim) in zip(axes, panels):
        values = [float(metrics[label][metric_key]) for label in labels]
        bars = ax.bar(positions, values, color=colors, width=0.8)
        annotate_bars(ax, list(bars), value_fmt)
        ax.set_title(title, fontsize=11)
        ax.set_xticks(positions, labels, rotation=20, ha="right")
        ax.set_ylim(*ylim)
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)

    fig.suptitle(
        "ProofNet-valid Triggered-Subset Hallucination Metrics: Pass1 vs Pass2",
        fontsize=13,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=200, bbox_inches="tight")
    print(f"Wrote figure to {args.output}")
    for label in labels:
        print(label, metrics[label])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
