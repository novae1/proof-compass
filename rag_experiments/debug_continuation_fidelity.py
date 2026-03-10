#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prompt_hints.prompt_config import DeepSeekProverV2HintNonCoTPromptConfig
from src.prover_generation.prompt_config import DeepSeekProverV2CoTPromptConfig


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "debug_runs"
DEFAULT_MODEL = "deepseek-ai/DeepSeek-Prover-V2-7B"
SCHEMA_VERSION = 1
SUPPORTED_TRANSFORMERS_VERSION = "4.57.6"
ALLOW_UNSUPPORTED_ENV_VAR = "PROOF_COMPASS_ALLOW_UNSUPPORTED_TRANSFORMERS"

MSC_SPEC_PATHS = {
    "no-hint": SCRIPT_DIR / "specs" / "msc180_v2_A_spec.json",
    "theorem-statements": SCRIPT_DIR / "specs" / "msc180_v2_B_spec.json",
    "theorem-statements-and-examples": SCRIPT_DIR / "specs" / "msc180_v2_C_spec.json",
}

PROMPT_PRESETS: dict[str, dict[str, str]] = {
    "mathd_algebra_10": {
        "header": (
            "import Mathlib\n"
            "import Aesop\n\n"
            "set_option maxHeartbeats 0\n\n"
            "open BigOperators Real Nat Topology Rat"
        ),
        "formal_statement": (
            "/-- What is the positive difference between $120\\%$ of 30 and $130\\%$ of 20? "
            "Show that it is 10.-/\n"
            "theorem mathd_algebra_10 : "
            "abs ((120 : \\u211d) / 100 * 30 - 130 / 100 * 20) = 10 := by\n"
            "  sorry"
        ),
        "theorem_hint": "",
    }
}

PROMPT_BUILDERS = {
    "deepseek_noncot": DeepSeekProverV2HintNonCoTPromptConfig,
    "deepseek_cot": DeepSeekProverV2CoTPromptConfig,
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Standalone continuation-fidelity harness for DeepSeek Prover V2. "
            "It can inspect tokenizer behavior, generate from a prompt, and test "
            "continuations from truncated generations."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Build a prompt and inspect tokenizer encodings without loading the model.",
    )
    _add_source_args(inspect_parser)
    inspect_parser.add_argument(
        "--encoding-path",
        choices=["plain", "chat", "both"],
        default="both",
        help="Which prompt-encoding path(s) to inspect.",
    )
    inspect_parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model id or local model path.",
    )
    inspect_parser.add_argument(
        "--output-name",
        help="Optional output filename inside rag_experiments/debug_runs.",
    )

    generate_parser = subparsers.add_parser(
        "generate",
        help="Generate completions from one prompt encoding path or both paths.",
    )
    _add_source_args(generate_parser)
    generate_parser.add_argument(
        "--encoding-path",
        choices=["plain", "chat", "both"],
        default="plain",
        help="Which prompt-encoding path(s) to generate from.",
    )
    generate_parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model id or local model path.",
    )
    generate_parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=64,
        help="Generation length.",
    )
    generate_parser.add_argument(
        "--num-return-sequences",
        type=int,
        default=1,
        help="How many samples to draw per encoding path.",
    )
    generate_parser.add_argument(
        "--do-sample",
        action="store_true",
        help="Enable sampling. Greedy decoding is used by default.",
    )
    generate_parser.add_argument(
        "--temperature",
        type=float,
        default=1.0,
        help="Sampling temperature when --do-sample is set.",
    )
    generate_parser.add_argument(
        "--top-p",
        type=float,
        default=0.95,
        help="Top-p when --do-sample is set.",
    )
    generate_parser.add_argument(
        "--seed",
        type=int,
        help="Optional torch random seed.",
    )
    generate_parser.add_argument(
        "--output-name",
        help="Optional output filename inside rag_experiments/debug_runs.",
    )

    continue_parser = subparsers.add_parser(
        "continue",
        help="Continue from a truncated earlier generation artifact.",
    )
    continue_parser.add_argument(
        "artifact_json",
        type=Path,
        help="Path to a generation artifact created by this harness.",
    )
    continue_parser.add_argument(
        "--generation-index",
        type=int,
        default=0,
        help="Which generation entry inside the artifact to continue from.",
    )
    cut_group = continue_parser.add_mutually_exclusive_group(required=True)
    cut_group.add_argument(
        "--cut-total-token-count",
        type=int,
        help="Absolute prefix length in tokens within the saved full output ids.",
    )
    cut_group.add_argument(
        "--cut-generated-token-count",
        type=int,
        help="Prefix length measured only within generated tokens after the prompt.",
    )
    continue_parser.add_argument(
        "--variants",
        nargs="+",
        choices=["exact_prefix_ids", "retokenized_same_path"],
        default=["exact_prefix_ids", "retokenized_same_path"],
        help="Which continuation variants to run.",
    )
    continue_parser.add_argument(
        "--max-new-tokens",
        type=int,
        help="Override continuation length. Defaults to the remaining reference suffix length.",
    )
    continue_parser.add_argument(
        "--do-sample",
        action="store_true",
        help="Override the source generation config and sample instead of using greedy decoding.",
    )
    continue_parser.add_argument(
        "--temperature",
        type=float,
        default=1.0,
        help="Sampling temperature when --do-sample is set.",
    )
    continue_parser.add_argument(
        "--top-p",
        type=float,
        default=0.95,
        help="Top-p when --do-sample is set.",
    )
    continue_parser.add_argument(
        "--seed",
        type=int,
        help="Optional torch random seed.",
    )
    continue_parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Model id or local model path.",
    )
    continue_parser.add_argument(
        "--output-name",
        help="Optional output filename inside rag_experiments/debug_runs.",
    )

    return parser.parse_args()


