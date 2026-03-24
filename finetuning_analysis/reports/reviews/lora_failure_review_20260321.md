# Review: Why the LoRA fine-tune failed on MSC-180 no-hint

## Scope
This note reviews likely causes of the failure of the tactic-only Mathlib LoRA run on:

- `rag_experiments/outputs/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json`
- `rag_experiments/outputs/20260313_msc180-v2-nohint_lora_deepseekv2_7b_lean4-15_verified.json`

Headline result from the benchmark:
- Base: `77/400` successful attempts, `6/20` problems solved
- LoRA: `4/400` successful attempts, `2/20` problems solved

Related summary:
- `finetuning_analysis/reports/msc180_nohint/msc180_nohint_base_vs_lora_20260313.md`

## Findings

### 1. The training distribution is badly mismatched to the benchmark distribution
This is the most likely root cause.

The SFT dataset was built from validated standalone Mathlib theorem files in `mathlib_fine_tuning/build_tactic_sft_dataset.py`.
Key behavior:
- the prompt is built from a reconstructed standalone theorem environment plus `:= by\n  sorry`: `mathlib_fine_tuning/build_tactic_sft_dataset.py:143`
- the assistant completion is the full theorem text in a fenced block: `mathlib_fine_tuning/build_tactic_sft_dataset.py:151`
- the prompt/completion are chat-formatted with the real tokenizer template: `mathlib_fine_tuning/build_tactic_sft_dataset.py:155`

The problem is what these training examples actually look like.

Measured on the processed training set:
- `100%` of completions contain `manual_` theorem names
- `95.66%` of completions contain trailing `end ...` lines
- `78.24%` of prompts contain `namespace`
- `55.33%` of prompts contain `section`
- `87.93%` of prompts contain `open`
- `92.47%` of prompts contain `variable`
- average prompt block length: `403.4` chars

By contrast, the MSC-180 no-hint benchmark prompts are much simpler:
- `0%` contain `namespace`
- `0%` contain `section`
- `50%` contain `open`
- `5%` contain `variable`
- average prompt block length: `260.9` chars

So the model was trained mostly on:
- long Mathlib-internal standalone contexts
- renamed theorem declarations (`manual_*`)
- namespace-scaffolded theorem files
- completions that often close namespaces explicitly

But it was evaluated on:
- short benchmark prompts
- almost no namespace/section structure
- novel theorem names
- no retrieved theorem hints

This is a strong domain mismatch. The model learned to imitate "Mathlib standalone proof files," not to solve short no-hint proving tasks.

### 2. The fine-tune appears to have harmed theorem-name grounding, not Lean surface fluency
This is the clearest observed behavioral regression.

The LoRA run has far more unknown-name failures:
- base unknown-attempt rate: `27.75%`
- LoRA unknown-attempt rate: `64.50%`

Among failed attempts:
- base: `34.37%` include `unknown`
- LoRA: `65.15%` include `unknown`

Representative hallucinated or non-resolving names from the LoRA run:
- `exists_isLUB`
- `isField_of_surjective`
- `isField_iff_isField_of_quotient`
- `MeasureTheory.measureOf_add_measureOf_of_almost_disjoint`
- `Int.gcd_dvd`
- `adjoin_eq_top_iff_range_eq_top`

These are not random garbage strings. They are plausible Mathlib-style theorem names.
That strongly suggests the LoRA fine-tune shifted the model toward emitting theorem-like names that "sound right" in Mathlib, but do not actually exist in the benchmark environment.

This matches the dataset construction:
- the target completion is the full theorem with proof, so the model is rewarded for reproducing theorem invocations inside finished Mathlib-style proofs
- nothing in the objective directly teaches the model how to stay calibrated on theorem names in a new sparse-context problem

### 3. Validation loss was not informative for the benchmark task
The training run itself looked healthy.

Training config in `mathlib_fine_tuning/runs/deepseek_noncot_tactic_lora_v1/train_config.json`:
- train rows: `55712`
- valid rows: `1155`
- batch size: `1`
- gradient accumulation: `8`
- learning rate: `5e-5`
- epochs: `1.0`
- LoRA rank: `16`

Final metrics:
- train loss: `0.29945`
- eval loss: `0.27301`

So optimization was stable. The run did not obviously diverge.

But the validation split was just another slice of the same transformed Mathlib distribution. It measured:
- how well the model imitates held-out Mathlib standalone theorem completions

It did **not** measure:
- theorem-name grounding on new no-hint problems
- proof search under sparse context
- benchmark transfer performance

So the monotone decrease in validation loss was real, but it was measuring the wrong thing for this downstream task.

This is why the run can look good in training and still fail badly on MSC-180.

### 4. The dataset includes synthetic artifacts that likely hurt transfer
The processed dataset is not raw Mathlib source. It is derived from reconstructed standalone theorem files.

Two synthetic artifacts stand out:

