#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROMPT_MARKERS = [
    (
        "The plan should highlight key ideas, intermediate lemmas, and proof structures "
        "that will guide the construction of the final formal proof."
    ),
    (
        "Before producing the Lean 4 code to formally prove the given theorem, provide a "
        "detailed proof plan outlining the main proof steps and strategies."
    ),
]

HEADER_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
CODE_BLOCK_RE = re.compile(r"```lean4?|```lean", re.I)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze markdown heading structure in CoT-style model outputs."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repo root to scan. Defaults to the current repo root.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional path to write full JSON analysis.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        help="Optional path to write a compact markdown summary.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="How many top headings/orders to include in the summary.",
    )
    return parser.parse_args()


def iter_raw_outputs(obj: Any) -> list[str]:
    outputs: list[str] = []
    if isinstance(obj, dict):
        raw = obj.get("raw_output")
        if isinstance(raw, str):
            outputs.append(raw)
        for value in obj.values():
            outputs.extend(iter_raw_outputs(value))
    elif isinstance(obj, list):
        for item in obj:
            outputs.extend(iter_raw_outputs(item))
    return outputs


def extract_completion(raw_output: str) -> str | None:
    for marker in PROMPT_MARKERS:
        idx = raw_output.rfind(marker)
        if idx != -1:
            return raw_output[idx + len(marker) :].lstrip()
    return None


