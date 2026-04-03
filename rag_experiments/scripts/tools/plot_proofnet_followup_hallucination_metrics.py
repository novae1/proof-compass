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
DEFAULT_EXTRA_NOHINT = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260401_proofnet-valid_nohint-trigger-subset_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_PASS2_NOHINT = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260401_proofnet-valid_nohint-pass2_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_TOP4_NOHINT = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260401_proofnet-valid_nohint-attempt-rag-top4_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_TOP6_NOHINT = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260402_proofnet-valid_nohint-allhall-attempt-top6_base_deepseekv2_7b_lean4-15_verified.json"
)

DEFAULT_BASE_RAG = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260331_proofnet-valid_statement-rag-top2_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_EXTRA_RAG = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260401_proofnet-valid_statement-rag-top2-trigger-subset_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_PASS2_RAG = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260401_proofnet-valid_statement-rag-top2-pass2_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_TOP4_RAG = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260401_proofnet-valid_statement-rag-top2-attempt-rag-top4_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_TOP6_RAG = Path(
    "rag_experiments/outputs/proofnet/valid/"
    "20260402_proofnet-valid_statement-rag-top2-allhall-attempt-top6_base_deepseekv2_7b_lean4-15_verified.json"
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
    "20260402_proofnet_valid_followup_hallucination_metrics.png"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Plot hallucination metrics for ProofNet-valid follow-up retrieval runs on the "
            "no-hint trigger subset and the statement-RAG-top2 trigger subset."
        )
    )
    parser.add_argument("--base-nohint", type=Path, default=DEFAULT_BASE_NOHINT)
    parser.add_argument("--extra-nohint", type=Path, default=DEFAULT_EXTRA_NOHINT)
    parser.add_argument("--pass2-nohint", type=Path, default=DEFAULT_PASS2_NOHINT)
    parser.add_argument("--top4-nohint", type=Path, default=DEFAULT_TOP4_NOHINT)
    parser.add_argument("--top6-nohint", type=Path, default=DEFAULT_TOP6_NOHINT)
    parser.add_argument("--base-rag", type=Path, default=DEFAULT_BASE_RAG)
    parser.add_argument("--extra-rag", type=Path, default=DEFAULT_EXTRA_RAG)
    parser.add_argument("--pass2-rag", type=Path, default=DEFAULT_PASS2_RAG)
    parser.add_argument("--top4-rag", type=Path, default=DEFAULT_TOP4_RAG)
    parser.add_argument("--top6-rag", type=Path, default=DEFAULT_TOP6_RAG)
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
    return problem_key.split("/", 1)[1] if "/" in problem_key else problem_key


def build_key_map(payload: dict[str, Any]) -> dict[str, str]:
    return {canonical_problem_key(problem_key): problem_key for problem_key in payload}


def subset_metrics(
    run_payload: dict[str, Any],
    summary: dict[str, Any],
    canonical_keys: set[str],
) -> dict[str, float]:
    key_map = build_key_map(run_payload)
    attempts = 0
    attempts_with_hall = 0
    failed_attempts = 0
    failed_attempts_with_hall = 0
    problems = 0
    problems_with_hall = 0
    failed_problems = 0
    failed_problems_with_hall = 0

    for canonical_key in canonical_keys:
        actual_key = key_map[canonical_key]
        attempts_data = run_payload[actual_key]["attempts"]
        problem_summary = summary["problems"][actual_key]
        problems += 1
        solved = any(bool(attempt.get("success")) for attempt in attempts_data)
        problem_has_hall = problem_summary["attempts_with_filtered_unresolved_name"] > 0
        if problem_has_hall:
            problems_with_hall += 1
        if not solved:
            failed_problems += 1
            if problem_has_hall:
                failed_problems_with_hall += 1

        for attempt_row in problem_summary["attempt_rows"]:
            attempts += 1
            has_hall = bool(attempt_row["filtered_names"])
            if has_hall:
                attempts_with_hall += 1
            if not attempt_row["success"]:
                failed_attempts += 1
                if has_hall:
                    failed_attempts_with_hall += 1

    return {
        "attempt_hall_rate": 100.0 * attempts_with_hall / attempts if attempts else 0.0,
        "failed_attempt_hall_rate": (
            100.0 * failed_attempts_with_hall / failed_attempts if failed_attempts else 0.0
        ),
        "problem_hall_rate": 100.0 * problems_with_hall / problems if problems else 0.0,
        "failed_problem_hall_rate": (
            100.0 * failed_problems_with_hall / failed_problems if failed_problems else 0.0
        ),
    }


def annotate_bars(ax: plt.Axes, bars: list[Any]) -> None:
    for bar in bars:
        height = float(bar.get_height())
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 1.4,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            fontsize=8,
        )


def build_run_metrics(
    run_paths: dict[str, Path],
    canonical_keys: set[str],
) -> dict[str, dict[str, float]]:
    metrics: dict[str, dict[str, float]] = {}
    for label, path in run_paths.items():
        payload = load_json(path)
        summary = summarize(path, min_name_length=7, top=20)
        metrics[label] = subset_metrics(payload, summary, canonical_keys)
    return metrics


def main() -> int:
    args = parse_args()

    spec_nohint = load_json(args.spec_nohint)["problems"]
    spec_rag = load_json(args.spec_rag)["problems"]

    nohint_keys = set(spec_nohint.keys())
    rag_keys = set(spec_rag.keys())

    nohint_runs = {
        "Base4": args.base_nohint,
        "Extra4": args.extra_nohint,
        "Pass2": args.pass2_nohint,
        "Top4": args.top4_nohint,
        "Top6": args.top6_nohint,
    }
    rag_runs = {
        "Base4": args.base_rag,
        "Extra4": args.extra_rag,
        "Pass2": args.pass2_rag,
        "Top4": args.top4_rag,
        "Top6": args.top6_rag,
    }

    metrics_nohint = build_run_metrics(nohint_runs, nohint_keys)
    metrics_rag = build_run_metrics(rag_runs, rag_keys)

    run_labels = list(nohint_runs.keys())
    colors = ["#7a1f1f", "#c46b48", "#f0b37e", "#4c956c", "#2d6a8e"]
    positions = list(range(len(run_labels)))

    panels = [
        ("attempt_hall_rate", "Attempt Hallucination Rate"),
        ("failed_attempt_hall_rate", "Failed-Attempt Hallucination Rate"),
        ("problem_hall_rate", "Problem Hallucination Rate"),
        ("failed_problem_hall_rate", "Failed-Problem Hallucination Rate"),
    ]

    fig, axes = plt.subplots(2, 4, figsize=(18, 8), constrained_layout=True)

    for row_idx, (row_title, metrics) in enumerate(
        [("NoHint Trigger Set N", metrics_nohint), ("RAG-Top2 Trigger Set R", metrics_rag)]
    ):
        for col_idx, (metric_key, title) in enumerate(panels):
            ax = axes[row_idx][col_idx]
            values = [metrics[label][metric_key] for label in run_labels]
            bars = ax.bar(positions, values, color=colors, width=0.75)
            annotate_bars(ax, list(bars))
            ax.set_title(title, fontsize=11)
            ax.set_xticks(positions, run_labels, rotation=25, ha="right")
            ax.set_ylim(0, 105)
            ax.grid(axis="y", alpha=0.25)
            ax.set_axisbelow(True)
            if col_idx == 0:
                ax.set_ylabel(row_title, fontsize=10)

    fig.suptitle(
        "ProofNet-valid Follow-up Hallucination Metrics on Triggered Subsets",
        fontsize=14,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=220, bbox_inches="tight")
    print(f"Wrote figure to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
