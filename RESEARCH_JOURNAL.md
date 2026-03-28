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
- Implemented a dedicated hallucination extractor in `rag_experiments/scripts/tools/extract_hallucinations.py`. It now pulls unresolved names from verified Lean outputs, handles both `unknown identifier` and `unknown constant` forms plus dotted-identifier variants, and aggregates them per problem with both occurrence counts and attempt counts.
- Settled on a simple first-pass unresolved-name filter: minimum length `>= 7` characters. This is strict enough to remove low-information junk while still keeping theorem-like names that are useful as retrieval seeds.
- Confirmed that Lean Finder can be queried programmatically through the public Hugging Face Space, so no private API access is needed for the first prototype. Implemented `rag_experiments/scripts/tools/leanfinder_client.py` with a cache-first design, a minimal number of live requests, and parsing of the streamed Gradio response into structured theorem results.
- Implemented `rag_experiments/scripts/tools/build_iterative_rag_specs.py` to build both pass-1 and pass-2 theorem-context specs from existing verified runs rather than from fresh generations.
- The current plan is now more efficient: do not rerun pass 1. Use existing `A` no-hint and `B` theorem-statements runs on the 20-problem MSC-180 slice as offline sources of information, then make the first new model run the pass-2 retry run.
- The pass-2 constructor currently works like this:
  - start from the statement-only Lean Finder top-`2`
  - combine hallucinations mined from failed `A` and `B` attempts
  - rank them by frequency
  - take the top `2`
  - for each one, query Lean Finder with `hallucination + statement`
  - add the first distinct retrieved theorem from the top-`5`
- Small validation runs on representative problems showed the right general behavior: pass 1 recovers the global theorem family, while pass 2 adds more local theorem-family signal derived from frequent hallucinations.
- One practical lesson from the builder validation is that we should prefer theorem/lemma results over defs when selecting hallucination-derived additions. That keeps the added context closer to what the model can actually use in a proof.
