# Progress

## 2026-03-10

- Created the dedicated `continuation_recovery/` workspace.
- Confirmed the study will use the local `DeepSeek-Prover-V2-7B` model under a
  pinned `transformers==4.57.6` environment. This was initially a dedicated
  `.venvs/continuation-tf457` setup and is now superseded by the main repo
  `.venv` after pinning `requirements.txt`.
- Confirmed the available source families:
  - MSC prompt specs in `rag_experiments/specs/`
  - verified MSC v2 outputs in `rag_experiments/outputs/20260301_msc180-v2_deepseekv2_7b_lean4-15_verified.json`
  - existing theorem-continuation outputs in `rag_experiments/outputs/20260306_msc180-v3-theorem-continuations_deepseekv2_7b_lean4-15.json`
- Initial working hypothesis:
  - `transformers==4.57.6` fixes the gross tokenizer corruption
  - the remaining problem is boundary recoverability from raw truncated text
  - robust recovery will likely require searching backward from unstable cut
    positions to the nearest stable text boundary
- Wrote the first standalone study harness in
  `continuation_recovery/scripts/recovery_study.py`.
- The initial harness supports:
  - building mixed reference cases from MSC prompts, theorem-continuation slot
    prefixes, and a manual preset
  - sweeping many cut positions
  - evaluating multiple text-only recovery strategies
  - summarizing aggregate continuation fidelity
- Adjusted the harness to use the real `DeepSeekProverV2HintNonCoTPromptConfig`
  builder path and to focus cuts on generated regions instead of static prompt
  prefixes.
- First smoke sweep exposed an evaluator issue:
  - even in greedy mode, the model is not perfectly bit-for-bit reproducible
    across separate GPU runs
  - comparing recovered continuations directly against the original long-run
    suffix can therefore overstate failure
- Updated the recovery metric design:
  - for each cut, generate a fresh short oracle continuation from the exact
    token-prefix boundary
  - compare text-only recovery strategies against that oracle continuation
    instead of only against the original long-run suffix
- Found a second evaluation nuance:
  - if a strategy intentionally backtracks to a different boundary, its
    continuation should be compared against the oracle continuation for that
    recovered boundary, not for the original requested cut
- Updated the harness so each strategy is now scored against the oracle
  continuation for its own recovered prefix boundary.
- Smoke sweep results on 3 reference cases:
  - `as_is` is poor
  - trimming whitespace helps only on whitespace-ending cuts
  - `lexical_then_stable` is strong but backtracks aggressively
  - `adaptive_simple` and `adaptive_stable` are viable compromise rules
- Medium greedy continuation sweep on 13 cases:
  - `lexical_then_stable`: oracle continuation recovery `0.936`, average
    backtrack `8.61`
  - `adaptive_stable`: oracle continuation recovery `0.880`, average backtrack
    `5.93`
  - `adaptive_simple`: oracle continuation recovery `0.842`, average backtrack
    `5.26`
  - `stable_probe`: oracle continuation recovery `0.735`, average backtrack
    `1.89`
- Medium sampled continuation sweep on 9 cases:
  - same ranking shape as the greedy run
  - sampled outputs make the adaptive rules relatively more attractive on MSC
    prompt cases, but they do not overtake the best lexical strategy
- Added a new CPU-only `prefix_scan.py` script to scan all generated-region cut
  positions instead of only sampled cuts.
- Prefix scans over all cuts in the medium case sets suggested a better hybrid:
  - `adaptive_lexical_first`
  - rule: trim horizontal whitespace when the visible text ends with it; if the
    visible text ends with identifier characters, force `lexical_then_stable`;
    otherwise keep stable cuts as-is and fall back to a stability probe search
- Final continuation sweeps with `adaptive_lexical_first`:
  - greedy medium: prefix/oracle continuation recovery `0.940`, average
    backtrack `8.39`
  - sampled medium: prefix/oracle continuation recovery `0.937`, average
    backtrack `6.84`
