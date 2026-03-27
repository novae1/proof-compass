# Fine-Tuning Summary

## Purpose
This note summarizes the recent fine-tuning effort on a small open Lean prover, the evaluations that were run, the main failure mode that was observed, and the current best explanation for that failure.

It is meant to be readable without prior repo-specific context.

## One-Paragraph Summary
We fine-tuned `DeepSeek-Prover-V2-7B` with LoRA on a tactic-only corpus of standalone Mathlib theorem proofs and then evaluated the resulting models on a hard sparse-context benchmark slice: a `20`-problem no-hint subset of the `MSC-180` theorem-proving benchmark, with `20` attempts per problem and Lean verification for every attempt. The base model achieved `77/400` successful attempts and solved `6/20` problems. The fine-tuned models performed much worse: rank-`16` LoRA achieved `4/400` and `2/20`, rank-`64` achieved `1/400` and `1/20`, and rank-`128` achieved `2/400` and `2/20`. The evidence suggests that the fine-tunes improved imitation of standalone Mathlib-style proof text, but degraded theorem grounding under sparse benchmark context. In particular, explicit unresolved theorem-name errors increased sharply after fine-tuning, while the generated outputs still looked structurally like Lean proofs. The current conclusion is that another generic proof-supervised fine-tuning run is not the right next step; retrieval- or repair-based theorem grounding is the stronger next direction.

## What Was Trained
### Base model
- `DeepSeek-Prover-V2-7B`
- local model path used by the training scripts: `models/deepseek-ai/DeepSeek-Prover-V2-7B`

### Training data
- processed tactic-only supervised fine-tuning dataset built from standalone Mathlib theorem proofs
- retained processed split sizes from the saved training configs:
  - training examples: `55,712`
  - validation examples: `1,155`
- maximum sequence length: `1024`

### Fine-tuned variants
Three LoRA variants were trained and evaluated:
- LoRA rank `16`
- LoRA rank `64`
- LoRA rank `128`

### Shared training recipe
Across all three runs:
- one training epoch
- learning rate `5e-5`
- LoRA dropout `0.05`
- same target modules:
  - `q_proj,k_proj,v_proj,o_proj,gate_proj,up_proj,down_proj`
- seed `42`

### Important caveat about the rank sweep
The three LoRA runs used the same dataset and broadly the same training recipe, but they were not a perfectly matched hardware-controlled ablation. The saved configs show slight batch-size differences across ranks.

That means the rank comparison is still informative, but it should not be oversold as a perfectly controlled optimization study.

## What Was Evaluated
### Main benchmark used for the negative result
- `MSC-180`, a Lean theorem-proving benchmark spanning many mathematical subjects
- the evaluation here used a `20`-problem subset under a no-hint setting
- each problem was sampled `20` times
- total evaluated attempts per model: `400`
- every attempt was verified in Lean

### Why this evaluation matters
This is a sparse-context setting:
- the model sees the theorem statement
- it does **not** get theorem hints
- so success depends heavily on selecting and using the right library theorems without help

That is precisely the setting where theorem-name hallucination becomes visible.

## Main Quantitative Results
The table below uses a narrow, reproducible hallucination metric:
- attempts containing an explicit Lean `unknown identifier` error
- total `unknown identifier` occurrences
- distinct unresolved identifier names

This avoids mixing together multiple broader heuristics for “theorem-like hallucination.”

| Model | Successful attempts | Problems solved | Attempts with explicit `unknown identifier` | Total `unknown identifier` occurrences | Distinct unresolved names |
|---|---:|---:|---:|---:|---:|
| Base model (`DeepSeek-Prover-V2-7B`) | `77 / 400` | `6 / 20` | `64 / 400` | `126` | `56` |
| LoRA rank `16` | `4 / 400` | `2 / 20` | `207 / 400` | `274` | `224` |
| LoRA rank `64` | `1 / 400` | `1 / 20` | `220 / 400` | `278` | `247` |
| LoRA rank `128` | `2 / 400` | `2 / 20` | `220 / 400` | `339` | `279` |

## Immediate Interpretation
Three things are clear.

1. Fine-tuning hurt performance badly.
- The base model solved `6/20` problems.
- None of the fine-tuned models solved more than `2/20`.

2. Increasing LoRA rank did not repair the regression.
- Rank `64` and rank `128` did not recover the gap to the base model.
- So “the adapter rank was just too small” is not a good main explanation.

3. Explicit unresolved names increased sharply after fine-tuning.
- The base model had `64` attempts with explicit `unknown identifier` errors.
- The fine-tuned models had `207`, `220`, and `220` such attempts.

That points to a theorem-grounding problem, not a small performance fluctuation.

## What The Outputs Looked Like
The fine-tuned models did **not** collapse into empty strings, parser garbage, or literal duplicate outputs.

Representative output-structure measurements:

| Model | Mean raw output length | Mean parsed proof length | Mean unique parsed proofs per problem |
|---|---:|---:|---:|
| Base model | `1087.6` chars | `742.8` chars | `18.15` |
| LoRA rank `16` | `1019.4` chars | `674.5` chars | `19.95` |
| LoRA rank `64` | `1082.7` chars | `737.8` chars | `20.00` |
| LoRA rank `128` | `1106.3` chars | `761.4` chars | `20.00` |

The existing structure analysis also found that theorem headers still matched the target statements essentially all the time.

