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
- pass2 subset: `6/232` successful attempts, `6/58` solved problems

Full-benchmark composite:
- first-pass no-hint: `155/740` successful attempts, `47/185` solved problems
- with pass2 substituted on triggered problems: `161/740`, `53/185`

Delta:
- successful attempts: `+6`
- solved problems: `+6`

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
- problems with at least one filtered hallucination: `63/185` (`34.1%`) -> `42/185` (`22.7%`)
- failed problems with at least one filtered hallucination: `58/138` (`42.0%`) -> `32/132` (`24.2%`)
- failed attempts with at least one filtered hallucination: `119/585` (`20.3%`) -> `89/579` (`15.4%`)

For the `statement-rag-top2 -> pass2` composite:
- problems with at least one filtered hallucination: `52/185` (`28.1%`) -> `35/185` (`18.9%`)
- failed problems with at least one filtered hallucination: `50/138` (`36.2%`) -> `30/134` (`22.4%`)
- failed attempts with at least one filtered hallucination: `103/584` (`17.6%`) -> `69/580` (`11.9%`)

So the specific hallucination-aware retrieval step is doing something that plain theorem-statement retrieval does not do very well.
