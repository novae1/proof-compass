#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import time
from pathlib import Path
from typing import Any

from leanfinder_client import LeanFinderClient


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT = ROOT / "benchmarks" / "processed" / "proofnet_valid.json"
DEFAULT_NOHINT_SPEC = ROOT / "rag_experiments" / "data" / "specs" / "20260331_proofnet_valid_nohint_spec.json"
DEFAULT_RAG_SPEC = (
    ROOT / "rag_experiments" / "data" / "specs" / "20260331_proofnet_valid_statement_rag_top2_spec.json"
)
DEFAULT_METADATA = (
    ROOT / "rag_experiments" / "reports" / "iterative_rag" / "20260331_proofnet_valid_statement_rag_metadata.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build no-hint and statement-only RAG specs for ProofNet-valid. "
            "The RAG spec queries LeanFinder with the formal statement, inspects top-k "
            "results, prefers theorem/lemma declarations, and keeps the final top 2."
        )
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--nohint-spec", type=Path, default=DEFAULT_NOHINT_SPEC)
    parser.add_argument("--rag-spec", type=Path, default=DEFAULT_RAG_SPEC)
    parser.add_argument("--metadata-json", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--cache-path", type=Path, help="LeanFinder cache path override.")
    parser.add_argument("--max-problems", type=int, help="Optional cap for smoke/debug runs.")
    parser.add_argument(
        "--statement-search-topk",
        type=int,
        default=5,
        help="Number of LeanFinder results to inspect before theorem/lemma filtering.",
    )
    parser.add_argument(
        "--statement-topk",
        type=int,
        default=2,
        help="Number of theorem statements to keep in the final prompt.",
    )
    parser.add_argument(
        "--request-delay-s",
        type=float,
        default=0.35,
        help="Delay between uncached LeanFinder requests to reduce rate-limit risk.",
    )
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise TypeError(f"Expected JSON list at {path}")
    return rows


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def declaration_kind(formal_statement: str) -> str:
    first_line = formal_statement.strip().splitlines()[0] if formal_statement.strip() else ""
    return first_line.split(maxsplit=1)[0] if first_line else ""


def trim_declaration_to_signature(formal_statement: str) -> str:
    text = formal_statement.strip()
    if ":=" in text:
        text = text.split(":=", 1)[0].rstrip()
    return text


def dedup_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for result in results:
        key = result.get("full_name") or trim_declaration_to_signature(result.get("formal_statement", ""))
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(result)
    return deduped


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


def problem_key(row: dict[str, Any]) -> str:
    name = row.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("ProofNet row is missing a non-empty 'name'.")
    return name.strip()


def build_problem_keys(rows: list[dict[str, Any]]) -> list[str]:
    counts = collections.Counter(problem_key(row) for row in rows)
    seen: collections.Counter[str] = collections.Counter()
    keys: list[str] = []
    for row in rows:
        base = problem_key(row)
        seen[base] += 1
        if counts[base] == 1:
            keys.append(base)
        else:
            keys.append(f"{base}__{seen[base]}")
    return keys


def build_base_entry(row: dict[str, Any]) -> dict[str, str]:
    header = str(row.get("header", "")).strip()
    formal_statement = str(row.get("formal_statement", "")).strip()
    if not header or not formal_statement:
        raise ValueError(f"Problem {problem_key(row)} is missing header/formal_statement.")
    return {
        "header": header,
        "formal_statement": formal_statement,
        "theorem_hint": "",
    }


def main() -> int:
    args = parse_args()
    rows = load_rows(args.input)
    if args.max_problems is not None:
        rows = rows[: max(args.max_problems, 0)]
    if not rows:
        raise ValueError("No ProofNet-valid rows selected.")
    unique_keys = build_problem_keys(rows)

    nohint_spec: dict[str, Any] = {"problems": {}}
    rag_spec: dict[str, Any] = {"problems": {}}
    metadata: dict[str, Any] = {
        "input": str(args.input),
        "config": {
            "statement_search_topk": args.statement_search_topk,
            "statement_topk": args.statement_topk,
            "request_delay_s": args.request_delay_s,
        },
        "problems": {},
    }
    client = LeanFinderClient(cache_path=args.cache_path)

    total = len(rows)
    for idx, (row, key) in enumerate(zip(rows, unique_keys, strict=True), start=1):
        source_name = problem_key(row)
        base_entry = build_base_entry(row)
        nohint_spec["problems"][key] = dict(base_entry)

        statement_query = base_entry["formal_statement"]
        cache_key = json.dumps({"query": statement_query.strip(), "k": args.statement_search_topk}, ensure_ascii=False, sort_keys=True)
        was_cached = cache_key in client._cache  # cache probe only, used to throttle politely on misses
        results = client.retrieve(statement_query, k=args.statement_search_topk)
        selected_results = dedup_results(prefer_theorems_and_lemmas(results))[: args.statement_topk]

        rag_entry = dict(base_entry)
        rag_entry["theorem_hint"] = build_hint_block(selected_results)
        rag_spec["problems"][key] = rag_entry

        metadata["problems"][key] = {
            "source_name": source_name,
            "source_row_index": idx - 1,
            "goal": row.get("goal"),
            "informal_prefix": row.get("informal_prefix"),
            "statement_query": statement_query,
            "statement_results": results,
            "selected_results": selected_results,
        }

        save_json(args.nohint_spec, nohint_spec)
        save_json(args.rag_spec, rag_spec)
        save_json(args.metadata_json, metadata)

        selected_names = [r.get("full_name") or "<?>"
                          for r in selected_results]
        print(f"[{idx}/{total}] {key}: {', '.join(selected_names) if selected_names else 'no results'}")
        if not was_cached and args.request_delay_s > 0:
            time.sleep(args.request_delay_s)

    print(f"Wrote no-hint spec to {args.nohint_spec}")
    print(f"Wrote statement-only RAG spec to {args.rag_spec}")
    print(f"Wrote metadata to {args.metadata_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
