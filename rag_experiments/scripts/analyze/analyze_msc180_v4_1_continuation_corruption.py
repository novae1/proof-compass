#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_OUTPUT = Path(
    "rag_experiments/outputs/msc180/theorem_continuations/v4/20260310_msc180-v4-theorem-continuations-recovered_deepseekv2_7b_lean4-15.json"
)
RUN_METADATA_KEY = "__meta__"

CONFIG_ORDER = [
    "no-hint",
    "theorem-statements",
    "theorem-statements-and-examples",
]

LEGACY_ARTIFACT_MARKER_RE = re.compile(r"[ĠĊ]|âŁ|Ã")
LEGACY_SQUASHED_SPACING_RE = re.compile(r"apply[A-Z?]|byapply|linarithhave|haveh:|exacth|subst_varsdone")
PLACEHOLDER_META_RE = re.compile(r"\?apply|\?have|exact\?|apply\?|\bsorry\b")
LEAN_COMMENT_RE = re.compile(r"(?m)--.*$")
MARKDOWN_PROSE_RE = re.compile(
    r"(?mi)(?:^\s{0,3}#{1,6}\s|^\s*\d+\.\s|\*\*|Explanation|Refined Lean 4 Code|Complete the following Lean 4 code:)"
)

PRIMARY_ORDER = [
    "clean",
    "lean_comment_only",
    "prose_explanation_restart",
    "placeholder_meta",
    "tokenizer_artifact",
    "squashed_spacing",
    "mixed_structural",
]

STRUCTURAL_LABELS = {
    "prose_explanation_restart",
    "placeholder_meta",
    "tokenizer_artifact",
    "squashed_spacing",
    "mixed_structural",
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze v4 continuation outputs with a stricter split between benign Lean comments "
            "and truly structural corruption."
        )
    )
    parser.add_argument(
        "output_json",
        type=Path,
        nargs="?",
        default=DEFAULT_OUTPUT,
        help="Path to theorem-continuation output JSON.",
    )
    parser.add_argument("--samples-per-label", type=int, default=5)
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


def _strip_lean_comments(text: str) -> str:
    return LEAN_COMMENT_RE.sub("", text)


def _has_restarting_fence(text_without_comments: str) -> bool:
    idx = text_without_comments.find("```")
    while idx != -1:
        if text_without_comments[idx + 3 :].strip():
            return True
        idx = text_without_comments.find("```", idx + 3)
    return False


def _legacy_flagged(text: str) -> bool:
    if LEGACY_ARTIFACT_MARKER_RE.search(text):
        return True
    if LEGACY_SQUASHED_SPACING_RE.search(text):
        return True
    if PLACEHOLDER_META_RE.search(text):
        return True
    if "--" in text or re.search(r"Explanation|Step\s+\d+|Use the|We need to|ByRolle|By Rolle", text):
        return True
    text_wo_comments = _strip_lean_comments(text)
    return _has_restarting_fence(text_wo_comments)


def _classify_primary(text: str) -> tuple[str, dict[str, bool]]:
    text_wo_comments = _strip_lean_comments(text)
    has_lean_comment = bool(LEAN_COMMENT_RE.search(text))
    has_artifact = bool(LEGACY_ARTIFACT_MARKER_RE.search(text))
    has_squashed = bool(LEGACY_SQUASHED_SPACING_RE.search(text))
    has_placeholder = bool(PLACEHOLDER_META_RE.search(text_wo_comments))
    has_restarting_fence = _has_restarting_fence(text_wo_comments)
    has_markdown_prose = bool(MARKDOWN_PROSE_RE.search(text_wo_comments))
    has_prose_restart = has_restarting_fence or has_markdown_prose

    structural_hits = sum([has_artifact, has_squashed, has_placeholder, has_prose_restart])
    details = {
        "has_lean_comment": has_lean_comment,
        "has_artifact": has_artifact,
        "has_squashed": has_squashed,
        "has_placeholder": has_placeholder,
        "has_prose_restart": has_prose_restart,
        "has_restarting_fence": has_restarting_fence,
        "has_markdown_prose": has_markdown_prose,
    }

    if structural_hits > 1:
        return "mixed_structural", details
    if has_artifact:
        return "tokenizer_artifact", details
    if has_squashed:
        return "squashed_spacing", details
    if has_placeholder:
        return "placeholder_meta", details
    if has_prose_restart:
        return "prose_explanation_restart", details
    if has_lean_comment:
        return "lean_comment_only", details
    return "clean", details


