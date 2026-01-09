#!/usr/bin/env python3
"""Export attempts JSON into per-problem .lean files and a zip archive.

Usage:
  python3 scripts/export_attempts_to_lean.py <path/to/attempts_verified.json>
  python3 scripts/export_attempts_to_lean.py <path/to/attempts_verified.json> --overwrite

This script:
  - Creates an output folder next to the input JSON (same name, without .json).
  - Writes one subfolder per problem, named with the problem index and key.
  - Writes one .lean file per attempt containing header + parsed_proof.
  - Creates a .zip archive of the output folder next to the input JSON.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


def _safe_name(name: str) -> str:
    safe = name.replace("/", "_").replace("\\", "_")
    if os.sep != "/":
        safe = safe.replace(os.sep, "_")
    if os.altsep:
        safe = safe.replace(os.altsep, "_")
    return safe


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_attempt_files(
    lean_path: Path,
    raw_path: Path,
    header: str,
    parsed_proof: str,
    raw_output: str,
) -> None:
    lean_content = f"{header}\n\n{parsed_proof}"
    lean_path.write_text(lean_content, encoding="utf-8")
    raw_path.write_text(raw_output, encoding="utf-8")


def _prepare_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not overwrite:
            raise FileExistsError(f"Output directory already exists: {path}")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=False)


def _prepare_zip_path(path: Path, overwrite: bool) -> None:
    if path.exists():
        if not overwrite:
            raise FileExistsError(f"Output zip already exists: {path}")
        path.unlink()


def export_attempts(input_path: Path, overwrite: bool) -> tuple[Path, Path]:
    payload = _load_json(input_path)
    if not isinstance(payload, dict):
        raise TypeError("Input JSON must be an object of problems.")

    output_dir = input_path.with_suffix("")
    zip_path = input_path.with_suffix(".zip")

    _prepare_output_dir(output_dir, overwrite)
    _prepare_zip_path(zip_path, overwrite)

    for idx, (problem_key, problem) in enumerate(payload.items(), start=1):
        safe_key = _safe_name(problem_key)
        folder_name = f"{idx}_{safe_key}"
        problem_dir = output_dir / folder_name
        problem_dir.mkdir(parents=True, exist_ok=False)

        header = str(problem.get("header", ""))
        attempts = problem.get("attempts", [])

        for attempt_idx, attempt in enumerate(attempts, start=1):
            parsed_proof = str(attempt.get("parsed_proof", ""))
            raw_output = str(attempt.get("raw_output", ""))
            base_name = f"attempt{attempt_idx}_{folder_name}"
            lean_path = problem_dir / f"{base_name}.lean"
            raw_path = problem_dir / f"{base_name}.txt"
            _write_attempt_files(lean_path, raw_path, header, parsed_proof, raw_output)

    shutil.make_archive(
        base_name=str(output_dir),
        format="zip",
        root_dir=str(output_dir.parent),
        base_dir=output_dir.name,
    )

    return output_dir, zip_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export attempts JSON into a folder of per-problem .lean files."
    )
    parser.add_argument("input_json", type=Path, help="Path to attempts_verified.json")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output directory and zip file.",
    )
    args = parser.parse_args()

    output_dir, zip_path = export_attempts(args.input_json, args.overwrite)
    print(f"Wrote attempts to {output_dir}")
    print(f"Wrote zip to {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
