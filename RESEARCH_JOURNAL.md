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

## 2026-03-27

- Wrote `FINETUNING_SUMMARY.md` as the advisor-facing summary of the LoRA experiments. It now contains the training setup, evaluation setup, main results, failure analysis, hypotheses considered, and targeted fine-tuning alternatives.
- The fine-tuning conclusion is now stable: supervised fine-tuning on standalone Mathlib theorem-block completion hurt theorem grounding under sparse benchmark context, and increasing LoRA rank from `16` to `64` to `128` did not fix that.
- The strongest current direction is retrieval-and-repair for hallucinated Mathlib theorem names, not another generic proof-SFT run.
- Ran a manual retrieval study on a small set of `MSC-180` no-hint failure cases where the model hallucinated theorem-like names. The study started from a casebook built from real failed attempts and corresponding benchmark statements.
- For the first pass, we tested both `LeanExplore` and `LeanFinder`, initially using broader top-`k` inspection to see what theorem families each query recovered.
- We compared several query types:
  - hallucinated theorem name only
  - formal theorem statement only
  - hallucinated theorem name + formal statement
  - in some cases, theorem statement + both hallucinated names from the same failed proof
- The main retrieval result is now fairly clear:
  - the formal theorem statement carries most of the global retrieval signal
  - the hallucinated theorem name can add useful local signal
  - hallucination-only queries can preserve distinct theorem intent, but they are less stable
  - `hallucination + statement` looks like the best single query format overall
- We then tightened the manual study to `LeanFinder` with top-`2` retrieval, since that is much closer to a realistic retry setting than looking at top-`5` or larger lists.
- On the current structured cases, top-`2` retrieval was already strong enough to justify a first prototype. The strongest problems so far are `MSC-180_12_001`, `MSC-180_14_003`, and `MSC-180_65_003`. `MSC-180_52_002` remains a weaker case.
- One important design lesson from the retrieval study is that combining too much information can wash out the local theorem signal. In particular, “statement + both hallucinations” often helps global relevance but is less useful if the goal is to recover what a specific hallucinated theorem was trying to do.
- If fine-tuning is revisited later, the most relevant variants are now much narrower than before:
  - hinted continuation training
  - targeted anti-hallucination training
  - retrieval-aware training
  - small coherent Mathlib domain slices
- The project claim should stay narrow: targeted repair of hallucinated Mathlib references in small Lean provers, not generic retrieval for theorem proving.