### What that means
The problem is not:
- text truncation
- degenerate repetition
- failure to produce Lean-shaped proofs

The problem is semantic:
- the models still write Lean-looking proofs
- but they increasingly reach for theorem names or local APIs that do not actually resolve in the benchmark environment

## Representative Failure Mode
The hallmark error pattern is:
- theorem-like but wrong identifier generation

Examples seen in the analyses include names like:
- `exists_isLUB`
- `root_multiplicity_factorization`
- `chinese_remainder_theorem`
- `AddMonoidHom.quotientKerEquivOfSurjective`

These are not random strings. They often look like plausible Mathlib names or close variants of real theorem families. That is important because it suggests the model is not failing to speak Lean at all. It is failing to **ground** its theorem references correctly.

## Hypotheses Considered

| Hypothesis | Status | Reason |
|---|---|---|
| The adapter rank was too small | Unsupported | Increasing rank from `16` to `64` and `128` did not recover performance |
| Fine-tuning caused syntax collapse | Unsupported | Outputs remain Lean-shaped, non-empty, and highly diverse within each problem |
| Fine-tuning increased theorem-name hallucination | Supported | Explicit unresolved identifiers increased sharply after fine-tuning |
| The training objective and benchmark task were mismatched | Supported | The data rewarded standalone theorem-block completion, while the benchmark requires theorem grounding under weak context |
| Exact train/eval contamination explains the result | Unresolved | Benchmark-to-benchmark overlap checks were clean, but the exact raw source corpus was not locally available for a full direct audit |

## Current Best Explanation
The most plausible explanation is:
- the training data and objective rewarded imitation of standalone Mathlib theorem proofs
- the evaluation task instead required theorem selection under sparse context with no hints
- the fine-tunes therefore improved local proof-style imitation without improving, and likely harming, theorem grounding

In other words:
- the model became more willing to write plausible Lean proof text
- but less calibrated about which Mathlib theorem names are actually available and correct in the current setting

## What We Ruled Out
The current evidence is strong enough to rule out two tempting explanations.

### 1. “It just needed a higher LoRA rank.”
No. That was tested directly.

### 2. “The model forgot how to write Lean.”
No. The generated proofs still look like Lean proofs and remain diverse. The issue is not basic syntactic fluency.

## What We Did Not Yet Establish

At the time of this summary, the key negative result is grounded most strongly in the `MSC-180` no-hint evaluation slice. A broader regression pass on other benchmark families would still be useful, but it is not needed to conclude that the current fine-tuning recipe failed on the task we actually cared about.

## Implications
The main implication is simple:
- another generic proof-supervised fine-tuning run is not the right immediate next experiment

The stronger next direction is:
- theorem grounding through retrieval and repair

This is also supported by other evidence already present in the repo:
- theorem hints helped in earlier prompt-based experiments
- manual semantic-search experiments show that the theorem statement and the hallucinated theorem name together often retrieve useful real Mathlib theorems

So the next step should probably not be “train again and hope.”
It should be:
- retrieve grounded theorem candidates
- retry with those candidates in context
- and only later consider training on the repair traces if that works

## Fine-Tuning Ideas Worth Trying Later
If we return to fine-tuning, the next run should be designed around the failure mode that was observed here: incorrect theorem grounding. The most relevant options are below.

### 1. Hinted continuation training
Train on short proof continuations where the model is given the theorem statement together with one or a few useful theorem hints.

Why this is different from the failed run:
- the old run trained standalone theorem-block completion
- this would train the model to use grounded theorem information that is already present in the prompt

Why it may help:
- it targets the actual missing skill more directly
- it may teach the model to use retrieved or curated theorem context instead of inventing theorem names from memory

### 2. Targeted negative training against hallucinated theorem names
Construct training examples where the model is penalized for producing theorem-like names that are plausible but wrong in the current environment.

Why this is different from the failed run:
- the old run had only positive proof-imitation supervision
- this would add an explicit anti-hallucination signal

Why it may help:
- it directly attacks the failure mode seen in evaluation
- it may improve calibration about when a theorem reference is unsafe or unsupported

### 3. Retrieval-aware fine-tuning
Train the model in the same setting we expect to use at inference time: theorem statement plus a very small retrieved theorem context.

Why this is different from the failed run:
- the old run assumed the model should produce the full proof from its internal memory
- this would train the model to read and use external theorem context

Why it may help:
- it aligns training with the current retrieval-and-repair direction
- it may reduce the gap between benchmark prompts and training prompts

### 4. Small coherent Mathlib domain slice
Instead of training on a broad generic Mathlib corpus, restrict training to one coherent area of Mathlib where theorem families are tightly related.

Examples:
- polynomial theorems
- convexity and metric geometry
- quotient constructions

Why this is different from the failed run:
- the old run asked one small model to absorb a very broad theorem distribution at once
- this would test whether theorem grounding improves when the domain is narrower and internally coherent

Why it may help:
- it is a cheaper and cleaner test of whether targeted transfer is possible at all
- if this fails too, another broad generic fine-tune is even less likely to work

## Fine-Tuning Direction Summary
If fine-tuning is revisited, the most defensible next variants are:
- hinted continuation training
- targeted negative anti-hallucination training
- retrieval-aware fine-tuning
- small-domain fine-tuning on a coherent Mathlib slice

These all differ from the failed run in the same important way: they try to teach theorem grounding explicitly, rather than assuming it will emerge from generic standalone proof imitation.
