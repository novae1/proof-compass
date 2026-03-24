# Multi-Rank Hallucination Analysis

## Scope
- theorem index: `/home/nicolas/Documents/lean_project/data/mathlib_theorem_index.jsonl`
- r16: `rag_experiments/outputs/20260313_msc180-v2-nohint_lora_deepseekv2_7b_lean4-15_verified.json`
- r64: `rag_experiments/outputs/20260323_msc180-v2-nohint_lora_r64_deepseekv2_7b_lean4-15_verified.json`
- r128: `rag_experiments/outputs/20260323_msc180-v2-nohint_lora_r128_deepseekv2_7b_lean4-15_verified.json`

## Headline
- `r16`: `4/400` successes, `342` distinct unknown names, `428` unknown occurrences, theorem-like exact/normalized/near/nonmatch occurrences = `85` / `11` / `68` / `244`
- `r64`: `1/400` successes, `344` distinct unknown names, `402` unknown occurrences, theorem-like exact/normalized/near/nonmatch occurrences = `76` / `12` / `86` / `213`
- `r128`: `2/400` successes, `402` distinct unknown names, `531` unknown occurrences, theorem-like exact/normalized/near/nonmatch occurrences = `78` / `19` / `116` / `231`

## Overlap Of Distinct Unknown Names
- `r16`: r16: 342 (J=1.0), r64: 25 (J=0.0378), r128: 26 (J=0.0362)
- `r64`: r16: 25 (J=0.0378), r64: 344 (J=1.0), r128: 34 (J=0.0478)
- `r128`: r16: 26 (J=0.0362), r64: 34 (J=0.0478), r128: 402 (J=1.0)

## r16
- Top theorem-like unknown names:
- `exists_isLUB`: `8` occurrences, `exact_short_theorem_ambiguous`, candidates: `IsCompact.exists_isLUB, Real.exists_isLUB`
- `map₂`: `5` occurrences, `exact_short_theorem_ambiguous`, candidates: `CategoryTheory.OverPresheafAux.MakesOverArrow.map₂, Filter.NeBot.map₂, Hyperreal.IsSt.map₂`
- `root_multiplicity_factorization`: `5` occurrences, `no_convincing_theorem_match`
- `deriv`: `5` occurrences, `exact_short_theorem_ambiguous`, candidates: `AffineMap.deriv, AnalyticOn.deriv, AnalyticOnNhd.deriv`
- `adjoin_induction`: `4` occurrences, `exact_short_theorem_ambiguous`, candidates: `Algebra.adjoin_induction, IntermediateField.adjoin_induction, NonUnitalAlgebra.adjoin_induction`
- `excedance_coexcedance_card`: `3` occurrences, `no_convincing_theorem_match`
- `mem_univ`: `3` occurrences, `exact_short_theorem_ambiguous`, candidates: `Class.mem_univ, Finset.mem_univ, Semiquot.mem_univ`
- `modByMVar_spec`: `3` occurrences, `no_convincing_theorem_match`
- `chinese_remainder_theorem`: `3` occurrences, `no_convincing_theorem_match`
- `elim`: `3` occurrences, `exact_short_theorem_ambiguous`, candidates: `BEx.elim, ContravariantClass.elim, CovariantClass.elim`
- `le_succ`: `3` occurrences, `exact_short_theorem_ambiguous`, candidates: `Order.le_succ, SuccOrder.le_succ, WCovBy.le_succ`
- `isLeast_csSup`: `3` occurrences, `no_convincing_theorem_match`
- Category breakdown over theorem-like unknown occurrences:
- `no_convincing_theorem_match`: `244` occurrences
- `exact_short_theorem_ambiguous`: `73` occurrences
- `near_theorem_match`: `68` occurrences
- `normalized_theorem_match_unique`: `9` occurrences
- `exact_short_theorem_unique`: `7` occurrences
- `exact_full_theorem`: `5` occurrences
- `normalized_theorem_match_ambiguous`: `2` occurrences
- Problem-specific dominant unknowns:
- `no-hint/MSC-180_26_002` -> `exists_isLUB` (`8` occurrences)
- `no-hint/MSC-180_12_001` -> `map₂` (`5` occurrences)
- `no-hint/MSC-180_14_003` -> `root_multiplicity_factorization` (`5` occurrences)
- `no-hint/MSC-180_08_001` -> `adjoin_induction` (`4` occurrences)
- `no-hint/MSC-180_05_003` -> `excedance_coexcedance_card` (`3` occurrences)
- `no-hint/MSC-180_12_002` -> `chinese_remainder_theorem` (`3` occurrences)
- `no-hint/MSC-180_14_001` -> `ker` (`3` occurrences)
- `no-hint/MSC-180_15_003` -> `le_succ` (`3` occurrences)

