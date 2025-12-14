from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "miniF2F" / "Test.txt"
DESTINATION = ROOT / "processed" / "miniF2F_test.json"
JSON_SOURCE_DIR = ROOT / "miniF2F" / "test"

# Pattern captures each theorem block lazily until the next theorem declaration
THEOREM_PATTERN = re.compile(r"^theorem\s+(\S+)(.*?)(?=^theorem\s|\Z)", re.MULTILINE | re.DOTALL)


def clean_formal_statement(raw_statement: str) -> str:
    """Remove trailing sorry proofs and tidy whitespace."""
    statement = raw_statement.rstrip()
    statement = re.sub(r":= by\s+sorry\s*\Z", ":= by", statement)
    return statement


def parse_minif2f_test() -> dict[str, dict[str, str]]:
    text = SOURCE.read_text(encoding="utf-8")
    benchmark: dict[str, dict[str, str]] = {}

    for match in THEOREM_PATTERN.finditer(text):
        name = match.group(1)
        body = match.group(0)
        formal_statement = clean_formal_statement(body)
        benchmark[name] = {
            "formal_statement": formal_statement,
            "header": "",
        }
        json_path = JSON_SOURCE_DIR / f"{name}.json"
        if json_path.exists():
            try:
                informal_payload = json.loads(json_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                informal_payload = {}
            informal_statement = informal_payload.get("informal_statement", "")
            if informal_statement:
                benchmark[name]["informal_statement"] = informal_statement

    if not benchmark:
        raise RuntimeError("No theorems were parsed from the miniF2F Test.txt file.")

    return benchmark


def main() -> None:
    benchmark = parse_minif2f_test()
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    DESTINATION.write_text(json.dumps(benchmark, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
