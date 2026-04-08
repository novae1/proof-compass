#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

from transformers import AutoTokenizer


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from prompt_hints.prompt_config import DeepSeekProverV2HintNonCoTPromptConfig
INPUT_PATH = ROOT / "mathlib_fine_tuning" / "data" / "raw" / "mathlib_theorems_validated_tactic.jsonl"
OUTPUT_DIR = ROOT / "mathlib_fine_tuning" / "data" / "processed"
TRAIN_PATH = OUTPUT_DIR / "deepseek_noncot_tactic_1024_train.jsonl"
VALID_PATH = OUTPUT_DIR / "deepseek_noncot_tactic_1024_valid.jsonl"
SUMMARY_PATH = OUTPUT_DIR / "deepseek_noncot_tactic_1024_summary.json"
MODEL_PATH = ROOT / "models" / "deepseek-ai" / "DeepSeek-Prover-V2-7B"

MAX_SEQ_LENGTH = 1024
VALID_PERCENT = 2

DECL_RE = re.compile(r"(?m)^\s*(?:(?:private|protected|nonrec)\s+)*(theorem|lemma)\b")
END_LINE_RE = re.compile(r"^\s*end(?:\s+\S+)?\s*$")


@dataclass
class ProcessedRow:
    prompt: str
    completion: str
    text: str
    token_count: int


def _find_decl(text: str) -> re.Match[str] | None:
    return DECL_RE.search(text)


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


def _split_standalone_lean(text: str) -> tuple[str, str, str, str] | None:
    decl_match = _find_decl(text)
    if decl_match is None:
        return None

    header = text[: decl_match.start()].rstrip()
    theorem_text = _strip_trailing_file_tail(text[decl_match.start() :].strip())
    assign_idx = _scan_outer_assign(theorem_text)
    if assign_idx is None:
        return None

    theorem_prefix = theorem_text[:assign_idx].rstrip()
    proof_start = theorem_text[assign_idx + 2 :].lstrip()
    if not proof_start.startswith("by"):
        return None

    theorem_sorry = theorem_prefix + " := by\n  sorry"
    kind = decl_match.group(1)
    return header, theorem_sorry, theorem_text, kind


def _strip_trailing_file_tail(theorem_text: str) -> str:
    lines = theorem_text.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    while lines and END_LINE_RE.match(lines[-1]):
        lines.pop()
        while lines and not lines[-1].strip():
            lines.pop()
    return "\n".join(lines).strip()


def _build_prompt(header: str, theorem_sorry: str) -> str:
    return DeepSeekProverV2HintNonCoTPromptConfig.build(
        header=header,
        informal_statement=None,
        formal_statement=theorem_sorry,
    )


def _build_completion(full_theorem: str) -> str:
    return f"```lean4\n{full_theorem.strip()}\n```"


def _tokenize_row(tokenizer, prompt: str, completion: str) -> tuple[str, int]:
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": completion},
    ]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )
    token_ids = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=False,
    )
    return text, len(token_ids)


def _assign_split(theorem_text: str) -> str:
    digest = hashlib.sha256(theorem_text.encode("utf-8")).digest()
    bucket = int.from_bytes(digest[:8], "big") % 100
    return "valid" if bucket < VALID_PERCENT else "train"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-path", type=Path, default=INPUT_PATH)
    parser.add_argument("--train-path", type=Path, default=TRAIN_PATH)
    parser.add_argument("--valid-path", type=Path, default=VALID_PATH)
    parser.add_argument("--summary-path", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.train_path.parent.mkdir(parents=True, exist_ok=True)
    args.valid_path.parent.mkdir(parents=True, exist_ok=True)
    args.summary_path.parent.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(str(args.model_path), trust_remote_code=True)

    summary: dict[str, object] = {
        "input_path": str(args.input_path.relative_to(ROOT)),
        "model_path": str(args.model_path.relative_to(ROOT)),
        "max_seq_length": MAX_SEQ_LENGTH,
        "valid_percent": VALID_PERCENT,
        "input_rows": 0,
        "skipped": {
            "no_decl_header": 0,
            "no_outer_assign_or_unparsed": 0,
            "non_tactic_outer": 0,
            "over_max_seq_length": 0,
        },
        "retained_rows": 0,
        "split_counts": {"train": 0, "valid": 0},
    }
    retained_token_counts: list[int] = []

    with (
        args.input_path.open("r", encoding="utf-8") as src,
        args.train_path.open("w", encoding="utf-8") as train_out,
        args.valid_path.open("w", encoding="utf-8") as valid_out,
    ):
        for idx, line in enumerate(src, start=1):
            summary["input_rows"] = idx
            row = json.loads(line)
            standalone_lean = row["standalone_lean"]

            decl_match = _find_decl(standalone_lean)
            if decl_match is None:
                summary["skipped"]["no_decl_header"] += 1
                continue

            split_result = _split_standalone_lean(standalone_lean)
            if split_result is None:
                if ":=" in standalone_lean:
                    summary["skipped"]["non_tactic_outer"] += 1
                else:
                    summary["skipped"]["no_outer_assign_or_unparsed"] += 1
                continue

            header, theorem_sorry, theorem_text, _kind = split_result
            prompt = _build_prompt(header, theorem_sorry)
            completion = _build_completion(theorem_text)
            text, token_count = _tokenize_row(tokenizer, prompt, completion)

            if token_count > MAX_SEQ_LENGTH:
                summary["skipped"]["over_max_seq_length"] += 1
                continue

            output_row = ProcessedRow(
                prompt=prompt,
                completion=completion,
                text=text,
                token_count=token_count,
            )
            split = _assign_split(theorem_text)
            out_f = train_out if split == "train" else valid_out
            out_f.write(
                json.dumps(output_row.__dict__, ensure_ascii=False) + "\n"
            )

            summary["retained_rows"] += 1
            summary["split_counts"][split] += 1
            retained_token_counts.append(token_count)

            if idx % 10000 == 0:
                print(
                    f"progress input_rows={idx} retained={summary['retained_rows']} "
                    f"train={summary['split_counts']['train']} valid={summary['split_counts']['valid']}"
                )

    if retained_token_counts:
        retained_sorted = sorted(retained_token_counts)

        def pct(p: float) -> float:
            pos = (len(retained_sorted) - 1) * p
            lo = int(pos)
            hi = min(lo + 1, len(retained_sorted) - 1)
            frac = pos - lo
            return retained_sorted[lo] * (1 - frac) + retained_sorted[hi] * frac

        summary["retained_token_stats"] = {
            "mean": round(statistics.mean(retained_token_counts), 2),
            "median": round(pct(0.5), 2),
            "p90": round(pct(0.9), 2),
            "p95": round(pct(0.95), 2),
            "p99": round(pct(0.99), 2),
            "max": max(retained_token_counts),
        }

    args.summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"wrote train={args.train_path.relative_to(ROOT)}")
    print(f"wrote valid={args.valid_path.relative_to(ROOT)}")
    print(f"wrote summary={args.summary_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