## r64
- Top theorem-like unknown names:
- `some`: `5` occurrences, `exact_short_theorem_ambiguous`, candidates: `Nat.Partrec.some, Partrec.some`
- `Polynomial.emultiplicity`: `5` occurrences, `near_theorem_match`, candidates: `Polynomial.rootMultiplicity_C (0.88), Polynomial.rootMultiplicity_add (0.846), Polynomial.rootMultiplicity_mul (0.846)`
- `row_column_factorization`: `5` occurrences, `no_convincing_theorem_match`
- `card_map`: `4` occurrences, `exact_short_theorem_ambiguous`, candidates: `Finset.card_map, Multiset.card_map`
- `Int.xgcd`: `4` occurrences, `no_convincing_theorem_match`
- `Euclid.gcd`: `3` occurrences, `no_convincing_theorem_match`
- `mem_ker`: `3` occurrences, `exact_short_theorem_ambiguous`, candidates: `AddMonoidHom.mem_ker, Filter.mem_ker, IsAddGroupHom.mem_ker`
- `mem_filter`: `2` occurrences, `exact_short_theorem_ambiguous`, candidates: `BoxIntegral.Prepartition.mem_filter, BoxIntegral.TaggedPrepartition.mem_filter, Finset.mem_filter`
- `mem_univ`: `2` occurrences, `exact_short_theorem_ambiguous`, candidates: `Class.mem_univ, Finset.mem_univ, Semiquot.mem_univ`
- `Set.leftInvOn_of_injective`: `2` occurrences, `near_theorem_match`, candidates: `Set.injOn_of_injective (0.857)`
- `algHom_ext`: `2` occurrences, `exact_short_theorem_ambiguous`, candidates: `AddMonoidAlgebra.algHom_ext, AdjoinRoot.algHom_ext, Algebra.EssFiniteType.algHom_ext`
- `le_sup_of_le_left_of_le_right`: `2` occurrences, `no_convincing_theorem_match`
- Category breakdown over theorem-like unknown occurrences:
- `no_convincing_theorem_match`: `213` occurrences
- `near_theorem_match`: `86` occurrences
- `exact_short_theorem_ambiguous`: `57` occurrences
- `exact_short_theorem_unique`: `15` occurrences
- `normalized_theorem_match_unique`: `8` occurrences
- `exact_full_theorem`: `4` occurrences
- `normalized_theorem_match_ambiguous`: `4` occurrences
- Problem-specific dominant unknowns:
- `no-hint/MSC-180_12_001` -> `Polynomial.emultiplicity` (`5` occurrences)
- `no-hint/MSC-180_15_003` -> `row_column_factorization` (`5` occurrences)
- `no-hint/MSC-180_05_003` -> `card_map` (`4` occurrences)
- `no-hint/MSC-180_08_003` -> `some` (`4` occurrences)
- `no-hint/MSC-180_68_002` -> `Int.xgcd` (`4` occurrences)
- `no-hint/MSC-180_14_001` -> `mem_ker` (`3` occurrences)
- `no-hint/MSC-180_28_003` -> `box` (`3` occurrences)
- `no-hint/MSC-180_08_001` -> `Set.leftInvOn_of_injective` (`2` occurrences)

