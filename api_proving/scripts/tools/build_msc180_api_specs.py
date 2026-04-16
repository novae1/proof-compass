#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from api_proving.retrieval import LeanFinderClient, build_hint_block, top_results

DEFAULT_SOURCE_SPEC = ROOT / "rag_experiments" / "data" / "specs" / "msc180_v2_A_spec.json"
DEFAULT_NOHINT_SPEC = (
    ROOT / "api_proving" / "data" / "specs" / "20260416_msc180_verified20_nohint_spec.json"
)
DEFAULT_BASIC_RAG_SPEC = (
    ROOT / "api_proving" / "data" / "specs" / "20260416_msc180_verified20_statement_rag_top4_spec.json"
)
DEFAULT_METADATA = (
    ROOT / "api_proving" / "reports" / "20260416_msc180_verified20_statement_rag_top4_metadata.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize API-facing MSC-180 specs: a local no-hint copy and a statement-only "
            "LeanFinder top-4 retrieval spec."
        )
    )
    parser.add_argument("--source-spec", type=Path, default=DEFAULT_SOURCE_SPEC)
    parser.add_argument("--nohint-spec", type=Path, default=DEFAULT_NOHINT_SPEC)
    parser.add_argument("--basic-rag-spec", type=Path, default=DEFAULT_BASIC_RAG_SPEC)
    parser.add_argument("--metadata-json", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--cache-path", type=Path, help="LeanFinder cache path override.")
    parser.add_argument(
        "--statement-search-topk",
        type=int,
        default=8,
        help="LeanFinder results to inspect before theorem/lemma filtering.",
    )
    parser.add_argument(
        "--final-theorem-budget",
        type=int,
        default=4,
        help="Number of retrieved theorems to keep in the final prompt.",
    )
    parser.add_argument(
        "--request-delay-s",
        type=float,
        default=0.35,
        help="Delay between uncached LeanFinder requests to reduce rate-limit risk.",
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


def cached_probe(client: LeanFinderClient, query: str, k: int) -> bool:
    cache_key = json.dumps({"query": query.strip(), "k": k}, ensure_ascii=False, sort_keys=True)
    return cache_key in client._cache


def main() -> int:
    args = parse_args()
    source = load_json(args.source_spec)
    problems = source.get("problems")
    if not isinstance(problems, dict):
        raise TypeError("Source spec must contain a 'problems' object.")

    client = LeanFinderClient(cache_path=args.cache_path)

    nohint_spec: dict[str, Any] = {"problems": {}}
    basic_rag_spec: dict[str, Any] = {"problems": {}}
    metadata: dict[str, Any] = {
        "source_spec": str(args.source_spec),
        "config": {
            "statement_search_topk": args.statement_search_topk,
            "final_theorem_budget": args.final_theorem_budget,
        },
        "problems": {},
    }

    total = len(problems)
    for index, (problem_key, entry) in enumerate(sorted(problems.items()), start=1):
        if not isinstance(entry, dict):
            raise TypeError(f"Problem {problem_key} must be a JSON object.")
        header = str(entry.get("header", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        if not header or not formal_statement:
            raise ValueError(f"Problem {problem_key} is missing header/formal_statement.")

        nohint_spec["problems"][problem_key] = {
            "header": header,
            "formal_statement": formal_statement,
            "theorem_hint": "",
        }

        query = formal_statement
        was_cached = cached_probe(client, query, args.statement_search_topk)
        results = client.retrieve(query, k=args.statement_search_topk)
        selected = top_results(results, limit=args.final_theorem_budget)

        basic_rag_spec["problems"][problem_key] = {
            "header": header,
            "formal_statement": formal_statement,
            "theorem_hint": build_hint_block(selected),
        }
        metadata["problems"][problem_key] = {
            "statement_query": query,
            "statement_results": results,
            "selected_results": selected,
        }

        save_json(args.nohint_spec, nohint_spec)
        save_json(args.basic_rag_spec, basic_rag_spec)
        save_json(args.metadata_json, metadata)

        selected_names = [row.get("full_name") or "<?>" for row in selected]
        print(
            f"[msc180 statement-top4 {index}/{total}] {problem_key}: "
            + (", ".join(selected_names) if selected_names else "no results")
        )
        if not was_cached and args.request_delay_s > 0:
            time.sleep(args.request_delay_s)

    print(f"Wrote {args.nohint_spec}")
    print(f"Wrote {args.basic_rag_spec}")
    print(f"Wrote {args.metadata_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
