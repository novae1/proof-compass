#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_OUTPUT = Path(
    "rag_experiments/outputs/20260305_msc180-v3-theorem-continuations_deepseekv2_7b_lean4-15.json"
)

CONFIG_ORDER = [
    "no-hint",
    "theorem-statements",
    "theorem-statements-and-examples",
]

CORRUPTION_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("artifact_marker", re.compile(r"[ĠĊ]|âŁ|Ã")),
    ("code_fence_restart", re.compile(r"```|lean4theorem|Complete the following Lean 4 code:")),
    ("commentary_text", re.compile(r"--|Explanation|Step\s+\d+|Use the|We need to|ByRolle|By Rolle")),
    ("placeholder_meta", re.compile(r"\?apply|\?have|exact\?|apply\?|sorry\b")),
    ("squashed_spacing", re.compile(r"apply[A-Z?]|byapply|linarithhave|haveh:|exacth|subst_varsdone")),
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze continuation outputs for corruption patterns such as tokenization artifacts, "
            "code-fence restarts, commentary, and placeholder/meta text."
        )
    )
    parser.add_argument(
        "output_json",
        type=Path,
        nargs="?",
        default=DEFAULT_OUTPUT,
        help="Path to theorem-continuation output JSON.",
    )
    parser.add_argument(
        "--samples-per-category",
        type=int,
        default=5,
        help="How many example continuations to print for each corruption category.",
    )
    parser.add_argument(
        "--top-slots",
        type=int,
        default=10,
        help="How many most-corrupted slots to print.",
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

    attempts_total = 0
    clean_attempts = 0

    category_counts = Counter()
    config_attempt_counts = Counter()
    config_category_counts: dict[str, Counter[str]] = defaultdict(Counter)
    slot_corruption_counts = Counter()
    slot_attempt_counts = Counter()
    samples: dict[str, list[tuple[str, str, str]]] = defaultdict(list)

    for slot_key, entry in payload.items():
        if not isinstance(entry, dict):
            continue
        source_key = str(entry.get("header", "")).strip()
        config = _config_from_source_key(source_key)
        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            continue

        for attempt in attempts:
            if not isinstance(attempt, dict):
                continue
            parsed_proof = str(attempt.get("parsed_proof", "") or "")
            attempts_total += 1
            config_attempt_counts[config] += 1
            slot_attempt_counts[slot_key] += 1

            triggered: list[str] = []
            for category, pattern in CORRUPTION_RULES:
                if pattern.search(parsed_proof):
                    triggered.append(category)
                    category_counts[category] += 1
                    config_category_counts[config][category] += 1
                    if len(samples[category]) < args.samples_per_category:
                        samples[category].append((slot_key, config, parsed_proof[:180]))

            if triggered:
                slot_corruption_counts[slot_key] += 1
            else:
                clean_attempts += 1

    slots_total = len(slot_attempt_counts)
    corrupted_slots = sum(1 for k in slot_attempt_counts if slot_corruption_counts[k] > 0)

    print(f"Output file: {args.output_json}")
    print(f"Slots total: {slots_total}")
    print(f"Attempts total: {attempts_total}")

    _print_section("Metric 1: Clean vs Corrupted Attempts")
    corrupted_attempts = attempts_total - clean_attempts
    print(f"{'clean_attempts':24} {_pct(clean_attempts, attempts_total):6.2f}% ({clean_attempts}/{attempts_total})")
    print(
        f"{'corrupted_attempts':24} "
        f"{_pct(corrupted_attempts, attempts_total):6.2f}% ({corrupted_attempts}/{attempts_total})"
    )

    _print_section("Metric 2: Corruption Category Rates")
    for category, _ in CORRUPTION_RULES:
        count = category_counts[category]
        print(f"{category:24} {_pct(count, attempts_total):6.2f}% ({count}/{attempts_total})")

    _print_section("Metric 3: Corruption Rates By Config")
    for config in CONFIG_ORDER:
        denom = config_attempt_counts[config]
        print(config)
        if denom == 0:
            print("  no attempts")
            continue
        corrupted = sum(config_category_counts[config][category] > 0 for category, _ in CORRUPTION_RULES)
        clean = denom
        for category, _ in CORRUPTION_RULES:
            count = config_category_counts[config][category]
            print(f"  {category:22} {_pct(count, denom):6.2f}% ({count}/{denom})")

    _print_section("Metric 4: Slot-Level Corruption")
    print(f"{'slots_with_any_corruption':24} {_pct(corrupted_slots, slots_total):6.2f}% ({corrupted_slots}/{slots_total})")

    _print_section("Metric 5: Most-Corrupted Slots")
    print(f"{'slot':72} {'corrupted':>10} {'attempts':>10} {'rate':>8}")
    for slot_key, count in slot_corruption_counts.most_common(args.top_slots):
        attempts = slot_attempt_counts[slot_key]
        print(f"{slot_key[:72]:72} {count:10d} {attempts:10d} {_pct(count, attempts):7.2f}%")

    _print_section("Metric 6: Example Corrupt Continuations")
    for category, _ in CORRUPTION_RULES:
        print(category)
        if not samples[category]:
            print("  none")
            continue
        for slot_key, config, snippet in samples[category]:
            print(f"  [{config}] {slot_key}")
            print(f"    {snippet!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
