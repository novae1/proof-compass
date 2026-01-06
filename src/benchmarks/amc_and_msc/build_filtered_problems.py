#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

MINIF2F_PATH = ROOT / "benchmarks" / "processed" / "miniF2F_valid.json"
MSC180_PATH = ROOT / "benchmarks" / "MSC-180" / "MSC-180.json"
OUTPUT_DIR = ROOT / "experiments" / "amc_and_msc"
OUTPUT_PATH = OUTPUT_DIR / "filtered_problems.json"


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _split_header_and_theorem(text: str) -> tuple[str, str]:
    lines = text.splitlines()
    last_idx = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("theorem "):
            last_idx = idx

    if last_idx is None:
        raise ValueError("No theorem declaration found in MSC-180 lean_statement.")

    header = "\n".join(lines[:last_idx]).strip()
    theorem = "\n".join(lines[last_idx:]).strip()

    if not header:
        raise ValueError("MSC-180 header is empty after split.")
    if not theorem:
        raise ValueError("MSC-180 formal statement is empty after split.")

    return header, theorem


def _load_minif2f_amc() -> dict[str, dict[str, str]]:
    data = _load_json(MINIF2F_PATH)
    if not isinstance(data, dict):
        raise TypeError("miniF2F_valid.json must be a JSON object.")

    filtered: dict[str, dict[str, str]] = {}
    for problem_id, entry in data.items():
        if not str(problem_id).lower().startswith("amc"):
            continue
        if not isinstance(entry, dict):
            raise TypeError(f"miniF2F entry '{problem_id}' must be a JSON object.")

        header = str(entry.get("header", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        if not header:
            raise ValueError(f"miniF2F entry '{problem_id}' has an empty header.")
        if not formal_statement:
            raise ValueError(f"miniF2F entry '{problem_id}' has an empty formal_statement.")

        filtered[f"miniF2F/{problem_id}"] = {
            "header": header,
            "formal_statement": formal_statement,
        }

    return filtered


def _load_msc180_undergrad() -> dict[str, dict[str, str]]:
    data = _load_json(MSC180_PATH)
    if not isinstance(data, list):
        raise TypeError("MSC-180.json must be a JSON list.")

    filtered: dict[str, dict[str, str]] = {}
    for entry in data:
        if not isinstance(entry, dict):
            raise TypeError("MSC-180 entries must be JSON objects.")

        difficulty = str(entry.get("difficult", ""))
        if "Undergraduate-Level" not in difficulty:
            continue

        problem_id = str(entry.get("problem_id", "")).strip()
        if not problem_id:
            raise ValueError("MSC-180 entry is missing problem_id.")

        lean_statements = entry.get("lean_statement", [])
        if not isinstance(lean_statements, list) or not lean_statements:
            raise ValueError(f"MSC-180 entry '{problem_id}' has no lean_statement.")

        header, formal_statement = _split_header_and_theorem(str(lean_statements[0]))
        filtered[f"MSC-180/{problem_id}"] = {
            "header": header,
            "formal_statement": formal_statement,
        }

    return filtered


def main() -> int:
    minif2f = _load_minif2f_amc()
    msc180 = _load_msc180_undergrad()
    combined: dict[str, dict[str, str]] = {}
    combined.update(minif2f)
    combined.update(msc180)
    _save_json(combined, OUTPUT_PATH)
    print(f"Wrote {len(combined)} problems to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
