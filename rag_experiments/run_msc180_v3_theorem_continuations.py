#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.problem_structure import Attempt, TheoremProcessor
from src.prover_generation.artifacts import load_artifacts
from src.prover_generation.generation_params import GenerationParams


EXPERIMENT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = EXPERIMENT_DIR / "outputs"

DATE_PREFIX = "20260306"
DEFAULT_SOURCE_OUTPUT = (
    EXPERIMENT_DIR / "outputs" / "20260301_msc180-v2_deepseekv2_7b_lean4-15_verified.json"
)
DEFAULT_THEOREM_INDEX = EXPERIMENT_DIR / "data" / "mathlib_theorem_name_index.json"

MODEL_CONFIGS = {
    "deepseek": {
        "model_id": "deepseek-ai/DeepSeek-Prover-V2-7B",
        "suffix": "deepseekv2_7b",
        "micro_batch_size": 8,
    }
}

ATTEMPTS_PER_SLOT = 8
TEMPERATURE = 1.0
TOP_P = 0.95
MAX_NEW_TOKENS = 24
EXPECTED_SLOT_COUNT = 95
RUN_SCHEMA_VERSION = 2
RUN_METADATA_KEY = "__meta__"

USABLE_SOURCE_KEYS = {
    "no-hint/MSC-180_08_002",
    "no-hint/MSC-180_14_001",
    "no-hint/MSC-180_20_001",
    "no-hint/MSC-180_26_002",
    "no-hint/MSC-180_68_002",
    "theorem-statements/MSC-180_08_002",
    "theorem-statements/MSC-180_08_003",
    "theorem-statements/MSC-180_14_001",
    "theorem-statements/MSC-180_20_001",
    "theorem-statements/MSC-180_26_002",
    "theorem-statements/MSC-180_65_001",
    "theorem-statements-and-examples/MSC-180_05_003",
    "theorem-statements-and-examples/MSC-180_08_002",
    "theorem-statements-and-examples/MSC-180_14_001",
    "theorem-statements-and-examples/MSC-180_20_001",
    "theorem-statements-and-examples/MSC-180_26_002",
    "theorem-statements-and-examples/MSC-180_60_002",
    "theorem-statements-and-examples/MSC-180_68_002",
}

IDENTIFIER_RE = re.compile(r"\b[A-Za-z][A-Za-z0-9_']*(?:\.[A-Za-z][A-Za-z0-9_']*)*\b")
COMMENT_LINE_RE = re.compile(r"--.*$")


@dataclass(frozen=True)
class Slot:
    slot_key: str
    source_key: str
    source_attempt_index: int
    target_full_name: str
    target_token: str
    token_count_in_attempt: int
    prompt_prefix: str
    prompt_token_ids: tuple[int, ...]
    prompt_cut_char: int
    actual_prompt_char_end: int


