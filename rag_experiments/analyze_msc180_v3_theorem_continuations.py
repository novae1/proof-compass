#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


CONFIG_ORDER = [
    "no-hint",
    "theorem-statements",
    "theorem-statements-and-examples",
]

CLASSIFICATION_ORDER = [
    "exact_match",
    "other_valid_mathlib_theorem",
    "hallucinated_theorem_like_name",
    "incomplete_identifier",
    "no_theorem_like_identifier",
]

DEFAULT_OUTPUT = Path(
    "rag_experiments/outputs/20260305_msc180-v3-theorem-continuations_deepseekv2_7b_lean4-15.json"
)


@dataclass
class SlotStats:
    attempts: int = 0
    exact_attempts: int = 0
    hallucination_attempts: int = 0
    other_valid_attempts: int = 0
    incomplete_attempts: int = 0
    no_identifier_attempts: int = 0

    def update(self, classification: str) -> None:
        self.attempts += 1
        if classification == "exact_match":
            self.exact_attempts += 1
        elif classification == "hallucinated_theorem_like_name":
            self.hallucination_attempts += 1
        elif classification == "other_valid_mathlib_theorem":
            self.other_valid_attempts += 1
        elif classification == "incomplete_identifier":
            self.incomplete_attempts += 1
        elif classification == "no_theorem_like_identifier":
            self.no_identifier_attempts += 1

    def has_exact(self) -> bool:
        return self.exact_attempts > 0

    def has_hallucination(self) -> bool:
        return self.hallucination_attempts > 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze theorem-continuation probes and report exact-match and hallucination "
            "rates overall, by config, and by target theorem."
        )
    )
    parser.add_argument(
        "output_json",
        type=Path,
        nargs="?",
        default=DEFAULT_OUTPUT,
        help="Path to continuation output JSON.",
    )
    parser.add_argument(
        "--top-hallucinations",
        type=int,
        default=20,
        help="How many hallucinated identifiers to print.",
    )
    parser.add_argument(
        "--top-other-valid",
        type=int,
        default=20,
        help="How many non-target valid Mathlib identifiers to print.",
    )
    return parser.parse_args()


def _pct(numer: int, denom: int) -> float:
    if denom == 0:
        return 0.0
    return 100.0 * numer / denom


def _config_from_source_key(source_key: str) -> str:
    if "/" not in source_key:
        return source_key
    return source_key.split("/", 1)[0]


