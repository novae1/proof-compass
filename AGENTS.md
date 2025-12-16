# AGENTS.md

## General guidelines
- If the session is in read-only mode (for example `sandbox_mode=read-only`, or the user asks you to treat the session as read-only):
  - Do not modify the repo in any way (no `apply_patch`, no commands that write files, no formatting/lint/test runs that rewrite or generate files).
  - Do not suggest concrete code changes (no code snippets, diffs, patches, or line-by-line edit instructions).
  - Only inspect and summarize what you find; ask to switch to a write-enabled mode before proposing any edits.
