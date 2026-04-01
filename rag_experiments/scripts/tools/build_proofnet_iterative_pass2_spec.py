#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from extract_hallucinations import summarize as summarize_hallucinations
from leanfinder_client import LeanFinderClient


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_BASE_METADATA = (
    ROOT / "rag_experiments" / "reports" / "iterative_rag" / "20260331_proofnet_valid_statement_rag_metadata.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a ProofNet-valid iterative pass2 spec from a verified source run. "
            "Only includes problems that are unsolved and contain at least one filtered "
            "theorem-like hallucination."
        )
    )
    parser.add_argument("--input", type=Path, required=True, help="Verified source run.")
    parser.add_argument(
        "--base-metadata",
        type=Path,
        default=DEFAULT_BASE_METADATA,
        help="Metadata JSON from the statement-only ProofNet-valid spec builder.",
    )
    parser.add_argument("--output-spec", type=Path, required=True)
    parser.add_argument("--output-metadata", type=Path, required=True)
    parser.add_argument("--cache-path", type=Path, help="LeanFinder cache path override.")
    parser.add_argument(
        "--min-name-length",
        type=int,
        default=7,
        help="Minimum character length for filtered unresolved theorem-like names.",
    )
    parser.add_argument(
        "--hallucination-topk",
        type=int,
        default=5,
        help="Top-k LeanFinder results to inspect for statement+hallucination queries.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected JSON object at {path}")
    return payload


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonical_problem_key(run_key: str) -> str:
    return run_key.split("/", 1)[-1]


def trim_declaration_to_signature(formal_statement: str) -> str:
    text = formal_statement.strip()
    if ":=" in text:
        text = text.split(":=", 1)[0].rstrip()
    return text


def declaration_kind(formal_statement: str) -> str:
    first_line = formal_statement.strip().splitlines()[0] if formal_statement.strip() else ""
    return first_line.split(maxsplit=1)[0] if first_line else ""


