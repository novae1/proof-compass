# ProofNet-valid Iterative Pass2 Analysis

## Scope
This note analyzes the corrected ProofNet-valid iterative pass2 runs after fixing the external Lean REPL toolchain mismatch.

Verified files:
- `rag_experiments/outputs/proofnet/valid/20260331_proofnet-valid_nohint_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260331_proofnet-valid_statement-rag-top2_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260401_proofnet-valid_nohint-pass2_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/proofnet/valid/20260401_proofnet-valid_statement-rag-top2-pass2_base_deepseekv2_7b_lean4-15_verified.json`

Pass2 specs only target problems that were:
- unsolved in the corresponding first-pass run
- and had at least one filtered theorem-like hallucination

So there are two useful views:
- triggered-subset analysis
- full-benchmark composite analysis, where pass2 replaces first-pass results only on triggered problems

## Verification note
The first pass2 verification attempt produced meaningless `unknown namespace` failures on every attempt. That was not a model effect. The root cause was an external REPL mismatch:
- `lean_project` was on Lean `4.15.0`
- the REPL binary had been built from tag `v4.27.0-rc1`

After rebuilding the external REPL at `v4.15.0` and restarting the Flask server, verification behaved normally again. The corrected results below are the only ones that should be used.

## Headline
The corrected pass2 runs are positive.

### `no-hint -> pass2`
Triggered subset:
- baseline subset: `0/232` successful attempts, `0/58` solved problems
- pass2 subset: `5/232` successful attempts, `5/58` solved problems

Full-benchmark composite:
- first-pass no-hint: `155/740` successful attempts, `47/185` solved problems
- with pass2 substituted on triggered problems: `160/740`, `52/185`

Delta:
- successful attempts: `+5`
- solved problems: `+5`

### `statement-rag-top2 -> pass2`
Triggered subset:
- baseline subset: `0/200` successful attempts, `0/50` solved problems
- pass2 subset: `4/200` successful attempts, `4/50` solved problems

Full-benchmark composite:
- first-pass statement-RAG-top2: `156/740` successful attempts, `47/185` solved problems
- with pass2 substituted on triggered problems: `160/740`, `51/185`

Delta:
- successful attempts: `+4`
- solved problems: `+4`

## Most important result
The most interesting result is not just that pass2 solves some additional problems. It is that hallucination-conditioned retrieval reduces theorem-like hallucination burden much more strongly than statement-only RAG did.

### First-pass statement-only RAG helped only modestly
Relative to no-hint on the full benchmark:
- problems with at least one filtered hallucination: `63/185` (`34.1%`) -> `52/185` (`28.1%`)
- failed problems with at least one filtered hallucination: `58/138` (`42.0%`) -> `50/138` (`36.2%`)
- failed attempts with at least one filtered hallucination: `119/585` (`20.3%`) -> `103/584` (`17.6%`)

This is real improvement, but it is not large.

### Hallucination-conditioned pass2 helped much more
For the `no-hint -> pass2` composite:
- problems with at least one filtered hallucination: `63/185` (`34.1%`) -> `32/185` (`17.3%`)
- failed problems with at least one filtered hallucination: `58/138` (`42.0%`) -> `23/133` (`17.3%`)
- failed attempts with at least one filtered hallucination: `119/585` (`20.3%`) -> `67/580` (`11.6%`)

For the `statement-rag-top2 -> pass2` composite:
- problems with at least one filtered hallucination: `52/185` (`28.1%`) -> `35/185` (`18.9%`)
- failed problems with at least one filtered hallucination: `50/138` (`36.2%`) -> `30/134` (`22.4%`)
- failed attempts with at least one filtered hallucination: `103/584` (`17.6%`) -> `69/580` (`11.9%`)

So the specific hallucination-aware retrieval step is doing something that plain theorem-statement retrieval does not do very well.

## Triggered-subset metrics
These are the cleanest measurements of the pass2 intervention itself.

### `no-hint -> pass2`
Triggered set size:
- `58` problems
- `232` attempts

Metrics:
- attempt success rate: `0/232 = 0.0%` -> `5/232 = 2.2%`
- problem success rate: `0/58 = 0.0%` -> `5/58 = 8.6%`
- attempts with any filtered hallucination: `110/232 = 47.4%` -> `58/232 = 25.0%`
- failed attempts with any filtered hallucination: `110/232 = 47.4%` -> `58/227 = 25.6%`
- problems with any filtered hallucination: `58/58 = 100.0%` -> `27/58 = 46.6%`
- failed problems with any filtered hallucination: `58/58 = 100.0%` -> `23/53 = 43.4%`
- attempts with any `unknown`: `111/232 = 47.8%` among failed attempts -> `64/227 = 28.2%`

