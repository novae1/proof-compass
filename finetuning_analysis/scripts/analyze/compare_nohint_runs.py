#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


UNKNOWN_RE = re.compile(r"\bunknown\b", flags=re.IGNORECASE)


def canonical_problem_key(key: str) -> str:
    return key.split("/", 1)[-1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two verified run outputs and write JSON/Markdown summaries."
    )
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--candidate-label", default="candidate")
    parser.add_argument("--output-prefix", type=Path, required=True)
    return parser.parse_args()


def load_payload(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Expected JSON object at {path}")
    return data


def to_text(obj: object) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "\n".join(to_text(x) for x in obj)
    if isinstance(obj, dict):
        return json.dumps(obj, ensure_ascii=False)
    return str(obj)


def summarize(payload: dict) -> dict:
    attempts_total = 0
    attempts_success = 0
    attempts_with_unknown = 0
    total_unknown_occurrences = 0
    per_problem_successes: dict[str, int] = {}
    per_problem_attempts: dict[str, int] = {}

    for key, entry in payload.items():
        if not isinstance(entry, dict):
            continue
        canonical_key = canonical_problem_key(key)
        if canonical_key in per_problem_successes:
            raise ValueError(f"Duplicate canonical problem key after prefix stripping: {canonical_key}")
        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            attempts = []

        success_count = 0
        attempt_count = 0
        for attempt in attempts:
            if not isinstance(attempt, dict):
                continue
            attempt_count += 1
            attempts_total += 1
            if bool(attempt.get("success")):
                attempts_success += 1
                success_count += 1
            msg_text = to_text(attempt.get("message"))
            occurrences = len(UNKNOWN_RE.findall(msg_text))
            if occurrences > 0:
                attempts_with_unknown += 1
                total_unknown_occurrences += occurrences

        per_problem_successes[canonical_key] = success_count
        per_problem_attempts[canonical_key] = attempt_count

    problems_total = len(per_problem_successes)
    problems_solved = sum(1 for v in per_problem_successes.values() if v > 0)
    failed_attempts = attempts_total - attempts_success

    return {
        "attempts_total": attempts_total,
        "attempts_success": attempts_success,
        "attempt_pass_rate": attempts_success / attempts_total if attempts_total else 0.0,
        "attempts_with_unknown": attempts_with_unknown,
        "unknown_attempt_rate": attempts_with_unknown / attempts_total if attempts_total else 0.0,
        "total_unknown_occurrences": total_unknown_occurrences,
        "failed_attempts": failed_attempts,
        "unknown_among_failed_rate": attempts_with_unknown / failed_attempts if failed_attempts else 0.0,
        "problems_total": problems_total,
        "problems_solved": problems_solved,
        "problem_pass_rate": problems_solved / problems_total if problems_total else 0.0,
        "per_problem_successes": per_problem_successes,
        "per_problem_attempts": per_problem_attempts,
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def format_pct(x: float) -> str:
    return f"{100.0 * x:.2f}%"


def main() -> int:
    args = parse_args()
    baseline_payload = load_payload(args.baseline)
    candidate_payload = load_payload(args.candidate)

    baseline_summary = summarize(baseline_payload)
    candidate_summary = summarize(candidate_payload)

    baseline_keys = set(baseline_summary["per_problem_successes"])
    candidate_keys = set(candidate_summary["per_problem_successes"])
    if baseline_keys != candidate_keys:
        raise ValueError("Baseline and candidate runs do not cover the same problem set.")

    problem_deltas = []
    for key in sorted(baseline_keys):
        baseline_successes = baseline_summary["per_problem_successes"][key]
        candidate_successes = candidate_summary["per_problem_successes"][key]
        problem_deltas.append(
            {
                "problem": key,
                "baseline_successes": baseline_successes,
                "candidate_successes": candidate_successes,
                "delta": candidate_successes - baseline_successes,
            }
        )

    improved = [x for x in problem_deltas if x["delta"] > 0]
    regressed = [x for x in problem_deltas if x["delta"] < 0]
    unchanged = [x for x in problem_deltas if x["delta"] == 0]

    improved.sort(key=lambda x: (-x["delta"], x["problem"]))
    regressed.sort(key=lambda x: (x["delta"], x["problem"]))

    summary = {
        "baseline_label": args.baseline_label,
        "candidate_label": args.candidate_label,
        "baseline_path": str(args.baseline),
        "candidate_path": str(args.candidate),
        "baseline": baseline_summary,
        "candidate": candidate_summary,
        "delta": {
            "attempt_successes": candidate_summary["attempts_success"] - baseline_summary["attempts_success"],
            "problems_solved": candidate_summary["problems_solved"] - baseline_summary["problems_solved"],
            "attempts_with_unknown": candidate_summary["attempts_with_unknown"] - baseline_summary["attempts_with_unknown"],
            "total_unknown_occurrences": candidate_summary["total_unknown_occurrences"] - baseline_summary["total_unknown_occurrences"],
        },
        "improved_problems": improved,
        "regressed_problems": regressed,
        "unchanged_problem_count": len(unchanged),
    }

    json_path = args.output_prefix.with_suffix(".json")
    md_path = args.output_prefix.with_suffix(".md")
    write_json(json_path, summary)

    md = f"""# Verified Run Comparison

## Scope
- baseline: `{args.baseline}`
- candidate: `{args.candidate}`

Labels:
- baseline: `{args.baseline_label}`
- candidate: `{args.candidate_label}`

## Headline
- {args.baseline_label}: `{baseline_summary['attempts_success']}/{baseline_summary['attempts_total']}` successful attempts, `{baseline_summary['problems_solved']}/{baseline_summary['problems_total']}` problems solved
- {args.candidate_label}: `{candidate_summary['attempts_success']}/{candidate_summary['attempts_total']}` successful attempts, `{candidate_summary['problems_solved']}/{candidate_summary['problems_total']}` problems solved

Delta:
- successful attempts: `{summary['delta']['attempt_successes']:+d}`
- problems solved: `{summary['delta']['problems_solved']:+d}`
- attempts with unknown: `{summary['delta']['attempts_with_unknown']:+d}`
- total unknown occurrences: `{summary['delta']['total_unknown_occurrences']:+d}`

## Metrics
### {args.baseline_label}
- attempt pass rate: `{format_pct(baseline_summary['attempt_pass_rate'])}`
- problem pass rate: `{format_pct(baseline_summary['problem_pass_rate'])}`
- attempts with unknown: `{baseline_summary['attempts_with_unknown']}/{baseline_summary['attempts_total']}` (`{format_pct(baseline_summary['unknown_attempt_rate'])}`)
- unknown among failed attempts: `{format_pct(baseline_summary['unknown_among_failed_rate'])}`

### {args.candidate_label}
- attempt pass rate: `{format_pct(candidate_summary['attempt_pass_rate'])}`
- problem pass rate: `{format_pct(candidate_summary['problem_pass_rate'])}`
- attempts with unknown: `{candidate_summary['attempts_with_unknown']}/{candidate_summary['attempts_total']}` (`{format_pct(candidate_summary['unknown_attempt_rate'])}`)
- unknown among failed attempts: `{format_pct(candidate_summary['unknown_among_failed_rate'])}`

## Improved Problems
"""
    if improved:
        for row in improved[:20]:
            baseline_attempts = baseline_summary["per_problem_attempts"].get(row["problem"], 0)
            candidate_attempts = candidate_summary["per_problem_attempts"].get(row["problem"], 0)
            if baseline_attempts == candidate_attempts:
                denom_text = str(baseline_attempts)
                md += (
                    f"- `{row['problem']}`: "
                    f"`{row['baseline_successes']}/{denom_text} -> {row['candidate_successes']}/{denom_text}`\n"
                )
            else:
                md += (
                    f"- `{row['problem']}`: "
                    f"`{row['baseline_successes']}/{baseline_attempts} -> "
                    f"{row['candidate_successes']}/{candidate_attempts}`\n"
                )
    else:
        md += "- none\n"

    md += "\n## Regressed Problems\n"
    if regressed:
        for row in regressed[:20]:
            baseline_attempts = baseline_summary["per_problem_attempts"].get(row["problem"], 0)
            candidate_attempts = candidate_summary["per_problem_attempts"].get(row["problem"], 0)
            if baseline_attempts == candidate_attempts:
                denom_text = str(baseline_attempts)
                md += (
                    f"- `{row['problem']}`: "
                    f"`{row['baseline_successes']}/{denom_text} -> {row['candidate_successes']}/{denom_text}`\n"
                )
            else:
                md += (
                    f"- `{row['problem']}`: "
                    f"`{row['baseline_successes']}/{baseline_attempts} -> "
                    f"{row['candidate_successes']}/{candidate_attempts}`\n"
                )
    else:
        md += "- none\n"

    md += f"\n## Unchanged Problems\n- `{len(unchanged)}` problems unchanged\n"

    md_path.write_text(md, encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