def dedup_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for result in results:
        key = result.get("full_name") or trim_declaration_to_signature(result.get("formal_statement", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(result)
    return out


def prefer_theorems_and_lemmas(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preferred: list[dict[str, Any]] = []
    fallback: list[dict[str, Any]] = []
    for result in results:
        kind = declaration_kind(result.get("formal_statement", ""))
        if kind in {"theorem", "lemma"}:
            preferred.append(result)
        else:
            fallback.append(result)
    return preferred + fallback


def build_hint_block(selected_results: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for result in selected_results:
        signature = trim_declaration_to_signature(result["formal_statement"])
        theorem_name = result.get("full_name") or trim_declaration_to_signature(result.get("formal_statement", ""))
        blocks.append(
            "-- this theorem might be useful in the proof of the problem\n"
            f"-- Use as: {theorem_name}\n"
            + signature
        )
    return "\n\n".join(blocks).strip()


def choose_top_hallucinations(problem_summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = problem_summary.get("top_filtered_names", [])
    if not isinstance(rows, list):
        return []
    return sorted(
        rows,
        key=lambda row: (-int(row.get("attempts", 0)), -int(row.get("occurrences", 0)), str(row.get("name", ""))),
    )


def take_distinct_new_results(
    results: list[dict[str, Any]],
    already_selected: list[dict[str, Any]],
    *,
    limit: int,
) -> list[dict[str, Any]]:
    seen = {
        result.get("full_name") or trim_declaration_to_signature(result.get("formal_statement", ""))
        for result in already_selected
    }
    chosen: list[dict[str, Any]] = []
    for result in prefer_theorems_and_lemmas(results):
        key = result.get("full_name") or trim_declaration_to_signature(result.get("formal_statement", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        chosen.append(result)
        if len(chosen) >= limit:
            break
    return chosen


def main() -> int:
    args = parse_args()
    source_payload = load_json(args.input)
    base_metadata = load_json(args.base_metadata)
    base_problems = base_metadata.get("problems")
    if not isinstance(base_problems, dict):
        raise TypeError(f"Expected 'problems' object in {args.base_metadata}")

    hall_summary = summarize_hallucinations(
        args.input,
        min_name_length=args.min_name_length,
        top=50,
    )
    client = LeanFinderClient(cache_path=args.cache_path)

    out_spec: dict[str, Any] = {"problems": {}}
    out_metadata: dict[str, Any] = {
        "input": str(args.input),
        "base_metadata": str(args.base_metadata),
        "config": {
            "min_name_length": args.min_name_length,
            "hallucination_topk": args.hallucination_topk,
            "base_theorem_budget": 2,
            "max_added_theorems": 2,
        },
        "totals": {
            "source_problems": 0,
            "unsolved_problems": 0,
            "unsolved_with_filtered_hallucination": 0,
            "triggered_problems": 0,
            "one_hallucination_triggers": 0,
            "multi_hallucination_triggers": 0,
        },
        "problems": {},
    }

    for run_key, entry in sorted(source_payload.items()):
        if not isinstance(entry, dict):
            continue
        out_metadata["totals"]["source_problems"] += 1
        attempts = entry.get("attempts", [])
        if not isinstance(attempts, list):
            attempts = []
        solved = any(bool(a.get("success")) for a in attempts if isinstance(a, dict))
        if solved:
            continue
        out_metadata["totals"]["unsolved_problems"] += 1

        problem_summary = hall_summary["problems"].get(run_key, {})
        top_hallucinations = choose_top_hallucinations(problem_summary)
        if not top_hallucinations:
            continue

        out_metadata["totals"]["unsolved_with_filtered_hallucination"] += 1
        canonical_key = canonical_problem_key(run_key)
        base_row = base_problems.get(canonical_key)
        if not isinstance(base_row, dict):
            raise KeyError(f"Missing base metadata for {canonical_key}")

        selected_results = list(base_row.get("selected_results", []))
        if not isinstance(selected_results, list):
            raise TypeError(f"selected_results must be a list for {canonical_key}")
        final_results = list(selected_results)

        hallucination_rows: list[dict[str, Any]] = []
        if len(top_hallucinations) == 1:
            out_metadata["totals"]["one_hallucination_triggers"] += 1
            chosen_halls = top_hallucinations[:1]
            hall_name = str(chosen_halls[0]["name"])
            query = f"{hall_name}\n{entry['formal_statement']}"
            results = client.retrieve(query, k=args.hallucination_topk)
            added = take_distinct_new_results(results, final_results, limit=2)
            final_results.extend(added)
            hallucination_rows.append(
                {
                    "name": hall_name,
                    "attempts": chosen_halls[0].get("attempts", 0),
                    "occurrences": chosen_halls[0].get("occurrences", 0),
                    "query": query,
                    "results": results,
                    "selected_results": added,
                }
            )
        else:
            out_metadata["totals"]["multi_hallucination_triggers"] += 1
            chosen_halls = top_hallucinations[:2]
            for row in chosen_halls:
                hall_name = str(row["name"])
                query = f"{hall_name}\n{entry['formal_statement']}"
                results = client.retrieve(query, k=args.hallucination_topk)
                added = take_distinct_new_results(results, final_results, limit=1)
                final_results.extend(added)
                hallucination_rows.append(
                    {
                        "name": hall_name,
                        "attempts": row.get("attempts", 0),
                        "occurrences": row.get("occurrences", 0),
                        "query": query,
                        "results": results,
                        "selected_results": added,
                    }
                )

        final_results = dedup_results(final_results)
        out_spec["problems"][canonical_key] = {
            "header": str(entry.get("header", "")).strip(),
            "formal_statement": str(entry.get("formal_statement", "")).strip(),
            "theorem_hint": build_hint_block(final_results),
        }
        out_metadata["problems"][canonical_key] = {
            "source_run_key": run_key,
            "solved_in_source": solved,
            "trigger_reason": "unsolved_and_has_filtered_hallucination",
            "failed_attempts": problem_summary.get("failed_attempts"),
            "attempts_with_filtered_unresolved_name": problem_summary.get("attempts_with_filtered_unresolved_name"),
            "filtered_unresolved_name_occurrences": problem_summary.get("filtered_unresolved_name_occurrences"),
            "top_filtered_names": top_hallucinations,
            "base_selected_results": selected_results,
            "hallucination_rows": hallucination_rows,
            "final_selected_results": final_results,
        }
        out_metadata["totals"]["triggered_problems"] += 1

    save_json(args.output_spec, out_spec)
    save_json(args.output_metadata, out_metadata)
    print(f"Wrote {args.output_spec}")
    print(f"Wrote {args.output_metadata}")
    print(json.dumps(out_metadata["totals"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
