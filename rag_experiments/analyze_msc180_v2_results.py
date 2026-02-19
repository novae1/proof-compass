#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


CONFIG_ORDER = [
    "no-hint",
    "theorem-statements",
    "theorem-statements-and-examples",
]


@dataclass
class ConfigMetrics:
    attempts_total: int = 0
    attempts_success: int = 0
    attempts_with_unknown: int = 0
    total_unknown_occurrences: int = 0
    problems_total: int = 0
    problems_pass_at_8: int = 0
    per_problem_successes: dict[str, int] | None = None
    per_problem_attempts: dict[str, int] | None = None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze MSC-180 v2 combined output and print per-config metrics "
            "for success and unknown-constant errors."
        )
    )
    parser.add_argument(
        "output_json",
        type=Path,
        nargs="?",
        default=Path("rag_experiments/outputs/20260217_msc180-v2_deepseekv2_7b_lean4-15.json"),
        help="Path to combined output JSON (default: latest v2 deepseek path).",
    )
    parser.add_argument(
        "--unknown-regex",
        default=r"unknown\s+constant",
        help="Regex used to count unknown-constant occurrences from attempt message text.",
    )
    return parser.parse_args()


def _to_text(obj: object) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "\n".join(_to_text(x) for x in obj)
    if isinstance(obj, dict):
        return json.dumps(obj, ensure_ascii=False)
    return str(obj)


def _normalize_problem_id(raw_problem_key: str) -> str:
    # "MSC-180_05_003" -> "05_003", fallback keeps raw key.
    m = re.search(r"(\d{2}_\d{3})$", raw_problem_key)
    return m.group(1) if m else raw_problem_key


def _compute_metrics(payload: dict, unknown_pattern: re.Pattern[str]) -> dict[str, ConfigMetrics]:
    by_config: dict[str, dict[str, list[dict]]] = {cfg: {} for cfg in CONFIG_ORDER}

    for merged_key, entry in payload.items():
        if not isinstance(entry, dict):
            continue
        if "/" not in merged_key:
            continue
        config, raw_problem = merged_key.split("/", 1)
        if config not in by_config:
            continue
        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            attempts = []
        problem = _normalize_problem_id(raw_problem)
        by_config[config][problem] = attempts

    metrics: dict[str, ConfigMetrics] = {}
    for config in CONFIG_ORDER:
        per_problem_successes: dict[str, int] = {}
        per_problem_attempts: dict[str, int] = {}
        attempts_total = 0
        attempts_success = 0
        attempts_with_unknown = 0
        total_unknown_occurrences = 0

        for problem, attempts in by_config[config].items():
            s = 0
            n = 0
            for attempt in attempts:
                if not isinstance(attempt, dict):
                    continue
                n += 1
                attempts_total += 1
                if bool(attempt.get("success")):
                    attempts_success += 1
                    s += 1
                msg_text = _to_text(attempt.get("message"))
                occurrences = len(unknown_pattern.findall(msg_text))
                if occurrences > 0:
                    attempts_with_unknown += 1
                    total_unknown_occurrences += occurrences

            per_problem_successes[problem] = s
            per_problem_attempts[problem] = n

        problems_total = len(by_config[config])
        problems_pass_at_8 = sum(1 for p in by_config[config] if per_problem_successes.get(p, 0) > 0)

        metrics[config] = ConfigMetrics(
            attempts_total=attempts_total,
            attempts_success=attempts_success,
            attempts_with_unknown=attempts_with_unknown,
            total_unknown_occurrences=total_unknown_occurrences,
            problems_total=problems_total,
            problems_pass_at_8=problems_pass_at_8,
            per_problem_successes=per_problem_successes,
            per_problem_attempts=per_problem_attempts,
        )

    return metrics


def _pct(numer: int, denom: int) -> float:
    if denom == 0:
        return 0.0
    return 100.0 * numer / denom


def _print_section(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def _print_metrics(metrics: dict[str, ConfigMetrics]) -> None:
    _print_section("Metric 1: Attempt Pass Rate (%)")
    for cfg in CONFIG_ORDER:
        m = metrics[cfg]
        print(
            f"{cfg:32} {_pct(m.attempts_success, m.attempts_total):6.2f}% "
            f"({m.attempts_success}/{m.attempts_total})"
        )

    _print_section("Metric 2: Problem Pass@8 (%)")
    for cfg in CONFIG_ORDER:
        m = metrics[cfg]
        print(
            f"{cfg:32} {_pct(m.problems_pass_at_8, m.problems_total):6.2f}% "
            f"({m.problems_pass_at_8}/{m.problems_total})"
        )

    _print_section("Metric 3: Attempts With Unknown Constant (%)")
    for cfg in CONFIG_ORDER:
        m = metrics[cfg]
        print(
            f"{cfg:32} {_pct(m.attempts_with_unknown, m.attempts_total):6.2f}% "
            f"({m.attempts_with_unknown}/{m.attempts_total})"
        )

    _print_section("Metric 4: Total Unknown Constant Occurrences")
    for cfg in CONFIG_ORDER:
        m = metrics[cfg]
        print(f"{cfg:32} {m.total_unknown_occurrences}")

    _print_section("Metric 5: Per-Problem Pass Count (k/attempts)")
    problem_ids: list[str] = sorted(
        {pid for cfg in CONFIG_ORDER for pid in (metrics[cfg].per_problem_successes or {}).keys()}
    )
    print(
        f"{'problem':10} {'no-hint':>12} {'theorem-statements':>20} "
        f"{'theorem-statements-and-examples':>34}"
    )
    for pid in problem_ids:
        cells: list[str] = []
        for cfg in CONFIG_ORDER:
            m = metrics[cfg]
            ps = m.per_problem_successes or {}
            pa = m.per_problem_attempts or {}
            cells.append(f"{ps.get(pid, 0)}/{pa.get(pid, 0)}")
        print(f"{pid:10} {cells[0]:>12} {cells[1]:>20} {cells[2]:>34}")


def main() -> int:
    args = _parse_args()
    if not args.output_json.exists():
        raise FileNotFoundError(f"Output file not found: {args.output_json}")

    payload = json.loads(args.output_json.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Output JSON root must be an object.")

    unknown_pattern = re.compile(args.unknown_regex, flags=re.IGNORECASE)
    metrics = _compute_metrics(payload, unknown_pattern)

    print(f"Output file: {args.output_json}")
    print(f"Unknown matcher regex: {args.unknown_regex}")
    _print_metrics(metrics)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
