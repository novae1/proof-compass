# Research Journal

This file is an append-only working journal. Keep entries short. Use
`EMPIRICAL_EVIDENCE.md`, `OPEN_QUESTIONS.md`, and `NEXT_EXPERIMENTS.md` for the
current canonical view.

## 2026-03-25

- The rank sweep is now informative enough to rule out "LoRA rank too small" as the main explanation for the MSC-180 no-hint failure.
- The current best explanation is objective mismatch: the fine-tunes learned standalone theorem-block imitation better than theorem grounding under sparse benchmark context.
- The important positive result from the continuation branch is that recovery is viable; boundary handling, not tokenizer corruption, was the real issue there.
- The theorem-guidance and prompt-hint branches still look promising, but they need a real aggregate summary before they can compete fairly with the fine-tuning branch for attention.
- The next work should reduce uncertainty before using more GPU time: summarize retrieval-style results, define the theorem-grounding benchmark, and design the smallest contamination-safe dataset.
