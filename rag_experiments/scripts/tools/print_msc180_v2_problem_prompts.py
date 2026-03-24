#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from prompt_hints.prompt_config import DeepSeekProverV2HintPromptConfig  # noqa: E402


SPEC_ORDER = [
    ("A", "msc180_v2_A_spec.json"),
    ("B", "msc180_v2_B_spec.json"),
    ("C", "msc180_v2_C_spec.json"),
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_problem_id(raw: str) -> str:
    s = raw.strip()
    if s.startswith("MSC-180/"):
        return s
    if s.startswith("MSC-180_"):
        return s.replace("_", "/", 1)
    return f"MSC-180/{s}"


def _build_prompt(*, header: str, formal_statement: str, theorem_hint: str) -> str:
    return DeepSeekProverV2HintPromptConfig.build(
        header=header,
        informal_statement=theorem_hint or None,
        formal_statement=formal_statement,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print A/B/C prompts for one MSC-180 theorem ID from v2 specs."
    )
    parser.add_argument(
        "problem_id",
        help="Theorem/problem id: e.g. 08_001 or MSC-180/08_001 or MSC-180_08_001",
    )
    parser.add_argument(
        "--spec-dir",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "data" / "specs",
        help="Directory containing msc180_v2_A/B/C spec files.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    spec_dir = args.spec_dir
    if not spec_dir.exists():
        raise FileNotFoundError(f"Spec directory not found: {spec_dir}")

    problem_key = _normalize_problem_id(args.problem_id)

    loaded_specs: list[tuple[str, str, dict]] = []
    for label, filename in SPEC_ORDER:
        path = spec_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing spec file: {path}")
        loaded_specs.append((label, filename, _load_json(path)))

    # Validate key presence and print available nearby if missing.
    for label, filename, spec in loaded_specs:
        problems = spec.get("problems")
        if not isinstance(problems, dict):
            raise TypeError(f"{filename} must contain a 'problems' object.")
        if problem_key not in problems:
            available = ", ".join(sorted(problems.keys())[:10])
            raise KeyError(
                f"{problem_key} not found in {filename}. "
                f"Example available keys: {available}"
            )

    print(f"================== Problem: {problem_key} ==================\n")
    for label, filename, spec in loaded_specs:
        entry = spec["problems"][problem_key]
        if not isinstance(entry, dict):
            raise TypeError(f"{filename} entry for {problem_key} must be an object.")

        header = str(entry.get("header", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        theorem_hint = str(entry.get("theorem_hint", "")).strip()
        if not header:
            raise ValueError(f"{filename} / {problem_key} has empty header.")
        if not formal_statement:
            raise ValueError(f"{filename} / {problem_key} has empty formal_statement.")

        prompt = _build_prompt(
            header=header,
            formal_statement=formal_statement,
            theorem_hint=theorem_hint,
        )
        print(f"----- {label} ({filename}) -----\n")
        print(prompt)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