def _add_source_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--prompt-file",
        type=Path,
        help="Path to a file containing the full prompt text to use as-is.",
    )
    group.add_argument(
        "--slot-json",
        type=Path,
        help="Path to a continuation-slot JSON file; prompt text is read from entry.nl_proof.",
    )
    group.add_argument(
        "--msc-key",
        help="MSC problem key such as 'MSC-180/08_002'; requires --msc-condition.",
    )
    group.add_argument(
        "--preset",
        choices=sorted(PROMPT_PRESETS),
        help="Built-in prompt preset.",
    )
    parser.add_argument(
        "--slot-key",
        help="Slot key inside --slot-json.",
    )
    parser.add_argument(
        "--msc-condition",
        choices=sorted(MSC_SPEC_PATHS),
        help="MSC prompt family to load from specs.",
    )
    parser.add_argument(
        "--builder",
        choices=sorted(PROMPT_BUILDERS),
        default="deepseek_noncot",
        help="Prompt builder used for preset/spec inputs.",
    )


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _save_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _date_prefix() -> str:
    return time.strftime("%Y%m%d", time.gmtime())


def _slug(text: str) -> str:
    chars: list[str] = []
    last_dash = False
    for ch in text.lower():
        if ch.isalnum():
            chars.append(ch)
            last_dash = False
            continue
        if not last_dash:
            chars.append("-")
            last_dash = True
    slug = "".join(chars).strip("-")
    return slug or "debug"


def _output_path(output_name: str | None, default_stem: str) -> Path:
    if output_name:
        return OUTPUT_DIR / output_name
    filename = f"{_date_prefix()}_{default_stem}.json"
    return OUTPUT_DIR / filename


def _models_root() -> Path:
    return ROOT / "models"


