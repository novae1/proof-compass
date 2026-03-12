#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from transformers import AutoTokenizer


ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "deepseek-ai" / "DeepSeek-Prover-V2-7B"
DEFAULT_TRAIN = ROOT / "mathlib_fine_tuning" / "processed" / "deepseek_noncot_tactic_1024_train.jsonl"
DEFAULT_VALID = ROOT / "mathlib_fine_tuning" / "processed" / "deepseek_noncot_tactic_1024_valid.jsonl"
DEFAULT_SUMMARY = ROOT / "mathlib_fine_tuning" / "processed" / "deepseek_noncot_tactic_1024_summary.json"
DEFAULT_REPORT = ROOT / "mathlib_fine_tuning" / "processed" / "deepseek_noncot_tactic_1024_validation.json"

PROMPT_PREFIX = "Complete the following Lean 4 code:\n\n```lean4\n"
DECL_RE = re.compile(r"(?m)^\s*(?:(?:private|protected|nonrec)\s+)*(theorem|lemma)\s+([^\s(:{]+)")


def _iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            yield idx, json.loads(line)


def _extract_outer_fenced_block(text: str) -> str | None:
    marker = "```lean4\n"
    if not text.startswith(marker):
        return None
    if not text.endswith("\n```"):
        return None
    return text[len(marker) : -len("\n```")]


def _extract_decl_name(text: str) -> str | None:
    m = DECL_RE.search(text)
    return m.group(2) if m else None


def _scan_outer_assign(text: str) -> int | None:
    depth_paren = 0
    depth_brack = 0
    depth_brace = 0
    i = 0
    in_string = False
    block_comment_depth = 0
    line_comment = False

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if line_comment:
            if ch == "\n":
                line_comment = False
            i += 1
            continue

        if block_comment_depth:
            if ch == "/" and nxt == "-":
                block_comment_depth += 1
                i += 2
                continue
            if ch == "-" and nxt == "/":
                block_comment_depth -= 1
                i += 2
                continue
            i += 1
            continue

        if in_string:
            if ch == "\\":
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue

        if ch == "-" and nxt == "-":
            line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "-":
            block_comment_depth = 1
            i += 2
            continue
        if ch == '"':
            in_string = True
            i += 1
            continue

        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren = max(depth_paren - 1, 0)
        elif ch == "[":
            depth_brack += 1
        elif ch == "]":
            depth_brack = max(depth_brack - 1, 0)
        elif ch == "{":
            depth_brace += 1
        elif ch == "}":
            depth_brace = max(depth_brace - 1, 0)
        elif (
            ch == ":"
            and nxt == "="
            and depth_paren == 0
            and depth_brack == 0
            and depth_brace == 0
        ):
            return i
        i += 1

    return None


def _starts_with_outer_tactic(text: str) -> bool:
    assign_idx = _scan_outer_assign(text)
    if assign_idx is None:
        return False
    return text[assign_idx + 2 :].lstrip().startswith("by")


def _expected_split_from_completion(completion_block: str, valid_percent: int) -> str:
    digest = hashlib.sha256(completion_block.encode("utf-8")).digest()
    bucket = int.from_bytes(digest[:8], "big") % 100
    return "valid" if bucket < valid_percent else "train"


