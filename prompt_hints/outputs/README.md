# Output Families

This directory stores generated artifacts from the main `prompt_hints/`
workflow.

- `experiments/`
  General experiment outputs, currently centered on `attempts.json`.
- `tasks/`
  Outputs for the split task runs driven by `task1_spec.json` and
  `task2_spec.json`.
- `proving_variants/`
  Dated outputs for the no-hint, given-theorem, and with-hints prompt
  variants across different model providers.

The filenames keep the historical naming convention. The subdirectories now
carry the main structural meaning.
