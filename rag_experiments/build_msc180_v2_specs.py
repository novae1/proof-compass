#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIED_DIR = ROOT / "rag_experiments" / "MSC-180" / "verified_problems"
SPEC_DIR = ROOT / "rag_experiments" / "specs"

SPEC_A = SPEC_DIR / "msc180_v2_A_spec.json"
SPEC_B = SPEC_DIR / "msc180_v2_B_spec.json"
SPEC_C = SPEC_DIR / "msc180_v2_C_spec.json"

STATEMENT_SECTION = "/- Statements of the listed theorems -/"
EXAMPLES_SECTION = "/- ===== Mathlib usage examples (theorem name changed to `example`) ===== -/"


@dataclass
class TheoremStmt:
    name: str
    statement: str


@dataclass
class UsageExample:
    theorem_name: str
    example_block: str


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _extract_header(text: str) -> str:
    m = re.search(r"^theorem\b", text, flags=re.M)
    if not m:
        raise ValueError("No theorem declaration found.")
    return text[: m.start()].rstrip()


def _extract_formal_statement(text: str) -> str:
    m = re.search(r"^theorem\b[\s\S]*?:=\s*by", text, flags=re.M)
    if not m:
        raise ValueError("Could not extract theorem statement up to ':= by'.")
    stmt = m.group(0).rstrip()
    return stmt + "\n  sorry"


def _extract_between(text: str, start_marker: str, end_marker: str | None) -> str:
    start = text.find(start_marker)
    if start == -1:
        raise ValueError(f"Marker not found: {start_marker}")
    start += len(start_marker)
    if end_marker is None:
        return text[start:]
    end = text.find(end_marker, start)
    if end == -1:
        raise ValueError(f"End marker not found: {end_marker}")
    return text[start:end]


def _extract_theorem_statements(text: str) -> list[TheoremStmt]:
    chunk = _extract_between(text, STATEMENT_SECTION, EXAMPLES_SECTION)
    lines = chunk.splitlines()
    out: list[TheoremStmt] = []
    i = 0

    first_re = re.compile(r"^\s*--\s*theorem\s+([A-Za-z_][A-Za-z0-9_.'/]*)\s*:\s*(.*)$")
    cont_re = re.compile(r"^\s*--\s{3}(.*)$")

    while i < len(lines):
        m = first_re.match(lines[i])
        if not m:
            i += 1
            continue
        name = m.group(1).strip()
        parts = [m.group(2).rstrip()]
        i += 1
        while i < len(lines):
            cm = cont_re.match(lines[i])
            if not cm:
                break
            parts.append(cm.group(1).rstrip())
            i += 1
        statement = "theorem " + name + " : " + "\n".join(parts).strip()
        out.append(TheoremStmt(name=name, statement=statement))
    if not out:
        raise ValueError("No commented theorem statements found in statement section.")
    return out


def _extract_usage_examples(text: str) -> list[UsageExample]:
    chunk = _extract_between(text, EXAMPLES_SECTION, None)
    lines = chunk.splitlines()
    out: list[UsageExample] = []
    i = 0

    uses_re = re.compile(r"^\s*--\s*Uses\s+`([^`]+)`\s*$")
    source_re = re.compile(r"^\s*--\s*Source:\s*(.*)$")
    example_re = re.compile(r"^\s*(?:@\[[^\]]+\]\s*)*(?:noncomputable\s+)?example\b")

    while i < len(lines):
        um = uses_re.match(lines[i])
        if not um:
            i += 1
            continue
        theorem_name = um.group(1).strip()
        i += 1

        # Optional source line may appear next; ignore it in the extracted hint payload.
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        if i >= len(lines):
            raise ValueError(f"Missing example block after Uses `{theorem_name}`")
        if source_re.match(lines[i]):
            i += 1

        while i < len(lines) and lines[i].strip() == "":
            i += 1
        if i >= len(lines) or not example_re.match(lines[i]):
            raise ValueError(f"Missing example block after Uses `{theorem_name}`")

        start = i
        i += 1
        while i < len(lines):
            if uses_re.match(lines[i]):
                break
            i += 1

        block = "\n".join(lines[start:i]).rstrip()
        out.append(UsageExample(theorem_name=theorem_name, example_block=block))

    if not out:
        raise ValueError("No usage examples found in examples section.")
    return out


def _build_hint_B(statements: list[TheoremStmt]) -> str:
    blocks = [
        "-- this theorem might be useful in the proof of the problem\n" + s.statement
        for s in statements
    ]
    return "\n\n".join(blocks).strip()


def _build_hint_C(statements: list[TheoremStmt], usages: list[UsageExample]) -> str:
    # Pair by theorem name in statement order, consuming first available matching usage each time.
    remaining = usages[:]
    blocks: list[str] = []
    for s in statements:
        idx = next((j for j, u in enumerate(remaining) if u.theorem_name == s.name), None)
        if idx is None:
            raise ValueError(f"No usage example found for theorem `{s.name}`")
        u = remaining.pop(idx)
        theorem_block = "-- this theorem might be useful in the proof of the problem\n" + s.statement
        example_block = (
            f"-- this is an example of how theorem {s.name} is used\n"
            f"{u.example_block}"
        )
        blocks.append(f"{theorem_block}\n\n{example_block}")
    return "\n\n".join(blocks).strip()


def _problem_key(path: Path) -> str:
    return f"MSC-180/{path.stem}"


def _build_specs() -> tuple[dict, dict, dict]:
    files = sorted(VERIFIED_DIR.glob("*.lean"))
    if len(files) != 20:
        raise ValueError(f"Expected 20 verified problem files, found {len(files)}")

    spec_a: dict[str, dict] = {"problems": {}}
    spec_b: dict[str, dict] = {"problems": {}}
    spec_c: dict[str, dict] = {"problems": {}}

    for path in files:
        text = _load(path)
        header = _extract_header(text)
        formal_statement = _extract_formal_statement(text)
        statements = _extract_theorem_statements(text)
        usages = _extract_usage_examples(text)

        key = _problem_key(path)
        spec_a["problems"][key] = {
            "header": header,
            "formal_statement": formal_statement,
            "theorem_hint": "",
        }
        spec_b["problems"][key] = {
            "header": header,
            "formal_statement": formal_statement,
            "theorem_hint": _build_hint_B(statements),
        }
        spec_c["problems"][key] = {
            "header": header,
            "formal_statement": formal_statement,
            "theorem_hint": _build_hint_C(statements, usages),
        }

    return spec_a, spec_b, spec_c


def main() -> int:
    spec_a, spec_b, spec_c = _build_specs()
    _save_json(SPEC_A, spec_a)
    _save_json(SPEC_B, spec_b)
    _save_json(SPEC_C, spec_c)
    print(f"Wrote {SPEC_A}")
    print(f"Wrote {SPEC_B}")
    print(f"Wrote {SPEC_C}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