#### 4a. Theorem names are all rewritten to `manual_*`
Examples from the processed dataset:
- `manual_map_add_nsmul`
- `manual_map_add_nat`
- `manual_map_const`

This means the model was trained for one epoch on a world where theorem names systematically look like `manual_*`.

Even though the benchmark prompt provides the target theorem name explicitly and the model usually copies it, this is still likely harmful. It teaches the model a non-natural theorem-header distribution and moves it further away from real benchmark problems.

#### 4b. Most completions include trailing `end ...` lines
About `95.66%` of training completions contain trailing `end ...` lines.

That means the assistant target is often not just:
- theorem statement + proof

but:
- theorem statement + proof + namespace cleanup

This is valid Lean, but it is not what the benchmark really wants the model to focus on. It adds extra completion structure that is mostly irrelevant to solving the theorem.

### 5. The training objective optimized "proof imitation" more than "proof selection"
The current training target is the full theorem block inside a fenced `lean4` completion.

This is coherent with the repo interface, but it strongly emphasizes:
- reproducing a completed proof in a context where the right supporting lemmas already exist in the model's memory

The benchmark task is different:
- the model must decide which lemmas to use under much weaker contextual guidance
- it gets no retrieval hint in the no-hint setup

So the objective probably improved local style and theorem-body imitation, but not the harder skill that mattered for MSC-180: selecting the right theorem names under uncertainty.

### 6. The generation path is probably not the main culprit
The generation code was patched to use the proper chat template:
- `src/prover_generation/batch_generation.py:25`
- it now uses `tokenizer.apply_chat_template(..., add_generation_prompt=True)`

This change affected both the base and LoRA runs the same way.
So for the **comparison between those two runs**, generation-path mismatch is unlikely to explain the regression.

The benchmark runner itself is simple and fair:
- `rag_experiments/run_msc180_v2_nohint.py`
- same prompt config for both models: `DeepSeekProverV2HintNonCoTPromptConfig`
- same attempts, temperature, top-p, and max-new-tokens
- only difference is whether an adapter is loaded: `rag_experiments/run_msc180_v2_nohint.py:144`

So the comparison result should be treated as real.

## Lower-confidence contributing factors

### 7. Tactic-only filtering may have narrowed the training distribution too much
The dataset builder kept only outer tactic-style proofs by requiring the proof to start with `by`:
- `mathlib_fine_tuning/build_tactic_sft_dataset.py:134`
- `mathlib_fine_tuning/build_tactic_sft_dataset.py:135`

That cut out a large fraction of validated Mathlib theorems.
This may have made the model more brittle by overfitting to one proof surface style.

This is probably secondary compared with the theorem-name grounding issue, but it is a plausible contributor.

### 8. The learning rate may still have been aggressive relative to the task mismatch
`5e-5` for one epoch of LoRA is not unreasonable.
The run was stable, so there is no strong evidence that the LR itself was bad.

Still, when the fine-tune target is poorly aligned with the evaluation target, even a stable update can move the model away from the benchmark optimum.

So I would not call LR the main cause, but I also would not rule out that a smaller update could have reduced the regression.

## What is *not* the main explanation

### Not a simple training failure
The run completed cleanly and losses were sensible.
This is not a "the model blew up" story.

### Not a verification bug
The output files were later verified with the same checking pipeline for both models.
The large difference in results is not explained by a checker mismatch.

### Not just verbosity
The LoRA outputs are only somewhat shorter than the base outputs.
The dominant issue is unresolved names and bad proof choices, not output length.

## Most likely causal chain
1. We fine-tuned on standalone Mathlib theorem files, not benchmark-style problems.
2. Those examples contained heavy namespace/context scaffolding and synthetic `manual_*` theorem headers.
3. The objective rewarded reproducing compact theorem-completion patterns using plausible Mathlib lemma names.
4. On MSC-180 no-hint, the model had to choose names without retrieval support.
5. It became overconfident about theorem names that looked plausible but did not resolve.
6. Benchmark performance collapsed, even though validation loss improved.

## Strongest current hypothesis
The failure is primarily a **distribution/objective mismatch**, not a low-level bug in the training script.

In one sentence:
- the fine-tune improved imitation of reconstructed Mathlib proof files, but degraded theorem-name grounding in sparse no-hint benchmark settings.

## Highest-value next changes
If this line of work continues, the highest-value changes would likely be:

1. Remove `manual_*` names from the training targets.
2. Remove trailing `end ...` lines from assistant completions.
3. Train on examples closer to the target task format, not just standalone library proofs.
4. Include theorem-hint/retrieval context during training if the target evaluation will use it.
5. Track a small benchmark-aligned validation set during training, not just corpus loss.

## Immediate practical conclusion
The current LoRA adapter should be treated as a negative benchmark result.

The pipeline worked technically. The fine-tune objective did not transfer to MSC-180 no-hint.