- Final conclusion from the experiments:
  - text-only continuation recovery is viable under `transformers==4.57.6`
  - arbitrary cuts are not equally recoverable
  - the strongest tested rule is `adaptive_lexical_first`
  - the decisive failure mode is identifier-ending cuts, not whitespace alone
- Next implementation phase:
  - build a separate `v4` continuation runner that applies
    `adaptive_lexical_first`
  - validate it on a tiny slice
  - if the slice looks clean, rerun the full continuation experiment and add
    matching `v4` analyzers
- Implemented:
  - `rag_experiments/run_msc180_v4_theorem_continuations.py`
  - `rag_experiments/analyze_msc180_v4_theorem_continuations.py`
  - `rag_experiments/analyze_msc180_v4_continuation_corruption.py`
- Tiny validation slice (`10` slots, `1` attempt, `24` tokens) on
  `20260310_v4_slice_max10_a1_t24.json`:
  - exact `8/10`
  - other valid `2/10`
  - hallucinated `0/10`
  - artifact markers `0/10`
  - commentary-text corruption still appears in some exact continuations, but
    the old tokenizer-artifact failure mode is gone
- Decision:
  - the slice is clean enough to justify a full v4 rerun
- Full v4 rerun completed:
  - output:
    `rag_experiments/outputs/20260310_msc180-v4-theorem-continuations-recovered_deepseekv2_7b_lean4-15.json`
  - theorem metrics:
    - exact `600/760` (`78.95%`)
    - other valid `90/760` (`11.84%`)
    - hallucinated `57/760` (`7.50%`)
    - no-theorem-like-identifier `13/760` (`1.71%`)
    - slot exact@k `87/95`
    - slot hallucination@k `9/95`
  - recovery behavior:
    - `rstrip_horizontal_ws`: `520` attempts, `481` exact
    - `stable_probe`: `240` attempts, `119` exact
  - corruption metrics:
    - clean `587/760` (`77.24%`)
    - artifact markers `0/760`
    - commentary text `173/760`
    - code-fence restart `11/760`
    - slot-level corruption `36/95`
- Relative to the original broken v3 full run:
  - exact matches increased from `147/760` to `600/760`
  - hallucinated theorem-like identifiers dropped from `411/760` to `57/760`
  - corrupted attempts dropped from `563/760` to `173/760`
- Final assessment:
  - the recovery-rule approach works
  - it is strong enough to replace the old broken continuation path
  - the main remaining issue is commentary leakage, not tokenizer corruption
- Follow-up interpretation of the `173` v4 “corrupted” attempts:
  - `162/173` are `commentary_text` only
  - `147/162` of those are still theorem-valid (`132` exact, `15` other valid)
  - the current corruption analyzer is therefore overcounting valid Lean
    comment lines as corruption
  - the clearly structural corruption bucket is much smaller:
    `10` code-fence restarts plus `1` code-fence restart with `exact?`
- Follow-up analysis of the remaining `57` v4 hallucination-labeled attempts:
  - wrote `continuation_recovery/scripts/analyze_hallucinations.py`
  - generated:
    - `continuation_recovery/artifacts/hallucination_analysis_v4.json`
    - `continuation_recovery/artifacts/hallucination_analysis_v4.md`
  - the `57` attempts collapse to only `9` slots and only `3` unique first
    identifiers:
    - `43 x p_all`
    - `13 x Exists.intro`
    - `1 x mem_ker`
  - primary-cause split:
    - `44/57` are `boundary_fragment`
    - `13/57` are `non_theorem_namespace_symbol`
    - `0/57` are unresolved-other
  - boundary-fragment analysis shows the dominant failure is the recovered
    prefix ending in `sim`, so the continuation visibly starts with the suffix
    of `simp` or `simp_all`
  - the `Exists.intro` bucket is not a theorem-name hallucination in the usual
    sense; it is a constructor-like opener on an existential goal
  - net result:
    - the v4 theorem-continuation run no longer has evidence of broad residual
      theorem-name hallucination
    - the remaining attempt-level bucket is mostly parser/classification
      semantics plus a narrow boundary issue around `stable_probe`
