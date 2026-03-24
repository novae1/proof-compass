# MSC-180 v2 No-Hint: Base vs LoRA (2026-03-13)

## Scope
This compares two verified no-hint MSC-180 v2 A runs:

- Base model: `rag_experiments/outputs/20260313_msc180-v2-nohint_base_deepseekv2_7b_lean4-15_verified.json`
- Fine-tuned LoRA model: `rag_experiments/outputs/20260313_msc180-v2-nohint_lora_deepseekv2_7b_lean4-15_verified.json`

Both runs use:
- no-hint only
- non-CoT prompt
- 20 attempts per problem
- 20 problems total
- later verification via `scripts/checking_problems.py`

Machine-readable summary:
- `finetuning_analysis/reports/msc180_nohint/msc180_nohint_base_vs_lora_20260313.json`

## Headline result
The fine-tuned LoRA model is much worse than the base model on this benchmark.

### Aggregate metrics
| Model | Successful attempts | Attempt pass rate | Problems solved | Problem pass@20 | Attempts with `unknown` |
|---|---:|---:|---:|---:|---:|
| Base | 77 / 400 | 19.25% | 6 / 20 | 30.0% | 111 / 400 |
| LoRA | 4 / 400 | 1.0% | 2 / 20 | 10.0% | 258 / 400 |

### Immediate interpretation
The LoRA model does not just underperform slightly. It collapses on this benchmark.

The strongest signal is the jump in unknown-name errors:
- Base unknown-attempt rate: 27.75%
- LoRA unknown-attempt rate: 64.50%

Among failed attempts:
- Base: 34.37% contain `unknown`
- LoRA: 65.15% contain `unknown`

This strongly suggests the fine-tune pushed the model toward producing theorem-like Lean text that references names that do not actually exist in the benchmark context.

## Where the base model still works
The base model solves 6 problems:
- `no-hint/MSC-180_12_003` with 16/20 successful attempts
- `no-hint/MSC-180_14_001` with 14/20
- `no-hint/MSC-180_20_001` with 19/20
- `no-hint/MSC-180_26_002` with 19/20
- `no-hint/MSC-180_28_003` with 3/20
- `no-hint/MSC-180_68_002` with 6/20

The LoRA model solves only 2 problems:
- `no-hint/MSC-180_14_001` with 1/20
- `no-hint/MSC-180_20_001` with 3/20

## Biggest regressions
Per-problem success deltas (LoRA minus base):

- `no-hint/MSC-180_26_002`: 19/20 -> 0/20 (delta -19)
- `no-hint/MSC-180_20_001`: 19/20 -> 3/20 (delta -16)
- `no-hint/MSC-180_12_003`: 16/20 -> 0/20 (delta -16)
- `no-hint/MSC-180_14_001`: 14/20 -> 1/20 (delta -13)
- `no-hint/MSC-180_68_002`: 6/20 -> 0/20 (delta -6)
- `no-hint/MSC-180_28_003`: 3/20 -> 0/20 (delta -3)

No problem improved under LoRA.

## Error-pattern differences
### Base: main failed-attempt patterns
Most common error heads in the base run:
- `unsolved goals` (147)
- `linarith failed to find a contradiction` (133)
- `application type mismatch` (73)
- `type mismatch` (62)
- `tactic 'rewrite' failed, did not find instance of the pattern in the target expression` (38)
- `failed to synthesize` (29)
- `invalid field notation...` (29)

This is what a strong but imperfect prover usually looks like: many attempts are structurally reasonable Lean proofs that fail during refinement or closing goals.

### LoRA: main failed-attempt patterns
Most common error heads in the LoRA run:
- `application type mismatch` (61)
- `unsolved goals` (57)
- `no goals to be solved` (55)
- `tactic 'rewrite' failed, equality or iff proof expected` (50)
- `tactic 'rewrite' failed, did not find instance of the pattern in the target expression` (43)
- `invalid field notation...` (38)
- `function expected at` (21)
- `type mismatch` (18)

The structurally interesting difference is in the explicit unknown-name errors. Frequent LoRA-only unknown targets include:
- `map₂` (5)
- `root_multiplicity_factorization` (5)
- `exists_isLUB` (5)
- `adjoin_induction` (4)
- `excedance_coexcedance_card` (3)
- `chinese_remainder_theorem` (3)
- `MeasureTheory.Lebesgue.volume` (3)

These look like plausible mathlib-style names, but they do not resolve in the benchmark environment.

## Representative examples
### 1. `MSC-180_26_002`: base concise and correct, LoRA hallucinates missing names
Base successful proof:
```lean
 theorem exists_sup_of_bddAbove {A : Set ℝ} (hne : A.Nonempty) (hbd : BddAbove A) :
     ∃ s : ℝ, IsLUB A s := by
   refine' ⟨sSup A, _⟩
   exact isLUB_csSup hne hbd
```