def _resolve_model(model_ref: str) -> tuple[str, Path]:
    raw = model_ref.strip()
    if not raw:
        raise ValueError("model_ref must be non-empty.")

    direct_path = Path(raw)
    if direct_path.exists():
        return raw, direct_path.resolve()

    if "/" in raw:
        candidate = _models_root() / raw
        if candidate.exists():
            return raw, candidate.resolve()

    matches = sorted(_models_root().glob(f"*/{raw}"))
    if len(matches) == 1:
        match = matches[0]
        return f"{match.parent.name}/{match.name}", match.resolve()

    raise FileNotFoundError(
        f"Could not resolve model '{model_ref}'. "
        f"Pass a local path, 'org/name', or a unique basename present under {_models_root()}."
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


def _require_supported_transformers() -> None:
    import os
    import transformers

    version = str(transformers.__version__)
    if os.environ.get(ALLOW_UNSUPPORTED_ENV_VAR) == "1":
        return
    if version != SUPPORTED_TRANSFORMERS_VERSION:
        raise SystemExit(
            "Continuation debug harness requires "
            f"transformers=={SUPPORTED_TRANSFORMERS_VERSION}; found {version}. "
            "Use .venv/bin/python after running ./init.sh, or set "
            f"{ALLOW_UNSUPPORTED_ENV_VAR}=1 to bypass this check."
        )


def _load_tokenizer(model_path: Path):
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)


def _selected_paths(choice: str) -> list[str]:
    if choice == "both":
        return ["plain", "chat"]
    return [choice]


def _normalize_ids(maybe_ids: Any) -> list[int]:
    if isinstance(maybe_ids, Mapping):
        if "input_ids" not in maybe_ids:
            raise ValueError("Expected an 'input_ids' key in the encoded prompt payload.")
        maybe_ids = maybe_ids["input_ids"]
    if hasattr(maybe_ids, "tolist"):
        maybe_ids = maybe_ids.tolist()
    if isinstance(maybe_ids, list) and maybe_ids and isinstance(maybe_ids[0], list):
        if len(maybe_ids) != 1:
            raise ValueError("Expected a single encoded prompt, but received a batch.")
        maybe_ids = maybe_ids[0]
    return [int(x) for x in maybe_ids]


def _safe_decode(tokenizer, ids: list[int], *, skip_special_tokens: bool, clean_up_tokenization_spaces: bool | None) -> str:
    kwargs: dict[str, Any] = {"skip_special_tokens": skip_special_tokens}
    if clean_up_tokenization_spaces is not None:
        kwargs["clean_up_tokenization_spaces"] = clean_up_tokenization_spaces
    try:
        return str(tokenizer.decode(ids, **kwargs))
    except TypeError:
        return str(tokenizer.decode(ids, skip_special_tokens=skip_special_tokens))


def _safe_backend_decode(tokenizer, ids: list[int], *, skip_special_tokens: bool) -> str | None:
    backend = getattr(tokenizer, "backend_tokenizer", None)
    if backend is None:
        return None
    try:
        return str(backend.decode(ids, skip_special_tokens=skip_special_tokens))
    except Exception:
        return None


def _encode_plain(prompt_text: str, tokenizer) -> dict[str, Any]:
    ids = _normalize_ids(tokenizer(prompt_text, add_special_tokens=True)["input_ids"])
    return {
        "path_kind": "plain",
        "rendered_text": prompt_text,
        "token_count": len(ids),
        "input_ids": ids,
        "tokens": tokenizer.convert_ids_to_tokens(ids),
        "decoded_with_special": _safe_decode(
            tokenizer,
            ids,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        ),
        "decoded_skip_special": _safe_decode(
            tokenizer,
            ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        ),
        "backend_decoded_with_special": _safe_backend_decode(tokenizer, ids, skip_special_tokens=False),
        "backend_decoded_skip_special": _safe_backend_decode(tokenizer, ids, skip_special_tokens=True),
    }


