#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForSeq2Seq,
    Trainer,
    TrainingArguments,
    set_seed,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRAIN = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "deepseek_noncot_tactic_1024_train.jsonl"
DEFAULT_VALID = ROOT / "mathlib_fine_tuning" / "data" / "processed" / "deepseek_noncot_tactic_1024_valid.jsonl"
DEFAULT_MODEL = ROOT / "models" / "deepseek-ai" / "DeepSeek-Prover-V2-7B"
DEFAULT_OUTPUT = ROOT / "mathlib_fine_tuning" / "runs" / "deepseek_noncot_tactic_lora_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-path", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument("--valid-path", type=Path, default=DEFAULT_VALID)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--per-device-train-batch-size", type=int, default=2)
    parser.add_argument("--per-device-eval-batch-size", type=int, default=2)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=5e-5)
    parser.add_argument("--num-train-epochs", type=float, default=1.0)
    parser.add_argument("--warmup-ratio", type=float, default=0.03)
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--logging-steps", type=int, default=10)
    parser.add_argument("--eval-steps", type=int, default=200)
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--max-train-samples", type=int, default=None)
    parser.add_argument("--max-valid-samples", type=int, default=None)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument(
        "--lora-target-modules",
        type=str,
        default="q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def apply_smoke_defaults(args: argparse.Namespace) -> None:
    if not args.smoke:
        return
    if args.max_train_samples is None:
        args.max_train_samples = 256
    if args.max_valid_samples is None:
        args.max_valid_samples = 64
    if args.max_steps < 0:
        args.max_steps = 20
    if args.eval_steps == 200:
        args.eval_steps = 10
    if args.logging_steps == 10:
        args.logging_steps = 5


def ensure_prereqs(args: argparse.Namespace) -> None:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required for training.")
    for path in [args.train_path, args.valid_path, args.model_path]:
        if not path.exists():
            raise FileNotFoundError(f"Required path not found: {path}")


def build_datasets(args: argparse.Namespace, tokenizer):
    raw = load_dataset(
        "json",
        data_files={"train": str(args.train_path), "valid": str(args.valid_path)},
    )

    if args.max_train_samples is not None:
        raw["train"] = raw["train"].select(range(min(args.max_train_samples, len(raw["train"]))))
    if args.max_valid_samples is not None:
        raw["valid"] = raw["valid"].select(range(min(args.max_valid_samples, len(raw["valid"]))))

    def preprocess(example: dict) -> dict:
        user_messages = [{"role": "user", "content": example["prompt"]}]
        full_messages = [
            {"role": "user", "content": example["prompt"]},
            {"role": "assistant", "content": example["completion"]},
        ]
        prompt_ids = tokenizer.apply_chat_template(
            user_messages,
            tokenize=True,
            add_generation_prompt=False,
        )
        full_ids = tokenizer.apply_chat_template(
            full_messages,
            tokenize=True,
            add_generation_prompt=False,
        )
        if len(full_ids) > args.max_seq_length:
            raise ValueError(f"Encountered sequence longer than max_seq_length: {len(full_ids)}")
        labels = list(full_ids)
        labels[: len(prompt_ids)] = [-100] * len(prompt_ids)
        return {
            "input_ids": full_ids,
            "attention_mask": [1] * len(full_ids),
            "labels": labels,
        }

    remove_columns = raw["train"].column_names
    tokenized = raw.map(
        preprocess,
        remove_columns=remove_columns,
        desc="Tokenizing dataset",
    )
    return tokenized


def load_model_and_tokenizer(args: argparse.Namespace):
    tokenizer = AutoTokenizer.from_pretrained(str(args.model_path), trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        str(args.model_path),
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    model.config.use_cache = False
    return model, tokenizer


def wrap_with_lora(model, args: argparse.Namespace):
    try:
        from peft import LoraConfig, TaskType, get_peft_model
    except ImportError as exc:
        raise ImportError(
            "peft is required for LoRA training. Install it with `pip install peft` "
            "or add it to the project environment."
        ) from exc

    target_modules = [m.strip() for m in args.lora_target_modules.split(",") if m.strip()]
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        target_modules=target_modules,
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    return model


def write_config(args: argparse.Namespace, output_dir: Path, dataset_sizes: dict[str, int]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    config = vars(args).copy()
    config["train_path"] = str(args.train_path)
    config["valid_path"] = str(args.valid_path)
    config["model_path"] = str(args.model_path)
    config["output_dir"] = str(args.output_dir)
    config["dataset_sizes"] = dataset_sizes
    (output_dir / "train_config.json").write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    apply_smoke_defaults(args)
    ensure_prereqs(args)
    set_seed(args.seed)

    model, tokenizer = load_model_and_tokenizer(args)
    tokenized = build_datasets(args, tokenizer)
    model = wrap_with_lora(model, args)

    output_dir = args.output_dir
    dataset_sizes = {
        "train": len(tokenized["train"]),
        "valid": len(tokenized["valid"]),
    }
    write_config(args, output_dir, dataset_sizes)

    collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        model=model,
        label_pad_token_id=-100,
        pad_to_multiple_of=8,
        return_tensors="pt",
    )

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        do_train=True,
        do_eval=True,
        eval_strategy="steps",
        save_strategy="no",
        eval_steps=args.eval_steps,
        logging_steps=args.logging_steps,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        weight_decay=args.weight_decay,
        warmup_ratio=args.warmup_ratio,
        num_train_epochs=args.num_train_epochs,
        max_steps=args.max_steps,
        lr_scheduler_type="cosine",
        bf16=True,
        report_to="none",
        remove_unused_columns=False,
        seed=args.seed,
        data_seed=args.seed,
        logging_first_step=True,
        dataloader_pin_memory=True,
        save_safetensors=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["valid"],
        data_collator=collator,
        tokenizer=tokenizer,
    )

    train_result = trainer.train()
    trainer.save_model()
    metrics = train_result.metrics
    eval_metrics = trainer.evaluate()

    (output_dir / "train_metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "eval_metrics.json").write_text(
        json.dumps(eval_metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"train_metrics": metrics, "eval_metrics": eval_metrics}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
