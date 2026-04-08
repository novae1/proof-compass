#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL = ROOT / "models" / "deepseek-ai" / "DeepSeek-Prover-V2-7B"
DEFAULT_ADAPTER = ROOT / "mathlib_fine_tuning" / "runs" / "memorization_100_lora_e30_from_e20"
DEFAULT_DATASET = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "memorization_100" / "valid.jsonl"
DEFAULT_OUTPUT = ROOT / "mathlib_fine_tuning" / "runs" / "memorization_100_lora_e30_from_e20" / "inference_eval.json"

BOS_MARKER = "<｜begin▁of▁sentence｜>"
FENCE_OPEN_RE = re.compile(r"^\s*```lean4\s*", re.IGNORECASE)
FENCE_CLOSE_RE = re.compile(r"\s*```\s*$", re.MULTILINE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--adapter-dir", type=Path, default=None)
    parser.add_argument("--dataset-path", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--max-new-tokens", type=int, default=1024)
    return parser.parse_args()


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def _normalize_completion(text: str) -> str:
    stripped = text.strip()
    stripped = FENCE_OPEN_RE.sub("", stripped)
    stripped = FENCE_CLOSE_RE.sub("", stripped)
    lines = [line.rstrip() for line in stripped.splitlines()]
    return "\n".join(lines).strip()


def _render_prompt(tokenizer, prompt: str) -> str:
    rendered = str(
        tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )
    )
    return rendered.removeprefix(BOS_MARKER)


def _extract_completion(full_text: str, rendered_prompt: str) -> str:
    if full_text.startswith(rendered_prompt):
        return full_text[len(rendered_prompt) :].lstrip()
    assistant_marker = "<｜Assistant｜>"
    if assistant_marker in full_text:
        idx = full_text.rfind(assistant_marker)
        return full_text[idx + len(assistant_marker) :].lstrip()
    return full_text.strip()


def main() -> int:
    args = parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for inference.")

    tokenizer = AutoTokenizer.from_pretrained(str(args.model_path), trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        str(args.model_path),
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    if args.adapter_dir is not None:
        model = PeftModel.from_pretrained(model, str(args.adapter_dir))
    model.eval()

    rows = _read_jsonl(args.dataset_path)
    prompts = [row["prompt"] for row in rows]
    rendered_prompts = [_render_prompt(tokenizer, prompt) for prompt in prompts]
    prompt_ids = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=True,
            add_generation_prompt=True,
        )
        for prompt in prompts
    ]

    results: list[dict] = []
    exact_matches = 0
    normalized_matches = 0

    for start in range(0, len(rows), args.batch_size):
        batch_rows = rows[start : start + args.batch_size]
        batch_prompt_ids = prompt_ids[start : start + args.batch_size]
        batch_rendered = rendered_prompts[start : start + args.batch_size]

        encoded = tokenizer.pad({"input_ids": batch_prompt_ids}, return_tensors="pt", padding=True)
        encoded = {k: v.to(model.device) for k, v in encoded.items()}

        with torch.no_grad():
            outputs = model.generate(
                **encoded,
                do_sample=False,
                max_new_tokens=args.max_new_tokens,
                pad_token_id=tokenizer.pad_token_id,
            )

        for idx, row in enumerate(batch_rows):
            full_text = tokenizer.decode(outputs[idx], skip_special_tokens=True).strip()
            completion = _extract_completion(full_text, batch_rendered[idx])
            exact_match = completion == row["completion"]
            normalized_match = _normalize_completion(completion) == _normalize_completion(row["completion"])
            exact_matches += int(exact_match)
            normalized_matches += int(normalized_match)
            results.append(
                {
                    "index": start + idx,
                    "prompt": row["prompt"],
                    "gold_completion": row["completion"],
                    "generated_completion": completion,
                    "exact_match": exact_match,
                    "normalized_match": normalized_match,
                }
            )

    summary = {
        "dataset_path": str(args.dataset_path),
        "adapter_dir": str(args.adapter_dir) if args.adapter_dir is not None else None,
        "num_examples": len(rows),
        "exact_match_count": exact_matches,
        "normalized_match_count": normalized_matches,
        "exact_match_rate": exact_matches / len(rows) if rows else 0.0,
        "normalized_match_rate": normalized_matches / len(rows) if rows else 0.0,
        "results": results,
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    args.output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
