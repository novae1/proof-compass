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
DEFAULT_TOP4_SPEC = (
    ROOT
    / "rag_experiments"
    / "data"
    / "specs"
    / "20260401_proofnet_valid_statement_rag_top4_followup_spec.json"
)
DEFAULT_TOP4_METADATA = (
    ROOT
    / "rag_experiments"
    / "reports"
    / "iterative_rag"
    / "20260401_proofnet_valid_statement_rag_top4_followup_metadata.json"
)
DEFAULT_NOHINT_ATTEMPT_SPEC = (
    ROOT
    / "rag_experiments"
    / "data"
    / "specs"
    / "20260401_proofnet_valid_nohint_attempt_rag_top4_spec.json"
)
DEFAULT_NOHINT_ATTEMPT_METADATA = (
    ROOT
    / "rag_experiments"
    / "reports"
    / "iterative_rag"
    / "20260401_proofnet_valid_nohint_attempt_rag_top4_metadata.json"
)
DEFAULT_TOP2_ATTEMPT_SPEC = (
    ROOT
    / "rag_experiments"
    / "data"
    / "specs"
    / "20260401_proofnet_valid_statement_rag_top2_attempt_rag_top4_spec.json"
)
DEFAULT_TOP2_ATTEMPT_METADATA = (
    ROOT
    / "rag_experiments"
    / "reports"
    / "iterative_rag"
    / "20260401_proofnet_valid_statement_rag_top2_attempt_rag_top4_metadata.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build follow-up ProofNet-valid specs: statement-rag-top4 on the solved-or-triggered "
            "subset, plus branch-specific whole-attempt top4 specs on the no-hint and top2-RAG "
            "trigger sets."
        )
    )
    parser.add_argument("--nohint-spec", type=Path, default=DEFAULT_NOHINT_SPEC)
    parser.add_argument("--top2-spec", type=Path, default=DEFAULT_TOP2_SPEC)
    parser.add_argument("--nohint-trigger-spec", type=Path, default=DEFAULT_NOHINT_TRIGGER_SPEC)
    parser.add_argument("--top2-trigger-spec", type=Path, default=DEFAULT_TOP2_TRIGGER_SPEC)
    parser.add_argument("--nohint-run", type=Path, default=DEFAULT_NOHINT_RUN)
    parser.add_argument("--top2-run", type=Path, default=DEFAULT_TOP2_RUN)
    parser.add_argument("--top4-spec", type=Path, default=DEFAULT_TOP4_SPEC)
    parser.add_argument("--top4-metadata", type=Path, default=DEFAULT_TOP4_METADATA)
    parser.add_argument("--nohint-attempt-spec", type=Path, default=DEFAULT_NOHINT_ATTEMPT_SPEC)
    parser.add_argument(
        "--nohint-attempt-metadata", type=Path, default=DEFAULT_NOHINT_ATTEMPT_METADATA
    )
    parser.add_argument("--top2-attempt-spec", type=Path, default=DEFAULT_TOP2_ATTEMPT_SPEC)
    parser.add_argument(
        "--top2-attempt-metadata", type=Path, default=DEFAULT_TOP2_ATTEMPT_METADATA
    )
    parser.add_argument("--cache-path", type=Path, help="LeanFinder cache path override.")
    parser.add_argument(
        "--statement-search-topk",
        type=int,
        default=8,
        help="LeanFinder results to inspect for statement-only top4 retrieval.",
    )
    parser.add_argument(
        "--attempt-search-topk",
        type=int,
        default=8,
        help="LeanFinder results to inspect for whole-attempt top4 retrieval.",
    )
    parser.add_argument(
        "--request-delay-s",
        type=float,
        default=0.35,
        help="Delay between uncached LeanFinder requests to reduce rate-limit risk.",
    )
    parser.add_argument(
        "--min-name-length",
        type=int,
        default=7,
        help="Minimum character length for filtered unresolved theorem-like names.",
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


def dedup_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
        theorem_name = result.get("full_name") or trim_declaration_to_signature(
            result.get("formal_statement", "")
        )
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
    ordered = sorted(
        rows,
        key=lambda row: (
            -int(row.get("attempts", 0)),
            -int(row.get("occurrences", 0)),
            str(row.get("name", "")),
        ),
    )
    return ordered[:2]


def solved_problem_keys(payload: dict[str, Any]) -> set[str]:
    solved: set[str] = set()
    for run_key, entry in payload.items():
        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            continue
        if any(bool(attempt.get("success")) for attempt in attempts if isinstance(attempt, dict)):
            solved.add(canonical_problem_key(run_key))
    return solved


def key_map(payload: dict[str, Any]) -> dict[str, str]:
    return {canonical_problem_key(problem_key): problem_key for problem_key in payload}


def cached_probe(client: LeanFinderClient, query: str, k: int) -> bool:
    cache_key = json.dumps({"query": query.strip(), "k": k}, ensure_ascii=False, sort_keys=True)
    return cache_key in client._cache


def select_attempt_indices_for_top_hallucinations(
    problem_summary: dict[str, Any],
) -> tuple[list[int], list[dict[str, Any]]]:
    top_hallucinations = choose_top_hallucinations(problem_summary)
    target = {str(row["name"]) for row in top_hallucinations}
    if not target:
        return [], []

    attempt_rows = problem_summary.get("attempt_rows", [])
    indexed_sets: list[tuple[int, set[str]]] = []
    for row in attempt_rows:
        attempt_index = int(row["attempt_index"])
        names = set(str(name) for name in row.get("filtered_names", []))
        if not names:
            continue
        indexed_sets.append((attempt_index, names))

    single_cover = [idx for idx, names in indexed_sets if target.issubset(names)]
    if single_cover:
        return [min(single_cover)], top_hallucinations

    candidate_indices = [idx for idx, names in indexed_sets if names & target]
    candidate_indices.sort()
    for left_pos, left_idx in enumerate(candidate_indices):
        left_names = next(names for idx, names in indexed_sets if idx == left_idx)
        for right_idx in candidate_indices[left_pos + 1 :]:
            right_names = next(names for idx, names in indexed_sets if idx == right_idx)
            if target.issubset(left_names | right_names):
                return [left_idx, right_idx], top_hallucinations

    raise ValueError(f"Could not cover hallucinations {sorted(target)} with one or two attempts.")


def attempt_query_text(entry: dict[str, Any], selected_indices: list[int]) -> str:
    attempts = entry.get("attempts")
    if not isinstance(attempts, list):
        raise TypeError("Expected 'attempts' list in run entry.")

    chunks: list[str] = []
    for attempt_index in selected_indices:
        attempt = attempts[attempt_index]
        if not isinstance(attempt, dict):
            raise TypeError(f"Attempt {attempt_index} is not a JSON object.")
        text = str(attempt.get("parsed_proof") or attempt.get("raw_output") or "").strip()
        if not text:
            raise ValueError(f"Attempt {attempt_index} is missing parsed_proof/raw_output.")
        chunks.append(text)
    return "\n\n".join(chunks).strip()


def top_results(results: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return dedup_results(prefer_theorems_and_lemmas(results))[:limit]


def main() -> int:
    args = parse_args()

    nohint_spec = load_json(args.nohint_spec)["problems"]
    top2_spec = load_json(args.top2_spec)["problems"]
    nohint_trigger_spec = load_json(args.nohint_trigger_spec)["problems"]
    top2_trigger_spec = load_json(args.top2_trigger_spec)["problems"]
    nohint_run = load_json(args.nohint_run)
    top2_run = load_json(args.top2_run)

    nohint_key_map = key_map(nohint_run)
    top2_key_map = key_map(top2_run)
    nohint_summary = summarize_hallucinations(
        args.nohint_run, min_name_length=args.min_name_length, top=50
    )
    top2_summary = summarize_hallucinations(
        args.top2_run, min_name_length=args.min_name_length, top=50
    )

    solved_union = solved_problem_keys(nohint_run) | solved_problem_keys(top2_run)
    nohint_trigger_keys = set(nohint_trigger_spec.keys())
    top2_trigger_keys = set(top2_trigger_spec.keys())
    solved_or_triggered = solved_union | nohint_trigger_keys | top2_trigger_keys

    client = LeanFinderClient(cache_path=args.cache_path)

    top4_spec: dict[str, Any] = {"problems": {}}
    top4_metadata: dict[str, Any] = {
        "config": {
            "statement_search_topk": args.statement_search_topk,
            "final_theorem_budget": 4,
        },
        "subset": {
            "solved_union": len(solved_union),
            "nohint_trigger_keys": len(nohint_trigger_keys),
            "top2_trigger_keys": len(top2_trigger_keys),
            "solved_or_triggered": len(solved_or_triggered),
        },
        "problems": {},
    }

    nohint_attempt_spec: dict[str, Any] = {"problems": {}}
    nohint_attempt_metadata: dict[str, Any] = {
        "config": {
            "attempt_search_topk": args.attempt_search_topk,
            "final_theorem_budget": 4,
            "hallucination_selection": "top2_by_attempts_then_occurrences",
            "attempt_selection": "one_attempt_if_top2_hallucinations_cooccur_else_smallest_two-attempt cover",
        },
        "subset": {"triggered_problems": len(nohint_trigger_keys)},
        "problems": {},
    }

    top2_attempt_spec: dict[str, Any] = {"problems": {}}
    top2_attempt_metadata: dict[str, Any] = {
        "config": {
            "attempt_search_topk": args.attempt_search_topk,
            "final_theorem_budget": 4,
            "hallucination_selection": "top2_by_attempts_then_occurrences",
            "attempt_selection": "one_attempt_if_top2_hallucinations_cooccur_else_smallest_two-attempt cover",
        },
        "subset": {"triggered_problems": len(top2_trigger_keys)},
        "problems": {},
    }

    total_statement = len(solved_or_triggered)
    for index, problem_key in enumerate(sorted(solved_or_triggered), start=1):
        base_entry = nohint_spec.get(problem_key) or top2_spec.get(problem_key)
        if not isinstance(base_entry, dict):
            raise KeyError(f"Missing base spec entry for {problem_key}")
        query = str(base_entry["formal_statement"]).strip()
        was_cached = cached_probe(client, query, args.statement_search_topk)
        results = client.retrieve(query, k=args.statement_search_topk)
        selected = top_results(results, limit=4)
        top4_spec["problems"][problem_key] = {
            "header": str(base_entry["header"]).strip(),
            "formal_statement": str(base_entry["formal_statement"]).strip(),
            "theorem_hint": build_hint_block(selected),
        }
        top4_metadata["problems"][problem_key] = {
            "in_solved_union": problem_key in solved_union,
            "in_nohint_trigger_set": problem_key in nohint_trigger_keys,
            "in_statement_rag_top2_trigger_set": problem_key in top2_trigger_keys,
            "statement_query": query,
            "statement_results": results,
            "selected_results": selected,
        }
        save_json(args.top4_spec, top4_spec)
        save_json(args.top4_metadata, top4_metadata)
        selected_names = [row.get("full_name") or "<?>" for row in selected]
        print(
            f"[statement-top4 {index}/{total_statement}] {problem_key}: "
            + (", ".join(selected_names) if selected_names else "no results")
        )
        if not was_cached and args.request_delay_s > 0:
            time.sleep(args.request_delay_s)

    def build_attempt_spec(
        *,
        branch_name: str,
        trigger_keys: set[str],
        run_payload: dict[str, Any],
        summary: dict[str, Any],
        run_key_map: dict[str, str],
        output_spec: dict[str, Any],
        output_metadata: dict[str, Any],
        spec_path: Path,
        metadata_path: Path,
    ) -> None:
        total = len(trigger_keys)
        for index, problem_key in enumerate(sorted(trigger_keys), start=1):
            actual_key = run_key_map[problem_key]
            entry = run_payload[actual_key]
            problem_summary = summary["problems"][actual_key]
            selected_attempt_indices, selected_hallucinations = select_attempt_indices_for_top_hallucinations(
                problem_summary
            )
            query = attempt_query_text(entry, selected_attempt_indices)
            was_cached = cached_probe(client, query, args.attempt_search_topk)
            results = client.retrieve(query, k=args.attempt_search_topk)
            selected = top_results(results, limit=4)
            base_entry = nohint_spec.get(problem_key) or top2_spec.get(problem_key)
            if not isinstance(base_entry, dict):
                raise KeyError(f"Missing base spec entry for {problem_key}")
            output_spec["problems"][problem_key] = {
                "header": str(base_entry["header"]).strip(),
                "formal_statement": str(base_entry["formal_statement"]).strip(),
                "theorem_hint": build_hint_block(selected),
            }
            selected_attempt_rows = []
            for attempt_index in selected_attempt_indices:
                attempt_row = problem_summary["attempt_rows"][attempt_index]
                selected_attempt_rows.append(
                    {
                        "attempt_index": attempt_index,
                        "filtered_names": attempt_row.get("filtered_names", []),
                        "match_count": attempt_row.get("match_count"),
                    }
                )
            output_metadata["problems"][problem_key] = {
                "source_run_key": actual_key,
                "top_hallucinations": selected_hallucinations,
                "selected_attempt_indices": selected_attempt_indices,
                "selected_attempt_rows": selected_attempt_rows,
                "query_chars": len(query),
                "query_preview": query[:500],
                "attempt_results": results,
                "selected_results": selected,
            }
            save_json(spec_path, output_spec)
            save_json(metadata_path, output_metadata)
            selected_names = [row.get("full_name") or "<?>" for row in selected]
            print(
                f"[{branch_name} attempt-top4 {index}/{total}] {problem_key}: "
                + (", ".join(selected_names) if selected_names else "no results")
            )
            if not was_cached and args.request_delay_s > 0:
                time.sleep(args.request_delay_s)

    build_attempt_spec(
        branch_name="nohint",
        trigger_keys=nohint_trigger_keys,
        run_payload=nohint_run,
        summary=nohint_summary,
        run_key_map=nohint_key_map,
        output_spec=nohint_attempt_spec,
        output_metadata=nohint_attempt_metadata,
        spec_path=args.nohint_attempt_spec,
        metadata_path=args.nohint_attempt_metadata,
    )

    build_attempt_spec(
        branch_name="statement-rag-top2",
        trigger_keys=top2_trigger_keys,
        run_payload=top2_run,
        summary=top2_summary,
        run_key_map=top2_key_map,
        output_spec=top2_attempt_spec,
        output_metadata=top2_attempt_metadata,
        spec_path=args.top2_attempt_spec,
        metadata_path=args.top2_attempt_metadata,
    )

    print(f"Wrote {args.top4_spec}")
    print(f"Wrote {args.top4_metadata}")
    print(f"Wrote {args.nohint_attempt_spec}")
    print(f"Wrote {args.nohint_attempt_metadata}")
    print(f"Wrote {args.top2_attempt_spec}")
    print(f"Wrote {args.top2_attempt_metadata}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
