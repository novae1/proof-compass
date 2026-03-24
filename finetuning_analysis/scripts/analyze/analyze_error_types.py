#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path


PATTERNS = [
    ("unknown_name", [r"^unknown (?:identifier|constant) '"]),
    ("rewrite_failed", [r"^tactic 'rewrite' failed"]),
    (
        "type_mismatch",
        [
            r"^application type mismatch",
            r"^type mismatch",
            r"^function expected at",
            r"^invalid argument name",
            r"^dependent elimination failed, type mismatch",
        ],
    ),
    ("field_error", [r"^invalid field notation", r"^invalid field '"]),
    (
        "synthesis_error",
        [
            r"^failed to synthesize",
            r"^typeclass instance problem is stuck",
            r"^type class instance expected",
            r"^failed to infer",
            r"^synthesizing instance",
        ],
    ),
    (
        "automation_no_progress",
        [
            r"^linarith failed to find a contradiction",
            r"^tactic 'aesop' failed",
            r"^aesop: failed to prove the goal",
            r"^omega could not prove the goal",
            r"^`exact\?` could not close the goal",
            r"^`apply\?` could not close the goal",
            r"^simp made no progress",
        ],
    ),
    ("unsolved_goals", [r"^unsolved goals$"]),
    (
        "shape_or_induction_error",
        [
            r"^rcases tactic failed",
            r"^tactic 'introN' failed",
            r"^invalid constructor",
            r"^tactic 'induction' failed",
            r"^cases tactic failed",
            r"^constructor tactic failed",
        ],
    ),
    ("apply_failed", [r"^tactic 'apply' failed"]),
    ("calc_error", [r"^'calc' expression has type"]),
    (
        "timeout",
        [
            r"^\(deterministic\) timeout",
            r"^maximum recursion depth has been reached",
            r"^kernel recursion depth exceeded",
        ],
    ),
    ("goal_state_error", [r"^no goals to be solved"]),
    ("parser_error", [r"^unexpected ", r"^unterminated ", r"^expected "]),
]
COMPILED = [(category, [re.compile(p) for p in patterns]) for category, patterns in PATTERNS]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare verifier error-type distributions between two verified runs."
    )
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--candidate-label", default="candidate")
    parser.add_argument("--output-prefix", type=Path, required=True)
    return parser.parse_args()


def classify(message: str) -> str:
    first = message.split("\n", 1)[0]
    for category, regexes in COMPILED:
        if any(regex.search(first) for regex in regexes):
            return category
    return "other"


