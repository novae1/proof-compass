#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any


THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from leanfinder_client import LeanFinderClient  # noqa: E402


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

COMPLETE_HEADING_RE = re.compile(
    r"^(?:complete lean 4 proof|complete formal proof|complete lean 4 code|lean 4 code)$",
    re.I,
)
HEADER_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Query LeanFinder with penultimate sections from failed DeepSeek-V2 CoT outputs."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("rag_experiments/outputs/msc180/v2/20260217_msc180-v2_deepseekv2_7b_lean4-15_verified.json"),
        help="Verified output JSON to mine failed attempts from.",
    )
    parser.add_argument(
        "--condition-prefix",
        default="no-hint/",
        help="Only analyze entries whose key starts with this prefix.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of LeanFinder results to request.",
    )
    parser.add_argument(
        "--cache-path",
        type=Path,
        default=Path("/tmp/leanfinder_penultimate_section_cache.json"),
        help="LeanFinder cache path.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional JSON output path.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        help="Optional markdown output path.",
    )
    return parser.parse_args()


def canonicalize(title: str) -> str:
    text = title.lower().strip()
    text = re.sub(r"[`*_:\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def classify_penultimate_heading(title: str) -> str:
    text = canonicalize(title)
    if text.startswith("explanation") or "explanation of" in text:
        return "explanation"
    if "lean 4" in text and (
        "have" in text or "proof sketch" in text or "lean proof" in text or "plan with have" in text
    ):
        return "lean_sketch"
    if "lean have statements" in text or "have statements" in text or "proof sketch with have" in text:
        return "lean_sketch"
    if "detailed proof" in text or "analysis" in text or text in {"proof sketch", "proof plan"}:
        return "analysis"
    if "abstract plan" in text:
        return "abstract_plan"
    return "other"


def extract_completion(raw_output: str) -> str | None:
    for marker in PROMPT_MARKERS:
        idx = raw_output.rfind(marker)
        if idx != -1:
            return raw_output[idx + len(marker) :].lstrip()
    return None


def extract_penultimate_section(completion: str) -> dict[str, Any] | None:
    headings = list(HEADER_RE.finditer(completion))
    complete_idx: int | None = None
    for i, match in enumerate(headings):
        if COMPLETE_HEADING_RE.match(canonicalize(match.group(2))):
            complete_idx = i
            break
    if complete_idx is None or complete_idx == 0:
        return None

    prev = headings[complete_idx - 1]
    prev_body = completion[prev.end() : headings[complete_idx].start()].strip()
    if not prev_body:
        return None

    return {
        "heading": prev.group(2).strip(),
        "heading_level": len(prev.group(1)),
        "heading_category": classify_penultimate_heading(prev.group(2)),
        "body": prev_body,
        "body_chars": len(prev_body),
    }


def build_markdown(results: dict[str, Any]) -> str:
    agg = results["aggregate"]
    lines: list[str] = []
    lines.append("# LeanFinder Check: Penultimate Section Only")
    lines.append("")
    lines.append(f"Source run: `{results['config']['input']}`")
    lines.append(f"Condition prefix: `{results['config']['condition_prefix']}`")
    lines.append(f"LeanFinder top-k: `{results['config']['k']}`")
    lines.append("")
    lines.append("## Aggregate")
    lines.append("")
    lines.append(f"- problems analyzed: `{agg['problems']}`")
    lines.append(f"- mean penultimate section length: `{agg['penultimate_body_mean_chars']:.1f}` chars")
    lines.append(f"- std penultimate section length: `{agg['penultimate_body_std_chars']:.1f}` chars")
    lines.append(f"- median penultimate section length: `{agg['penultimate_body_median_chars']}` chars")
    lines.append("")
    lines.append("### Penultimate Section Types")
    lines.append("")
    for item in agg["heading_categories"]:
        lines.append(f"- `{item['category']}`: `{item['count']}` ({item['rate_pct']:.1f}%)")
    lines.append("")
    lines.append("### Most Common Penultimate Headings")
    lines.append("")
    for item in agg["top_penultimate_headings"]:
        lines.append(f"- `{item['heading']}`: `{item['count']}`")
    lines.append("")
    lines.append("### Most Common LeanFinder Top-1 Results")
    lines.append("")
    for item in agg["top1_results"]:
        lines.append(f"- `{item['name']}`: `{item['count']}`")
    lines.append("")
    lines.append("### Most Common Retrieved Results Across Top-5")
    lines.append("")
    for item in agg["all_retrieved_results"]:
        lines.append(f"- `{item['name']}`: `{item['count']}`")
    lines.append("")
    lines.append("## Per Problem")
    lines.append("")
    for problem in results["problems"]:
        lines.append(f"### `{problem['problem_id']}`")
        lines.append("")
        lines.append(f"- selected attempt index: `{problem['attempt_index']}`")
        lines.append(f"- penultimate heading: `{problem['penultimate_heading']}`")
        lines.append(f"- heading category: `{problem['penultimate_heading_category']}`")
        lines.append(f"- penultimate body length: `{problem['penultimate_body_chars']}` chars")
        lines.append("")
        lines.append("#### Penultimate Section Body")
        lines.append("")
        lines.append("```text")
        lines.append(problem["penultimate_body"])
        lines.append("```")
        lines.append("")
        lines.append("#### LeanFinder Top-5")
        lines.append("")
        for result in problem["leanfinder_results"]:
            lines.append(f"{result['rank']}. `{result['full_name'] or '<unknown>'}`")
            lines.append(f"   - `{result['formal_statement'].splitlines()[0]}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    client = LeanFinderClient(cache_path=args.cache_path, max_attempts=2, backoff_s=1.0)

    problem_records: list[dict[str, Any]] = []
    heading_counter: Counter[str] = Counter()
    heading_category_counter: Counter[str] = Counter()
    top1_counter: Counter[str] = Counter()
    retrieved_counter: Counter[str] = Counter()

    for key in sorted(data):
        if not key.startswith(args.condition_prefix):
            continue
        entry = data[key]
        candidates: list[dict[str, Any]] = []
        for idx, attempt in enumerate(entry.get("attempts", [])):
            if attempt.get("success"):
                continue
            raw_output = attempt.get("raw_output")
            if not isinstance(raw_output, str) or not raw_output.strip():
                continue
            completion = extract_completion(raw_output)
            if not completion:
                continue
            extracted = extract_penultimate_section(completion)
            if not extracted:
                continue
            candidates.append(
                {
                    "attempt_index": idx,
                    **extracted,
                }
            )
        if not candidates:
            continue

        # Pick the richest penultimate section to maximize signal in this exploratory pass.
        selected = max(candidates, key=lambda record: record["body_chars"])
        results = client.retrieve(selected["body"], k=args.k, use_cache=True)

        heading_counter[selected["heading"]] += 1
        heading_category_counter[selected["heading_category"]] += 1
        if results:
            top1_counter[results[0].get("full_name") or "<unknown>"] += 1
        for result in results:
            retrieved_counter[result.get("full_name") or "<unknown>"] += 1

        problem_id = key[len(args.condition_prefix) :]
        problem_records.append(
            {
                "problem_key": key,
                "problem_id": problem_id,
                "attempt_index": selected["attempt_index"],
                "penultimate_heading": selected["heading"],
                "penultimate_heading_category": selected["heading_category"],
                "penultimate_body_chars": selected["body_chars"],
                "penultimate_body": selected["body"],
                "leanfinder_results": results,
            }
        )

    body_lengths = [record["penultimate_body_chars"] for record in problem_records]
    aggregate = {
        "problems": len(problem_records),
        "penultimate_body_mean_chars": statistics.mean(body_lengths) if body_lengths else 0.0,
        "penultimate_body_std_chars": statistics.stdev(body_lengths) if len(body_lengths) >= 2 else 0.0,
        "penultimate_body_median_chars": statistics.median(body_lengths) if body_lengths else 0.0,
        "heading_categories": [
            {
                "category": category,
                "count": count,
                "rate_pct": (100.0 * count / len(problem_records)) if problem_records else 0.0,
            }
            for category, count in heading_category_counter.most_common()
        ],
        "top_penultimate_headings": [
            {"heading": heading, "count": count}
            for heading, count in heading_counter.most_common(10)
        ],
        "top1_results": [
            {"name": name, "count": count}
            for name, count in top1_counter.most_common(10)
        ],
        "all_retrieved_results": [
            {"name": name, "count": count}
            for name, count in retrieved_counter.most_common(15)
        ],
    }

    payload = {
        "config": {
            "input": str(args.input),
            "condition_prefix": args.condition_prefix,
            "k": args.k,
        },
        "aggregate": aggregate,
        "problems": problem_records,
    }

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    markdown = build_markdown(payload)
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(markdown, encoding="utf-8")
    else:
        print(markdown, end="")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
