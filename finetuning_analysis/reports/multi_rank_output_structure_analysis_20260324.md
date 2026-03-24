# Multi-Rank Output Structure Analysis

## Headline
- `r16`: `4/400` successes, `281/400` attempts with unknowns, `342` distinct unknown names, unique parsed proofs per problem mean `19.95`, unique first proof steps mean `16.85`
- `r64`: `1/400` successes, `286/400` attempts with unknowns, `344` distinct unknown names, unique parsed proofs per problem mean `20`, unique first proof steps mean `17.7`
- `r128`: `2/400` successes, `295/400` attempts with unknowns, `402` distinct unknown names, unique parsed proofs per problem mean `20`, unique first proof steps mean `17.2`

## Structural Findings
- None of the three LoRA runs collapsed into literal duplicate outputs. Every run keeps about `20/20` unique parsed proofs per problem.
- The theorem header still matches the target statement in essentially all attempts (`theorem_name_match_rate = 1.0`).
- The collapse is semantic rather than textual: many attempts within a problem differ in wording but reuse the same small invented mini-API or theorem family.
- Higher-rank runs are slightly longer on average than `r16`, so the failure is not a truncation or empty-output issue.

## r16
- Parsed proof length mean/median/p90: `674.5` / `477.0` / `1217`
- Raw output length mean/median/p90: `1019.4` / `822.5` / `1653`
- Unique parsed proofs per problem: `{'min': 19, 'median': 20.0, 'mean': 19.95, 'max': 20}`
- Unique first proof steps per problem: `{'min': 11, 'median': 18.0, 'mean': 16.85, 'max': 20}`
- Top proof keywords:
- `rw [`: `223` attempts
- `simp`: `200` attempts
- `have `: `143` attempts
- `obtain `: `119` attempts
- `rcases`: `51` attempts
- `linarith`: `25` attempts
- `calc`: `16` attempts
- `omega`: `8` attempts
- `aesop`: `5` attempts
- Top first proof steps:
- `classical`: `24`
- `constructor`: `18`
- `ext x`: `5`
- `intro p q hp hq hfp hfq`: `5`
- `rintro d₁ d₂ ⟨h₁, h₂, h₃, h₄⟩ ⟨h₅, h₆, h₇, h₈⟩`: `4`
- `intro p q hp hq hp0 hq0`: `4`
- `rw [convex_iff_forall_pos]`: `4`
- `ext a`: `3`
- `haveI := Fact.mk hp`: `3`
- `apply algHom_ext`: `2`
- Dominant unknown names by problem:
- `no-hint/MSC-180_26_002` -> `exists_isLUB` (`8` occurrences)
- `no-hint/MSC-180_12_001` -> `map₂` (`5` occurrences)
- `no-hint/MSC-180_14_003` -> `root_multiplicity_factorization` (`5` occurrences)
- `no-hint/MSC-180_08_001` -> `adjoin_induction` (`4` occurrences)
- `no-hint/MSC-180_05_003` -> `excedance_coexcedance_card` (`3` occurrences)
- `no-hint/MSC-180_12_002` -> `chinese_remainder_theorem` (`3` occurrences)
- `no-hint/MSC-180_14_001` -> `ker` (`3` occurrences)
- `no-hint/MSC-180_15_003` -> `le_succ` (`3` occurrences)

