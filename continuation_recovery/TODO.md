# TODO

- Adopt `v4` plus the refined corruption interpretation as the working
  continuation baseline.
- Add a follow-up theorem-classification pass that separates:
  - boundary fragments like `p_all`
  - non-theorem namespace symbols like `Exists.intro`
  - genuine unresolved theorem-like names
- If needed, tighten the `stable_probe` recovery branch so it avoids recovered
  prefixes ending in `sim`.
- If cleaner continuations matter, design a separate follow-up pass to reduce
  commentary leakage without changing the core boundary-recovery rule.
- Keep the recovery-study workspace as the audit trail for the decision.
