# MSC-180 Verified-20 V2 Experiment Plan

## Summary
Prepare a single markdown planning doc for later review that freezes the agreed experiment design:
- 20 problems from `rag_experiments/data/benchmarks/msc180/verified_problems`
- 3 specs
- 8 attempts/problem
- single unified prompt config across conditions

## Public API / Interface Changes
- None now.
- Later (implementation phase) this doc will describe new v2 spec/runner scripts, but no code is changed in this step.

## Markdown File
- Path: `rag_experiments/msc180_verified20_v2_plan.md`

## 1. Goal
- New MSC-180 benchmark run with 3 conditions and 8 attempts/problem.

## 2. Conditions (fixed)
- `A`: no hints (imports + theorem only).
- `B`: theorem statements only (from listed `#check` theorems).
- `C`: theorem statements + usage examples (`-- Uses` + `example` blocks).

## 3. Prompt Strategy (fixed)
- Use one prompt config for all 3 conditions.
- Only `theorem_hint` content changes between A/B/C.

## 4. Dataset Scope (fixed)
- All 20 files in `rag_experiments/data/benchmarks/msc180/verified_problems`.

## 5. Planned New Artifacts (later implementation)
- 3 new spec JSON files (v2-only).
- New v2 runner script (defaults to 8 attempts/problem).
- New v2 prompt printer script.
- New v2 merge script with 3 groups:
  - `no-hint`
  - `theorem-statements`
  - `theorem-statements-and-examples`

## 6. Extraction Rules
- `header`: imports/open block before the first theorem.
- `formal_statement`: first theorem normalized to `:= by sorry`.
- `B` hint: theorem statements from `#check`.
- `C` hint: `B` content + corresponding usage examples.
- Ignore unrelated examples not tied to a `-- Uses` block.

## 7. Validation Checklist
- 3 specs each contain exactly 20 identical problem keys.
- A has empty hints, B has statements only, C has statements+examples.
- Counts align with source files (`#check` and `-- Uses` totals).
- Prompt template identical across A/B/C.
- Runner default attempts = 8.

## 8. Open Items (for later review)
- Final naming convention for v2 output filenames/date tags.
- Whether to include per-problem metadata summary table in the doc.

## Test Cases and Scenarios
- Doc review scenario: read markdown and confirm all decisions are explicit and implementation-ready.
- Consistency scenario: verify no contradictions with existing `rag_experiments/scripts/run/run_msc180_manual_suite.py` behavior assumptions.

## Assumptions and Defaults
- No code/spec changes now; only planning documentation.
- Existing 5-spec manual pilot remains untouched.
- Unified prompt config is the selected default for cleaner ablation.
