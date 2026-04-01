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

## 2026-03-30

- Built and committed the first uncontaminated iterative-RAG specs from the no-hint MSC-180 base run only. The pass1 spec uses statement-only LeanFinder retrieval, and the pass2 spec augments that with hallucination-conditioned retrieved theorems.
- Ran and verified the first pass2 experiment. Result: `87/400` successful attempts and `11/20` solved problems, versus the no-hint base at `77/400` and `6/20`.
- Pass2 also reduced unresolved-name style failures materially relative to base: attempts with `unknown` dropped from `111/400` to `86/400`.
- Realized the statement-only ablation was still missing, then ran and verified pass1. Result: `92/400` successful attempts and `9/20` solved problems.
- This changed the interpretation in an important way: statement-only retrieval already accounts for a large share of the gain. Hallucination-conditioned additions still help, but mainly by improving solved-problem coverage and reducing unknown-name failures rather than by maximizing raw attempt pass rate.
- Current picture:
  - base: weaker on both attempts and solved problems
  - pass1: best raw attempt pass rate
  - pass2: best solved-problem count and best unknown-name reduction
- The main belief update is that the iterative-RAG idea is working, but the hallucination-conditioned step should be treated as a targeted augmentation on top of strong statement-based retrieval, not as the whole story.
- Wrote a dedicated synthesis note at `rag_experiments/reports/iterative_rag/20260330_iterative_rag_pass1_pass2_analysis.md`.

## 2026-03-31

- Extended the pass1/pass2 iterative-RAG analysis with direct qualitative inspection of full outputs, error messages, and per-problem hallucination behavior.
- The main caution is now explicit: several pass2-only solved problems are only `1/20` or `2/20`, so they cannot be treated as strong evidence on counts alone.
- After reading the outputs, the pass2 gains split into two groups:
  - robust/genuine improvements, such as `MSC-180_14_001`, where pass2 adds the correct quotient-kernel theorem family and sharply reduces hallucinations
  - low-count gains that are promising but ambiguous, such as `MSC-180_60_002` and especially `MSC-180_90_001`, where some of the improvement may just be sampling luck
- The regressions are also now clearer:
  - `MSC-180_08_001` is a strong negative example where extra pass2 context appears to induce namespace confusion (`ext_of_adjoin_eq_top` vs `AlgHom.ext_of_adjoin_eq_top`)
  - `MSC-180_12_003` is another strong negative example where pass2 adds nearby quotient/field lemmas and the model starts hallucinating the wrong variants
- The more precise current hypothesis is: hallucination-conditioned retrieval is helpful when the model is genuinely missing a theorem family, but once statement-only retrieval already provides a clean anchor, extra related theorems can over-expand the local search space and create new hallucinations.
- Switched the next development benchmark to `ProofNet-valid` and built two non-CoT specs:
  - no-hint
  - statement-only RAG with statement-query LeanFinder top-`2` theorem hints
- Verified both ProofNet-valid runs and compared them. Headline result:
  - no-hint: `155/740` successful attempts, `47/185` solved problems
  - statement-RAG-top2: `156/740` successful attempts, `47/185` solved problems
- So statement-only RAG did not improve solved-problem count on this `4`-attempt run, but it did reduce unresolved-name burden:
  - attempts with `unknown`: `122 -> 108`
  - total `unknown` occurrences: `158 -> 134`
- Hallucinations on ProofNet-valid are present but not dominant. With the filtered theorem-like metric:
  - no-hint has hallucinations on `63/185` problems
  - statement-RAG-top2 has hallucinations on `52/185` problems
  - among failed problems, the corresponding rates are `58/138` and `50/138`
- Built two iterative pass2 specs for ProofNet-valid, each restricted to problems that are:
  - unsolved
  - and have at least one filtered theorem-like hallucination
- Trigger counts differ materially:
  - no-hint pass2 triggers on `58` problems
  - statement-RAG-top2 pass2 triggers on `50` problems
  - overlap is only `31` problems
- The two pass2 specs are not redundant. Even on shared triggered problems, the hallucination-conditioned theorem additions only partially align:
  - exact added-theorem-set match on `12/31`
  - disjoint added-theorem sets on `9/31`
  - average added-set Jaccard `0.5`
- Wrote the overlap analysis at `rag_experiments/reports/iterative_rag/20260331_proofnet_valid_pass2_spec_overlap_analysis.md`.

## 2026-04-01

- Diagnosed a false-negative ProofNet pass2 verification failure. The initial all-zero pass2 result was caused by an external Lean REPL mismatch, not by the model: `lean_project` was on Lean `4.15.0`, while the REPL binary had been built from tag `v4.27.0-rc1`.
- After rebuilding the external REPL at `v4.15.0` and restarting the Flask server, verification behaved normally again. This confirmed that the stripped-header verification path is still valid when the base REPL environment is actually correct.
- Re-verified both ProofNet-valid pass2 runs under the corrected REPL:
  - `20260401_proofnet-valid_nohint-pass2_base_deepseekv2_7b_lean4-15_verified.json`
  - `20260401_proofnet-valid_statement-rag-top2-pass2_base_deepseekv2_7b_lean4-15_verified.json`
- Corrected results are positive for both iterative branches.
  - `no-hint -> pass2` improves the full-benchmark composite from `47/185` solved problems to `52/185`.
  - `statement-RAG-top2 -> pass2` improves the full-benchmark composite from `47/185` to `51/185`.
- The most important new belief update is about hallucination reduction, not just solve counts.
  - On ProofNet-valid, first-pass statement-only RAG reduced filtered theorem-like hallucination prevalence only modestly:
    - failed problems with hallucinations: `42.0% -> 36.2%`
    - failed attempts with hallucinations: `20.3% -> 17.6%`
  - The hallucination-conditioned pass2 reduces them much more strongly:
    - `no-hint -> pass2` composite: failed problems with hallucinations `42.0% -> 17.3%`, failed attempts `20.3% -> 11.6%`
    - `statement-RAG-top2 -> pass2` composite: failed problems `36.2% -> 22.4%`, failed attempts `17.6% -> 11.9%`
- This is now one of the clearest project-level results so far: theorem retrieval from the formal statement alone does not substantially suppress hallucinations, but theorem retrieval conditioned on the model's actual hallucinated names does.
- Wrote the corrected analysis to `rag_experiments/reports/iterative_rag/20260401_proofnet_valid_iterative_pass2_analysis.md`.