Representative LoRA failure uses nonexistent names and broken field notation:
- `Set.BddAbove`
- `exists_isLUB`

The generated proof starts with:
```lean
 theorem exists_sup_of_bddAbove {A : Set ℝ} (hne : A.Nonempty) (hbd : BddAbove A) :
     ∃ s : ℝ, IsLUB A s := by
   have hne_lb : A.Nonempty := hne
   have hne_ub : A.BddAbove := hbd
   let lub := Classical.choose (exists_isLUB A)
```

This is a strong example of the failure mode: theorem-like but non-resolving names.

### 2. `MSC-180_12_003`: LoRA invents field/maximal-ideal lemmas
Base successful proof:
```lean
 theorem maximal_ideal_iff_quotient_field {R : Type*} [CommRing R] [Nontrivial R]
     (M : Ideal R) :
     M.IsMaximal ↔ IsField (R ⧸ M) := by
   constructor
   · intro h
     exact @Field.toIsField _ (Ideal.Quotient.field M)
   · intro h
     exact?
```

Representative LoRA failure uses unknown identifiers:
- `isField_of_surjective`
- `isField_iff_isField_of_quotient`

Generated proof:
```lean
 theorem maximal_ideal_iff_quotient_field {R : Type*} [CommRing R] [Nontrivial R]
     (M : Ideal R) :
     M.IsMaximal ↔ IsField (R ⧸ M) := by
   constructor
   · exact isField_of_surjective _
   · intro h
     obtain ⟨n, hn⟩ := @isField_iff_isField_of_quotient _ _ h
```

Again: the output looks plausible, but the names are wrong.

### 3. `MSC-180_20_001`: one of the few problems where LoRA still works sometimes
Base successful proof:
```lean
 theorem my_favorite_theorem {G : Type*} [CommGroup G] [Fintype G]
     (hG : Fintype.card G ≠ 0) (p : ℕ) (hp : Nat.Prime p)
     (hG1 : p ∣ Fintype.card G) :
     ∃ x : G, orderOf x = p := by
   haveI := Fact.mk hp
   classical
   obtain ⟨x, hx⟩ := exists_prime_orderOf_dvd_card p hG1
   exact ⟨x, hx⟩
```

LoRA successful proof:
```lean
 theorem my_favorite_theorem {G : Type*} [CommGroup G] [Fintype G]
     (hG : Fintype.card G ≠ 0) (p : ℕ) (hp : Nat.Prime p)
     (hG1 : p ∣ Fintype.card G) :
     ∃ x : G, orderOf x = p := by
   haveI := Fact.mk hp
   exact exists_prime_orderOf_dvd_card p hG1
```

So the LoRA model is still capable of short correct proofs in some cases. The problem is consistency.

## Output-shape differences
Average output sizes:

| Metric | Base | LoRA |
|---|---:|---:|
| mean raw output length | 1087.6 chars | 1019.4 chars |
| median raw output length | 1020.5 | 822.5 |
| mean parsed proof length | 742.8 chars | 674.5 chars |
| median parsed proof length | 600.5 | 477.0 |
| mean generation time | 1.746s | 3.770s |
| median generation time | 1.545s | 2.398s |

The LoRA outputs are slightly shorter on average, but they are not dramatically shorter. The main issue is quality, not verbosity.

The LoRA model is also slower here, roughly 2x in mean generation time.

## Best current hypothesis
The fine-tune on tactic-style standalone mathlib theorems appears to have improved local proof-pattern imitation, but harmed theorem-name calibration in this benchmark setting.

Likely mechanism:
- training distribution heavily rewards producing compact mathlib-flavored proofs
- benchmark prompts do not include theorem hints
- the model fills gaps by reaching for plausible theorem names
- many of those names are slightly wrong, obsolete, or nonexistent in the actual benchmark context

So the regression is consistent with:
- better Lean-like surface form
- worse name grounding under no-hint theorem proving

## Practical takeaway
For this project, the current LoRA checkpoint should be treated as a negative result on MSC-180 v2 no-hint.

It is still useful:
- it shows the pipeline works end-to-end
- it gives a concrete failure mode to target
- it suggests future fine-tuning should probably include stronger constraints around theorem-name grounding, not just proof-style imitation

## Suggested next analyses
1. Compare raw generations for the same prompt/attempt index on a few regressed problems.
2. Measure whether the LoRA model emits more globally-ambiguous or nonexistent theorem names than the base model.
3. Test whether theorem-statement hints narrow the gap, since that may reduce unguided name hallucination.
4. Consider a dataset variant that keeps theorem references more explicit or includes retrieval/hint context during training.
