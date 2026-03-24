# Continuation Recovery

This workspace investigates how to continue generation from raw truncated text
without relying on saved token ids.

## Goal

Given visible text that ends at an arbitrary truncation point, find a robust
recovery rule that:

1. maps the text to a recoverable prefix,
2. preserves the intended continuation behavior as often as possible, and
3. works for text that did not originate from this exact experiment pipeline.

## Scope

The study runs on the local `DeepSeek-Prover-V2-7B` model under the dedicated
continuation environment:

- `transformers==4.57.6`
- `tokenizers==0.22.2`
- `accelerate==1.13.0`
- `huggingface-hub==0.36.2`
- `sentencepiece==0.2.1`

## Layout

- `reports/`: running notes, findings, and next-step planning
- `scripts/`: standalone experiment code
- `outputs/`: generated JSON and Markdown artifacts from the study

## Notes

- This workspace is an audit trail for the continuation-recovery decision, not a
  general benchmark runner.
- Benchmark inputs live in `rag_experiments/`; this folder stores the study code,
  its reports, and its derived outputs.
