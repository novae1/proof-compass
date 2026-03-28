#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path
from typing import Iterable


UNKNOWN_PATTERNS = [
    re.compile(r"^unknown (identifier|constant) '([^']+)'"),
    re.compile(r"^unknown (identifier|constant) `([^`]+)`"),
    re.compile(r"^invalid dotted identifier notation, unknown (identifier|constant) `([^`]+)` from expected type"),
    re.compile(r"^invalid dotted identifier notation, unknown (identifier|constant) '([^']+)' from expected type"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract theorem-like unresolved names from verified Lean outputs. "
            "The default filter keeps only names with at least 7 characters."
        )
    )
    parser.add_argument("--input", type=Path, required=True, help="Verified JSON run output.")
    parser.add_argument("--output-json", type=Path, help="Optional JSON output path.")
    parser.add_argument("--output-md", type=Path, help="Optional Markdown summary output path.")
    parser.add_argument(
        "--min-name-length",
        type=int,
        default=7,
        help="Minimum character length for the filtered theorem-like name list.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="How many top names/problems to print and include in Markdown summaries.",
    )
    return parser.parse_args()


def load_payload(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected a JSON object at {path}")
    return payload


def iter_error_texts(attempt: dict) -> Iterable[str]:
    message = attempt.get("message")
    blobs = message if isinstance(message, list) else [message]
    for blob in blobs:
        if isinstance(blob, dict):
            if blob.get("severity") != "error":
                continue
            text = blob.get("data", "")
        else:
            text = blob or ""
        if isinstance(text, str) and text:
            yield text


def extract_unknown_name(first_line: str) -> tuple[str, str] | None:
    for pattern in UNKNOWN_PATTERNS:
        match = pattern.search(first_line)
        if match:
            kind = match.group(1)
            name = match.group(2).strip()
            if name:
                return kind, name
    return None


def top_items(
    occurrence_counter: collections.Counter[str],
    attempt_counter: collections.Counter[str],
    limit: int,
) -> list[dict[str, int | str]]:
    items = sorted(
        occurrence_counter.items(),
        key=lambda kv: (-kv[1], -attempt_counter[kv[0]], kv[0]),
    )[:limit]
    return [
        {
            "name": name,
            "occurrences": count,
            "attempts": attempt_counter[name],
        }
        for name, count in items
    ]


def summarize(path: Path, min_name_length: int, top: int) -> dict:
    payload = load_payload(path)

    summary = {
        "input_path": str(path),
        "filters": {"min_name_length": min_name_length},
        "totals": {
            "problems": 0,
            "attempts": 0,
            "failed_attempts": 0,
            "attempts_with_any_unresolved_name": 0,
            "attempts_with_filtered_unresolved_name": 0,
            "unknown_identifier_occurrences": 0,
            "unknown_constant_occurrences": 0,
            "raw_unresolved_name_occurrences": 0,
            "filtered_unresolved_name_occurrences": 0,
            "distinct_raw_unresolved_names": 0,
            "distinct_filtered_unresolved_names": 0,
        },
        "top_raw_names": [],
        "top_filtered_names": [],
        "problems": {},
    }

    raw_counter: collections.Counter[str] = collections.Counter()
    filtered_counter: collections.Counter[str] = collections.Counter()
    raw_attempt_counter: collections.Counter[str] = collections.Counter()
    filtered_attempt_counter: collections.Counter[str] = collections.Counter()

    for problem_key, entry in sorted(payload.items()):
        if not isinstance(entry, dict):
            continue
        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            continue

        summary["totals"]["problems"] += 1
        problem_raw_counter: collections.Counter[str] = collections.Counter()
        problem_filtered_counter: collections.Counter[str] = collections.Counter()
        problem_raw_attempt_counter: collections.Counter[str] = collections.Counter()
        problem_filtered_attempt_counter: collections.Counter[str] = collections.Counter()
        attempts_with_any = 0
        attempts_with_filtered = 0
        failed_attempts = 0
        attempt_rows = []

        for attempt_index, attempt in enumerate(attempts):
            summary["totals"]["attempts"] += 1
            if not isinstance(attempt, dict):
                continue
            success = bool(attempt.get("success"))
            if not success:
                failed_attempts += 1
                summary["totals"]["failed_attempts"] += 1

            matches = []
            filtered_names = []
            seen_this_attempt = set()
            seen_filtered_this_attempt = set()
            for text in iter_error_texts(attempt):
                first_line = text.split("\n", 1)[0]
                extracted = extract_unknown_name(first_line)
                if extracted is None:
                    continue
                kind, name = extracted
                matches.append({"kind": kind, "name": name, "message": first_line})
                raw_counter[name] += 1
                problem_raw_counter[name] += 1
                summary["totals"]["raw_unresolved_name_occurrences"] += 1
                if kind == "identifier":
                    summary["totals"]["unknown_identifier_occurrences"] += 1
                else:
                    summary["totals"]["unknown_constant_occurrences"] += 1
                seen_this_attempt.add(name)

                if len(name) >= min_name_length:
                    filtered_names.append(name)
                    filtered_counter[name] += 1
                    problem_filtered_counter[name] += 1
                    summary["totals"]["filtered_unresolved_name_occurrences"] += 1
                    seen_filtered_this_attempt.add(name)

            if seen_this_attempt:
                attempts_with_any += 1
                summary["totals"]["attempts_with_any_unresolved_name"] += 1
                for name in seen_this_attempt:
                    raw_attempt_counter[name] += 1
                    problem_raw_attempt_counter[name] += 1
            if seen_filtered_this_attempt:
                attempts_with_filtered += 1
                summary["totals"]["attempts_with_filtered_unresolved_name"] += 1
                for name in seen_filtered_this_attempt:
                    filtered_attempt_counter[name] += 1
                    problem_filtered_attempt_counter[name] += 1

            attempt_rows.append(
                {
                    "attempt_index": attempt_index,
                    "success": success,
                    "match_count": len(matches),
                    "matches": matches,
                    "filtered_names": sorted(set(filtered_names)),
                }
            )

        summary["problems"][problem_key] = {
            "attempts": len(attempts),
            "failed_attempts": failed_attempts,
            "attempts_with_any_unresolved_name": attempts_with_any,
            "attempts_with_filtered_unresolved_name": attempts_with_filtered,
            "raw_unresolved_name_occurrences": sum(problem_raw_counter.values()),
            "filtered_unresolved_name_occurrences": sum(problem_filtered_counter.values()),
            "top_raw_names": top_items(problem_raw_counter, problem_raw_attempt_counter, top),
            "top_filtered_names": top_items(
                problem_filtered_counter, problem_filtered_attempt_counter, top
            ),
            "attempt_rows": attempt_rows,
        }

    summary["totals"]["distinct_raw_unresolved_names"] = len(raw_counter)
    summary["totals"]["distinct_filtered_unresolved_names"] = len(filtered_counter)
    summary["top_raw_names"] = top_items(raw_counter, raw_attempt_counter, top)
    summary["top_filtered_names"] = top_items(filtered_counter, filtered_attempt_counter, top)
    return summary


def top_problem_rows(summary: dict, limit: int) -> list[tuple[str, dict]]:
    problems = list(summary["problems"].items())
    problems.sort(
        key=lambda kv: (
            -kv[1]["filtered_unresolved_name_occurrences"],
            -kv[1]["attempts_with_filtered_unresolved_name"],
            kv[0],
        )
    )
    return problems[:limit]


def print_summary(summary: dict, top: int) -> None:
    totals = summary["totals"]
    print(f"input: {summary['input_path']}")
    print(f"filter: min_name_length >= {summary['filters']['min_name_length']}")
    print(f"problems: {totals['problems']}")
    print(f"attempts: {totals['attempts']}")
    print(f"failed attempts: {totals['failed_attempts']}")
    print(
        "attempts with any unresolved name: "
        f"{totals['attempts_with_any_unresolved_name']}/{totals['attempts']}"
    )
    print(
        "attempts with filtered unresolved name: "
        f"{totals['attempts_with_filtered_unresolved_name']}/{totals['attempts']}"
    )
    print(
        "unknown occurrences: "
        f"identifier={totals['unknown_identifier_occurrences']} "
        f"constant={totals['unknown_constant_occurrences']}"
    )
    print(
        "filtered unresolved names: "
        f"{totals['filtered_unresolved_name_occurrences']} occurrences, "
        f"{totals['distinct_filtered_unresolved_names']} distinct"
    )

    print("\ntop filtered names:")
    for row in summary["top_filtered_names"][:top]:
        print(f"  {row['occurrences']:>4} occ  {row['attempts']:>4} att  {row['name']}")

    print("\nmost hallucination-heavy problems:")
    for key, problem in top_problem_rows(summary, top):
        print(
            f"  {key}: filtered_occurrences={problem['filtered_unresolved_name_occurrences']}, "
            f"attempts_with_filtered={problem['attempts_with_filtered_unresolved_name']}/{problem['attempts']}"
        )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown(path: Path, summary: dict, top: int) -> None:
    totals = summary["totals"]
    md = [
        "# Hallucination Extraction Summary",
        "",
        f"- input: `{summary['input_path']}`",
        f"- minimum name length: `{summary['filters']['min_name_length']}`",
        "",
        "## Totals",
        "",
        f"- problems: `{totals['problems']}`",
        f"- attempts: `{totals['attempts']}`",
        f"- failed attempts: `{totals['failed_attempts']}`",
        f"- attempts with any unresolved name: `{totals['attempts_with_any_unresolved_name']}/{totals['attempts']}`",
        f"- attempts with filtered unresolved name: `{totals['attempts_with_filtered_unresolved_name']}/{totals['attempts']}`",
        f"- unknown identifier occurrences: `{totals['unknown_identifier_occurrences']}`",
        f"- unknown constant occurrences: `{totals['unknown_constant_occurrences']}`",
        f"- filtered unresolved-name occurrences: `{totals['filtered_unresolved_name_occurrences']}`",
        f"- distinct filtered unresolved names: `{totals['distinct_filtered_unresolved_names']}`",
        "",
        "## Top Filtered Names",
        "",
    ]
    for row in summary["top_filtered_names"][:top]:
        md.append(
            f"- `{row['name']}`: `{row['occurrences']}` occurrences, `{row['attempts']}` attempts"
        )

    md.extend(["", "## Most Hallucination-Heavy Problems", ""])
    for key, problem in top_problem_rows(summary, top):
        md.append(
            f"- `{key}`: filtered occurrences `{problem['filtered_unresolved_name_occurrences']}`, "
            f"attempts with filtered names `{problem['attempts_with_filtered_unresolved_name']}/{problem['attempts']}`"
        )
        top_names = problem["top_filtered_names"][: min(5, top)]
        for row in top_names:
            md.append(
                f"  - `{row['name']}`: `{row['occurrences']}` occurrences, `{row['attempts']}` attempts"
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(md) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    summary = summarize(args.input, args.min_name_length, args.top)
    print_summary(summary, args.top)

    if args.output_json:
        write_json(args.output_json, summary)
        print(f"\nwrote {args.output_json}")
    if args.output_md:
        write_markdown(args.output_md, summary, args.top)
        print(f"wrote {args.output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