Newly solved problems:
- `exercise_27_4`
- `exercise_2_4_36`
- `exercise_32_1`
- `exercise_38_6`
- `exercise_3_2_21a`

### `statement-rag-top2 -> pass2`
Triggered set size:
- `50` problems
- `200` attempts

Metrics:
- attempt success rate: `0/200 = 0.0%` -> `4/200 = 2.0%`
- problem success rate: `0/50 = 0.0%` -> `4/50 = 8.0%`
- attempts with any filtered hallucination: `101/200 = 50.5%` -> `67/200 = 33.5%`
- failed attempts with any filtered hallucination: `101/200 = 50.5%` -> `67/196 = 34.2%`
- problems with any filtered hallucination: `50/50 = 100.0%` -> `33/50 = 66.0%`
- failed problems with any filtered hallucination: `50/50 = 100.0%` -> `30/46 = 65.2%`
- attempts with any `unknown`: `102/200 = 51.0%` among failed attempts -> `69/196 = 35.2%`

Newly solved problems:
- `exercise_13_4_10`
- `exercise_2_5_30`
- `exercise_32_1`
- `exercise_3_2_21a`

## Composite benchmark metrics
These are the numbers that matter if the system is interpreted as an iterative pipeline that only triggers pass2 on selected problems.

### `no-hint -> pass2`
- successful attempts: `155/740` -> `160/740`
- solved problems: `47/185` -> `52/185`
- attempts with any filtered hallucination: `119/740` (`16.1%`) -> `67/740` (`9.1%`)
- failed attempts with any filtered hallucination: `119/585` (`20.3%`) -> `67/580` (`11.6%`)
- problems with any filtered hallucination: `63/185` (`34.1%`) -> `32/185` (`17.3%`)
- failed problems with any filtered hallucination: `58/138` (`42.0%`) -> `23/133` (`17.3%`)
- unknown among failed attempts: `122/585` (`20.9%`) -> `75/580` (`12.9%`)

### `statement-rag-top2 -> pass2`
- successful attempts: `156/740` -> `160/740`
- solved problems: `47/185` -> `51/185`
- attempts with any filtered hallucination: `103/740` (`13.9%`) -> `69/740` (`9.3%`)
- failed attempts with any filtered hallucination: `103/584` (`17.6%`) -> `69/580` (`11.9%`)
- problems with any filtered hallucination: `52/185` (`28.1%`) -> `35/185` (`18.9%`)
- failed problems with any filtered hallucination: `50/138` (`36.2%`) -> `30/134` (`22.4%`)
- unknown among failed attempts: `108/584` (`18.5%`) -> `75/580` (`12.9%`)

## Interpretation
Three conclusions look justified.

### 1. The iterative pass is real, not just noise
Both pass2 branches improve on their triggered subsets.
- `no-hint -> pass2`: `+5` solved problems on the composite benchmark
- `statement-rag-top2 -> pass2`: `+4` solved problems on the composite benchmark

### 2. Hallucination-aware retrieval is doing something more specific than statement-only RAG
Statement-only RAG on ProofNet-valid barely changed solved-problem count and only modestly reduced hallucination prevalence.

In contrast, hallucination-conditioned pass2 sharply reduced hallucination burden, especially on failed problems and failed attempts.

This strongly suggests that the local hallucination signal is useful in a way that global theorem-statement retrieval is not.

### 3. On this benchmark, `no-hint -> pass2` was slightly stronger than `statement-rag-top2 -> pass2`
The no-hint branch ended at:
- `160/740` successful attempts
- `52/185` solved problems

The statement-RAG-first branch ended at:
- `160/740` successful attempts
- `51/185` solved problems

So the two branches converge on attempts, but the no-hint-first branch retains a small edge on solved-problem count.

## Open questions
- Why do some triggered problems still retain filtered hallucinations even after pass2?
- Are the remaining failures shifting into a small number of stable non-hallucination buckets such as unsolved goals or type mismatch?
- Would a more conservative pass2 theorem budget remove more hallucinations without sacrificing the newly solved problems?
- Does the next iteration belong on ProofNet-valid, or should these gains now be checked back on MSC-180?
