#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
from typing import Any

from extract_hallucinations import summarize as summarize_hallucinations
from leanfinder_client import LeanFinderClient


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PASS1_SPEC = ROOT / "rag_experiments" / "data" / "specs" / "msc180_iterative_rag_pass1_spec.json"
DEFAULT_PASS2_SPEC = ROOT / "rag_experiments" / "data" / "specs" / "msc180_iterative_rag_pass2_spec.json"
DEFAULT_METADATA_JSON = (
    ROOT / "rag_experiments" / "reports" / "iterative_rag" / "msc180_iterative_rag_spec_metadata.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build pass-1 and pass-2 theorem-context specs for iterative RAG experiments. "
            "Pass 1 uses statement-only retrieval. Pass 2 augments that set using frequent "
            "hallucinated theorem-like names from failed attempts."
        )
    )
    parser.add_argument("--input", type=Path, required=True, help="Verified JSON run used as the source.")
    parser.add_argument(
        "--problem-prefix",
        default="no-hint/",
        help="Only include run keys with this prefix. Use empty string to include all keys.",
    )
    parser.add_argument(
        "--problem-key",
        action="append",
        default=[],
        help="Optional exact run keys to include. Can be repeated.",
    )
    parser.add_argument("--max-problems", type=int, help="Optional cap for cheap validation runs.")
    parser.add_argument("--pass1-spec", type=Path, default=DEFAULT_PASS1_SPEC)
    parser.add_argument("--pass2-spec", type=Path, default=DEFAULT_PASS2_SPEC)
    parser.add_argument("--metadata-json", type=Path, default=DEFAULT_METADATA_JSON)
    parser.add_argument("--cache-path", type=Path, help="LeanFinder cache path override.")
    parser.add_argument(
        "--statement-topk",
        type=int,
        default=2,
        help="Number of statement-only theorems to keep in the final prompt.",
    )
    parser.add_argument(
        "--statement-search-topk",
        type=int,
        default=5,
        help="Number of statement-only LeanFinder results to inspect before theorem/lemma filtering.",
    )
    parser.add_argument(
        "--hallucination-topk",
        type=int,
        default=5,
        help="Top-k to inspect for statement+hallucination retrieval.",
    )
    parser.add_argument(
        "--max-hallucinations",
        type=int,
        default=2,
        help="Maximum number of problem-level hallucinations to augment with.",
    )
    parser.add_argument(
        "--min-name-length",
        type=int,
        default=7,
        help="Minimum unresolved-name length passed to the hallucination extractor.",
    )
    parser.add_argument(
        "--use-attempt-frequency",
        action="store_true",
        help="Rank hallucinations by number of attempts they appear in, then by occurrences.",
    )
    return parser.parse_args()


