from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # benchmarks/
PROCESSED_DIR = ROOT / "processed"

MINIF2F_DIR = ROOT / "miniF2F"
PROOFNET_DIR = ROOT / "proofnet"

THEOREM_PATTERN = re.compile(r"^theorem\s+(\S+)(.*?)(?=^theorem\s|\Z)", re.MULTILINE | re.DOTALL)


def _clean_processed_dir() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for path in PROCESSED_DIR.iterdir():
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()


def clean_formal_statement(raw_statement: str) -> str:
    statement = raw_statement.rstrip()
    m = re.search(r":=\s*by\b", statement)
    if m:
        statement = statement[: m.end()].rstrip()
    return statement


def build_minif2f(split: str) -> None:
    source = MINIF2F_DIR / ("Test.txt" if split == "test" else "Valid.txt")
    json_source_dir = MINIF2F_DIR / split
    destination = PROCESSED_DIR / f"miniF2F_{split}.json"

    text = source.read_text(encoding="utf-8")
    benchmark: dict[str, dict[str, str]] = {}

    for match in THEOREM_PATTERN.finditer(text):
        name = match.group(1)
        body = match.group(0)
        benchmark[name] = {"formal_statement": clean_formal_statement(body), "header": ""}

        json_path = json_source_dir / f"{name}.json"
        if json_path.exists():
            informal_payload = json.loads(json_path.read_text(encoding="utf-8"))
            informal_statement = informal_payload.get("informal_statement", "")
            if informal_statement:
                benchmark[name]["informal_statement"] = informal_statement

    destination.write_text(json.dumps(benchmark, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_proofnet(split: str) -> None:
    source = PROOFNET_DIR / "proofnet.jsonl"
    destination = PROCESSED_DIR / f"proofnet_{split}.json"

    rows: list[dict] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("split") == split:
            rows.append(row)

    destination.write_text(json.dumps(rows, indent=4) + "\n", encoding="utf-8")


def main() -> None:
    _clean_processed_dir()
    build_minif2f("test")
    build_minif2f("valid")
    build_proofnet("test")
    build_proofnet("valid")


if __name__ == "__main__":
    main()
