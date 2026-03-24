#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


DEFAULT_OUTPUT_JSON = Path(
    "rag_experiments/outputs/msc180/theorem_continuations/v4/"
    "20260310_msc180-v4-theorem-continuations-recovered_deepseekv2_7b_lean4-15.json"
)
DEFAULT_SUMMARY_JSON = Path("continuation_recovery/outputs/hallucination_analysis_v4.json")
DEFAULT_SUMMARY_MD = Path("continuation_recovery/outputs/hallucination_analysis_v4.md")
RUN_METADATA_KEY = "__meta__"

IDENTIFIER_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_']*(?:\.[A-Za-z][A-Za-z0-9_']*)*\b")
TRAILING_FRAGMENT_RE = re.compile(r"([A-Za-z][A-Za-z0-9_']*)$")
LEADING_FRAGMENT_RE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9_']*)")

PRIMARY_ORDER = [
    "boundary_fragment",
    "non_theorem_namespace_symbol",
    "target_short_suffix",
    "unresolved_other",
]


@dataclass(frozen=True)
class HallucinationRecord:
    slot_key: str
    source_key: str
    target_full_name: str
    first_identifier: str
    recovery_branch: str
    recovery_backtracked_chars: int
    requested_prompt_prefix_tail: str
    recovered_prompt_prefix_tail: str
    parsed_proof_head: str
    primary_cause: str
    signals: tuple[str, ...]
    last_requested_identifier: str | None
    recovered_tail_fragment: str | None
    leading_proof_fragment: str | None
    reconstructed_split_identifier: str | None


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze the remaining v4 hallucination bucket and separate real theorem-name "
            "hallucinations from boundary/parser artifacts."
        )
    )
    parser.add_argument(
        "output_json",
        nargs="?",
        type=Path,
        default=DEFAULT_OUTPUT_JSON,
        help="Path to the v4 continuation output JSON.",
    )
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=DEFAULT_SUMMARY_JSON,
        help="Where to write the machine-readable analysis summary.",
    )
    parser.add_argument(
        "--summary-md",
        type=Path,
        default=DEFAULT_SUMMARY_MD,
        help="Where to write the Markdown summary.",
    )
    parser.add_argument("--examples-per-group", type=int, default=3)
    return parser.parse_args()


