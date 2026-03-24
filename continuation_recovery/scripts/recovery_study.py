#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from prompt_hints.prompt_config import DeepSeekProverV2HintNonCoTPromptConfig


WORKSPACE_DIR = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = WORKSPACE_DIR / "outputs"
DEFAULT_MODEL = ROOT / "models" / "deepseek-ai" / "DeepSeek-Prover-V2-7B"
SUPPORTED_TRANSFORMERS_VERSION = "4.57.6"
ALLOW_UNSUPPORTED_ENV_VAR = "PROOF_COMPASS_ALLOW_UNSUPPORTED_TRANSFORMERS"

MSC_SPEC_PATH = ROOT / "rag_experiments" / "data" / "specs" / "msc180_v2_A_spec.json"
MSC_VERIFIED_OUTPUT = (
    ROOT
    / "rag_experiments"
    / "outputs"
    / "msc180"
    / "v2"
    / "20260301_msc180-v2_deepseekv2_7b_lean4-15_verified.json"
)
CONTINUATION_OUTPUT = (
    ROOT
    / "rag_experiments"
    / "outputs"
    / "msc180"
    / "theorem_continuations"
    / "v3"
    / "20260306_msc180-v3-theorem-continuations_deepseekv2_7b_lean4-15.json"
)

DEFAULT_PROBES = ["a", " ", "\n", "(", ".", ":", "_", "\n  "]
IDENT_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'.")


@dataclass
class ReferenceCase:
    case_id: str
    family: str
    source_kind: str
    prompt_text: str
    full_text: str
    generation_mode: str
    prompt_token_count: int
    full_token_ids: list[int]
    generated_token_ids: list[int]
    tokens: list[str]
    metadata: dict[str, Any]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Standalone study of text-only continuation recovery strategies."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build-cases", help="Generate a mixed reference case set.")
    build_parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    build_parser.add_argument("--seed", type=int, default=30)
    build_parser.add_argument("--max-new-tokens", type=int, default=96)
    build_parser.add_argument("--sample-prompts", type=int, default=4)
    build_parser.add_argument("--sample-slots", type=int, default=6)
    build_parser.add_argument("--do-sample", action="store_true")
    build_parser.add_argument("--temperature", type=float, default=1.0)
    build_parser.add_argument("--top-p", type=float, default=0.95)
    build_parser.add_argument("--output-name", default="reference_cases.json")

    sweep_parser = subparsers.add_parser("sweep-cuts", help="Evaluate recovery strategies over many cuts.")
    sweep_parser.add_argument("reference_json", type=Path)
    sweep_parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    sweep_parser.add_argument("--seed", type=int, default=30)
    sweep_parser.add_argument("--max-cuts-per-case", type=int, default=24)
    sweep_parser.add_argument("--max-new-tokens", type=int, default=12)
    sweep_parser.add_argument("--max-backtrack", type=int, default=32)
    sweep_parser.add_argument("--strategy-set", choices=["core", "extended"], default="extended")
    sweep_parser.add_argument("--probe", action="append", dest="probes")
    sweep_parser.add_argument("--output-name", default="recovery_sweep.json")

    summary_parser = subparsers.add_parser("summarize", help="Summarize a sweep artifact.")
    summary_parser.add_argument("sweep_json", type=Path)
    summary_parser.add_argument("--output-name", default="recovery_summary.md")

    return parser.parse_args()


def _require_supported_transformers() -> None:
    import transformers

    version = str(transformers.__version__)
    if os.environ.get(ALLOW_UNSUPPORTED_ENV_VAR) == "1":
        return
    if version != SUPPORTED_TRANSFORMERS_VERSION:
        raise SystemExit(
            "Continuation recovery study requires "
            f"transformers=={SUPPORTED_TRANSFORMERS_VERSION}; found {version}. "
            "Use .venv/bin/python after running ./init.sh, or set "
            f"{ALLOW_UNSUPPORTED_ENV_VAR}=1 to bypass this check."
        )


def _load_versions() -> dict[str, Any]:
    import tokenizers
    import torch
    import transformers

    return {
        "transformers": transformers.__version__,
        "tokenizers": tokenizers.__version__,
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
    }


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _save_text(text: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load_tokenizer(model_path: Path):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)


