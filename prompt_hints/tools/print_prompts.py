#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from prompt_hints.prompt_config import DeepSeekProverV2HintPromptConfig

HINTS_DIR = Path(__file__).resolve().parents[1]
SPEC_PATH = HINTS_DIR / "specs" / "experiment_spec.json"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print prompts for the prompt-hints experiment.")
    parser.add_argument("--spec", type=Path, default=SPEC_PATH)
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if not args.spec.exists():
        raise FileNotFoundError(f"Spec not found at {args.spec}")

    spec = _load_json(args.spec)
    problems = spec.get("problems")
    if not isinstance(problems, dict):
        raise TypeError("Spec must contain a 'problems' object.")

    for idx, (key, entry) in enumerate(problems.items(), start=1):
        if not isinstance(entry, dict):
            raise TypeError(f"Problem '{key}' must be a JSON object.")

        header = str(entry.get("header", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        theorem_hint = str(entry.get("theorem_hint", "")).strip() or None

        prompt = DeepSeekProverV2HintPromptConfig.build(
            header=header,
            informal_statement=theorem_hint,
            formal_statement=formal_statement,
        )

        print(f"\n===== [{idx}] {key} =====\n")
        print(prompt)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