class TheoremIndex:
    def __init__(self, *, full_names: set[str], short_to_full: dict[str, set[str]]):
        self.full_names = full_names
        self.short_to_full = short_to_full

    @classmethod
    def load(cls, path: Path) -> "TheoremIndex":
        if path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise TypeError(f"Compact theorem index must be a JSON object: {path}")
            raw_full = payload.get("full_names")
            raw_unique = payload.get("unique_short_to_full")
            if not isinstance(raw_full, list) or not isinstance(raw_unique, dict):
                raise TypeError(f"Compact theorem index missing required keys: {path}")
            full_names = {str(x) for x in raw_full}
            short_to_full = {str(k): {str(v)} for k, v in raw_unique.items()}
            return cls(full_names=full_names, short_to_full=short_to_full)

        full_names: set[str] = set()
        short_to_full: dict[str, set[str]] = {}
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                obj = json.loads(line)
                full_name = str(obj["full_name"])
                short_name = str(obj["short_name"])
                full_names.add(full_name)
                short_to_full.setdefault(short_name, set()).add(full_name)
        return cls(full_names=full_names, short_to_full=short_to_full)

    def resolve(self, token: str) -> tuple[str | None, str]:
        if token in self.full_names:
            return token, "full"
        matches = self.short_to_full.get(token)
        if not matches:
            return None, "missing"
        if len(matches) == 1:
            return next(iter(matches)), "short_unique"
        return None, "short_ambiguous"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Probe theorem-name continuations by cutting successful non-CoT MSC-180 outputs "
            "immediately before a Mathlib theorem occurrence."
        )
    )
    parser.add_argument("mode", help="Only 'deepseek' is currently supported.")
    parser.add_argument(
        "--source-output",
        type=Path,
        default=DEFAULT_SOURCE_OUTPUT,
        help="Verified non-CoT source output JSON used to build the 95 continuation slots.",
    )
    parser.add_argument(
        "--theorem-index",
        type=Path,
        default=DEFAULT_THEOREM_INDEX,
        help="Path to the theorem-only Mathlib index (compact JSON or JSONL).",
    )
    parser.add_argument(
        "--attempts-per-slot",
        type=int,
        default=ATTEMPTS_PER_SLOT,
        help="Number of continuation samples to draw for each slot.",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=MAX_NEW_TOKENS,
        help="Short continuation budget for each probe.",
    )
    parser.add_argument(
        "--micro-batch-size",
        type=int,
        help="Optional override for repeated-sample batch size.",
    )
    parser.add_argument(
        "--output-name",
        help="Optional output filename inside rag_experiments/outputs.",
    )
    parser.add_argument(
        "--max-slots",
        type=int,
        help="Optional cap for smoke tests.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _required_attempt_message_keys() -> set[str]:
    return {
        "source_key",
        "source_attempt_index",
        "target_token",
        "target_full_name",
        "first_identifier",
        "prompt_prefix_length",
        "prompt_token_count",
        "prompt_cut_char",
        "actual_prompt_char_end",
        "cut_char_aligned",
        "classification",
        "resolved_full_name",
        "resolution",
    }


def _build_run_metadata(
    *,
    model_id: str,
    source_output: Path,
    theorem_index: Path,
    attempts_per_slot: int,
    max_new_tokens: int,
    micro_batch_size: int,
) -> dict[str, object]:
    return {
        "schema_version": RUN_SCHEMA_VERSION,
        "model_id": model_id,
        "source_output": str(source_output.resolve()),
        "theorem_index": str(theorem_index.resolve()),
        "attempts_per_slot": attempts_per_slot,
        "max_new_tokens": max_new_tokens,
        "micro_batch_size": micro_batch_size,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "expected_slot_count": EXPECTED_SLOT_COUNT,
    }


def _validate_existing_payload(payload: dict, expected_meta: dict[str, object], output_path: Path) -> None:
    existing_meta = payload.get(RUN_METADATA_KEY)
    if not isinstance(existing_meta, dict):
        raise ValueError(
            f"Existing output at {output_path} is legacy or incomplete. "
            "Use a fresh --output-name or remove the file before rerunning."
        )

    if existing_meta != expected_meta:
        raise ValueError(
            f"Existing output at {output_path} was created with different run settings. "
            "Use a fresh --output-name or remove the file before rerunning."
        )

    required_keys = _required_attempt_message_keys()
    for slot_key, entry in payload.items():
        if slot_key == RUN_METADATA_KEY:
            continue
        if not isinstance(entry, dict):
            continue
        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            continue
        for attempt_index, attempt in enumerate(attempts):
            if not isinstance(attempt, dict):
                raise TypeError(f"Attempt {attempt_index} of '{slot_key}' must be a JSON object.")
            message = attempt.get("message")
            if not isinstance(message, dict):
                raise ValueError(
                    f"Attempt {attempt_index} of '{slot_key}' is missing continuation metadata. "
                    "Use a fresh --output-name or remove the file before rerunning."
                )
            missing = sorted(required_keys - set(message))
            if missing:
                raise ValueError(
                    f"Attempt {attempt_index} of '{slot_key}' is missing required metadata keys: "
                    f"{', '.join(missing)}. Use a fresh --output-name or remove the file before rerunning."
                )


def _mask_comment_text(text: str) -> str:
    masked_lines: list[str] = []
    for line in text.splitlines():
        m = COMMENT_LINE_RE.search(line)
        if m is None:
            masked_lines.append(line)
            continue
        start = m.start()
        masked_lines.append(line[:start] + (" " * (len(line) - start)))
    return "\n".join(masked_lines)


def _body_after_by(proof: str) -> tuple[int, str]:
    marker = ":= by"
    idx = proof.find(marker)
    if idx == -1:
        raise ValueError("Parsed proof does not contain ':= by'.")
    body_start = idx + len(marker)
    return body_start, proof[body_start:]


def _is_plausible_theorem_token(token: str) -> bool:
    if "." in token:
        return True
    if "_" not in token:
        return False
    if token.startswith("h_"):
        return False
    if token in {
        "h_main",
        "h_surj",
        "h_field",
        "h_forward",
        "h_backward",
        "h_exponent_exists",
        "h_exponent_eq",
    }:
        return False
    return True


def _iter_resolved_theorem_tokens(body: str, theorem_index: TheoremIndex) -> Iterable[tuple[int, int, str, str]]:
    for match in IDENTIFIER_RE.finditer(body):
        token = match.group(0)
        if not _is_plausible_theorem_token(token):
            continue
        full_name, resolution = theorem_index.resolve(token)
        if full_name is None or resolution == "short_ambiguous":
            continue
        yield match.start(), match.end(), token, full_name


def _find_parsed_proof_in_raw_output(raw_output: str, parsed_proof: str) -> int:
    idx = raw_output.rfind(parsed_proof)
    if idx == -1:
        raise ValueError("Could not locate parsed_proof inside raw_output.")
    return idx


def _build_slot_key(source_key: str, attempt_index: int, target_token: str, ordinal: int) -> str:
    return f"{source_key}::attempt{attempt_index}::slot{ordinal:02d}::{target_token}"


def _tokenize_prompt_prefix(prompt_prefix: str, tokenizer) -> tuple[int, ...]:
    encoded = tokenizer(
        prompt_prefix,
        add_special_tokens=True,
    )
    input_ids = tuple(int(x) for x in encoded["input_ids"])
    if not input_ids:
        raise ValueError("Prompt prefix tokenization produced no input ids.")
    return input_ids


def _build_slots(payload: dict, theorem_index: TheoremIndex, tokenizer) -> list[Slot]:
    slots: list[Slot] = []

    for source_key in sorted(USABLE_SOURCE_KEYS):
        entry = payload.get(source_key)
        if not isinstance(entry, dict):
            raise KeyError(f"Missing source key in output JSON: {source_key}")

        attempts = entry.get("attempts")
        if not isinstance(attempts, list):
            continue

        for attempt_index, attempt in enumerate(attempts):
            if not isinstance(attempt, dict) or not bool(attempt.get("success")):
                continue

            raw_output = str(attempt.get("raw_output", ""))
            parsed_proof = str(attempt.get("parsed_proof", ""))
            if not raw_output.strip() or not parsed_proof.strip():
                continue

            body_offset, body = _body_after_by(parsed_proof)
            masked_body = _mask_comment_text(body)

            seen_full_names: set[str] = set()
            ordinal = 0
            proof_start = _find_parsed_proof_in_raw_output(raw_output, parsed_proof)

            for token_start, _token_end, token, full_name in _iter_resolved_theorem_tokens(masked_body, theorem_index):
                if full_name in seen_full_names:
                    continue
                seen_full_names.add(full_name)

                prompt_cut = proof_start + body_offset + token_start
                prompt_prefix = raw_output[:prompt_cut]
                prompt_token_ids = _tokenize_prompt_prefix(prompt_prefix, tokenizer)
                actual_prompt_char_end = prompt_cut
                if not prompt_prefix:
                    raise ValueError(f"Empty prompt prefix for {source_key} attempt {attempt_index}")

                ordinal += 1
                slots.append(
                    Slot(
                        slot_key=_build_slot_key(source_key, attempt_index, token, ordinal),
                        source_key=source_key,
                        source_attempt_index=attempt_index,
                        target_full_name=full_name,
                        target_token=token,
                        token_count_in_attempt=ordinal,
                        prompt_prefix=prompt_prefix,
                        prompt_token_ids=prompt_token_ids,
                        prompt_cut_char=prompt_cut,
                        actual_prompt_char_end=actual_prompt_char_end,
                    )
                )

    if len(slots) != EXPECTED_SLOT_COUNT:
        raise ValueError(f"Expected {EXPECTED_SLOT_COUNT} slots, found {len(slots)}")
    return slots


def _generate_suffix_batch(prefix_token_ids: tuple[int, ...], batch_size: int, model, tokenizer, params: GenerationParams) -> list[str]:
    import torch

    if batch_size <= 0:
        return []
    if not prefix_token_ids:
        raise ValueError("prefix_token_ids must be non-empty.")

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    pad_token_id = tokenizer.pad_token_id
    target_device = torch.device("cuda")

    input_ids = torch.tensor([list(prefix_token_ids)] * batch_size, dtype=torch.long, device=target_device)
    attention_mask = torch.ones_like(input_ids, device=target_device)

    outputs = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        do_sample=True,
        temperature=params.temperature,
        top_p=params.top_p,
        max_new_tokens=params.max_new_tokens,
        pad_token_id=pad_token_id,
    )

    prefix_len = input_ids.shape[1]
    suffixes: list[str] = []
    for idx in range(outputs.size(0)):
        generated = outputs[idx, prefix_len:]
        suffixes.append(tokenizer.decode(generated, skip_special_tokens=True))
    return suffixes


