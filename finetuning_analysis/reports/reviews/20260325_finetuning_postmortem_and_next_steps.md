# Postmortem And Next Steps After The Rank Sweep

## Scope

This note combines five CPU-only tasks:

- a concise postmortem of the recent fine-tuning results
- a contamination / overlap audit using the artifacts currently present in the repo
- a proposal for the next benchmark direction
- a proposal for the next training dataset direction
- a concrete miniF2F/mathd regression plan

It is meant to replace vague “what should we try next?” discussion with one concrete decision document.

## Executive Summary

The recent evidence points to one main conclusion:

- the LoRA runs failed because the training objective and data distribution were badly mismatched to MSC-180 no-hint
- increasing rank from `16` to `64` or `128` did not fix that mismatch
- the next step should not be another generic proof-SFT run

The strongest surviving hypothesis is:

- the fine-tunes improved imitation of standalone Mathlib proof files, but degraded theorem grounding under sparse benchmark context

The highest-value next direction is therefore:

- build and evaluate a theorem-grounding-oriented benchmark and dataset, likely with retrieval in the loop, rather than another generic standalone-theorem imitation dataset

## 1. What The Recent Runs Actually Show

### Aggregate MSC-180 v2 no-hint results

| model | successes | solved problems | unknown attempts | unknown occurrences |
|---|---:|---:|---:|---:|
| base | `77 / 400` | `6 / 20` | `111 / 400` | `196` |
| `r=16` | `4 / 400` | `2 / 20` | `258 / 400` | `347` |
| `r=64` | `1 / 400` | `1 / 20` | `268 / 400` | `357` |
| `r=128` | `2 / 400` | `2 / 20` | `280 / 400` | `448` |

### What this rules out

It is no longer reasonable to believe that the main issue was simply:

- the adapter rank was too small

That hypothesis was tested directly.

If low rank were the main cause, `r=64` and `r=128` should have recovered at least a meaningful fraction of the gap. They did not.

### What this does not look like

The failure does **not** primarily look like:

- syntax collapse
- output truncation
- repetitive duplicate generations
- broken theorem headers

The multi-rank output-structure analysis shows the opposite:

- proof bodies remain diverse within each problem
- theorem headers still match the target statement
- Lean-looking tactic structure remains present

So the failure is mostly semantic:

- the model still writes Lean-like proofs, but reaches for badly grounded theorem names and local APIs

## 2. Most Likely Failure Mode

The most plausible causal chain is:

1. the training set was built from standalone validated Mathlib theorem files
2. those examples rewarded completing standalone theorem blocks in a Mathlib-style environment
3. the benchmark task instead asks for proof search under sparse context, with no theorem hint
4. the fine-tune therefore reinforced theorem-like proof continuation patterns without actually teaching robust theorem grounding
5. at inference time, the model became more willing to emit plausible-but-wrong theorem names

This is consistent with the observed hallucinations:

- they are often Mathlib-like, not random garbage
- higher rank produces different hallucinations, not fewer hallucinations
- the main regression is in unresolved names, not in surface fluency

## 3. What The Current Evidence Supports

### Strongly supported

- objective mismatch matters more than capacity
- validation loss on the transformed Mathlib distribution was not predictive of MSC-180 no-hint transfer
- theorem grounding is the main missing skill

### Still plausible, but not yet directly proven

- the training set contains examples close enough to benchmark problems to matter for contamination or memorization concerns
- a smaller, more targeted training objective will recover useful transfer

The contamination question matters, but the current repo state only lets us answer part of it exactly.

## 4. Contamination And Overlap Audit

## What could be checked exactly today

I could check benchmark-to-benchmark overlap exactly, because those artifacts are present locally.

### Exact overlap results

Using normalized theorem statements, and also a declaration-stripped normalization that removes the theorem name but keeps the rest of the formal statement:

- MSC-180 all `180` problems vs miniF2F valid `244`: `0` exact overlaps
- MSC-180 v2 A subset `20` problems vs miniF2F valid `244`: `0`
- MSC-180 v2 A subset vs miniF2F mathd-valid subset `130`: `0`
- MSC-180 v2 A subset vs miniF2F AMC-valid subset `45`: `0`
- miniF2F valid `244` vs miniF2F test `244`: `0`

So at the benchmark level, there is no sign of direct formal-statement duplication among the benchmark sets we care about.

### Why this section matters

This contamination check is not the main research bottleneck.

Its purpose is narrower:

- keep the next benchmark honest
- keep the next dataset from accidentally teaching the evaluation set
- avoid attributing progress to learning when it is really leakage

So this section should be treated as a guardrail, not as the main argument about why the current fine-tune failed.

