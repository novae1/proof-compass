#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from peft import PeftModel
from transformers import DataCollatorForSeq2Seq, Trainer, TrainingArguments

from train_tactic_sft import build_datasets, load_model_and_tokenizer

DEFAULT_MODEL = ROOT / "models" / "deepseek-ai" / "DeepSeek-Prover-V2-7B"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--valid-path", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--adapter-dir", type=Path, default=None)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=1)
    parser.add_argument("--output-path", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    eval_args = argparse.Namespace(
        train_path=args.valid_path,
        valid_path=args.valid_path,
        model_path=args.model_path,
        output_dir=ROOT / "tmp_eval",
        max_seq_length=args.max_seq_length,
        max_train_samples=None,
        max_valid_samples=None,
    )

    model, tokenizer = load_model_and_tokenizer(eval_args)
    if args.adapter_dir is not None:
        model = PeftModel.from_pretrained(model, str(args.adapter_dir))

    tokenized = build_datasets(eval_args, tokenizer)
    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        label_pad_token_id=-100,
        pad_to_multiple_of=8,
        return_tensors="pt",
    )
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(ROOT / "tmp_eval"),
            do_train=False,
            do_eval=True,
            report_to="none",
            per_device_eval_batch_size=args.per_device_eval_batch_size,
            bf16=True,
            remove_unused_columns=False,
        ),
        eval_dataset=tokenized["valid"],
        data_collator=collator,
        tokenizer=tokenizer,
    )
    metrics = trainer.evaluate()
    if args.output_path is not None:
        args.output_path.parent.mkdir(parents=True, exist_ok=True)
        args.output_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
