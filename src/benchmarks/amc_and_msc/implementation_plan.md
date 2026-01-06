Implementation Plan: AMC + MSC-180 Goedel Test Harness

Goal
- Build a filtered problem dict from miniF2F (AMC only) and MSC-180 (undergrad only).
- Run generation per problem with Goedel prompt config, checkpointing after each problem.

Scope Summary
- Two new scripts under a new experiments/ subdir.
- Script 1: build a JSON dict keyed by source/problem_id with {header, formal_statement}.
- Script 2: load that JSON, build TheoremProcessor objects, generate attempts per problem, and checkpoint after each problem.

Script 1: Build Filtered Problems JSON
- Inputs:
  - benchmarks/processed/miniF2F_valid.json
  - benchmarks/MSC-180/MSC-180.json
- Filters:
  - miniF2F: keys starting with "amc" (amc12, amc12a, amc12b).
  - MSC-180: any entry where "difficult" contains "Undergraduate-Level" (including zero-width variants).
- MSC-180 split rule:
  - Use the last line that starts with "theorem" as the split point.
  - Everything before it is header; the theorem line and after is formal statement.
  - Keep imports and any preceding lines in the header.
  - Apply .strip() to header and formal_statement.
- Output:
  - experiments/<new_dir>/filtered_problems.json
  - Structure: { "miniF2F/<id>": { "header": "...", "formal_statement": "..." }, "MSC-180/<id>": { ... } }

Script 2: Run Attempts + Checkpoint
- Inputs:
  - experiments/<new_dir>/filtered_problems.json
- Params (top-of-file constants, all set to 0 initially):
  - MODEL_ID, TEMPERATURE, TOP_P, MAX_NEW_TOKENS, etc.
  - MAX_ATTEMPTS_PER_PROBLEM = 4
  - MICRO_BATCH_SIZE = 4
  - SERVER_URL = "" (server_client None)
- Flow:
  - Load artifacts via load_artifacts(MODEL_ID).
  - For each problem key:
    - Print "source/name" (the key itself).
    - Build TheoremProcessor with header + formal_statement.
    - Call generate_attempts with Goedel prompt config.
    - Add attempts to processor, then store processor.to_dict() in output map.
    - Save the full output dict after each problem (overwrite).
- Output:
  - experiments/<new_dir>/attempts.json (checkpoint, overwritten each iteration)

Notes
- No imports from src/benchmarks helpers; copy/inline any needed save logic.
- Use ASCII-only comments and strings where possible.