def _encode_chat(prompt_text: str, tokenizer) -> dict[str, Any]:
    chat_messages = [{"role": "user", "content": prompt_text}]
    rendered_text = tokenizer.apply_chat_template(
        chat_messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    ids = _normalize_ids(
        tokenizer.apply_chat_template(
            chat_messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors=None,
        )
    )
    return {
        "path_kind": "chat",
        "rendered_text": rendered_text,
        "chat_messages": chat_messages,
        "token_count": len(ids),
        "input_ids": ids,
        "tokens": tokenizer.convert_ids_to_tokens(ids),
        "decoded_with_special": _safe_decode(
            tokenizer,
            ids,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        ),
        "decoded_skip_special": _safe_decode(
            tokenizer,
            ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        ),
        "backend_decoded_with_special": _safe_backend_decode(tokenizer, ids, skip_special_tokens=False),
        "backend_decoded_skip_special": _safe_backend_decode(tokenizer, ids, skip_special_tokens=True),
    }


def _build_prompt_source(args: argparse.Namespace) -> dict[str, Any]:
    if args.prompt_file is not None:
        prompt_text = args.prompt_file.read_text(encoding="utf-8")
        return {
            "source_kind": "prompt_file",
            "prompt_text": prompt_text,
            "prompt_builder": None,
            "source_metadata": {
                "prompt_file": str(args.prompt_file.resolve()),
            },
        }

    if args.slot_json is not None:
        if not args.slot_key:
            raise ValueError("--slot-key is required with --slot-json.")
        payload = _load_json(args.slot_json)
        entry = payload.get(args.slot_key)
        if not isinstance(entry, dict):
            raise KeyError(f"Slot '{args.slot_key}' not found in {args.slot_json}")
        prompt_text = str(entry.get("nl_proof", "") or "")
        if not prompt_text:
            raise ValueError(f"Slot '{args.slot_key}' does not contain a non-empty nl_proof.")
        return {
            "source_kind": "continuation_slot",
            "prompt_text": prompt_text,
            "prompt_builder": None,
            "source_metadata": {
                "slot_json": str(args.slot_json.resolve()),
                "slot_key": args.slot_key,
                "header": entry.get("header"),
                "formal_statement": entry.get("formal_statement"),
                "informal_statement": entry.get("informal_statement"),
            },
        }

    if args.msc_key is not None:
        if not args.msc_condition:
            raise ValueError("--msc-condition is required with --msc-key.")
        spec_path = MSC_SPEC_PATHS[args.msc_condition]
        spec = _load_json(spec_path)
        problems = spec.get("problems")
        if not isinstance(problems, dict):
            raise TypeError(f"Spec file is missing a 'problems' object: {spec_path}")
        entry = problems.get(args.msc_key)
        if not isinstance(entry, dict):
            raise KeyError(f"Problem '{args.msc_key}' not found in {spec_path}")
        header = str(entry.get("header", "")).strip()
        formal_statement = str(entry.get("formal_statement", "")).strip()
        theorem_hint = str(entry.get("theorem_hint", "")).strip()
        prompt_builder = PROMPT_BUILDERS[args.builder]
        prompt_text = prompt_builder.build(header, theorem_hint or None, formal_statement)
        return {
            "source_kind": "msc_spec",
            "prompt_text": prompt_text,
            "prompt_builder": args.builder,
            "source_metadata": {
                "msc_condition": args.msc_condition,
                "msc_key": args.msc_key,
                "spec_path": str(spec_path.resolve()),
                "header": header,
                "formal_statement": formal_statement,
                "theorem_hint": theorem_hint,
            },
        }

    if args.preset is not None:
        entry = PROMPT_PRESETS[args.preset]
        header = entry["header"]
        formal_statement = entry["formal_statement"]
        theorem_hint = entry["theorem_hint"]
        prompt_builder = PROMPT_BUILDERS[args.builder]
        prompt_text = prompt_builder.build(header, theorem_hint or None, formal_statement)
        return {
            "source_kind": "preset",
            "prompt_text": prompt_text,
            "prompt_builder": args.builder,
            "source_metadata": {
                "preset": args.preset,
                "header": header,
                "formal_statement": formal_statement,
                "theorem_hint": theorem_hint,
            },
        }

    raise ValueError("One prompt source must be provided.")


def _build_prompt_artifact(args: argparse.Namespace, tokenizer) -> dict[str, Any]:
    prompt = _build_prompt_source(args)
    encodings: dict[str, Any] = {}
    for path_kind in _selected_paths(args.encoding_path):
        if path_kind == "plain":
            encodings[path_kind] = _encode_plain(prompt["prompt_text"], tokenizer)
        elif path_kind == "chat":
            encodings[path_kind] = _encode_chat(prompt["prompt_text"], tokenizer)
        else:
            raise ValueError(f"Unsupported encoding path: {path_kind}")
    return {
        "prompt": prompt,
        "encodings": encodings,
    }


def _artifact_header(*, command: str, model_name: str, model_path: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at_utc": _utc_timestamp(),
        "command": command,
        "model_name": model_name,
        "model_path": str(model_path),
        "versions": _load_versions(),
    }


def _next_device(model):
    return next(model.parameters()).device


def _ensure_pad_token(tokenizer) -> int:
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if tokenizer.pad_token_id is None:
        raise ValueError("Tokenizer has no pad_token_id after pad-token setup.")
    return int(tokenizer.pad_token_id)


def _load_model(model_path: Path):
    import torch
    from transformers import AutoModelForCausalLM

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for generation, but torch.cuda.is_available() is False.")

    return AutoModelForCausalLM.from_pretrained(
        str(model_path),
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )


def _generation_kwargs_from_args(args: argparse.Namespace) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "max_new_tokens": args.max_new_tokens,
        "num_return_sequences": args.num_return_sequences,
        "do_sample": bool(args.do_sample),
    }
    if args.do_sample:
        kwargs["temperature"] = args.temperature
        kwargs["top_p"] = args.top_p
    return kwargs