def load_payload(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected JSON object at {path}")
    return payload


def canonical_problem_key(run_key: str) -> str:
    tail = run_key.split("/", 1)[-1]
    if tail.startswith("MSC-180_"):
        return tail.replace("MSC-180_", "MSC-180/", 1)
    return tail


def trim_declaration_to_signature(formal_statement: str) -> str:
    text = formal_statement.strip()
    if ":=" in text:
        text = text.split(":=", 1)[0].rstrip()
    return text


def declaration_kind(formal_statement: str) -> str:
    line = formal_statement.strip().splitlines()[0] if formal_statement.strip() else ""
    return line.split(maxsplit=1)[0] if line else ""


def build_hint_block(selected_results: list[dict[str, Any]]) -> str:
    blocks = []
    for result in selected_results:
        signature = trim_declaration_to_signature(result["formal_statement"])
        theorem_name = result.get("full_name") or trim_declaration_to_signature(
            result.get("formal_statement", "")
        )
        blocks.append(
            "-- this theorem might be useful in the proof of the problem\n"
            f"-- Use as: {theorem_name}\n"
            + signature
        )
    return "\n\n".join(blocks).strip()


def dedup_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    out = []
    for result in results:
        key = result.get("full_name") or trim_declaration_to_signature(result.get("formal_statement", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(result)
    return out


def prefer_theorems_and_lemmas(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preferred = []
    fallback = []
    for result in results:
        kind = declaration_kind(result.get("formal_statement", ""))
        if kind in {"theorem", "lemma"}:
            preferred.append(result)
        else:
            fallback.append(result)
    return preferred + fallback


def select_problem_keys(payload: dict[str, Any], args: argparse.Namespace) -> list[str]:
    keys = sorted(k for k in payload if not args.problem_prefix or k.startswith(args.problem_prefix))
    if args.problem_key:
        wanted = set(args.problem_key)
        keys = [k for k in keys if k in wanted]
    if args.max_problems is not None:
        keys = keys[: args.max_problems]
    return keys


def choose_top_hallucinations(
    problem_summary: dict[str, Any],
    *,
    limit: int,
    use_attempt_frequency: bool,
) -> list[dict[str, Any]]:
    rows = problem_summary.get("top_filtered_names", [])
    if not isinstance(rows, list):
        return []
    def sort_key(row: dict[str, Any]) -> tuple:
        attempts = int(row.get("attempts", 0))
        occ = int(row.get("occurrences", 0))
        name = str(row.get("name", ""))
        if use_attempt_frequency:
            return (-attempts, -occ, name)
        return (-occ, -attempts, name)
    return sorted(rows, key=sort_key)[:limit]


def first_distinct_result(
    results: list[dict[str, Any]],
    already_selected: list[dict[str, Any]],
) -> dict[str, Any] | None:
    seen = {
        result.get("full_name") or trim_declaration_to_signature(result.get("formal_statement", ""))
        for result in already_selected
    }
    preferred = []
    fallback = []
    for result in results:
        kind = declaration_kind(result.get("formal_statement", ""))
        if kind in {"theorem", "lemma"}:
            preferred.append(result)
        else:
            fallback.append(result)
    for bucket in (preferred, fallback):
        for result in bucket:
            key = result.get("full_name") or trim_declaration_to_signature(result.get("formal_statement", ""))
            if key and key not in seen:
                return result
    return None


def build_specs(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    payload = load_payload(args.input)
    selected_keys = select_problem_keys(payload, args)
    if not selected_keys:
        raise ValueError("No problems matched the requested filters.")

    hallucination_summary = summarize_hallucinations(
        args.input, min_name_length=args.min_name_length, top=50
    )
    client = LeanFinderClient(cache_path=args.cache_path)

    pass1_spec: dict[str, Any] = {"problems": {}}
    pass2_spec: dict[str, Any] = {"problems": {}}
    metadata: dict[str, Any] = {
        "input": str(args.input),
        "problem_prefix": args.problem_prefix,
        "selected_run_keys": selected_keys,
        "config": {
            "statement_topk": args.statement_topk,
            "statement_search_topk": args.statement_search_topk,
            "hallucination_topk": args.hallucination_topk,
            "max_hallucinations": args.max_hallucinations,
            "min_name_length": args.min_name_length,
            "use_attempt_frequency": args.use_attempt_frequency,
        },
        "problems": {},
    }

    for run_key in selected_keys:
        entry = payload[run_key]
        if not isinstance(entry, dict):
            continue
        problem_key = canonical_problem_key(run_key)
        header = str(entry.get("header", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        if not header or not formal_statement:
            raise ValueError(f"Problem {run_key} is missing header/formal_statement.")

        statement_query = formal_statement
        statement_results = client.retrieve(statement_query, k=args.statement_search_topk)
        selected_statement_results = dedup_results(prefer_theorems_and_lemmas(statement_results))[
            : args.statement_topk
        ]
        pass1_hint = build_hint_block(selected_statement_results)

        problem_summary = hallucination_summary["problems"].get(run_key, {})
        top_hallucinations = choose_top_hallucinations(
            problem_summary,
            limit=args.max_hallucinations,
            use_attempt_frequency=args.use_attempt_frequency,
        )

        pass2_results = list(selected_statement_results)
        hallucination_rows = []
        for row in top_hallucinations:
            hallucinated_name = str(row["name"])
            query = f"{hallucinated_name}\n{formal_statement}"
            results = client.retrieve(query, k=args.hallucination_topk)
            chosen = first_distinct_result(results, pass2_results)
            if chosen is not None:
                pass2_results.append(chosen)
            hallucination_rows.append(
                {
                    "name": hallucinated_name,
                    "attempts": row.get("attempts", 0),
                    "occurrences": row.get("occurrences", 0),
                    "query": query,
                    "results": results,
                    "selected_result": chosen,
                }
            )

        pass2_results = dedup_results(pass2_results)
        pass2_hint = build_hint_block(pass2_results)

        pass1_spec["problems"][problem_key] = {
            "header": header,
            "formal_statement": formal_statement,
            "theorem_hint": pass1_hint,
        }
        pass2_spec["problems"][problem_key] = {
            "header": header,
            "formal_statement": formal_statement,
            "theorem_hint": pass2_hint,
        }

        metadata["problems"][problem_key] = {
            "source_run_key": run_key,
            "statement_query": statement_query,
            "statement_results": statement_results,
            "selected_statement_results": selected_statement_results,
            "top_hallucinations": top_hallucinations,
            "hallucination_queries": hallucination_rows,
            "pass1_hint": pass1_hint,
            "pass2_results": pass2_results,
            "pass2_hint": pass2_hint,
        }

    return pass1_spec, pass2_spec, metadata


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def print_summary(metadata: dict[str, Any]) -> None:
    print(f"input: {metadata['input']}")
    print(f"selected problems: {len(metadata['problems'])}")
    for problem_key, problem in metadata["problems"].items():
        print(f"\n{problem_key}")
        print("  statement top results:")
        for result in problem["selected_statement_results"]:
            name = result.get("full_name") or "<unknown>"
            print(f"    - {name}")
        print("  top hallucinations:")
        for row in problem["top_hallucinations"]:
            print(
                f"    - {row['name']} "
                f"(attempts={row.get('attempts', 0)}, occurrences={row.get('occurrences', 0)})"
            )
        print("  pass2 added results:")
        selected_from_halls = [
            row["selected_result"]
            for row in problem["hallucination_queries"]
            if row.get("selected_result") is not None
        ]
        if not selected_from_halls:
            print("    - none")
        else:
            for result in selected_from_halls:
                name = result.get("full_name") or "<unknown>"
                print(f"    - {name}")


def main() -> int:
    args = parse_args()
    pass1_spec, pass2_spec, metadata = build_specs(args)
    write_json(args.pass1_spec, pass1_spec)
    write_json(args.pass2_spec, pass2_spec)
    write_json(args.metadata_json, metadata)
    print_summary(metadata)
    print(f"\nwrote {args.pass1_spec}")
    print(f"wrote {args.pass2_spec}")
    print(f"wrote {args.metadata_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