def canonicalize_heading(title: str) -> str:
    text = title.lower().strip()
    text = re.sub(r"[`*_:\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify_heading(title: str) -> str | None:
    text = canonicalize_heading(title)
    if (
        "complete lean 4 proof" in text
        or "complete formal proof" in text
        or "complete lean 4 code" in text
        or text == "lean 4 code"
    ):
        return "complete_proof"
    if "abstract plan" in text:
        return "abstract_plan"
    if "lean 4" in text and ("have" in text or "proof sketch" in text or "lean proof" in text):
        return "lean_sketch"
    if text.startswith("explanation") or "explanation of" in text:
        return "explanation"
    if "detailed proof" in text or "analysis" in text or text in {"proof sketch", "proof plan"}:
        return "detailed_analysis"
    return None


def model_family_for_path(path_str: str) -> str:
    lowered = path_str.lower()
    for family in [
        "deepseekv2",
        "deepseek_v2",
        "deepseekv32",
        "goedelv2",
        "goedel_v2",
        "gpt52",
        "kimina",
    ]:
        if family in lowered:
            return family
    return "other"


def maybe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def summarize_numeric(values: list[int] | list[float]) -> dict[str, float | int]:
    if not values:
        return {"count": 0, "mean": 0.0, "median": 0.0}
    return {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
    }


def build_summary(results: dict[str, Any], *, top: int) -> str:
    agg = results["aggregate"]
    lines: list[str] = []
    lines.append("# CoT Markdown Structure Analysis")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- files scanned: `{agg['files_scanned']}`")
    lines.append(f"- CoT files matched: `{agg['cot_files']}`")
    lines.append(f"- CoT completions analyzed: `{agg['attempts']}`")
    lines.append("")
    lines.append("## Main Counts")
    lines.append("")
    lines.append(f"- with any markdown heading: `{agg['with_any_heading']}` ({100 * agg['with_any_heading_rate']:.1f}%)")
    lines.append(f"- with any recognized core heading: `{agg['with_any_core_heading']}` ({100 * agg['with_any_core_heading_rate']:.1f}%)")
    lines.append(f"- with Lean code block: `{agg['with_code_block']}` ({100 * agg['with_code_block_rate']:.1f}%)")
    lines.append(
        f"- parseable as `detailed_analysis + abstract_plan + complete_proof`: `{agg['parseable_detail_plan_proof']}` ({100 * agg['parseable_detail_plan_proof_rate']:.1f}%)"
    )
    lines.append(
        f"- parseable as `detailed_analysis + abstract_plan + lean_sketch + complete_proof`: `{agg['parseable_detail_plan_lean_proof']}` ({100 * agg['parseable_detail_plan_lean_proof_rate']:.1f}%)"
    )
    lines.append(
        f"- with some summary/analysis before final proof: `{agg['summary_before_complete_proof']}` ({100 * agg['summary_before_complete_proof_rate']:.1f}%)"
    )
    lines.append(
        f"- with complete proof as the last core section: `{agg['complete_proof_last']}` ({100 * agg['complete_proof_last_rate']:.1f}%)"
    )
    lines.append("")
    lines.append("## Size Statistics")
    lines.append("")
    lines.append(
        f"- completion length: mean `{agg['completion_chars']['mean']:.1f}`, median `{agg['completion_chars']['median']}`"
    )
    lines.append(
        f"- prose before first Lean code block: mean `{agg['pre_code_chars']['mean']:.1f}`, median `{agg['pre_code_chars']['median']}`"
    )
    lines.append(
        f"- prose before first Lean code block as share of total output: mean `{100 * agg['pre_code_pct']['mean']:.1f}%`, median `{100 * agg['pre_code_pct']['median']:.1f}%`"
    )
    lines.append("")
    lines.append("## Core Section Presence")
    lines.append("")
    for category in ["detailed_analysis", "abstract_plan", "lean_sketch", "explanation", "complete_proof"]:
        stats = agg["section_presence"][category]
        lines.append(f"- `{category}`: `{stats['count']}` ({100 * stats['rate']:.1f}%)")
    lines.append("")
    lines.append("## Core Section Sizes")
    lines.append("")
    for category in ["detailed_analysis", "abstract_plan", "lean_sketch", "explanation", "complete_proof"]:
        stats = agg["section_sizes"][category]
        lines.append(
            f"- `{category}`: mean `{stats['mean_chars']:.1f}` chars, median `{stats['median_chars']}`, mean share when present `{100 * stats['mean_pct_when_present']:.1f}%`"
        )
    lines.append("")
    lines.append("## Most Common Exact Headings")
    lines.append("")
    for item in agg["top_exact_headings"][:top]:
        lines.append(f"- `{item['heading']}`: `{item['count']}`")
    lines.append("")
    lines.append("## Most Common Normalized Core Orders")
    lines.append("")
    for item in agg["top_core_orders"][:top]:
        lines.append(f"- `{item['order']}`: `{item['count']}`")
    lines.append("")
    lines.append("## Most Common Last Pre-Code Headings")
    lines.append("")
    for item in agg["top_last_pre_code_headings"][:top]:
        lines.append(f"- `{item['heading']}`: `{item['count']}`")
    lines.append("")
    lines.append("## Model Family Summary")
    lines.append("")
    for family, stats in agg["by_model"].items():
        lines.append(f"### `{family}`")
        lines.append(f"- attempts: `{stats['attempts']}`")
        lines.append(f"- exact `Complete Lean 4 Proof`: `{stats['exact_complete_lean4_proof']}` ({100 * stats['exact_complete_lean4_proof_rate']:.1f}%)")
        lines.append(f"- any abstract-plan variant: `{stats['abstract_plan_variant']}` ({100 * stats['abstract_plan_variant_rate']:.1f}%)")
        lines.append(f"- any detailed-proof variant: `{stats['detailed_variant']}` ({100 * stats['detailed_variant_rate']:.1f}%)")
        lines.append(f"- any explanation variant: `{stats['explanation_variant']}` ({100 * stats['explanation_variant_rate']:.1f}%)")
        lines.append(f"- parseable `detail + plan + proof`: `{stats['core3']}` ({100 * stats['core3_rate']:.1f}%)")
        lines.append(f"- parseable `detail + plan + lean + proof`: `{stats['core4']}` ({100 * stats['core4_rate']:.1f}%)")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    root = args.root.resolve()

    cot_files: list[Path] = []
    scanned_files = 0
    for json_path in root.rglob("*.json"):
        if "outputs" not in json_path.parts:
            continue
        scanned_files += 1
        text = json_path.read_text(encoding="utf-8", errors="ignore")
        if any(marker in text for marker in PROMPT_MARKERS):
            cot_files.append(json_path)

    exact_heading_counts: Counter[str] = Counter()
    normalized_heading_counts: Counter[str] = Counter()
    top_level_heading_counts: Counter[str] = Counter()
    last_pre_code_heading_counts: Counter[str] = Counter()
    core_order_counts: Counter[str] = Counter()
    file_attempt_counts: Counter[str] = Counter()
    category_presence_counts: Counter[str] = Counter()
    model_counters: dict[str, Counter[str]] = defaultdict(Counter)
    attempt_records: list[dict[str, Any]] = []

    completion_chars: list[int] = []
    pre_code_chars: list[int] = []
    pre_code_pct: list[float] = []
    heading_count_all: list[int] = []
    core_heading_count_all: list[int] = []
    section_chars: dict[str, list[int]] = defaultdict(list)
    section_pct: dict[str, list[float]] = defaultdict(list)

    attempts = 0
    with_any_heading = 0
    with_any_core_heading = 0
    with_code_block = 0
    parseable_detail_plan_proof = 0
    parseable_detail_plan_lean_proof = 0
    summary_before_complete_proof = 0
    complete_proof_last = 0

    for json_path in sorted(cot_files):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        rel_path = json_path.relative_to(root).as_posix()
        model_family = model_family_for_path(rel_path)
        for raw_output in iter_raw_outputs(data):
            completion = extract_completion(raw_output)
            if completion is None or not completion.strip():
                continue

            attempts += 1
            file_attempt_counts[rel_path] += 1
            model_counters[model_family]["attempts"] += 1

            completion_length = len(completion)
            completion_chars.append(completion_length)

            code_match = CODE_BLOCK_RE.search(completion)
            if code_match:
                with_code_block += 1
                pre_code = completion[: code_match.start()].strip()
                pre_code_chars.append(len(pre_code))
                pre_code_pct.append(len(pre_code) / completion_length if completion_length else 0.0)
            else:
                pre_code = None

            headings = list(HEADER_RE.finditer(completion))
            heading_count_all.append(len(headings))
            if headings:
                with_any_heading += 1
                model_counters[model_family]["any_heading"] += 1

            exact_headings_in_order: list[str] = []
            normalized_headings_in_order: list[str] = []
            top_level_headings_in_order: list[str] = []
            core_categories_in_order: list[str] = []
            core_category_first_occurrence: list[str] = []
            core_section_lengths: dict[str, int] = defaultdict(int)
            core_seen: set[str] = set()

            for idx, match in enumerate(headings):
                hashes = match.group(1)
                title = match.group(2).strip()
                normalized = canonicalize_heading(title)
                category = classify_heading(title)

                exact_heading_counts[title] += 1
                normalized_heading_counts[normalized] += 1
                exact_headings_in_order.append(title)
                normalized_headings_in_order.append(normalized)

                if len(hashes) == 3:
                    top_level_heading_counts[normalized] += 1
                    top_level_headings_in_order.append(normalized)

                if category:
                    next_start = headings[idx + 1].start() if idx + 1 < len(headings) else len(completion)
                    core_categories_in_order.append(category)
                    core_section_lengths[category] += next_start - match.start()
                    if category not in core_seen:
                        core_category_first_occurrence.append(category)
                        core_seen.add(category)

            if pre_code is not None:
                pre_code_headings = list(HEADER_RE.finditer(pre_code))
                if pre_code_headings:
                    last_pre_code_heading = canonicalize_heading(pre_code_headings[-1].group(2))
                    last_pre_code_heading_counts[last_pre_code_heading] += 1
                else:
                    last_pre_code_heading = None
            else:
                last_pre_code_heading = None

            core_heading_count_all.append(len(core_categories_in_order))
            if core_categories_in_order:
                with_any_core_heading += 1
                model_counters[model_family]["any_core"] += 1
                core_order_counts[" -> ".join(core_category_first_occurrence)] += 1

                category_set = set(core_category_first_occurrence)
                for category in category_set:
                    category_presence_counts[category] += 1
                    model_counters[model_family][f"has_{category}"] += 1
                    section_chars[category].append(core_section_lengths[category])
                    section_pct[category].append(
                        core_section_lengths[category] / completion_length if completion_length else 0.0
                    )

                if {"detailed_analysis", "abstract_plan", "complete_proof"} <= category_set:
                    parseable_detail_plan_proof += 1
                    model_counters[model_family]["core3"] += 1
                if {
                    "detailed_analysis",
                    "abstract_plan",
                    "lean_sketch",
                    "complete_proof",
                } <= category_set:
                    parseable_detail_plan_lean_proof += 1
                    model_counters[model_family]["core4"] += 1
                if "complete_proof" in category_set:
                    complete_idx = core_category_first_occurrence.index("complete_proof")
                    if any(
                        category in core_category_first_occurrence[:complete_idx]
                        for category in ["detailed_analysis", "abstract_plan", "lean_sketch", "explanation"]
                    ):
                        summary_before_complete_proof += 1
                        model_counters[model_family]["summary_before_complete_proof"] += 1
                    if core_category_first_occurrence[-1] == "complete_proof":
                        complete_proof_last += 1
                        model_counters[model_family]["complete_proof_last"] += 1

            exact_heading_set = set(canonicalize_heading(title) for title in exact_headings_in_order)
            if "complete lean 4 proof" in exact_heading_set:
                model_counters[model_family]["exact_complete_lean4_proof"] += 1
            if any("abstract plan" in title for title in exact_heading_set):
                model_counters[model_family]["abstract_plan_variant"] += 1
            if any(
                title in {"detailed proof", "detailed proof and analysis", "proof plan", "proof sketch"}
                for title in exact_heading_set
            ):
                model_counters[model_family]["detailed_variant"] += 1
            if any(title.startswith("explanation") or "explanation of" in title for title in exact_heading_set):
                model_counters[model_family]["explanation_variant"] += 1

            attempt_records.append(
                {
                    "file": rel_path,
                    "model_family": model_family,
                    "completion_chars": completion_length,
                    "has_code_block": code_match is not None,
                    "pre_code_chars": len(pre_code) if pre_code is not None else None,
                    "pre_code_pct": (len(pre_code) / completion_length) if pre_code is not None and completion_length else None,
                    "heading_count": len(headings),
                    "core_heading_count": len(core_categories_in_order),
                    "exact_headings_in_order": exact_headings_in_order,
                    "normalized_headings_in_order": normalized_headings_in_order,
                    "top_level_headings_in_order": top_level_headings_in_order,
                    "core_categories_in_order": core_categories_in_order,
                    "core_categories_first_occurrence": core_category_first_occurrence,
                    "last_pre_code_heading": last_pre_code_heading,
                }
            )

    aggregate: dict[str, Any] = {
        "files_scanned": scanned_files,
        "cot_files": len(cot_files),
        "attempts": attempts,
        "with_any_heading": with_any_heading,
        "with_any_heading_rate": maybe_ratio(with_any_heading, attempts),
        "with_any_core_heading": with_any_core_heading,
        "with_any_core_heading_rate": maybe_ratio(with_any_core_heading, attempts),
        "with_code_block": with_code_block,
        "with_code_block_rate": maybe_ratio(with_code_block, attempts),
        "parseable_detail_plan_proof": parseable_detail_plan_proof,
        "parseable_detail_plan_proof_rate": maybe_ratio(parseable_detail_plan_proof, attempts),
        "parseable_detail_plan_lean_proof": parseable_detail_plan_lean_proof,
        "parseable_detail_plan_lean_proof_rate": maybe_ratio(parseable_detail_plan_lean_proof, attempts),
        "summary_before_complete_proof": summary_before_complete_proof,
        "summary_before_complete_proof_rate": maybe_ratio(summary_before_complete_proof, attempts),
        "complete_proof_last": complete_proof_last,
        "complete_proof_last_rate": maybe_ratio(complete_proof_last, attempts),
        "completion_chars": summarize_numeric(completion_chars),
        "pre_code_chars": summarize_numeric(pre_code_chars),
        "pre_code_pct": summarize_numeric(pre_code_pct),
        "heading_count": summarize_numeric(heading_count_all),
        "core_heading_count": summarize_numeric(core_heading_count_all),
        "section_presence": {},
        "section_sizes": {},
        "top_exact_headings": [
            {"heading": heading, "count": count}
            for heading, count in exact_heading_counts.most_common(args.top)
        ],
        "top_normalized_headings": [
            {"heading": heading, "count": count}
            for heading, count in normalized_heading_counts.most_common(args.top)
        ],
        "top_top_level_headings": [
            {"heading": heading, "count": count}
            for heading, count in top_level_heading_counts.most_common(args.top)
        ],
        "top_core_orders": [
            {"order": order, "count": count}
            for order, count in core_order_counts.most_common(args.top)
        ],
        "top_last_pre_code_headings": [
            {"heading": heading, "count": count}
            for heading, count in last_pre_code_heading_counts.most_common(args.top)
        ],
        "file_attempt_counts": [
            {"file": file_path, "count": count}
            for file_path, count in file_attempt_counts.most_common()
        ],
        "by_model": {},
    }

    for category in ["detailed_analysis", "abstract_plan", "lean_sketch", "explanation", "complete_proof"]:
        aggregate["section_presence"][category] = {
            "count": category_presence_counts[category],
            "rate": maybe_ratio(category_presence_counts[category], attempts),
        }
        aggregate["section_sizes"][category] = {
            "mean_chars": statistics.mean(section_chars[category]) if section_chars[category] else 0.0,
            "median_chars": statistics.median(section_chars[category]) if section_chars[category] else 0.0,
            "mean_pct_when_present": statistics.mean(section_pct[category]) if section_pct[category] else 0.0,
            "median_pct_when_present": statistics.median(section_pct[category]) if section_pct[category] else 0.0,
            "mean_pct_all_attempts": (
                sum(section_pct[category]) / attempts if attempts else 0.0
            ),
        }

    for model_family, counter in sorted(model_counters.items()):
        model_attempts = counter["attempts"]
        aggregate["by_model"][model_family] = {
            "attempts": model_attempts,
            "any_heading": counter["any_heading"],
            "any_heading_rate": maybe_ratio(counter["any_heading"], model_attempts),
            "any_core": counter["any_core"],
            "any_core_rate": maybe_ratio(counter["any_core"], model_attempts),
            "exact_complete_lean4_proof": counter["exact_complete_lean4_proof"],
            "exact_complete_lean4_proof_rate": maybe_ratio(counter["exact_complete_lean4_proof"], model_attempts),
            "abstract_plan_variant": counter["abstract_plan_variant"],
            "abstract_plan_variant_rate": maybe_ratio(counter["abstract_plan_variant"], model_attempts),
            "detailed_variant": counter["detailed_variant"],
            "detailed_variant_rate": maybe_ratio(counter["detailed_variant"], model_attempts),
            "explanation_variant": counter["explanation_variant"],
            "explanation_variant_rate": maybe_ratio(counter["explanation_variant"], model_attempts),
            "core3": counter["core3"],
            "core3_rate": maybe_ratio(counter["core3"], model_attempts),
            "core4": counter["core4"],
            "core4_rate": maybe_ratio(counter["core4"], model_attempts),
            "summary_before_complete_proof": counter["summary_before_complete_proof"],
            "summary_before_complete_proof_rate": maybe_ratio(
                counter["summary_before_complete_proof"], model_attempts
            ),
            "complete_proof_last": counter["complete_proof_last"],
            "complete_proof_last_rate": maybe_ratio(counter["complete_proof_last"], model_attempts),
        }

    results = {
        "config": {
            "root": str(root),
            "prompt_markers": PROMPT_MARKERS,
            "top": args.top,
        },
        "aggregate": aggregate,
        "attempts": attempt_records,
    }

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    markdown_summary = build_summary(results, top=args.top)
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(markdown_summary, encoding="utf-8")
    else:
        print(markdown_summary, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