def _validate_file(path: Path, expected_split: str, valid_percent: int, tokenizer) -> tuple[dict, set[str]]:
    stats = {
        "rows": 0,
        "bad_rows": 0,
        "errors": {},
        "token_count_min": None,
        "token_count_max": None,
    }
    signatures: set[str] = set()

    for _, row in _iter_jsonl(path):
        stats["rows"] += 1
        row_errors: list[str] = []

        if set(row.keys()) != {"prompt", "completion", "text", "token_count"}:
            row_errors.append("bad_keys")

        prompt = row.get("prompt")
        completion = row.get("completion")
        text = row.get("text")
        token_count = row.get("token_count")

        if not isinstance(prompt, str):
            row_errors.append("prompt_not_string")
        if not isinstance(completion, str):
            row_errors.append("completion_not_string")
        if not isinstance(text, str):
            row_errors.append("text_not_string")
        if not isinstance(token_count, int):
            row_errors.append("token_count_not_int")

        if row_errors:
            stats["bad_rows"] += 1
            for err in row_errors:
                stats["errors"][err] = stats["errors"].get(err, 0) + 1
            continue

        if not prompt.startswith(PROMPT_PREFIX):
            row_errors.append("prompt_prefix")

        prompt_block = None
        completion_block = None

        if prompt.count("```lean4\n") != 1:
            row_errors.append("prompt_open_fence_count")
        prompt_start = prompt.find("```lean4\n")
        if prompt_start == -1:
            row_errors.append("prompt_fence")
        else:
            prompt_inner = prompt[prompt_start:]
            prompt_block = _extract_outer_fenced_block(prompt_inner)
            if prompt_block is None:
                row_errors.append("prompt_fence")

        if completion.count("```lean4\n") != 1:
            row_errors.append("completion_open_fence_count")
        completion_block = _extract_outer_fenced_block(completion)

        if completion_block is None:
            row_errors.append("completion_fence")

        if prompt_block is not None:
            if not re.search(r":=\s*by\s*\n\s*sorry\b", prompt_block, re.S):
                row_errors.append("prompt_missing_by_sorry")
            if "sorry" not in prompt_block:
                row_errors.append("prompt_missing_sorry")

        if completion_block is not None:
            if "sorry" in completion_block:
                row_errors.append("completion_contains_sorry")
            if not _starts_with_outer_tactic(completion_block):
                row_errors.append("completion_not_tactic")

        if prompt_block is not None and completion_block is not None:
            prompt_name = _extract_decl_name(prompt_block)
            completion_name = _extract_decl_name(completion_block)
            if prompt_name != completion_name:
                row_errors.append("decl_name_mismatch")

            if _expected_split_from_completion(completion_block, valid_percent) != expected_split:
                row_errors.append("split_mismatch")

            signatures.add(hashlib.sha256(completion_block.encode("utf-8")).hexdigest())

        rendered = tokenizer.apply_chat_template(
            [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": completion},
            ],
            tokenize=False,
            add_generation_prompt=False,
        )
        if rendered != text:
            row_errors.append("text_mismatch")

        actual_token_count = len(
            tokenizer.apply_chat_template(
                [
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": completion},
                ],
                tokenize=True,
                add_generation_prompt=False,
            )
        )
        if actual_token_count != token_count:
            row_errors.append("token_count_mismatch")
        if actual_token_count > 1024:
            row_errors.append("token_count_over_limit")

        stats["token_count_min"] = actual_token_count if stats["token_count_min"] is None else min(stats["token_count_min"], actual_token_count)
        stats["token_count_max"] = actual_token_count if stats["token_count_max"] is None else max(stats["token_count_max"], actual_token_count)

        if row_errors:
            stats["bad_rows"] += 1
            for err in row_errors:
                stats["errors"][err] = stats["errors"].get(err, 0) + 1

    return stats, signatures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument("--valid", type=Path, default=DEFAULT_VALID)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_PATH), trust_remote_code=True)
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    valid_percent = int(summary["valid_percent"])

    train_stats, train_signatures = _validate_file(args.train, "train", valid_percent, tokenizer)
    valid_stats, valid_signatures = _validate_file(args.valid, "valid", valid_percent, tokenizer)

    report = {
        "summary_matches": {
            "train_rows": train_stats["rows"] == summary["split_counts"]["train"],
            "valid_rows": valid_stats["rows"] == summary["split_counts"]["valid"],
            "retained_rows": train_stats["rows"] + valid_stats["rows"] == summary["retained_rows"],
        },
        "train": train_stats,
        "valid": valid_stats,
        "overlap": {
            "shared_completion_blocks": len(train_signatures & valid_signatures),
        },
    }

    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