def _decode_generation(tokenizer, ids: list[int]) -> dict[str, Any]:
    return {
        "tokens": tokenizer.convert_ids_to_tokens(ids),
        "decoded_with_special": _safe_decode(
            tokenizer,
            ids,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        ),
        "decoded_skip_special": _safe_decode(
            tokenizer,
            ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        ),
        "backend_decoded_with_special": _safe_backend_decode(tokenizer, ids, skip_special_tokens=False),
        "backend_decoded_skip_special": _safe_backend_decode(tokenizer, ids, skip_special_tokens=True),
    }


def _run_generate(args: argparse.Namespace) -> Path:
    import torch

    model_name, model_path = _resolve_model(args.model)
    tokenizer = _load_tokenizer(model_path)
    prompt_artifact = _build_prompt_artifact(args, tokenizer)
    model = _load_model(model_path)

    if args.seed is not None:
        torch.manual_seed(args.seed)

    pad_token_id = _ensure_pad_token(tokenizer)
    generation_kwargs = _generation_kwargs_from_args(args)

    artifact: dict[str, Any] = {
        "__meta__": _artifact_header(command="generate", model_name=model_name, model_path=model_path),
        "prompt": prompt_artifact["prompt"],
        "encodings": prompt_artifact["encodings"],
        "generation_config": {
            **generation_kwargs,
            "seed": args.seed,
            "pad_token_id": pad_token_id,
        },
        "generations": [],
    }

    device = _next_device(model)
    for path_kind, encoding in prompt_artifact["encodings"].items():
        input_ids = encoding["input_ids"]
        input_tensor = torch.tensor([input_ids], dtype=torch.long, device=device)
        attention_mask = torch.ones_like(input_tensor, device=device)

        start = time.time()
        outputs = model.generate(
            input_ids=input_tensor,
            attention_mask=attention_mask,
            pad_token_id=pad_token_id,
            **generation_kwargs,
        )
        duration = time.time() - start

        for seq_index in range(outputs.size(0)):
            full_ids = [int(x) for x in outputs[seq_index].tolist()]
            prompt_token_count = len(input_ids)
            generated_ids = full_ids[prompt_token_count:]
            artifact["generations"].append(
                {
                    "path_kind": path_kind,
                    "prompt_token_count": prompt_token_count,
                    "full_output_ids": full_ids,
                    "generated_token_ids": generated_ids,
                    "full_output": _decode_generation(tokenizer, full_ids),
                    "generated_output": _decode_generation(tokenizer, generated_ids),
                    "generation_time_seconds": duration / max(outputs.size(0), 1),
                    "sequence_index_for_path": seq_index,
                }
            )

    stem = f"continuation-debug-generate-{_slug(prompt_artifact['prompt']['source_kind'])}"
    output_path = _output_path(args.output_name, stem)
    _save_json(artifact, output_path)
    return output_path