def main() -> int:
    args = _parse_args()
    if not args.output_json.exists():
        raise FileNotFoundError(f"Output file not found: {args.output_json}")

    payload = json.loads(args.output_json.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Output JSON root must be an object.")

    attempts_total = 0
    legacy_flagged_total = 0
    primary_counts = Counter()
    config_primary_counts: dict[str, Counter[str]] = defaultdict(Counter)
    classification_by_primary: dict[str, Counter[str]] = defaultdict(Counter)
    primary_samples: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    legacy_to_primary = Counter()
    structural_total = 0
    structural_slots = set()
    bare_trailing_fence_only = 0

    for slot_key, entry in payload.items():
        if slot_key == RUN_METADATA_KEY:
            continue
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
            attempts_total += 1
            parsed_proof = str(attempt.get("parsed_proof", "") or "")
            classification = str(attempt.get("message", {}).get("classification", "") or "")

            primary, details = _classify_primary(parsed_proof)
            primary_counts[primary] += 1
            config_primary_counts[config][primary] += 1
            classification_by_primary[primary][classification] += 1
            if len(primary_samples[primary]) < args.samples_per_label:
                primary_samples[primary].append((slot_key, classification, parsed_proof[:220]))

            if primary in STRUCTURAL_LABELS:
                structural_total += 1
                structural_slots.add(slot_key)

            legacy = _legacy_flagged(parsed_proof)
            if legacy:
                legacy_flagged_total += 1
                legacy_to_primary[primary] += 1

            if "```" in parsed_proof and not _has_restarting_fence(_strip_lean_comments(parsed_proof)):
                bare_trailing_fence_only += 1

    print(f"Output file: {args.output_json}")
    print(f"Attempts total: {attempts_total}")

    _print_section("Metric 1: Revised Primary Labels")
    for label in PRIMARY_ORDER:
        count = primary_counts[label]
        print(f"{label:28} {_pct(count, attempts_total):6.2f}% ({count}/{attempts_total})")

    _print_section("Metric 2: Legacy-Flagged Attempts Reinterpreted")
    print(f"{'legacy_flagged_total':28} {_pct(legacy_flagged_total, attempts_total):6.2f}% ({legacy_flagged_total}/{attempts_total})")
    print(f"{'revised_structural_total':28} {_pct(structural_total, attempts_total):6.2f}% ({structural_total}/{attempts_total})")
    print(f"{'structural_slots':28} {len(structural_slots):6d}")
    print(f"{'bare_trailing_fence_only':28} {_pct(bare_trailing_fence_only, attempts_total):6.2f}% ({bare_trailing_fence_only}/{attempts_total})")

    _print_section("Metric 3: Legacy-Flagged -> Revised Label")
    for label, count in legacy_to_primary.most_common():
        print(f"{label:28} {_pct(count, legacy_flagged_total):6.2f}% ({count}/{legacy_flagged_total})")

    _print_section("Metric 4: Revised Labels By Config")
    for config in CONFIG_ORDER:
        denom = sum(config_primary_counts[config].values())
        print(config)
        if denom == 0:
            print("  no attempts")
            continue
        for label in PRIMARY_ORDER:
            count = config_primary_counts[config][label]
            print(f"  {label:26} {_pct(count, denom):6.2f}% ({count}/{denom})")

    _print_section("Metric 5: Theorem Classification By Revised Label")
    print(f"{'label':28} {'exact':>8} {'other':>8} {'halluc':>8} {'no_id':>8}")
    for label in PRIMARY_ORDER:
        counts = classification_by_primary[label]
        print(
            f"{label:28} "
            f"{counts['exact_match']:8d} "
            f"{counts['other_valid_mathlib_theorem']:8d} "
            f"{counts['hallucinated_theorem_like_name']:8d} "
            f"{counts['no_theorem_like_identifier']:8d}"
        )

    _print_section("Metric 6: Example Snippets")
    for label in PRIMARY_ORDER:
        print(label)
        if not primary_samples[label]:
            print("  none")
            continue
        for slot_key, classification, snippet in primary_samples[label]:
            print(f"  [{classification}] {slot_key}")
            print(f"    {snippet!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