def _first_theorem_like_identifier(text: str) -> str | None:
    for match in IDENTIFIER_RE.finditer(text):
        token = match.group(0)
        if _is_plausible_theorem_token(token):
            return token
    return None


def _classify_identifier(
    *,
    first_identifier: str | None,
    target_full_name: str,
    target_token: str,
    theorem_index: TheoremIndex,
) -> dict[str, object]:
    if first_identifier is None:
        return {
            "classification": "no_theorem_like_identifier",
            "resolved_full_name": None,
            "resolution": "missing",
        }

    resolved_full_name, resolution = theorem_index.resolve(first_identifier)
    if resolved_full_name == target_full_name:
        return {
            "classification": "exact_match",
            "resolved_full_name": resolved_full_name,
            "resolution": resolution,
        }
    if resolved_full_name is not None:
        return {
            "classification": "other_valid_mathlib_theorem",
            "resolved_full_name": resolved_full_name,
            "resolution": resolution,
        }
    if target_token.startswith(first_identifier) or target_full_name.startswith(first_identifier):
        return {
            "classification": "incomplete_identifier",
            "resolved_full_name": None,
            "resolution": resolution,
        }
    return {
        "classification": "hallucinated_theorem_like_name",
        "resolved_full_name": None,
        "resolution": resolution,
    }


