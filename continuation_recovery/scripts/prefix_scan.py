#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from continuation_recovery.scripts import recovery_study as rs


WORKSPACE_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = WORKSPACE_DIR / "artifacts"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prefix-only recovery scan over all cut positions.")
    parser.add_argument("reference_json", type=Path)
    parser.add_argument("--model", type=Path, default=rs.DEFAULT_MODEL)
    parser.add_argument("--max-backtrack", type=int, default=32)
    parser.add_argument("--strategy-set", choices=["core", "extended"], default="extended")
    parser.add_argument("--probe", action="append", dest="probes")
    parser.add_argument("--output-name", default="prefix_scan.json")
    return parser.parse_args()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _scan_case(case: dict[str, Any], tokenizer, probes: list[str], max_backtrack: int, strategy_set: str) -> dict[str, Any]:
    full_text = str(case["full_text"])
    prompt_text = str(case["prompt_text"])
    full_ids = [int(x) for x in case["full_token_ids"]]
    token_char_ends = rs._token_char_end_map(tokenizer, full_ids)

    result: dict[str, Any] = {
        "case_id": case["case_id"],
        "family": case["family"],
        "source_kind": case["source_kind"],
        "full_char_count": len(full_text),
        "cuts_scanned": max(len(full_text) - len(prompt_text) - 1, 0),
        "strategies": {},
    }

    strategy_stats = {
        name: {
            "count": 0,
            "prefix_exact": 0,
            "avg_backtrack_chars_total": 0,
            "by_kind": defaultdict(lambda: {"count": 0, "prefix_exact": 0, "backtrack_total": 0}),
        }
        for name in rs._strategy_names(strategy_set)
    }

    for cut in range(len(prompt_text) + 1, len(full_text)):
        visible_text = full_text[:cut]
        kind = rs._cut_kind(full_text, cut)
        for name in rs._strategy_names(strategy_set):
            recovered_text, _ = rs._strategy_text(name, visible_text, tokenizer, probes, max_backtrack)
            encoded_ids = tokenizer(recovered_text, add_special_tokens=True)["input_ids"]
            decoded_recovered_text = rs._safe_decode(tokenizer, encoded_ids)
            recovered_oracle_prefix_ids, _ = rs._oracle_prefix_for_visible_text(
                decoded_recovered_text,
                token_char_ends,
                full_ids,
            )
            exact = encoded_ids == recovered_oracle_prefix_ids
            backtrack = len(visible_text) - len(recovered_text)

            stats = strategy_stats[name]
            stats["count"] += 1
            stats["prefix_exact"] += int(exact)
            stats["avg_backtrack_chars_total"] += backtrack
            by_kind = stats["by_kind"][kind]
            by_kind["count"] += 1
            by_kind["prefix_exact"] += int(exact)
            by_kind["backtrack_total"] += backtrack

    for name, stats in strategy_stats.items():
        count = max(stats["count"], 1)
        result["strategies"][name] = {
            "count": stats["count"],
            "prefix_exact_rate": stats["prefix_exact"] / count,
            "avg_backtrack_chars": stats["avg_backtrack_chars_total"] / count,
            "by_kind": {
                kind: {
                    "count": kind_stats["count"],
                    "prefix_exact_rate": kind_stats["prefix_exact"] / max(kind_stats["count"], 1),
                    "avg_backtrack_chars": kind_stats["backtrack_total"] / max(kind_stats["count"], 1),
                }
                for kind, kind_stats in sorted(stats["by_kind"].items())
            },
        }

    return result


def _summary_markdown(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Prefix Scan Summary")
    lines.append("")
    lines.append(f"- created_at_utc: {payload['__meta__']['created_at_utc']}")
    lines.append(f"- source_reference_json: `{payload['__meta__']['source_reference_json']}`")
    lines.append(f"- case_count: {len(payload['cases'])}")
    lines.append("")
    lines.append("## Aggregate")
    lines.append("")

    aggregate: dict[str, dict[str, float]] = defaultdict(
        lambda: {"count": 0.0, "prefix_exact": 0.0, "backtrack_total": 0.0}
    )
    for case in payload["cases"]:
        for name, stats in case["strategies"].items():
            aggregate[name]["count"] += stats["count"]
            aggregate[name]["prefix_exact"] += stats["prefix_exact_rate"] * stats["count"]
            aggregate[name]["backtrack_total"] += stats["avg_backtrack_chars"] * stats["count"]

    for name in sorted(aggregate):
        stats = aggregate[name]
        count = max(stats["count"], 1.0)
        lines.append(
            f"- `{name}`: prefix_exact={stats['prefix_exact']/count:.3f}, "
            f"avg_backtrack={stats['backtrack_total']/count:.2f}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    rs._require_supported_transformers()
    args = _parse_args()
    tokenizer = rs._load_tokenizer(args.model)
    reference_payload = _load_json(args.reference_json)
    probes = args.probes or list(rs.DEFAULT_PROBES)

    result = {
        "__meta__": {
            "created_at_utc": _utc_timestamp(),
            "versions": rs._load_versions(),
            "model_path": str(Path(args.model).resolve()),
            "source_reference_json": str(args.reference_json.resolve()),
            "max_backtrack": args.max_backtrack,
            "strategy_set": args.strategy_set,
            "probes": probes,
        },
        "cases": [],
    }

    for case in reference_payload["cases"]:
        result["cases"].append(_scan_case(case, tokenizer, probes, args.max_backtrack, args.strategy_set))

    output_path = ARTIFACTS_DIR / args.output_name
    _save_json(result, output_path)
    summary_path = output_path.with_suffix(".md")
    summary_path.write_text(_summary_markdown(result), encoding="utf-8")
    print(output_path)
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