## r128
- Top theorem-like unknown names:
- `root_multiplicity_factorization`: `6` occurrences, `no_convincing_theorem_match`
- `chineseRemainder`: `5` occurrences, `near_theorem_match`, candidates: `chineseRemainder'_lt_lcm (0.865), chineseRemainder_lt_mul (0.865)`
- `trans`: `5` occurrences, `exact_full_theorem`, candidates: `trans`
- `card_compl`: `4` occurrences, `exact_short_theorem_unique`, candidates: `Finset.card_compl`
- `Polynomial.eq_of_sub_eq_zero`: `4` occurrences, `near_theorem_match`, candidates: `Polynomial.eq_zero_of_eq_zero (0.851)`
- `AddMonoidHom.quotientKerEquivOfSurjective`: `4` occurrences, `no_convincing_theorem_match`
- `univ`: `3` occurrences, `exact_short_theorem_ambiguous`, candidates: `AbsConvex.univ, Absorbs.univ, AddAction.IsBlock.univ`
- `coe_comp`: `3` occurrences, `exact_short_theorem_ambiguous`, candidates: `AddCommGrp.coe_comp, AddCommMonCat.coe_comp, AddConstMap.coe_comp`
- `coe_toRingHom`: `3` occurrences, `exact_short_theorem_ambiguous`, candidates: `AlgHom.coe_toRingHom, RingEquiv.coe_toRingHom`
- `ring_hom.map_zero`: `3` occurrences, `normalized_theorem_match_ambiguous`, candidates: `RingHom.map_zero, RingHom.map_zero'`
- `Subalgebra.coe_subtype`: `3` occurrences, `near_theorem_match`, candidates: `StarSubalgebra.coe_subtype (0.909), Subalgebra.coe_sub (0.889)`
- `mem_ker`: `3` occurrences, `exact_short_theorem_ambiguous`, candidates: `AddMonoidHom.mem_ker, Filter.mem_ker, IsAddGroupHom.mem_ker`
- Category breakdown over theorem-like unknown occurrences:
- `no_convincing_theorem_match`: `231` occurrences
- `near_theorem_match`: `116` occurrences
- `exact_short_theorem_ambiguous`: `54` occurrences
- `exact_short_theorem_unique`: `18` occurrences
- `normalized_theorem_match_unique`: `13` occurrences
- `exact_full_theorem`: `6` occurrences
- `normalized_theorem_match_ambiguous`: `6` occurrences
- Problem-specific dominant unknowns:
- `no-hint/MSC-180_90_001` -> `le` (`18` occurrences)
- `no-hint/MSC-180_65_001` -> `le` (`16` occurrences)
- `no-hint/MSC-180_14_003` -> `root_multiplicity_factorization` (`6` occurrences)
- `no-hint/MSC-180_12_002` -> `chineseRemainder` (`5` occurrences)
- `no-hint/MSC-180_65_003` -> `trans` (`5` occurrences)
- `no-hint/MSC-180_05_003` -> `card_compl` (`4` occurrences)
- `no-hint/MSC-180_12_001` -> `Polynomial.eq_of_sub_eq_zero` (`4` occurrences)
- `no-hint/MSC-180_14_001` -> `AddMonoidHom.quotientKerEquivOfSurjective` (`4` occurrences)

## Conclusions
- Increasing rank from `16` to `64` and `128` did not reduce theorem-name hallucination volume.
- `r128` has the largest unknown-name burden of the three LoRA runs, both in attempt rate and total occurrences.
- Many hallucinations remain theorem-adjacent: exact short names, normalized name matches, or near matches to real Mathlib theorem names.
- But the higher-rank runs also increase the number of names with no convincing theorem match, so the extra capacity did not repair name grounding.