### Useful side fact

MSC-180 already contains theorem-link metadata:

- `178 / 180` problems have non-empty `related_theorems`
- mean related-theorem count is about `2.01`
- median is `2`

That means MSC-180 is already closer to a theorem-grounding benchmark than it may have seemed.

## What could **not** be checked exactly today

The exact source file used to build the SFT dataset is not currently present in the local repo state:

- expected path: `mathlib_fine_tuning/data/raw/mathlib_standalone_theorems_validated.jsonl`
- current status: not present locally

This should be rechecked on the machine that still has the ignored local dataset payloads.

So I could not do an exact source-corpus-vs-benchmark statement overlap pass today.

That means:

- we do **not** currently have a complete exact contamination audit against the original fine-tuning source corpus
- we should not overclaim otherwise

## What can still be concluded despite that limitation

Even without the raw JSONL present, the retained metadata and earlier analysis already show:

- the training data came from a broad standalone Mathlib theorem corpus
- the builder used the full standalone theorem text as the assistant completion target
- the processed examples were optimized for standalone theorem completion, not benchmark-style theorem grounding
- the older review already established strong training/benchmark distribution mismatch

So the main current contamination risk is not obvious exact benchmark duplication. It is:

- building future datasets too close to MSC-180 or miniF2F without strong holdout rules

That is the contamination problem the next dataset design needs to solve explicitly.

## 5. What The Next Benchmark Should Measure

The next benchmark should isolate the skill that failed.

That skill is not “write Lean syntax.” It is:

- choose and use the right theorem under weak context

So the next benchmark should separate two things that are currently entangled in MSC-180 no-hint:

1. theorem grounding
2. full proof construction

## Recommendation: reuse MSC-180 rather than inventing a new benchmark immediately

Do **not** start by inventing a brand-new benchmark from scratch.

MSC-180 is already a good starting point because:

- it is the benchmark where the failure is clear
- it already has `related_theorems` metadata for almost all problems
- it spans many mathematical domains
- it is already embedded in the repo’s generation and verification workflows

That said, MSC-180 should probably not be the only benchmark family we rely on.

A good medium-term target is:

- primary benchmark: MSC-180 theorem grounding / hinted use / no-hint proving
- secondary split benchmark: something with an explicit valid/test split such as ProofNet, or a curated small Mathlib domain slice

The reason to keep a second benchmark family around is simple:

- MSC-180 is the right place to debug the current failure
- a split benchmark is the right place to check whether the next method generalizes cleanly

### Proposed benchmark structure

Use a staged benchmark, still anchored on MSC-180:

### Task A: theorem grounding from the goal

Input:
- header + theorem statement
- no proof hint

Target:
- a short ranked list of useful theorem candidates

Evaluation:
- recall@k against a curated target set
- maybe MRR if the target set is ranked

Important detail:
- the target set should be actual Lean/mathlib theorem names, not only the natural-language `related_theorems` labels

So this requires a small amount of curation.

If the curation burden is too high for all of MSC-180, start with a smaller subset first.

### Task B: hinted proof continuation

Input:
- header + theorem statement
- one correct theorem hint

Target:
- a short proof continuation or full proof

Evaluation:
- Lean verification success

This task isolates a different question:

- if the model is given the right theorem, can it actually use it?

That directly separates:

- theorem selection failure
from
- proof-construction failure

### Task C: no-hint full proving

Keep the existing MSC-180 no-hint benchmark as the final end-to-end task.

That gives a clean hierarchy:

- theorem grounding
- hinted theorem use
- no-hint full proof

## 6. What The Next Dataset Should Look Like

The next dataset should be designed around the failed skill.

It should **not** be another dataset whose main target is standalone theorem completion.

## Recommended supervision units

### 1. Goal/context -> theorem shortlist

Example shape:
- input: theorem header + target statement + maybe local context
- target: one or several useful theorem names

Why:
- directly trains theorem grounding
- much closer to the failure mode than full-proof imitation

### 2. Goal/context + theorem hint -> short continuation

Example shape:
- input: theorem header + target statement + one theorem hint
- target: first theorem-using tactic block, or a short continuation window

Why:
- teaches the model to use a theorem once grounded
- avoids requiring full-proof file imitation

### 3. Negative correction examples

Example shape:
- input: goal + wrong theorem-like name
- target: corrected theorem name, or “none of the above” style signal

Why:
- the current failure mode is overconfident plausible theorem names
- negative grounding supervision is therefore directly relevant

### 4. Optional: retrieval-style pairwise ranking data

Example shape:
- `(goal, theorem_a, theorem_b)` with one labeled as more useful

Why:
- if the model is going to be used together with retrieval, ranking supervision may matter more than pure generation