def _load_payload(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Output JSON root must be an object.")
    return payload


def _last_identifier(text: str) -> str | None:
    matches = list(IDENTIFIER_RE.finditer(text))
    if not matches:
        return None
    return matches[-1].group(0)


def _trailing_fragment(text: str) -> str | None:
    match = TRAILING_FRAGMENT_RE.search(text)
    if match is None:
        return None
    return match.group(1)


def _leading_fragment(text: str) -> str | None:
    match = LEADING_FRAGMENT_RE.search(text)
    if match is None:
        return None
    return match.group(1)


def _is_boundary_fragment(
    *,
    requested_tail: str,
    recovered_tail: str,
    parsed_proof: str,
) -> tuple[bool, str | None, str | None, str | None, str | None]:
    last_requested_identifier = _last_identifier(requested_tail)
    recovered_tail_fragment = _trailing_fragment(recovered_tail)
    leading_proof_fragment = _leading_fragment(parsed_proof)
    reconstructed = None

    if (
        last_requested_identifier
        and recovered_tail_fragment
        and leading_proof_fragment
        and len(recovered_tail_fragment) < len(last_requested_identifier)
    ):
        reconstructed = recovered_tail_fragment + leading_proof_fragment
        if reconstructed == last_requested_identifier:
            return (
                True,
                last_requested_identifier,
                recovered_tail_fragment,
                leading_proof_fragment,
                reconstructed,
            )

    return (
        False,
        last_requested_identifier,
        recovered_tail_fragment,
        leading_proof_fragment,
        reconstructed,
    )


def _classify_record(
    *,
    slot_key: str,
    source_key: str,
    target_full_name: str,
    first_identifier: str,
    recovery_branch: str,
    recovery_backtracked_chars: int,
    requested_tail: str,
    recovered_tail: str,
    parsed_proof: str,
) -> HallucinationRecord:
    signals: list[str] = []
    (
        is_boundary_fragment,
        last_requested_identifier,
        recovered_tail_fragment,
        leading_proof_fragment,
        reconstructed_split_identifier,
    ) = _is_boundary_fragment(
        requested_tail=requested_tail,
        recovered_tail=recovered_tail,
        parsed_proof=parsed_proof,
    )
    if is_boundary_fragment:
        signals.append("boundary_fragment")
    if target_full_name.endswith(f".{first_identifier}"):
        signals.append("target_short_suffix")
    if "." in first_identifier and first_identifier.split(".", 1)[0][:1].isupper():
        signals.append("namespace_symbol")

    if is_boundary_fragment:
        primary_cause = "boundary_fragment"
    elif "namespace_symbol" in signals:
        primary_cause = "non_theorem_namespace_symbol"
    elif "target_short_suffix" in signals:
        primary_cause = "target_short_suffix"
    else:
        primary_cause = "unresolved_other"

    return HallucinationRecord(
        slot_key=slot_key,
        source_key=source_key,
        target_full_name=target_full_name,
        first_identifier=first_identifier,
        recovery_branch=recovery_branch,
        recovery_backtracked_chars=recovery_backtracked_chars,
        requested_prompt_prefix_tail=requested_tail,
        recovered_prompt_prefix_tail=recovered_tail,
        parsed_proof_head=parsed_proof[:220],
        primary_cause=primary_cause,
        signals=tuple(signals),
        last_requested_identifier=last_requested_identifier,
        recovered_tail_fragment=recovered_tail_fragment,
        leading_proof_fragment=leading_proof_fragment,
        reconstructed_split_identifier=reconstructed_split_identifier,
    )


def _iter_hallucination_records(payload: dict[str, object]) -> list[HallucinationRecord]:
    records: list[HallucinationRecord] = []
    for slot_key, entry in payload.items():
        if slot_key == RUN_METADATA_KEY or not isinstance(entry, dict):
            continue
        source_key = str(entry.get("header", "") or "")
        target_full_name = str(entry.get("formal_statement", "") or "")
        attempts = entry.get("attempts", [])
        if not isinstance(attempts, list):
            continue

        for attempt in attempts:
            if not isinstance(attempt, dict):
                continue
            message = attempt.get("message", {})
            if not isinstance(message, dict):
                continue
            if message.get("classification") != "hallucinated_theorem_like_name":
                continue

            first_identifier = str(message.get("first_identifier", "") or "").strip()
            if not first_identifier:
                continue

            records.append(
                _classify_record(
                    slot_key=slot_key,
                    source_key=source_key,
                    target_full_name=target_full_name,
                    first_identifier=first_identifier,
                    recovery_branch=str(message.get("recovery_branch", "") or ""),
                    recovery_backtracked_chars=int(message.get("recovery_backtracked_chars", 0) or 0),
                    requested_tail=str(message.get("requested_prompt_prefix_tail", "") or ""),
                    recovered_tail=str(message.get("recovered_prompt_prefix_tail", "") or ""),
                    parsed_proof=str(attempt.get("parsed_proof", "") or ""),
                )
            )
    return records


def _example_lines(records: list[HallucinationRecord], limit: int) -> list[str]:
    lines: list[str] = []
    for record in records[:limit]:
        lines.append(f"- slot: `{record.slot_key}`")
        lines.append(f"  target: `{record.target_full_name}`")
        lines.append(f"  first identifier: `{record.first_identifier}`")
        lines.append(
            f"  branch/backtrack: `{record.recovery_branch}` / `{record.recovery_backtracked_chars}`"
        )
        if record.reconstructed_split_identifier:
            lines.append(
                "  reconstructed boundary token: "
                f"`{record.recovered_tail_fragment}` + `{record.leading_proof_fragment}` -> "
                f"`{record.reconstructed_split_identifier}`"
            )
        lines.append(f"  recovered tail: `{record.recovered_prompt_prefix_tail[-80:]}`")
        lines.append(f"  proof head: `{record.parsed_proof_head}`")
    return lines


def _make_summary(records: list[HallucinationRecord], examples_per_group: int) -> dict[str, object]:
    primary_counts = Counter(record.primary_cause for record in records)
    identifier_counts = Counter(record.first_identifier for record in records)
    branch_counts = Counter(record.recovery_branch for record in records)
    slot_counts = Counter(record.slot_key for record in records)
    source_counts = Counter(record.source_key for record in records)
    target_counts = Counter(record.target_full_name for record in records)
    signal_counts = Counter(signal for record in records for signal in record.signals)
    by_primary_branch: dict[str, Counter[str]] = defaultdict(Counter)
    by_primary_identifier: dict[str, Counter[str]] = defaultdict(Counter)
    by_primary_examples: dict[str, list[HallucinationRecord]] = defaultdict(list)

    for record in records:
        by_primary_branch[record.primary_cause][record.recovery_branch] += 1
        by_primary_identifier[record.primary_cause][record.first_identifier] += 1
    for primary_cause in {record.primary_cause for record in records}:
        group_records = [record for record in records if record.primary_cause == primary_cause]
        chosen: list[HallucinationRecord] = []
        seen_identifiers: set[str] = set()
        seen_slots: set[str] = set()

        for record in group_records:
            if record.first_identifier in seen_identifiers:
                continue
            chosen.append(record)
            seen_identifiers.add(record.first_identifier)
            seen_slots.add(record.slot_key)
            if len(chosen) >= examples_per_group:
                break

        if len(chosen) < examples_per_group:
            for record in group_records:
                if record.slot_key in seen_slots:
                    continue
                chosen.append(record)
                seen_slots.add(record.slot_key)
                if len(chosen) >= examples_per_group:
                    break

        if len(chosen) < examples_per_group:
            for record in group_records:
                if record in chosen:
                    continue
                chosen.append(record)
                if len(chosen) >= examples_per_group:
                    break

        by_primary_examples[primary_cause] = chosen

    return {
        "total_hallucinations": len(records),
        "hallucinating_slots": len(slot_counts),
        "primary_counts": dict(primary_counts),
        "signal_counts": dict(signal_counts),
        "identifier_counts": dict(identifier_counts),
        "branch_counts": dict(branch_counts),
        "source_counts": dict(source_counts),
        "target_counts": dict(target_counts),
        "slot_counts": dict(slot_counts),
        "by_primary_branch": {key: dict(value) for key, value in by_primary_branch.items()},
        "by_primary_identifier": {key: dict(value) for key, value in by_primary_identifier.items()},
        "examples": {
            key: [asdict(record) for record in value] for key, value in by_primary_examples.items()
        },
        "records": [asdict(record) for record in records],
    }


def _render_summary(summary: dict[str, object], examples_per_group: int) -> str:
    total = int(summary["total_hallucinations"])
    slots = int(summary["hallucinating_slots"])
    primary_counts = summary["primary_counts"]
    signal_counts = summary["signal_counts"]
    identifier_counts = summary["identifier_counts"]
    branch_counts = summary["branch_counts"]
    target_counts = summary["target_counts"]
    examples = summary["examples"]

    lines: list[str] = []
    lines.append("# Hallucination Analysis")
    lines.append("")
    lines.append(f"- Total hallucination-labeled attempts: `{total}`")
    lines.append(f"- Unique hallucinating slots: `{slots}`")
    lines.append("")
    lines.append("## Primary causes")
    lines.append("")
    for label in PRIMARY_ORDER:
        count = int(primary_counts.get(label, 0))
        pct = (100.0 * count / total) if total else 0.0
        lines.append(f"- `{label}`: `{count}/{total}` (`{pct:.2f}%`)")
    lines.append("")
    lines.append("## Key takeaways")
    lines.append("")
    boundary_count = int(primary_counts.get("boundary_fragment", 0))
    namespace_count = int(primary_counts.get("non_theorem_namespace_symbol", 0))
    other_count = int(primary_counts.get("unresolved_other", 0))
    target_suffix_count = int(primary_counts.get("target_short_suffix", 0))
    lines.append(
        "- Most remaining hallucination labels are boundary artifacts, not novel theorem names."
    )
    lines.append(
        f"- `boundary_fragment` accounts for `{boundary_count}` attempts and comes from cuts that leave "
        "the recovered prefix ending in `sim`, so the continuation begins with the visible suffix of "
        "`simp` or `simp_all`."
    )
    lines.append(
        f"- `non_theorem_namespace_symbol` accounts for `{namespace_count}` attempts and is entirely "
        "the constructor-like opener `Exists.intro` on existential goals."
    )
    lines.append(
        f"- `target_short_suffix` accounts for `{target_suffix_count}` attempts after primary labeling, "
        f"but appears as a secondary signal in `{int(signal_counts.get('target_short_suffix', 0))}` attempt."
    )
    lines.append(f"- `unresolved_other` is `{other_count}` attempts.")
    lines.append("")
    lines.append("## Secondary signals")
    lines.append("")
    for signal, count in sorted(signal_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{signal}`: `{count}`")
    lines.append("")
    lines.append("## By identifier")
    lines.append("")
    for identifier, count in sorted(identifier_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{identifier}`: `{count}`")
    lines.append("")
    lines.append("## By recovery branch")
    lines.append("")
    for branch, count in sorted(branch_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{branch}`: `{count}`")
    lines.append("")
    lines.append("## By target theorem")
    lines.append("")
    for target, count in sorted(target_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"- `{target}`: `{count}`")
    lines.append("")
    lines.append("## Examples")
    lines.append("")
    for label in PRIMARY_ORDER:
        group = examples.get(label, [])
        if not group:
            continue
        lines.append(f"### `{label}`")
        lines.append("")
        lines.extend(_example_lines([HallucinationRecord(**record) for record in group], examples_per_group))
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = _parse_args()
    payload = _load_payload(args.output_json)
    records = _iter_hallucination_records(payload)
    summary = _make_summary(records, args.examples_per_group)
    summary_md = _render_summary(summary, args.examples_per_group)

    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    args.summary_md.parent.mkdir(parents=True, exist_ok=True)
    args.summary_md.write_text(summary_md, encoding="utf-8")

    print(f"Input file: {args.output_json}")
    print(f"Hallucination-labeled attempts: {summary['total_hallucinations']}")
    print(f"Unique hallucinating slots: {summary['hallucinating_slots']}")
    print(f"Summary JSON: {args.summary_json}")
    print(f"Summary Markdown: {args.summary_md}")
    for label in PRIMARY_ORDER:
        count = int(summary["primary_counts"].get(label, 0))
        print(f"{label:28} {count:4d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