def _print_section(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def main() -> int:
    args = _parse_args()
    if not args.output_json.exists():
        raise FileNotFoundError(f"Output file not found: {args.output_json}")

    payload = json.loads(args.output_json.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Output JSON root must be an object.")

    slot_stats_by_key: dict[str, SlotStats] = {}
    slot_target_by_key: dict[str, str] = {}
    slot_source_by_key: dict[str, str] = {}

    attempts_total = 0
    classification_counts = Counter()
    config_attempt_counts = Counter()
    config_classification_counts: dict[str, Counter[str]] = defaultdict(Counter)
    hallucinated_identifiers = Counter()
    other_valid_identifiers = Counter()
    target_attempt_counts = Counter()
    target_classification_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for slot_key, entry in payload.items():
        if not isinstance(entry, dict):
            continue

        source_key = str(entry.get("header", "")).strip()
        target_theorem = str(entry.get("formal_statement", "")).strip()
        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            attempts = []

        slot_stats = SlotStats()
        slot_stats_by_key[slot_key] = slot_stats
        slot_target_by_key[slot_key] = target_theorem
        slot_source_by_key[slot_key] = source_key

        config = _config_from_source_key(source_key)
        for attempt in attempts:
            if not isinstance(attempt, dict):
                continue
            message = attempt.get("message")
            if not isinstance(message, dict):
                continue
            classification = str(message.get("classification", "")).strip()
            if classification not in CLASSIFICATION_ORDER:
                continue

            slot_stats.update(classification)
            attempts_total += 1
            classification_counts[classification] += 1
            config_attempt_counts[config] += 1
            config_classification_counts[config][classification] += 1
            target_attempt_counts[target_theorem] += 1
            target_classification_counts[target_theorem][classification] += 1

            first_identifier = message.get("first_identifier")
            if classification == "hallucinated_theorem_like_name" and isinstance(first_identifier, str):
                if first_identifier.strip():
                    hallucinated_identifiers[first_identifier.strip()] += 1
            if classification == "other_valid_mathlib_theorem":
                resolved = message.get("resolved_full_name")
                if isinstance(resolved, str) and resolved.strip():
                    other_valid_identifiers[resolved.strip()] += 1

    slots_total = len(slot_stats_by_key)
    slots_with_attempts = sum(1 for s in slot_stats_by_key.values() if s.attempts > 0)
    slot_exact_count = sum(1 for s in slot_stats_by_key.values() if s.has_exact())
    slot_hallucination_count = sum(1 for s in slot_stats_by_key.values() if s.has_hallucination())

    print(f"Output file: {args.output_json}")
    print(f"Slots total: {slots_total}")
    print(f"Slots with attempts: {slots_with_attempts}")
    print(f"Attempts total: {attempts_total}")

    _print_section("Metric 1: Attempt Classification Rate (%)")
    for cls in CLASSIFICATION_ORDER:
        count = classification_counts[cls]
        print(f"{cls:32} {_pct(count, attempts_total):6.2f}% ({count}/{attempts_total})")

    _print_section("Metric 2: Slot-Level Exact@k and Hallucination@k")
    print(f"{'slot_exact@k':32} {_pct(slot_exact_count, slots_total):6.2f}% ({slot_exact_count}/{slots_total})")
    print(
        f"{'slot_hallucination@k':32} "
        f"{_pct(slot_hallucination_count, slots_total):6.2f}% ({slot_hallucination_count}/{slots_total})"
    )

    _print_section("Metric 3: Attempt Classification By Config (%)")
    for cfg in CONFIG_ORDER:
        denom = config_attempt_counts[cfg]
        if denom == 0:
            print(f"{cfg}")
            print("  no attempts")
            continue
        print(cfg)
        for cls in CLASSIFICATION_ORDER:
            count = config_classification_counts[cfg][cls]
            print(f"  {cls:30} {_pct(count, denom):6.2f}% ({count}/{denom})")

    _print_section("Metric 4: Slot-Level Exact@k and Hallucination@k By Config")
    for cfg in CONFIG_ORDER:
        slot_keys = [k for k, source in slot_source_by_key.items() if _config_from_source_key(source) == cfg]
        denom = len(slot_keys)
        exact = sum(1 for k in slot_keys if slot_stats_by_key[k].has_exact())
        halluc = sum(1 for k in slot_keys if slot_stats_by_key[k].has_hallucination())
        print(f"{cfg}")
        print(f"  {'slot_exact@k':30} {_pct(exact, denom):6.2f}% ({exact}/{denom})")
        print(f"  {'slot_hallucination@k':30} {_pct(halluc, denom):6.2f}% ({halluc}/{denom})")

    _print_section("Metric 5: Most Common Hallucinated Identifiers")
    if hallucinated_identifiers:
        for name, count in hallucinated_identifiers.most_common(args.top_hallucinations):
            print(f"{count:4}  {name}")
    else:
        print("none")

    _print_section("Metric 6: Most Common Other Valid Mathlib Theorems")
    if other_valid_identifiers:
        for name, count in other_valid_identifiers.most_common(args.top_other_valid):
            print(f"{count:4}  {name}")
    else:
        print("none")

    _print_section("Metric 7: Per-Target Exact@k / Hallucination@k")
    print(f"{'target theorem':52} {'slots':>5} {'exact@k':>10} {'halluc@k':>10}")
    targets = sorted(set(slot_target_by_key.values()))
    for target in targets:
        slot_keys = [k for k, t in slot_target_by_key.items() if t == target]
        slots = len(slot_keys)
        exact = sum(1 for k in slot_keys if slot_stats_by_key[k].has_exact())
        halluc = sum(1 for k in slot_keys if slot_stats_by_key[k].has_hallucination())
        print(f"{target[:52]:52} {slots:5d} {exact:10d} {halluc:10d}")

    _print_section("Metric 8: Per-Target Attempt Exact Rate (%)")
    print(f"{'target theorem':52} {'attempts':>8} {'exact':>8} {'rate':>8}")
    for target in targets:
        denom = target_attempt_counts[target]
        exact = target_classification_counts[target]["exact_match"]
        print(f"{target[:52]:52} {denom:8d} {exact:8d} {_pct(exact, denom):7.2f}%")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
