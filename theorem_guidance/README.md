# Theorem Guidance

This workflow contains the experiment family previously called
`prompt_hints/newstuff_suite/`.

It focuses on theorem-guided proving runs over a small mixed suite with two
main conditions:

- `with_hints`
- `no_hint`

The historical filenames still include the old `newstuff-*` labels, but the
folder name and layout now describe the workflow by role rather than history.

## Layout

- `data/specs/`
  Theorem-guidance specs for the suite.
- `scripts/run/`
  Canonical local and API runners.
- `scripts/tools/`
  Small utilities such as exact-proof extraction from the specs.
- `outputs/no_hint/`
  Durable artifacts for the no-hint condition.
- `outputs/with_hints/`
  Durable artifacts for the with-hints condition.

## Dependency Note

This workflow still imports prompt builders from `prompt_hints/prompt_config.py`.
That dependency is intentional for now and should only be removed as part of a
later shared-code refactor into `src/`.
