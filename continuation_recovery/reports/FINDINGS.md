# Findings

## Final

- `transformers==4.57.6` is the correct environment for this work. The severe
  tokenizer corruption observed under `5.3.0` is not the limiting factor
  anymore once the study runs in the pinned continuation env.
- Raw-text continuation without saved token ids is viable.
- The hard part is not whole-string idempotence. The hard part is recovering a
  good boundary from truncated visible text.

## Main empirical result

The best tested recovery rule is `adaptive_lexical_first`.

Algorithm:

1. If the visible text ends in spaces or tabs, strip trailing horizontal
   whitespace.
2. Else if the visible text ends in identifier characters, treat the cut as
   suspicious and run `lexical_then_stable`:
   - backtrack over the trailing identifier fragment
   - then continue searching backward until the prefix is stable under the
     probe set
3. Else if the prefix is already stable under the probe set, keep it as-is.
4. Else backtrack to the nearest stability-probe boundary.

## Why this rule won

- Pure `as_is` continuation is too brittle.
- Whitespace-only cleanup solves whitespace cuts but not identifier cuts.
- `stable_probe` alone is not enough for identifier-ending cuts.
- `lexical_then_stable` is very strong but unnecessarily aggressive on safe
  whitespace cuts.
- `adaptive_lexical_first` keeps the identifier-handling strength of
  `lexical_then_stable` while avoiding its unnecessary extra backtracking on
  whitespace-ending cuts.

## Key numbers

Continuation sweeps:

- Greedy medium set:
  - `adaptive_lexical_first`: prefix/oracle continuation recovery `0.940`,
    average backtrack `8.39`
  - `lexical_then_stable`: prefix/oracle continuation recovery `0.936`,
    average backtrack `8.61`
  - `adaptive_stable`: prefix/oracle continuation recovery `0.880`,
    average backtrack `5.93`
- Sampled medium set:
  - `adaptive_lexical_first`: prefix/oracle continuation recovery `0.937`,
    average backtrack `6.84`
  - `lexical_then_stable`: prefix/oracle continuation recovery `0.929`,
    average backtrack `7.23`
  - `adaptive_stable`: prefix/oracle continuation recovery `0.849`,
    average backtrack `3.90`

Full v4 rerun on the real theorem-continuation experiment:

- exact `600/760` (`78.95%`)
- other valid `90/760` (`11.84%`)
- hallucinated `57/760` (`7.50%`)
- no-theorem-like-identifier `13/760` (`1.71%`)
- slot exact@k `87/95`
- slot hallucination@k `9/95`
- clean attempts `587/760` (`77.24%`)
- artifact markers `0/760`
- commentary-text corruption `173/760`
- of those `173` flagged attempts, `162` are `commentary_text` only, and
  `147` of those are still theorem-valid; this means the current corruption
  parser is too aggressive and treats many valid Lean comments as corruption
- the remaining `57` hallucination-labeled attempts are not `57` distinct
  theorem-name failures:
  - they affect only `9` slots
  - they reduce to only `3` unique first identifiers:
    - `p_all`
    - `Exists.intro`
    - `mem_ker`
  - `44/57` are boundary fragments caused by recovered prefixes that still end
    in `sim`, so the continuation begins with the visible suffix of `simp` or
    `simp_all`
  - `13/57` are `Exists.intro`, a non-theorem namespace/constructor opener on
    an existential goal
  - there are `0/57` unresolved-other cases after this split
  - this means the v4 run shows little to no evidence of broad residual
    theorem-name hallucination after recovery

Prefix scans over all generated-region cuts:

- Greedy medium:
  - `adaptive_lexical_first`: exact prefix recovery `0.934`, average backtrack
    `6.60`
  - `lexical_then_stable`: exact prefix recovery `0.927`, average backtrack
    `6.76`
- Sampled medium:
  - `adaptive_lexical_first`: exact prefix recovery `0.937`, average backtrack
    `5.18`
  - `lexical_then_stable`: exact prefix recovery `0.927`, average backtrack
    `5.38`

## Boundary-specific findings

- After trailing spaces:
  - simple horizontal-whitespace trimming is enough
- Inside identifier fragments:
  - lexical backtracking is the decisive move
- After punctuation and after newlines:
  - most reasonable strategies do well
- The biggest error source in raw-text continuation is leaving a cut at the end
  of an unstable identifier fragment

## Recommended next step

- The new `v4` runner already validates the recovery-rule approach.
- If this is going to become the working experiment path, the next practical
  move is not another large recovery study. The likely high-value follow-ups
  are:
  - refine the theorem-classification bucket so boundary fragments like
    `p_all` and non-theorem openers like `Exists.intro` are not counted as
    theorem hallucinations
  - optionally harden the `stable_probe` branch so it does not leave recovered
    prefixes ending in `sim`
  - separately address commentary leakage if cleaner continuations matter for
    downstream use
- Commentary leakage and label semantics are now the main quality problems.
  Tokenizer corruption is no longer the main blocker.