def _matching_prefix_length(left: list[int], right: list[int]) -> int:
    match_len = 0
    for left_id, right_id in zip(left, right):
        if left_id != right_id:
            break
        match_len += 1
    return match_len


def _retokenized_same_path_prefix(
    *,
    tokenizer,
    prompt_text: str,
    path_kind: str,
    generated_prefix_ids: list[int],
) -> dict[str, Any]:
    generated_prefix_text = _safe_decode(
        tokenizer,
        generated_prefix_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )

    if path_kind == "plain":
        reconstructed_text = prompt_text + generated_prefix_text
        prefix_ids = _normalize_ids(tokenizer(reconstructed_text, add_special_tokens=True)["input_ids"])
        rendered_text = reconstructed_text
    elif path_kind == "chat":
        messages = [
            {"role": "user", "content": prompt_text},
            {"role": "assistant", "content": generated_prefix_text},
        ]
        rendered_text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        prefix_ids = _normalize_ids(
            tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=False,
                return_tensors=None,
            )
        )
    else:
        raise ValueError(f"Unsupported path_kind: {path_kind}")

    return {
        "variant": "retokenized_same_path",
        "generated_prefix_text": generated_prefix_text,
        "rendered_text": rendered_text,
        "prefix_ids": prefix_ids,
    }


