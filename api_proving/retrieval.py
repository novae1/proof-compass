from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEANFINDER_TOOLS_DIR = ROOT / "rag_experiments" / "scripts" / "tools"
if str(LEANFINDER_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(LEANFINDER_TOOLS_DIR))

from leanfinder_client import LeanFinderClient  # type: ignore  # noqa: E402


def trim_declaration_to_signature(formal_statement: str) -> str:
    text = formal_statement.strip()
    if ":=" in text:
        text = text.split(":=", 1)[0].rstrip()
    return text


def declaration_kind(formal_statement: str) -> str:
    first_line = formal_statement.strip().splitlines()[0] if formal_statement.strip() else ""
    return first_line.split(maxsplit=1)[0] if first_line else ""


def dedup_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for result in results:
        key = result.get("full_name") or trim_declaration_to_signature(
            result.get("formal_statement", "")
        )
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(result)
    return out


def prefer_theorems_and_lemmas(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preferred: list[dict[str, Any]] = []
    fallback: list[dict[str, Any]] = []
    for result in results:
        kind = declaration_kind(result.get("formal_statement", ""))
        if kind in {"theorem", "lemma"}:
            preferred.append(result)
        else:
            fallback.append(result)
    return preferred + fallback


def top_results(results: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    return dedup_results(prefer_theorems_and_lemmas(results))[:limit]


def build_hint_block(selected_results: list[dict[str, Any]]) -> str:
    blocks: list[str] = []
    for result in selected_results:
        signature = trim_declaration_to_signature(result.get("formal_statement", ""))
        theorem_name = result.get("full_name") or signature
        blocks.append(
            "-- this theorem might be useful in the proof of the problem\n"
            f"-- Use as: {theorem_name}\n"
            + signature
        )
    return "\n\n".join(blocks).strip()


__all__ = [
    "LeanFinderClient",
    "build_hint_block",
    "declaration_kind",
    "dedup_results",
    "prefer_theorems_and_lemmas",
    "top_results",
    "trim_declaration_to_signature",
]