## What the dataset should **not** optimize for

Avoid making the main target:

- standalone theorem-block completion
- namespace scaffolding reproduction
- synthetic theorem headers like `manual_*`
- trailing namespace cleanup tokens such as repeated `end ...`

Those may be valid Lean completions, but they are not the skill we need.

## A practical first training setting

If the goal is to find out whether the model can learn theorem usage at all, the best first setting is probably not “all of Mathlib.”

A better first setting is:

- one relatively self-contained area
- simple theorems the base model can already solve sometimes
- retrieval available at training and evaluation time

That makes the experiment easier to interpret.

If a small, coherent domain slice does not improve theorem grounding there, another giant generic fine-tune is unlikely to help.

## 7. Contamination Rules For The Next Dataset

These should be explicit, not informal. They matter, but they are not more important than choosing the right benchmark family.

### Hard exclusions

- no exact MSC-180 problem statements in training
- no exact miniF2F/mathd evaluation statements in training
- no near-duplicate formal statements under simple normalization
- no direct benchmark answer leakage through hand-built theorem lists

### Split rules

Use a harder split than random example hashing.

Good options:
- hold out by benchmark family
- hold out by theorem cluster
- hold out by source file or topic cluster

Bad option:
- random line-level splitting only

Reason:
- theorem-grounding generalization is the thing we care about, so leakage through closely related statements is the actual risk

### Practical minimum rule

Before the next fine-tune, run an explicit overlap audit against:

- MSC-180 target benchmark set
- miniF2F valid/test
- any new theorem-grounding evaluation subset

That audit should be part of the pipeline, not a later manual check.

## 8. miniF2F/mathd Regression Plan

This still needs to be done, but the existing scripts should not be used blindly.

## Why the current mathd tooling is not enough

The current mathd variants pipeline under `src/benchmarks/mathd_variants/` is built around:

- `deepseek-ai/DeepSeek-Prover-V1.5-RL`
- `cot` / `noncot` / `wrong_proof` variants
- checkpoints under `experiments/mathd_runs/`

That does **not** answer the current regression question, which is:

- how do the V2 base model and the V2 LoRA adapters behave?

So the next regression check should **not** reuse that pipeline unchanged.

## What should be evaluated

Models:
- base V2
- `r=16`
- `r=64`
- `r=128`

Benchmark:
- the `mathd_*` subset of `benchmarks/processed/miniF2F_valid.json`
- size: `130` problems

Prompt style:
- same no-hint non-CoT style used in MSC-180 no-hint

This matters because we want to measure model change, not prompt-family change.

This regression is useful, but it is still a secondary sanity check.

It answers:

- did the fine-tune broadly damage proving ability outside MSC-180?

It does not answer:

- what benchmark and dataset we should build next

## Practical staged plan

### Stage 1: coarse regression screen

- benchmark: all `130` mathd valid problems
- attempts per problem: `4`
- models: base, `r16`, `r64`, `r128`

This is enough to tell whether the fine-tunes broadly degrade, preserve, or improve performance.

### Stage 2: deeper follow-up if needed

If the coarse screen shows something interesting:

- rerun a smaller selected subset with `20` attempts per problem
- focus on problems where the model rankings differ materially

## What needs to be added before that run exists

A V2-capable mathd runner, patterned after:
- `rag_experiments/scripts/run/run_msc180_v2_nohint.py`

It should support:
- base model runs
- `--adapter-dir` for LoRA runs
- raw JSON output
- later verification with the standard checker

A reasonable target location would be a new runner dedicated to V2 no-hint mathd evaluation.

## Minimum outputs to compare

For each model:
- raw attempts JSON
- verified JSON
- aggregate success rate
- problem solved count
- unknown-name rate
- top failed-attempt message heads

The same error-pattern analysis that was useful on MSC-180 should be applied here too.

## 9. Recommended Immediate Order Of Work

1. finish the paper review
2. recover the raw SFT source JSONL or an equivalent export so the contamination audit can be completed exactly
3. define the MSC-180 theorem-grounding benchmark subset
4. choose whether the secondary benchmark should be ProofNet, a small Mathlib domain slice, or both
5. define the targeted theorem-grounding dataset format
6. add the V2 no-hint mathd regression runner
7. run the miniF2F/mathd regression check
8. only then choose the next fine-tune

## 10. The Main Decision

The main decision after the rank sweep should be:

- do **not** spend the next GPU budget on another generic LoRA proof-SFT run

Instead:

- spend the next CPU budget on benchmark and dataset design
- spend the next GPU budget on a small theorem-grounding-oriented experiment

That is the shortest path that is still consistent with the evidence we now have.