def load_payload(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Expected JSON object at {path}")
    return data


def extract_stats(path: Path) -> dict:
    payload = load_payload(path)
    out = {
        "total_attempts": 0,
        "successful_attempts": 0,
        "failed_attempts": 0,
        "error_occurrences": collections.Counter(),
        "attempts_with_category": collections.Counter(),
        "first_error_category": collections.Counter(),
        "nonunknown_failures": 0,
        "error_occurrences_nonunknown_only": collections.Counter(),
        "attempts_with_category_nonunknown_only": collections.Counter(),
        "first_error_category_nonunknown_only": collections.Counter(),
        "unknown_only_failures": 0,
        "unknown_plus_other_failures": 0,
        "cooccurring_with_unknown": collections.Counter(),
        "other_first_lines": collections.Counter(),
    }

    for entry in payload.values():
        if not isinstance(entry, dict):
            continue
        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            continue
        for attempt in attempts:
            out["total_attempts"] += 1
            if not isinstance(attempt, dict):
                continue
            if bool(attempt.get("success")):
                out["successful_attempts"] += 1
                continue

            out["failed_attempts"] += 1
            categories: list[str] = []
            message = attempt.get("message")
            blobs = message if isinstance(message, list) else [message]
            for blob in blobs:
                if isinstance(blob, dict):
                    if blob.get("severity") != "error":
                        continue
                    text = blob.get("data", "")
                else:
                    text = blob or ""
                if not text:
                    continue
                category = classify(text)
                categories.append(category)
                out["error_occurrences"][category] += 1
                if category == "other":
                    out["other_first_lines"][text.split("\n", 1)[0]] += 1

            if not categories:
                continue

            for category in set(categories):
                out["attempts_with_category"][category] += 1
            out["first_error_category"][categories[0]] += 1

            categories_set = set(categories)
            if "unknown_name" in categories_set:
                if len(categories_set) == 1:
                    out["unknown_only_failures"] += 1
                else:
                    out["unknown_plus_other_failures"] += 1
                    for category in sorted(categories_set - {"unknown_name"}):
                        out["cooccurring_with_unknown"][category] += 1
            else:
                out["nonunknown_failures"] += 1
                for category in set(categories):
                    out["attempts_with_category_nonunknown_only"][category] += 1
                for category in categories:
                    out["error_occurrences_nonunknown_only"][category] += 1
                out["first_error_category_nonunknown_only"][categories[0]] += 1

    for key, value in list(out.items()):
        if isinstance(value, collections.Counter):
            out[key] = dict(value)
    return out


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def top_items(d: dict[str, int], n: int = 8) -> list[tuple[str, int]]:
    return sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def main() -> int:
    args = parse_args()
    baseline = extract_stats(args.baseline)
    candidate = extract_stats(args.candidate)

    payload = {
        "baseline_label": args.baseline_label,
        "candidate_label": args.candidate_label,
        "baseline_path": str(args.baseline),
        "candidate_path": str(args.candidate),
        "baseline": baseline,
        "candidate": candidate,
        "classification_notes": {
            "severity_filter": "Only verifier messages with severity=error are counted; warnings and info messages are excluded.",
            "category_order": [c for c, _ in PATTERNS] + ["other"],
        },
    }

    json_path = args.output_prefix.with_suffix(".json")
    md_path = args.output_prefix.with_suffix(".md")
    write_json(json_path, payload)

    md = f"""# Error Type Comparison

## Scope
- baseline: `{args.baseline}`
- candidate: `{args.candidate}`

Labels:
- baseline: `{args.baseline_label}`
- candidate: `{args.candidate_label}`

## Headline
- {args.baseline_label}: `{baseline['failed_attempts']}` failed attempts, `{baseline['nonunknown_failures']}` non-unknown-only failures
- {args.candidate_label}: `{candidate['failed_attempts']}` failed attempts, `{candidate['nonunknown_failures']}` non-unknown-only failures

Unknown-related split:
- {args.baseline_label}: `unknown_only={baseline['unknown_only_failures']}`, `unknown_plus_other={baseline['unknown_plus_other_failures']}`
- {args.candidate_label}: `unknown_only={candidate['unknown_only_failures']}`, `unknown_plus_other={candidate['unknown_plus_other_failures']}`

## Top Error Occurrences
### {args.baseline_label}
"""
    for key, value in top_items(baseline["error_occurrences"]):
        md += f"- `{key}`: `{value}`\n"
    md += f"\n### {args.candidate_label}\n"
    for key, value in top_items(candidate["error_occurrences"]):
        md += f"- `{key}`: `{value}`\n"

    md += f"\n## First Error Category Among Non-Unknown-Only Failures\n### {args.baseline_label}\n"
    for key, value in top_items(baseline["first_error_category_nonunknown_only"]):
        md += f"- `{key}`: `{value}`\n"
    md += f"\n### {args.candidate_label}\n"
    for key, value in top_items(candidate["first_error_category_nonunknown_only"]):
        md += f"- `{key}`: `{value}`\n"

    md += f"\n## Categories Co-Occurring With Unknown Names\n### {args.baseline_label}\n"
    for key, value in top_items(baseline["cooccurring_with_unknown"]):
        md += f"- `{key}`: `{value}`\n"
    md += f"\n### {args.candidate_label}\n"
    for key, value in top_items(candidate["cooccurring_with_unknown"]):
        md += f"- `{key}`: `{value}`\n"

    md_path.write_text(md, encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