def _load_model(model_path: Path):
    import torch
    from transformers import AutoModelForCausalLM

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for recovery-study generation.")

    return AutoModelForCausalLM.from_pretrained(
        str(model_path),
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )


def _ensure_pad_token(tokenizer) -> int:
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if tokenizer.pad_token_id is None:
        raise ValueError("Tokenizer still has no pad_token_id after setup.")
    return int(tokenizer.pad_token_id)


def _safe_decode(tokenizer, ids: list[int]) -> str:
    return str(tokenizer.decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=False))


def _prompt_from_spec_entry(entry: dict[str, Any]) -> str:
    header = str(entry.get("header") or "")
    formal_statement = str(entry.get("formal_statement") or "")
    theorem_hint = str(entry.get("theorem_hint") or "")
    return DeepSeekProverV2HintNonCoTPromptConfig.build(
        header=header,
        informal_statement=theorem_hint,
        formal_statement=formal_statement,
    )


def _manual_preset_prompt() -> str:
    return (
        "Complete the following Lean 4 code:\n\n"
        "```lean4\n"
        "import Mathlib\n"
        "import Aesop\n\n"
        "set_option maxHeartbeats 0\n\n"
        "open BigOperators Real Nat Topology Rat\n\n"
        "/-- What is the positive difference between $120\\%$ of 30 and $130\\%$ of 20? Show that it is 10.-/\n"
        "theorem mathd_algebra_10 : abs ((120 : ℝ) / 100 * 30 - 130 / 100 * 20) = 10 := by\n"
        "  sorry\n"
        "```\n\n"
        "Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.\n"
    )


def _load_msc_prompt_entries(limit: int) -> list[tuple[str, str]]:
    payload = _load_json(MSC_SPEC_PATH)
    problems = payload.get("problems")
    if not isinstance(problems, dict):
        raise ValueError(f"Unexpected spec shape in {MSC_SPEC_PATH}")
    keys = sorted(problems)[:limit]
    return [(key, _prompt_from_spec_entry(problems[key])) for key in keys]


def _load_slot_prefix_entries(limit: int) -> list[tuple[str, str]]:
    payload = _load_json(CONTINUATION_OUTPUT)
    pairs: list[tuple[str, str]] = []
    for key, entry in payload.items():
        if key == "__meta__":
            continue
        if not isinstance(entry, dict):
            continue
        prefix = entry.get("nl_proof")
        if not isinstance(prefix, str) or not prefix:
            continue
        pairs.append((key, prefix))
    return pairs[:limit]


def _generate_reference(
    *,
    case_id: str,
    family: str,
    source_kind: str,
    prompt_text: str,
    tokenizer,
    model,
    pad_token_id: int,
    max_new_tokens: int,
    do_sample: bool,
    temperature: float,
    top_p: float,
) -> ReferenceCase:
    import torch

    prompt_ids = tokenizer(prompt_text, add_special_tokens=True)["input_ids"]
    input_tensor = torch.tensor([prompt_ids], dtype=torch.long, device=next(model.parameters()).device)
    attention_mask = torch.ones_like(input_tensor)

    kwargs: dict[str, Any] = {
        "max_new_tokens": max_new_tokens,
        "do_sample": do_sample,
        "pad_token_id": pad_token_id,
    }
    if do_sample:
        kwargs["temperature"] = temperature
        kwargs["top_p"] = top_p

    outputs = model.generate(input_ids=input_tensor, attention_mask=attention_mask, **kwargs)
    full_ids = [int(x) for x in outputs[0].tolist()]
    generated_ids = full_ids[len(prompt_ids) :]
    full_text = _safe_decode(tokenizer, full_ids)
    return ReferenceCase(
        case_id=case_id,
        family=family,
        source_kind=source_kind,
        prompt_text=prompt_text,
        full_text=full_text,
        generation_mode="sample" if do_sample else "greedy",
        prompt_token_count=len(prompt_ids),
        full_token_ids=full_ids,
        generated_token_ids=generated_ids,
        tokens=tokenizer.convert_ids_to_tokens(full_ids),
        metadata={
            "generated_char_count": len(full_text) - len(prompt_text),
            "full_char_count": len(full_text),
        },
    )


