#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from extract_hallucinations import summarize as summarize_hallucinations
from leanfinder_client import LeanFinderClient


ROOT = Path(__file__).resolve().parents[3]

DEFAULT_NOHINT_SPEC = (
    ROOT / "rag_experiments" / "data" / "specs" / "20260331_proofnet_valid_nohint_spec.json"
)
DEFAULT_TOP2_SPEC = (
    ROOT / "rag_experiments" / "data" / "specs" / "20260331_proofnet_valid_statement_rag_top2_spec.json"
)
DEFAULT_NOHINT_TRIGGER_SPEC = (
    ROOT
    / "rag_experiments"
    / "data"
    / "specs"
    / "20260331_proofnet_valid_nohint_iterative_pass2_spec.json"
)
DEFAULT_TOP2_TRIGGER_SPEC = (
    ROOT
    / "rag_experiments"
    / "data"
    / "specs"
    / "20260331_proofnet_valid_statement_rag_top2_iterative_pass2_spec.json"
)
DEFAULT_NOHINT_RUN = (
    ROOT
    / "rag_experiments"
    / "outputs"
    / "proofnet"
    / "valid"
    / "20260331_proofnet-valid_nohint_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_TOP2_RUN = (
    ROOT
    / "rag_experiments"
    / "outputs"
    / "proofnet"
    / "valid"
    / "20260331_proofnet-valid_statement-rag-top2_base_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_NOHINT_OUTPUT_SPEC = (
    ROOT
    / "rag_experiments"
    / "data"
    / "specs"
    / "20260402_proofnet_valid_nohint_allhall_attempt_rag_top6_spec.json"
)
DEFAULT_NOHINT_OUTPUT_METADATA = (
    ROOT
    / "rag_experiments"
    / "reports"
    / "iterative_rag"
    / "20260402_proofnet_valid_nohint_allhall_attempt_rag_top6_metadata.json"
)
DEFAULT_TOP2_OUTPUT_SPEC = (
    ROOT
    / "rag_experiments"
    / "data"
    / "specs"
    / "20260402_proofnet_valid_statement_rag_top2_allhall_attempt_rag_top6_spec.json"
)
DEFAULT_TOP2_OUTPUT_METADATA = (
    ROOT
    / "rag_experiments"
    / "reports"
    / "iterative_rag"
    / "20260402_proofnet_valid_statement_rag_top2_allhall_attempt_rag_top6_metadata.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build whole-attempt top6 ProofNet-valid specs from the original 4-attempt runs. "
            "For each triggered problem, query LeanFinder with every failed attempt that contains "
            "a filtered theorem-like hallucination, merge theorem candidates by attempt frequency "
            "then best rank, and keep a final top 6."
        )
    )
    parser.add_argument("--nohint-spec", type=Path, default=DEFAULT_NOHINT_SPEC)
    parser.add_argument("--top2-spec", type=Path, default=DEFAULT_TOP2_SPEC)
    parser.add_argument("--nohint-trigger-spec", type=Path, default=DEFAULT_NOHINT_TRIGGER_SPEC)
    parser.add_argument("--top2-trigger-spec", type=Path, default=DEFAULT_TOP2_TRIGGER_SPEC)
    parser.add_argument("--nohint-run", type=Path, default=DEFAULT_NOHINT_RUN)
    parser.add_argument("--top2-run", type=Path, default=DEFAULT_TOP2_RUN)
    parser.add_argument("--nohint-output-spec", type=Path, default=DEFAULT_NOHINT_OUTPUT_SPEC)
    parser.add_argument(
        "--nohint-output-metadata", type=Path, default=DEFAULT_NOHINT_OUTPUT_METADATA
    )
    parser.add_argument("--top2-output-spec", type=Path, default=DEFAULT_TOP2_OUTPUT_SPEC)
    parser.add_argument("--top2-output-metadata", type=Path, default=DEFAULT_TOP2_OUTPUT_METADATA)
    parser.add_argument("--cache-path", type=Path, help="LeanFinder cache path override.")
    parser.add_argument(
        "--per-attempt-topk",
        type=int,
        default=6,
        help="LeanFinder results to inspect for each hallucination-bearing attempt query.",
    )
    parser.add_argument(
        "--final-topk",
        type=int,
        default=6,
        help="Final theorem budget after merging results across attempts.",
    )
    parser.add_argument(
        "--min-name-length",
        type=int,
        default=7,
        help="Minimum character length for filtered unresolved theorem-like names.",
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


def canonical_problem_key(problem_key: str) -> str:
    return problem_key.split("/", 1)[-1]


def trim_declaration_to_signature(formal_statement: str) -> str:
    text = formal_statement.strip()
    if ":=" in text:
        text = text.split(":=", 1)[0].rstrip()
    return text


def declaration_kind(formal_statement: str) -> str:
    first_line = formal_statement.strip().splitlines()[0] if formal_statement.strip() else ""
    return first_line.split(maxsplit=1)[0] if first_line else ""


def build_hint_block(selected_results: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
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


def is_preferred_result(result: dict[str, Any]) -> bool:
    return declaration_kind(result.get("formal_statement", "")) in {"theorem", "lemma"}


def dedup_by_name(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for result in results:
        key = result.get("full_name") or trim_declaration_to_signature(
            result.get("formal_statement", "")
        )
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(result)
    return out


def key_map(payload: dict[str, Any]) -> dict[str, str]:
    return {canonical_problem_key(problem_key): problem_key for problem_key in payload}


def cached_probe(client: LeanFinderClient, query: str, k: int) -> bool:
    cache_key = json.dumps({"query": query.strip(), "k": k}, ensure_ascii=False, sort_keys=True)
    return cache_key in client._cache


def attempt_query_text(attempt: dict[str, Any]) -> str:
    return str(attempt.get("parsed_proof") or attempt.get("raw_output") or "").strip()


def merge_attempt_results(
    per_attempt_rows: list[dict[str, Any]],
    *,
    final_topk: int,
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}

    for row in per_attempt_rows:
        attempt_index = int(row["attempt_index"])
        for result in row["results"]:
            theorem_name = result.get("full_name") or trim_declaration_to_signature(
                result.get("formal_statement", "")
            )
            if not theorem_name:
                continue
            group = grouped.setdefault(
                theorem_name,
                {
                    "full_name": theorem_name,
                    "formal_statement": result.get("formal_statement", ""),
                    "doc_url": result.get("doc_url"),
                    "informal_statement": result.get("informal_statement"),
                    "rank_positions": [],
                    "attempt_indices": [],
                    "preferred_kind": is_preferred_result(result),
                },
            )
            group["preferred_kind"] = bool(group["preferred_kind"] or is_preferred_result(result))
            group["rank_positions"].append(int(result.get("rank", len(row["results"]) + 1)))
            group["attempt_indices"].append(attempt_index)

    ranked_groups = sorted(
        grouped.values(),
        key=lambda row: (
            0 if row["preferred_kind"] else 1,
            -len(set(row["attempt_indices"])),
            min(row["rank_positions"]),
            row["full_name"],
        ),
    )

    selected_results: list[dict[str, Any]] = []
    fallback_results: list[dict[str, Any]] = []
    for row in ranked_groups:
        candidate = {
            "full_name": row["full_name"],
            "formal_statement": row["formal_statement"],
            "doc_url": row["doc_url"],
            "informal_statement": row["informal_statement"],
            "merged_attempt_count": len(set(row["attempt_indices"])),
            "best_rank": min(row["rank_positions"]),
        }
        if row["preferred_kind"]:
            selected_results.append(candidate)
        else:
            fallback_results.append(candidate)

    merged = dedup_by_name(selected_results + fallback_results)[:final_topk]
    return merged


def build_branch(
    *,
    branch_name: str,
    base_spec: dict[str, Any],
    trigger_spec: dict[str, Any],
    run_payload: dict[str, Any],
    hall_summary: dict[str, Any],
    client: LeanFinderClient,
    per_attempt_topk: int,
    final_topk: int,
    request_delay_s: float,
    output_spec_path: Path,
    output_metadata_path: Path,
) -> None:
    run_lookup = key_map(run_payload)
    trigger_keys = list(trigger_spec["problems"].keys())

    out_spec: dict[str, Any] = {"problems": {}}
    out_metadata: dict[str, Any] = {
        "source_run": branch_name,
        "config": {
            "per_attempt_topk": per_attempt_topk,
            "final_topk": final_topk,
            "merge_rule": "preferred_kind_then_attempt_count_then_best_rank_then_name",
            "attempt_source": "all_failed_attempts_with_filtered_hallucination_from_original_4_attempt_run",
        },
        "subset": {"triggered_problems": len(trigger_keys)},
        "problems": {},
    }

    total = len(trigger_keys)
    for index, problem_key in enumerate(sorted(trigger_keys), start=1):
        actual_key = run_lookup[problem_key]
        run_entry = run_payload[actual_key]
        base_entry = base_spec["problems"][problem_key]
        problem_summary = hall_summary["problems"][actual_key]

        per_attempt_rows: list[dict[str, Any]] = []
        for attempt_row in problem_summary.get("attempt_rows", []):
            filtered_names = list(attempt_row.get("filtered_names", []))
            if not filtered_names:
                continue
            attempt_index = int(attempt_row["attempt_index"])
            attempt = run_entry["attempts"][attempt_index]
            query = attempt_query_text(attempt)
            if not query:
                continue
            was_cached = cached_probe(client, query, per_attempt_topk)
            results = client.retrieve(query, k=per_attempt_topk)
            per_attempt_rows.append(
                {
                    "attempt_index": attempt_index,
                    "filtered_names": filtered_names,
                    "query_chars": len(query),
                    "query_preview": query[:500],
                    "results": results,
                }
            )
            if not was_cached and request_delay_s > 0:
                time.sleep(request_delay_s)

        if not per_attempt_rows:
            raise ValueError(f"No hallucination-bearing attempts found for {problem_key}")

        selected_results = merge_attempt_results(per_attempt_rows, final_topk=final_topk)
        out_spec["problems"][problem_key] = {
            "header": str(base_entry["header"]).strip(),
            "formal_statement": str(base_entry["formal_statement"]).strip(),
            "theorem_hint": build_hint_block(selected_results),
        }
        out_metadata["problems"][problem_key] = {
            "source_run_key": actual_key,
            "attempt_count_used": len(per_attempt_rows),
            "attempt_indices_used": [row["attempt_index"] for row in per_attempt_rows],
            "top_filtered_names": problem_summary.get("top_filtered_names", []),
            "per_attempt_rows": per_attempt_rows,
            "selected_results": selected_results,
        }

        save_json(output_spec_path, out_spec)
        save_json(output_metadata_path, out_metadata)
        selected_names = [row.get("full_name") or "<?>" for row in selected_results]
        print(
            f"[{branch_name} {index}/{total}] {problem_key}: "
            + (", ".join(selected_names) if selected_names else "no results")
        )


def main() -> int:
    args = parse_args()

    nohint_spec = load_json(args.nohint_spec)
    top2_spec = load_json(args.top2_spec)
    nohint_trigger_spec = load_json(args.nohint_trigger_spec)
    top2_trigger_spec = load_json(args.top2_trigger_spec)
    nohint_run = load_json(args.nohint_run)
    top2_run = load_json(args.top2_run)

    nohint_summary = summarize_hallucinations(
        args.nohint_run, min_name_length=args.min_name_length, top=50
    )
    top2_summary = summarize_hallucinations(
        args.top2_run, min_name_length=args.min_name_length, top=50
    )

    client = LeanFinderClient(cache_path=args.cache_path)

    build_branch(
        branch_name="nohint-allhall-attempt-top6",
        base_spec=nohint_spec,
        trigger_spec=nohint_trigger_spec,
        run_payload=nohint_run,
        hall_summary=nohint_summary,
        client=client,
        per_attempt_topk=args.per_attempt_topk,
        final_topk=args.final_topk,
        request_delay_s=args.request_delay_s,
        output_spec_path=args.nohint_output_spec,
        output_metadata_path=args.nohint_output_metadata,
    )

    build_branch(
        branch_name="statement-rag-top2-allhall-attempt-top6",
        base_spec=top2_spec,
        trigger_spec=top2_trigger_spec,
        run_payload=top2_run,
        hall_summary=top2_summary,
        client=client,
        per_attempt_topk=args.per_attempt_topk,
        final_topk=args.final_topk,
        request_delay_s=args.request_delay_s,
        output_spec_path=args.top2_output_spec,
        output_metadata_path=args.top2_output_metadata,
    )

    print(f"Wrote {args.nohint_output_spec}")
    print(f"Wrote {args.nohint_output_metadata}")
    print(f"Wrote {args.top2_output_spec}")
    print(f"Wrote {args.top2_output_metadata}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
