#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

DEFAULT_NOHINT_SOURCE = ROOT / "rag_experiments" / "data" / "specs" / "20260331_proofnet_valid_nohint_spec.json"
DEFAULT_NOHINT_TRIGGER = (
    ROOT / "rag_experiments" / "data" / "specs" / "20260331_proofnet_valid_nohint_iterative_pass2_spec.json"
)
DEFAULT_TOP2_TRIGGER = (
    ROOT
    / "rag_experiments"
    / "data"
    / "specs"
    / "20260331_proofnet_valid_statement_rag_top2_iterative_pass2_spec.json"
)
DEFAULT_NOHINT_UNION = (
    ROOT / "api_proving" / "data" / "specs" / "20260417_proofnet_valid_trigger_union_nohint_spec.json"
)
DEFAULT_METADATA = (
    ROOT / "api_proving" / "reports" / "20260417_proofnet_valid_trigger_union_metadata.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the ProofNet-valid trigger-union no-hint spec for API experiments."
    )
    parser.add_argument("--nohint-source", type=Path, default=DEFAULT_NOHINT_SOURCE)
    parser.add_argument("--nohint-trigger", type=Path, default=DEFAULT_NOHINT_TRIGGER)
    parser.add_argument("--top2-trigger", type=Path, default=DEFAULT_TOP2_TRIGGER)
    parser.add_argument("--nohint-union-spec", type=Path, default=DEFAULT_NOHINT_UNION)
    parser.add_argument("--metadata-json", type=Path, default=DEFAULT_METADATA)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"Expected JSON object at {path}")
    return payload


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    nohint_source = load_json(args.nohint_source)["problems"]
    nohint_trigger = set(load_json(args.nohint_trigger)["problems"].keys())
    top2_trigger = set(load_json(args.top2_trigger)["problems"].keys())
    union_keys = sorted(nohint_trigger | top2_trigger)

    union_spec: dict[str, Any] = {"problems": {}}
    for problem_key in union_keys:
        entry = nohint_source.get(problem_key)
        if not isinstance(entry, dict):
            raise KeyError(f"Missing nohint source entry for {problem_key}")
        union_spec["problems"][problem_key] = {
            "header": str(entry.get("header", "")).strip(),
            "formal_statement": str(entry.get("formal_statement", "")).strip(),
            "theorem_hint": "",
        }

    metadata = {
        "source_specs": {
            "nohint_source": str(args.nohint_source),
            "nohint_trigger": str(args.nohint_trigger),
            "statement_rag_top2_trigger": str(args.top2_trigger),
        },
        "counts": {
            "nohint_trigger": len(nohint_trigger),
            "statement_rag_top2_trigger": len(top2_trigger),
            "union": len(union_keys),
            "intersection": len(nohint_trigger & top2_trigger),
        },
        "union_problem_keys": union_keys,
    }

    save_json(args.nohint_union_spec, union_spec)
    save_json(args.metadata_json, metadata)
    print(f"Wrote {args.nohint_union_spec}")
    print(f"Wrote {args.metadata_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
