#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

HINTS_DIR = Path(__file__).resolve().parents[1]
SPEC_PATH = HINTS_DIR / "specs" / "task1_spec.json"


def main() -> int:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    problems = spec.get("problems")
    if not isinstance(problems, dict):
        raise TypeError("Spec must contain a 'problems' object.")

    for key, entry in problems.items():
        if not isinstance(entry, dict):
            raise TypeError(f"Problem '{key}' must be a JSON object.")
        formal = str(entry.get("formal_statement", "")).strip()
        hint = str(entry.get("theorem_hint", "")).strip()
        print(f"\n===== {key} =====\n")
        print("Formal statement:")
        print(formal)
        print("\nTheorem hint:")
        print(hint)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
