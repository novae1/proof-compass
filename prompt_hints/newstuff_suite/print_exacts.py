#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def _load_spec(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_theorem_name(theorem_hint: str) -> str:
    for line in theorem_hint.splitlines():
        line = line.strip()
        if line.startswith("theorem "):
            remainder = line[len("theorem ") :].strip()
            name = remainder.split(":", 1)[0].strip()
            if name:
                return name
    raise ValueError("Could not find theorem name in theorem_hint.")


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 prompt_hints/print_exacts.py <spec_path>")

    spec_path = Path(sys.argv[1])
    spec = _load_spec(spec_path)
    problems = spec.get("problems")
    if not isinstance(problems, dict):
        raise ValueError("Spec must contain a 'problems' object.")

    print("import Mathlib\n")

    for key, entry in problems.items():
        theorem_hint = str(entry.get("theorem_hint", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        if not theorem_hint:
            raise ValueError(f"Problem '{key}' is missing theorem_hint.")
        if not formal_statement:
            raise ValueError(f"Problem '{key}' is missing formal_statement.")

        theorem_name = _extract_theorem_name(theorem_hint)
        rendered = formal_statement.replace(":= by sorry", f":= by exact {theorem_name}")
        print(rendered)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