def _run_continue(args: argparse.Namespace) -> Path:
    import torch

    payload = _load_json(args.artifact_json)
    generations = payload.get("generations")
    if not isinstance(generations, list) or not generations:
        raise ValueError(f"Artifact does not contain any generations: {args.artifact_json}")

    if args.generation_index < 0 or args.generation_index >= len(generations):
        raise IndexError(
            f"--generation-index must be in [0, {len(generations) - 1}] for {args.artifact_json}"
        )

    generation = generations[args.generation_index]
    if not isinstance(generation, dict):
        raise TypeError("Selected generation entry must be a JSON object.")

    model_name, model_path = _resolve_model(args.model)
    tokenizer = _load_tokenizer(model_path)
    model = _load_model(model_path)

    if args.seed is not None:
        torch.manual_seed(args.seed)

    prompt = payload.get("prompt")
    if not isinstance(prompt, dict):
        raise ValueError("Artifact is missing prompt metadata.")
    prompt_text = str(prompt.get("prompt_text", "") or "")

    full_output_ids = [int(x) for x in generation.get("full_output_ids", [])]
    prompt_token_count = int(generation.get("prompt_token_count", 0))
    path_kind = str(generation.get("path_kind", "")).strip()
    if not full_output_ids or prompt_token_count <= 0 or not path_kind:
        raise ValueError("Selected generation entry is missing required fields.")

    generated_token_count = max(len(full_output_ids) - prompt_token_count, 0)
    if args.cut_total_token_count is not None:
        cut_total = args.cut_total_token_count
    else:
        cut_total = prompt_token_count + args.cut_generated_token_count

    if cut_total <= 0 or cut_total >= len(full_output_ids):
        raise ValueError(
            f"Cut must satisfy 0 < cut < {len(full_output_ids)}; received {cut_total}."
        )

    exact_prefix_ids = full_output_ids[:cut_total]
    generated_prefix_ids = full_output_ids[prompt_token_count:cut_total]
    reference_suffix_ids = full_output_ids[cut_total:]
    max_new_tokens = args.max_new_tokens if args.max_new_tokens is not None else len(reference_suffix_ids)
    if max_new_tokens <= 0:
        raise ValueError("Continuation max_new_tokens must be positive.")

    generation_config = payload.get("generation_config")
    if not isinstance(generation_config, dict):
        raise ValueError("Artifact is missing generation_config.")

    do_sample = bool(args.do_sample)
    if not args.do_sample:
        do_sample = bool(generation_config.get("do_sample", False))

    generate_kwargs: dict[str, Any] = {
        "max_new_tokens": max_new_tokens,
        "do_sample": do_sample,
        "num_return_sequences": 1,
        "pad_token_id": _ensure_pad_token(tokenizer),
    }
    if do_sample:
        generate_kwargs["temperature"] = args.temperature
        generate_kwargs["top_p"] = args.top_p

    continuation_variants: list[dict[str, Any]] = []
    if "exact_prefix_ids" in args.variants:
        continuation_variants.append(
            {
                "variant": "exact_prefix_ids",
                "rendered_text": None,
                "generated_prefix_text": None,
                "prefix_ids": exact_prefix_ids,
            }
        )
    if "retokenized_same_path" in args.variants:
        continuation_variants.append(
            _retokenized_same_path_prefix(
                tokenizer=tokenizer,
                prompt_text=prompt_text,
                path_kind=path_kind,
                generated_prefix_ids=generated_prefix_ids,
            )
        )

    artifact: dict[str, Any] = {
        "__meta__": _artifact_header(command="continue", model_name=model_name, model_path=model_path),
        "source_artifact": str(args.artifact_json.resolve()),
        "source_generation_index": args.generation_index,
        "cut": {
            "prompt_token_count": prompt_token_count,
            "generated_token_count": generated_token_count,
            "cut_total_token_count": cut_total,
            "cut_generated_token_count": cut_total - prompt_token_count,
            "reference_suffix_token_count": len(reference_suffix_ids),
        },
        "generation_config": {
            **generate_kwargs,
            "seed": args.seed,
        },
        "variants": [],
    }

    device = _next_device(model)
    for variant in continuation_variants:
        prefix_ids = [int(x) for x in variant["prefix_ids"]]
        input_tensor = torch.tensor([prefix_ids], dtype=torch.long, device=device)
        attention_mask = torch.ones_like(input_tensor, device=device)

        start = time.time()
        outputs = model.generate(
            input_ids=input_tensor,
            attention_mask=attention_mask,
            **generate_kwargs,
        )
        duration = time.time() - start

        full_ids = [int(x) for x in outputs[0].tolist()]
        continuation_ids = full_ids[len(prefix_ids) :]
        match_len = _matching_prefix_length(continuation_ids, reference_suffix_ids)

        artifact["variants"].append(
            {
                "variant": variant["variant"],
                "path_kind": path_kind,
                "prefix_token_count": len(prefix_ids),
                "prefix_vs_exact_match_length": _matching_prefix_length(prefix_ids, exact_prefix_ids),
                "prefix_ids_equal_to_exact": prefix_ids == exact_prefix_ids,
                "generated_prefix_text": variant.get("generated_prefix_text"),
                "rendered_text": variant.get("rendered_text"),
                "prefix_ids": prefix_ids,
                "continuation_token_ids": continuation_ids,
                "reference_suffix_token_ids": reference_suffix_ids,
                "reference_match_token_count": match_len,
                "reference_match_exhausted": match_len == len(reference_suffix_ids),
                "continuation_output": _decode_generation(tokenizer, continuation_ids),
                "generation_time_seconds": duration,
            }
        )

    stem = f"continuation-debug-continue-{_slug(path_kind)}"
    output_path = _output_path(args.output_name, stem)
    _save_json(artifact, output_path)
    return output_path


def _run_inspect(args: argparse.Namespace) -> Path:
    model_name, model_path = _resolve_model(args.model)
    tokenizer = _load_tokenizer(model_path)
    prompt_artifact = _build_prompt_artifact(args, tokenizer)

    artifact = {
        "__meta__": _artifact_header(command="inspect", model_name=model_name, model_path=model_path),
        "prompt": prompt_artifact["prompt"],
        "encodings": prompt_artifact["encodings"],
    }

    prompt_source = prompt_artifact["prompt"]["source_kind"]
    stem = f"continuation-debug-inspect-{_slug(prompt_source)}"
    output_path = _output_path(args.output_name, stem)
    _save_json(artifact, output_path)
    return output_path


def main() -> int:
    args = _parse_args()
    _require_supported_transformers()

    if args.command == "inspect":
        output_path = _run_inspect(args)
    elif args.command == "generate":
        output_path = _run_generate(args)
    elif args.command == "continue":
        output_path = _run_continue(args)
    else:
        raise ValueError(f"Unsupported command: {args.command}")

    print(f"Wrote debug artifact to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
