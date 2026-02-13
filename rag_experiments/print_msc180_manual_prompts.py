#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prompt_hints.prompt_config import (  # noqa: E402
    DeepSeekProverV2HintPromptConfig,
    DeepSeekProverV2HintWithUsagePromptConfig,
)

SPEC_ORDER = [
    ("A", "msc180_manual_A_spec.json", "basic"),
    ("B-main", "msc180_manual_B_main_spec.json", "basic"),
    ("B-all", "msc180_manual_B_all_spec.json", "basic"),
    ("C-main", "msc180_manual_C_main_spec.json", "usage"),
    ("C-all", "msc180_manual_C_all_spec.json", "usage"),
]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_prompt(
    style: str,
    *,
    header: str,
    formal_statement: str,
    theorem_hint: str,
) -> str:
    cfg = (
        DeepSeekProverV2HintWithUsagePromptConfig
        if style == "usage"
        else DeepSeekProverV2HintPromptConfig
    )
    return cfg.build(
        header=header,
        informal_statement=theorem_hint or None,
        formal_statement=formal_statement,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Print prompts for the 5 MSC-180 manual specs in interleaved order: "
            "problem i across all specs, then next problem."
        )
    )
    parser.add_argument(
        "--spec-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "specs",
        help="Directory containing msc180_manual_* spec JSON files.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    spec_dir = args.spec_dir
    if not spec_dir.exists():
        raise FileNotFoundError(f"Spec directory not found: {spec_dir}")

    loaded_specs: list[tuple[str, str, str, dict]] = []
    for label, filename, style in SPEC_ORDER:
        path = spec_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Missing spec file: {path}")
        loaded_specs.append((label, filename, style, _load_json(path)))

    # Use A-spec key insertion order as canonical problem order.
    first_label, first_file, _, first_spec = loaded_specs[0]
    first_problems = first_spec.get("problems")
    if not isinstance(first_problems, dict):
        raise TypeError(f"{first_file} must contain a 'problems' object.")
    problem_order = list(first_problems.keys())
    if not problem_order:
        raise ValueError(f"{first_file} has no problems.")

    # Validate all specs contain exactly these keys.
    expected = set(problem_order)
    for label, filename, _, spec in loaded_specs[1:]:
        problems = spec.get("problems")
        if not isinstance(problems, dict):
            raise TypeError(f"{filename} must contain a 'problems' object.")
        got = set(problems.keys())
        if got != expected:
            missing = sorted(expected - got)
            extra = sorted(got - expected)
            raise ValueError(
                f"{filename} problem keys mismatch. Missing={missing}, Extra={extra}"
            )

    for idx, problem_key in enumerate(problem_order, start=1):
        print(f"\n{'=' * 18} Problem {idx}: {problem_key} {'=' * 18}\n")
        for label, filename, style, spec in loaded_specs:
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
                style,
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