## r64
- Parsed proof length mean/median/p90: `737.8` / `528.0` / `1379`
- Raw output length mean/median/p90: `1082.7` / `881.0` / `1800`
- Unique parsed proofs per problem: `{'min': 20, 'median': 20.0, 'mean': 20, 'max': 20}`
- Unique first proof steps per problem: `{'min': 12, 'median': 18.5, 'mean': 17.7, 'max': 20}`
- Top proof keywords:
- `rw [`: `256` attempts
- `simp`: `226` attempts
- `have `: `166` attempts
- `obtain `: `138` attempts
- `rcases`: `57` attempts
- `linarith`: `35` attempts
- `calc`: `28` attempts
- `omega`: `8` attempts
- `aesop`: `5` attempts
- Top first proof steps:
- `classical`: `20`
- `constructor`: `10`
- `intro d₁ d₂ h₁ h₂`: `7`
- `ext x`: `6`
- `haveI := Fact.mk hp`: `4`
- `intro p q hp hq hfp hfq`: `4`
- `intro x hx y hy a b ha hb hab`: `3`
- `rw [convex_iff_forall_pos]`: `3`
- `by_cases hf : f = 0`: `2`
- `rw [Int.ModEq, Int.ModEq]`: `2`
- Dominant unknown names by problem:
- `no-hint/MSC-180_12_001` -> `Polynomial.emultiplicity` (`5` occurrences)
- `no-hint/MSC-180_15_003` -> `row_column_factorization` (`5` occurrences)
- `no-hint/MSC-180_05_003` -> `card_map` (`4` occurrences)
- `no-hint/MSC-180_08_003` -> `some` (`4` occurrences)
- `no-hint/MSC-180_68_002` -> `Int.xgcd` (`4` occurrences)
- `no-hint/MSC-180_14_001` -> `mem_ker` (`3` occurrences)
- `no-hint/MSC-180_28_003` -> `box` (`3` occurrences)
- `no-hint/MSC-180_08_001` -> `Set.leftInvOn_of_injective` (`2` occurrences)

## r128
- Parsed proof length mean/median/p90: `761.4` / `541.0` / `1531`
- Raw output length mean/median/p90: `1106.3` / `897.5` / `1982`
- Unique parsed proofs per problem: `{'min': 20, 'median': 20.0, 'mean': 20, 'max': 20}`
- Unique first proof steps per problem: `{'min': 11, 'median': 18.5, 'mean': 17.2, 'max': 20}`
- Top proof keywords:
- `rw [`: `255` attempts
- `simp`: `235` attempts
- `have `: `174` attempts
- `obtain `: `118` attempts
- `rcases`: `60` attempts
- `calc`: `31` attempts
- `linarith`: `29` attempts
- `omega`: `5` attempts
- `aesop`: `2` attempts
- Top first proof steps:
- `classical`: `20`
- `constructor`: `15`
- `ext x`: `7`
- `ext a`: `5`
- `intro x hx y hy a b ha hb hab`: `4`
- `haveI := Classical.decEq G`: `3`
- `use A.rank`: `3`
- `intro p q hp hq hfp hfq`: `3`
- `intro p q hp hq fp fq`: `3`
- `rw [convex_iff_forall_pos]`: `3`
- Dominant unknown names by problem:
- `no-hint/MSC-180_90_001` -> `le` (`18` occurrences)
- `no-hint/MSC-180_65_001` -> `le` (`16` occurrences)
- `no-hint/MSC-180_14_003` -> `root_multiplicity_factorization` (`6` occurrences)
- `no-hint/MSC-180_12_002` -> `chineseRemainder` (`5` occurrences)
- `no-hint/MSC-180_65_003` -> `trans` (`5` occurrences)
- `no-hint/MSC-180_05_003` -> `card_compl` (`4` occurrences)
- `no-hint/MSC-180_12_001` -> `Polynomial.eq_of_sub_eq_zero` (`4` occurrences)
- `no-hint/MSC-180_14_001` -> `AddMonoidHom.quotientKerEquivOfSurjective` (`4` occurrences)

## Conclusions
- The outputs still look syntactically like Lean proofs: non-empty theorem blocks, diverse proof bodies, and normal tactic vocabulary remain present.
- The main collapse is semantic concentration around a problem-specific invented theorem or API, not flat duplication or parser garbage.
- `r64` and `r128` remain highly similar in style; the higher-rank model is slightly longer and slightly more successful, but also more hallucination-heavy.
- So the failure mode after increasing rank is still “confident explicit proof with badly grounded names,” not “nonsensical broken text.”