def _metadata_json(slot: Slot) -> str:
    return json.dumps(
        {
            "source_key": slot.source_key,
            "source_attempt_index": slot.source_attempt_index,
            "target_token": slot.target_token,
            "target_full_name": slot.target_full_name,
            "prompt_cut_char": slot.prompt_cut_char,
            "actual_prompt_char_end": slot.actual_prompt_char_end,
            "prompt_token_count": len(slot.prompt_token_ids),
            "cut_char_aligned": slot.actual_prompt_char_end == slot.prompt_cut_char,
        },
        ensure_ascii=False,
    )


def _make_processor(slot: Slot) -> TheoremProcessor:
    return TheoremProcessor(
        formal_statement=slot.target_full_name,
        header=slot.source_key,
        informal_statement=_metadata_json(slot),
        nl_proof=slot.prompt_prefix,
    )


def main() -> int:
    args = _parse_args()
    mode = args.mode.strip().lower()
    cfg = MODEL_CONFIGS.get(mode)
    if cfg is None:
        raise SystemExit("Mode must be: deepseek")

    if not args.source_output.exists():
        raise FileNotFoundError(f"Source output file not found: {args.source_output}")
    if not args.theorem_index.exists():
        raise FileNotFoundError(f"Theorem index not found: {args.theorem_index}")
    if args.attempts_per_slot <= 0:
        raise ValueError("--attempts-per-slot must be positive")
    if args.max_new_tokens <= 0:
        raise ValueError("--max-new-tokens must be positive")

    micro_batch_size = args.micro_batch_size or cfg["micro_batch_size"]
    if micro_batch_size <= 0:
        raise ValueError("--micro-batch-size must be positive")
    params = GenerationParams(
        micro_batch_size=micro_batch_size,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_new_tokens=args.max_new_tokens,
    )
    run_metadata = _build_run_metadata(
        model_id=cfg["model_id"],
        source_output=args.source_output,
        theorem_index=args.theorem_index,
        attempts_per_slot=args.attempts_per_slot,
        max_new_tokens=args.max_new_tokens,
        micro_batch_size=micro_batch_size,
    )

    output_name = args.output_name or f"{DATE_PREFIX}_msc180-v3-theorem-continuations_{cfg['suffix']}_lean4-15.json"
    output_path = OUTPUT_DIR / output_name
    existing_payload: dict[str, object] = {}
    if output_path.exists():
        loaded = _load_json(output_path)
        if not isinstance(loaded, dict):
            raise TypeError(f"Existing output must be a JSON object: {output_path}")
        _validate_existing_payload(loaded, run_metadata, output_path)
        existing_payload = loaded
        print(f"Resuming existing output: {output_path} ({max(len(existing_payload) - 1, 0)} entries)")
    else:
        existing_payload[RUN_METADATA_KEY] = run_metadata

    existing_payload[RUN_METADATA_KEY] = run_metadata

    model, tokenizer = load_artifacts(cfg["model_id"])
    theorem_index = TheoremIndex.load(args.theorem_index)
    source_payload = _load_json(args.source_output)
    slots = _build_slots(source_payload, theorem_index, tokenizer)
    if args.max_slots is not None:
        slots = slots[: args.max_slots]


    total_slots = len(slots)
    for index, slot in enumerate(slots, start=1):
        print(f"[{index}/{total_slots}] {slot.slot_key}")
        processor = _make_processor(slot)

        existing = existing_payload.get(slot.slot_key)
        existing_attempts: list[Attempt] = []
        if isinstance(existing, dict):
            prior_attempts = existing.get("attempts")
            if isinstance(prior_attempts, list):
                existing_attempts = [Attempt.from_dict(x) for x in prior_attempts]
                for attempt in existing_attempts:
                    processor.add_attempt(attempt)

        if len(existing_attempts) >= args.attempts_per_slot:
            print(f"  skip: already {len(existing_attempts)}/{args.attempts_per_slot}")
            existing_payload[slot.slot_key] = processor.to_dict()
            continue

        remaining = args.attempts_per_slot - len(existing_attempts)
        continuations: list[str] = []
        generation_time = 0.0
        while len(continuations) < remaining:
            batch_size = min(remaining - len(continuations), params.micro_batch_size)
            generation_start = time.time()
            batch_continuations = _generate_suffix_batch(slot.prompt_token_ids, batch_size, model, tokenizer, params)
            generation_time += time.time() - generation_start
            continuations.extend(batch_continuations)
        average_generation_time = generation_time / len(continuations) if continuations else 0.0

        for continuation in continuations:
            raw_output = slot.prompt_prefix + continuation
            first_identifier = _first_theorem_like_identifier(continuation)
            classification = _classify_identifier(
                first_identifier=first_identifier,
                target_full_name=slot.target_full_name,
                target_token=slot.target_token,
                theorem_index=theorem_index,
            )
            message = {
                "source_key": slot.source_key,
                "source_attempt_index": slot.source_attempt_index,
                "target_token": slot.target_token,
                "target_full_name": slot.target_full_name,
                "first_identifier": first_identifier,
                "prompt_prefix_length": len(slot.prompt_prefix),
                "prompt_token_count": len(slot.prompt_token_ids),
                "prompt_cut_char": slot.prompt_cut_char,
                "actual_prompt_char_end": slot.actual_prompt_char_end,
                "cut_char_aligned": slot.actual_prompt_char_end == slot.prompt_cut_char,
                **classification,
            }
            attempt = Attempt(
                success=classification["classification"] == "exact_match",
                raw_output=raw_output,
                parsed_proof=continuation,
                message=message,
                generation_time=average_generation_time,
                verification_time=0.0,
            )
            processor.add_attempt(attempt)

        existing_payload[slot.slot_key] = processor.to_dict()
        _save_json(existing_payload, output_path)
        print(f"  stored {processor.count_attempts()}/{args.attempts_per_slot}")

    print(f"Wrote continuation probes to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
