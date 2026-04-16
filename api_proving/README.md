# API Proving

This workflow owns API-backed theorem-proving experiments that reuse the shared
prompting, parsing, and verification code from `src/`.

It is intended for fast model comparison runs over existing benchmark specs,
especially when local GPU generation is not the bottleneck or when stronger API
models are easier to evaluate.

## Layout

- `data/specs/`
  Small benchmark specs consumed by API runners.
- `scripts/run/`
  Canonical API-backed runners and launchers.
- `scripts/tools/`
  Small helpers and workflow-specific registries.
- `outputs/`
  Durable generated artifacts, grouped by benchmark family.
- `reports/`
  Short workflow-specific notes and smoke-test summaries.

## Notes

- Prompt construction still reuses `prompt_hints/prompt_config.py`.
- Verification still reuses the shared Lean Flask REPL path from `src/lean/`.
- API keys are read from the repo-root `keys.json` and are expected to stay
  outside version control.