def _reference_case_payload(cases: list[ReferenceCase], args: argparse.Namespace) -> dict[str, Any]:
    return {
        "__meta__": {
            "created_at_utc": _utc_timestamp(),
            "versions": _load_versions(),
            "model_path": str(Path(args.model).resolve()),
            "seed": args.seed,
            "max_new_tokens": args.max_new_tokens,
            "do_sample": bool(args.do_sample),
            "temperature": args.temperature if args.do_sample else None,
            "top_p": args.top_p if args.do_sample else None,
        },
        "cases": [asdict(case) for case in cases],
    }


def _token_char_end_map(tokenizer, ids: list[int]) -> list[int]:
    ends: list[int] = []
    for i in range(1, len(ids) + 1):
        ends.append(len(_safe_decode(tokenizer, ids[:i])))
    return ends


def _pick_cut_positions(text: str, max_positions: int, min_cut: int) -> list[int]:
    if len(text) < 8 or min_cut >= len(text):
        return []

    positions: set[int] = set()
    target_chars = [" ", "\n", ".", ":", "(", ")", "[", "]", "_", "·", ",", ";"]
    for idx, ch in enumerate(text, start=1):
        if idx <= max(2, min_cut) or idx >= len(text):
            continue
        if ch in target_chars:
            positions.add(idx)
        prev = text[idx - 2]
        if prev in IDENT_CHARS and ch in IDENT_CHARS:
            positions.add(idx)

    if not positions:
        span = max(1, len(text) - min_cut)
        step = max(1, span // max_positions)
        positions.update(range(min_cut + step, len(text), step))

    ordered = sorted(positions)
    if len(ordered) <= max_positions:
        return ordered

    buckets: list[int] = []
    for i in range(max_positions):
        frac = (i + 0.5) / max_positions
        index = min(len(ordered) - 1, math.floor(frac * len(ordered)))
        buckets.append(ordered[index])
    return sorted(set(buckets))


def _cut_kind(text: str, cut: int) -> str:
    if cut <= 0 or cut >= len(text):
        return "edge"
    left = text[cut - 1]
    right = text[cut]
    if left == "\n":
        return "after_newline"
    if left in " \t":
        return "after_space"
    if left in IDENT_CHARS and right in IDENT_CHARS:
        return "inside_identifier"
    if right in IDENT_CHARS and left not in IDENT_CHARS:
        return "before_identifier"
    if left in "()[]{}:.,;<>":
        return "after_punctuation"
    return "other"


def _strip_suffix_while(text: str, predicate) -> str:
    end = len(text)
    while end > 0 and predicate(text[end - 1]):
        end -= 1
    return text[:end]


def _backtrack_identifier_fragment(text: str) -> str:
    end = len(text)
    while end > 0 and text[end - 1] in IDENT_CHARS:
        end -= 1
    return text[:end]


def _is_stable_prefix(text: str, tokenizer, probes: list[str]) -> bool:
    base_ids = tokenizer(text, add_special_tokens=False)["input_ids"]
    for probe in probes:
        probe_ids = tokenizer(text + probe, add_special_tokens=False)["input_ids"]
        if probe_ids[: len(base_ids)] != base_ids:
            return False
    return True


def _search_backward_for_stable(text: str, tokenizer, probes: list[str], max_backtrack: int) -> tuple[str, dict[str, Any]]:
    start = len(text)
    base_stable = _is_stable_prefix(text, tokenizer, probes)
    if base_stable:
        return text, {"base_stable": True, "backtracked_chars": 0, "stable_found": True}

    for distance in range(1, min(max_backtrack, len(text)) + 1):
        candidate = text[: start - distance]
        if _is_stable_prefix(candidate, tokenizer, probes):
            return candidate, {
                "base_stable": False,
                "backtracked_chars": distance,
                "stable_found": True,
            }
    return text, {
        "base_stable": False,
        "backtracked_chars": 0,
        "stable_found": False,
    }


def _search_backward_lexical_then_stable(
    text: str,
    tokenizer,
    probes: list[str],
    max_backtrack: int,
) -> tuple[str, dict[str, Any]]:
    trimmed = text
    while trimmed and trimmed[-1] in IDENT_CHARS:
        trimmed = trimmed[:-1]
    stable_text, meta = _search_backward_for_stable(trimmed, tokenizer, probes, max_backtrack)
    meta["lexical_trim_chars"] = len(text) - len(trimmed)
    return stable_text, meta


def _strategy_text(
    strategy: str,
    prefix_text: str,
    tokenizer,
    probes: list[str],
    max_backtrack: int,
) -> tuple[str, dict[str, Any]]:
    if strategy == "as_is":
        return prefix_text, {}
    if strategy == "rstrip_spaces":
        return prefix_text.rstrip(" "), {}
    if strategy == "rstrip_horizontal_ws":
        return _strip_suffix_while(prefix_text, lambda ch: ch in " \t"), {}
    if strategy == "rstrip_all_ws":
        return prefix_text.rstrip(), {}
    if strategy == "drop_identifier_fragment":
        return _backtrack_identifier_fragment(prefix_text), {}
    if strategy == "stable_probe":
        return _search_backward_for_stable(prefix_text, tokenizer, probes, max_backtrack)
    if strategy == "rstrip_all_ws_then_stable":
        trimmed = prefix_text.rstrip()
        recovered, meta = _search_backward_for_stable(trimmed, tokenizer, probes, max_backtrack)
        meta["trimmed_chars"] = len(prefix_text) - len(trimmed)
        return recovered, meta
    if strategy == "lexical_then_stable":
        return _search_backward_lexical_then_stable(prefix_text, tokenizer, probes, max_backtrack)
    if strategy == "adaptive_simple":
        stable = _is_stable_prefix(prefix_text, tokenizer, probes)
        if stable:
            return prefix_text, {"branch": "as_is", "base_stable": True}
        if prefix_text and prefix_text[-1] in " \t":
            return _strip_suffix_while(prefix_text, lambda ch: ch in " \t"), {"branch": "rstrip_horizontal_ws"}
        if prefix_text and prefix_text[-1] in IDENT_CHARS:
            return _backtrack_identifier_fragment(prefix_text), {"branch": "drop_identifier_fragment"}
        recovered, meta = _search_backward_for_stable(prefix_text, tokenizer, probes, max_backtrack)
        meta["branch"] = "stable_probe"
        return recovered, meta
    if strategy == "adaptive_stable":
        stable = _is_stable_prefix(prefix_text, tokenizer, probes)
        if stable:
            return prefix_text, {"branch": "as_is", "base_stable": True}
        if prefix_text and prefix_text[-1] in " \t":
            trimmed = _strip_suffix_while(prefix_text, lambda ch: ch in " \t")
            return trimmed, {"branch": "rstrip_horizontal_ws"}
        if prefix_text and prefix_text[-1] in IDENT_CHARS:
            recovered, meta = _search_backward_lexical_then_stable(prefix_text, tokenizer, probes, max_backtrack)
            meta["branch"] = "lexical_then_stable"
            return recovered, meta
        recovered, meta = _search_backward_for_stable(prefix_text, tokenizer, probes, max_backtrack)
        meta["branch"] = "stable_probe"
        return recovered, meta
    if strategy == "adaptive_lexical_first":
        if prefix_text and prefix_text[-1] in " \t":
            return _strip_suffix_while(prefix_text, lambda ch: ch in " \t"), {"branch": "rstrip_horizontal_ws"}
        if prefix_text and prefix_text[-1] in IDENT_CHARS:
            recovered, meta = _search_backward_lexical_then_stable(prefix_text, tokenizer, probes, max_backtrack)
            meta["branch"] = "lexical_then_stable"
            return recovered, meta
        stable = _is_stable_prefix(prefix_text, tokenizer, probes)
        if stable:
            return prefix_text, {"branch": "as_is", "base_stable": True}
        recovered, meta = _search_backward_for_stable(prefix_text, tokenizer, probes, max_backtrack)
        meta["branch"] = "stable_probe"
        return recovered, meta
    raise ValueError(f"Unsupported strategy: {strategy}")


def _strategy_names(strategy_set: str) -> list[str]:
    core = ["as_is", "rstrip_spaces", "rstrip_all_ws", "stable_probe", "lexical_then_stable"]
    if strategy_set == "core":
        return core
    return core + [
        "rstrip_horizontal_ws",
        "drop_identifier_fragment",
        "rstrip_all_ws_then_stable",
        "adaptive_simple",
        "adaptive_stable",
        "adaptive_lexical_first",
    ]


def _matching_prefix_length(left: list[int], right: list[int]) -> int:
    length = 0
    for a, b in zip(left, right):
        if a != b:
            break
        length += 1
    return length


def _oracle_prefix_for_visible_text(
    visible_text: str,
    token_char_ends: list[int],
    full_ids: list[int],
) -> tuple[list[int], int]:
    k = 0
    for char_end in token_char_ends:
        if char_end > len(visible_text):
            break
        k += 1
    return full_ids[:k], k


def _generate_from_prefix(prefix_ids: list[int], model, pad_token_id: int, max_new_tokens: int) -> list[int]:
    import torch

    device = next(model.parameters()).device
    input_tensor = torch.tensor([prefix_ids], dtype=torch.long, device=device)
    attention_mask = torch.ones_like(input_tensor)
    outputs = model.generate(
        input_ids=input_tensor,
        attention_mask=attention_mask,
        max_new_tokens=max_new_tokens,
        do_sample=False,
        pad_token_id=pad_token_id,
    )
    return [int(x) for x in outputs[0].tolist()[len(prefix_ids) :]]


def _evaluate_case(
    case: dict[str, Any],
    tokenizer,
    model,
    pad_token_id: int,
    max_cuts_per_case: int,
    max_new_tokens: int,
    max_backtrack: int,
    strategy_set: str,
    probes: list[str],
) -> dict[str, Any]:
    full_text = str(case["full_text"])
    full_ids = [int(x) for x in case["full_token_ids"]]
    token_char_ends = _token_char_end_map(tokenizer, full_ids)
    prompt_text = str(case["prompt_text"])
    cuts = _pick_cut_positions(full_text, max_cuts_per_case, len(prompt_text))

    case_result: dict[str, Any] = {
        "case_id": case["case_id"],
        "family": case["family"],
        "source_kind": case["source_kind"],
        "generation_mode": case["generation_mode"],
        "full_char_count": len(full_text),
        "full_token_count": len(full_ids),
        "cuts": [],
    }

    for cut in cuts:
        visible_text = full_text[:cut]
        oracle_prefix_ids, oracle_token_count = _oracle_prefix_for_visible_text(visible_text, token_char_ends, full_ids)
        oracle_suffix_ids = full_ids[oracle_token_count:]
        cut_record: dict[str, Any] = {
            "cut_char": cut,
            "cut_kind": _cut_kind(full_text, cut),
            "visible_tail": visible_text[-40:],
            "oracle_token_count": oracle_token_count,
            "oracle_visible_char_count": len(_safe_decode(tokenizer, oracle_prefix_ids)),
            "strategies": [],
        }

        for strategy in _strategy_names(strategy_set):
            recovered_text, strategy_meta = _strategy_text(strategy, visible_text, tokenizer, probes, max_backtrack)
            encoded_ids = tokenizer(recovered_text, add_special_tokens=True)["input_ids"]
            decoded_recovered_text = _safe_decode(tokenizer, encoded_ids)
            recovered_oracle_prefix_ids, recovered_oracle_token_count = _oracle_prefix_for_visible_text(
                decoded_recovered_text,
                token_char_ends,
                full_ids,
            )
            prefix_match_len = _matching_prefix_length(encoded_ids, recovered_oracle_prefix_ids)
            continuation_ids = _generate_from_prefix(encoded_ids, model, pad_token_id, max_new_tokens)
            strategy_oracle_continuation_ids = (
                continuation_ids
                if encoded_ids == recovered_oracle_prefix_ids
                else _generate_from_prefix(recovered_oracle_prefix_ids, model, pad_token_id, max_new_tokens)
            )
            reference_suffix = full_ids[len(recovered_oracle_prefix_ids) : len(recovered_oracle_prefix_ids) + max_new_tokens]
            continuation_match_len = _matching_prefix_length(continuation_ids, reference_suffix)
            oracle_match_len = _matching_prefix_length(continuation_ids, strategy_oracle_continuation_ids)
            cut_record["strategies"].append(
                {
                    "name": strategy,
                    "requested_visible_char_count": len(visible_text),
                    "recovered_visible_char_count": len(recovered_text),
                    "decoded_recovered_visible_char_count": len(decoded_recovered_text),
                    "backtracked_chars": len(visible_text) - len(recovered_text),
                    "encoded_prefix_token_count": len(encoded_ids),
                    "oracle_prefix_token_count": len(recovered_oracle_prefix_ids),
                    "prefix_ids_equal_oracle": encoded_ids == recovered_oracle_prefix_ids,
                    "prefix_match_token_count": prefix_match_len,
                    "continuation_match_token_count": continuation_match_len,
                    "continuation_match_fraction": (
                        continuation_match_len / len(reference_suffix) if reference_suffix else 1.0
                    ),
                    "reference_suffix_token_count": len(reference_suffix),
                    "oracle_continuation_match_token_count": oracle_match_len,
                    "oracle_continuation_match_fraction": (
                        oracle_match_len / len(strategy_oracle_continuation_ids)
                        if strategy_oracle_continuation_ids
                        else 1.0
                    ),
                    "oracle_continuation_token_count": len(strategy_oracle_continuation_ids),
                    "recovered_tail": recovered_text[-40:],
                    "decoded_recovered_tail": decoded_recovered_text[-40:],
                    "strategy_meta": strategy_meta,
                }
            )
        case_result["cuts"].append(cut_record)

    return case_result


def _summarize_sweep(payload: dict[str, Any]) -> str:
    cases = payload["cases"]
    lines: list[str] = []
    lines.append("# Recovery Sweep Summary")
    lines.append("")
    lines.append(f"- created_at_utc: {payload['__meta__']['created_at_utc']}")
    lines.append(f"- model_path: `{payload['__meta__']['model_path']}`")
    lines.append(f"- versions: `{json.dumps(payload['__meta__']['versions'], ensure_ascii=False)}`")
    lines.append(f"- case_count: {len(cases)}")
    lines.append("")

    strategy_stats: dict[str, dict[str, float]] = {}
    for case in cases:
        for cut in case["cuts"]:
            for strat in cut["strategies"]:
                stats = strategy_stats.setdefault(
                    strat["name"],
                    {
                        "count": 0.0,
                        "prefix_exact": 0.0,
                        "oracle_cont_match_1": 0.0,
                        "oracle_cont_match_4": 0.0,
                        "oracle_cont_match_all": 0.0,
                        "ref_cont_match_all": 0.0,
                        "avg_backtrack": 0.0,
                    },
                )
                stats["count"] += 1
                stats["avg_backtrack"] += strat["backtracked_chars"]
                if strat["prefix_ids_equal_oracle"]:
                    stats["prefix_exact"] += 1
                if strat["oracle_continuation_match_token_count"] >= 1:
                    stats["oracle_cont_match_1"] += 1
                if strat["oracle_continuation_match_token_count"] >= min(4, strat["oracle_continuation_token_count"]):
                    stats["oracle_cont_match_4"] += 1
                if strat["oracle_continuation_match_token_count"] == strat["oracle_continuation_token_count"]:
                    stats["oracle_cont_match_all"] += 1
                if strat["continuation_match_token_count"] == strat["reference_suffix_token_count"]:
                    stats["ref_cont_match_all"] += 1

    lines.append("## Aggregate")
    lines.append("")
    for name in sorted(strategy_stats):
        stats = strategy_stats[name]
        count = max(stats["count"], 1.0)
        lines.append(
            f"- `{name}`: prefix_exact={stats['prefix_exact']/count:.3f}, "
            f"oracle_cont@1={stats['oracle_cont_match_1']/count:.3f}, "
            f"oracle_cont@4={stats['oracle_cont_match_4']/count:.3f}, "
            f"oracle_cont_all={stats['oracle_cont_match_all']/count:.3f}, "
            f"ref_cont_all={stats['ref_cont_match_all']/count:.3f}, "
            f"avg_backtrack={stats['avg_backtrack']/count:.2f}"
        )
    lines.append("")

    return "\n".join(lines) + "\n"


def _run_build_cases(args: argparse.Namespace) -> Path:
    import torch

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    tokenizer = _load_tokenizer(args.model)
    model = _load_model(args.model)
    pad_token_id = _ensure_pad_token(tokenizer)

    prompt_entries = _load_msc_prompt_entries(args.sample_prompts)
    slot_entries = _load_slot_prefix_entries(args.sample_slots)

    cases: list[ReferenceCase] = []
    for key, prompt_text in prompt_entries:
        cases.append(
            _generate_reference(
                case_id=f"msc_prompt::{key}",
                family="msc_prompt",
                source_kind=key,
                prompt_text=prompt_text,
                tokenizer=tokenizer,
                model=model,
                pad_token_id=pad_token_id,
                max_new_tokens=args.max_new_tokens,
                do_sample=args.do_sample,
                temperature=args.temperature,
                top_p=args.top_p,
            )
        )

    for key, prompt_text in slot_entries:
        cases.append(
            _generate_reference(
                case_id=f"continuation_slot::{key}",
                family="continuation_slot",
                source_kind=key,
                prompt_text=prompt_text,
                tokenizer=tokenizer,
                model=model,
                pad_token_id=pad_token_id,
                max_new_tokens=args.max_new_tokens,
                do_sample=args.do_sample,
                temperature=args.temperature,
                top_p=args.top_p,
            )
        )

    cases.append(
        _generate_reference(
            case_id="manual_preset::mathd_algebra_10",
            family="manual_preset",
            source_kind="mathd_algebra_10",
            prompt_text=_manual_preset_prompt(),
            tokenizer=tokenizer,
            model=model,
            pad_token_id=pad_token_id,
            max_new_tokens=args.max_new_tokens,
            do_sample=args.do_sample,
            temperature=args.temperature,
            top_p=args.top_p,
        )
    )

    output_path = OUTPUTS_DIR / args.output_name
    _save_json(_reference_case_payload(cases, args), output_path)
    return output_path


def _run_sweep_cuts(args: argparse.Namespace) -> Path:
    import torch

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    tokenizer = _load_tokenizer(args.model)
    model = _load_model(args.model)
    pad_token_id = _ensure_pad_token(tokenizer)

    reference_payload = _load_json(args.reference_json)
    cases = reference_payload["cases"]
    probes = args.probes or list(DEFAULT_PROBES)

    result = {
        "__meta__": {
            "created_at_utc": _utc_timestamp(),
            "versions": _load_versions(),
            "model_path": str(Path(args.model).resolve()),
            "source_reference_json": str(args.reference_json.resolve()),
            "seed": args.seed,
            "max_cuts_per_case": args.max_cuts_per_case,
            "max_new_tokens": args.max_new_tokens,
            "max_backtrack": args.max_backtrack,
            "strategy_set": args.strategy_set,
            "probes": probes,
        },
        "cases": [],
    }

    for case in cases:
        result["cases"].append(
            _evaluate_case(
                case=case,
                tokenizer=tokenizer,
                model=model,
                pad_token_id=pad_token_id,
                max_cuts_per_case=args.max_cuts_per_case,
                max_new_tokens=args.max_new_tokens,
                max_backtrack=args.max_backtrack,
                strategy_set=args.strategy_set,
                probes=probes,
            )
        )

    output_path = OUTPUTS_DIR / args.output_name
    _save_json(result, output_path)
    return output_path


def _run_summarize(args: argparse.Namespace) -> Path:
    payload = _load_json(args.sweep_json)
    summary = _summarize_sweep(payload)
    output_path = OUTPUTS_DIR / args.output_name
    _save_text(summary, output_path)
    return output_path


def main() -> int:
    _require_supported_transformers()
    args = _parse_args()
    if args.command == "build-cases":
        output_path = _run_build_cases(args)
    elif args.command == "sweep-cuts":
        output_path = _run_sweep_cuts(args)
    elif args.command == "summarize":
        output_path = _run_summarize(args)
    else:
        raise ValueError(f"Unsupported command: {args.command}")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
