#!/usr/bin/env python3
"""Export attempts JSON into per-problem .lean files and a zip archive.

Usage:
  python3 scripts/export_attempts_to_lean.py <kimina.json> <deepseek.json> <goedel.json>
  python3 scripts/export_attempts_to_lean.py <kimina.json> <deepseek.json> <goedel.json> --overwrite
  python3 scripts/export_attempts_to_lean.py <kimina.json> <deepseek.json> <goedel.json> \\
    --output-dir <output_dir>

This script:
  - Creates an output folder next to the Kimina JSON (name + "_models" by default).
  - Writes one subfolder per problem, named with the problem index and key.
  - Writes subfolders per model (kimina/deepseekv2/goedelv2).
  - Writes one .lean + .txt file per attempt in each model folder.
  - Creates a .zip archive of the output folder next to the output dir.
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


def _load_payload(path: Path, label: str) -> dict:
    payload = _load_json(path)
    if not isinstance(payload, dict):
        raise TypeError(f"{label} JSON must be an object of problems.")
    return payload


def _ordered_keys(primary: dict, *others: dict) -> list[str]:
    keys = list(primary.keys())
    seen = set(keys)
    for payload in others:
        for key in payload.keys():
            if key not in seen:
                keys.append(key)
                seen.add(key)
    return keys


def export_attempts(
    kimina_path: Path,
    deepseek_path: Path,
    goedel_path: Path,
    overwrite: bool,
    output_dir: Path | None,
) -> tuple[Path, Path]:
    kimina = _load_payload(kimina_path, "Kimina")
    deepseek = _load_payload(deepseek_path, "DeepSeekV2")
    goedel = _load_payload(goedel_path, "GoedelV2")

    if output_dir is None:
        base = kimina_path.with_suffix("")
        output_dir = Path(f"{base}_models")
    zip_path = output_dir.with_suffix(".zip")

    _prepare_output_dir(output_dir, overwrite)
    _prepare_zip_path(zip_path, overwrite)

    for idx, problem_key in enumerate(_ordered_keys(kimina, deepseek, goedel), start=1):
        safe_key = _safe_name(problem_key)
        folder_name = f"{idx}_{safe_key}"
        problem_dir = output_dir / folder_name
        problem_dir.mkdir(parents=True, exist_ok=False)

        for model_name, payload in (
            ("kimina", kimina),
            ("deepseekv2", deepseek),
            ("goedelv2", goedel),
        ):
            model_dir = problem_dir / model_name
            model_dir.mkdir(parents=True, exist_ok=False)
            problem = payload.get(problem_key)
            if not isinstance(problem, dict):
                continue

            header = str(problem.get("header", ""))
            attempts = problem.get("attempts", [])
            for attempt_idx, attempt in enumerate(attempts, start=1):
                parsed_proof = str(attempt.get("parsed_proof", ""))
                raw_output = str(attempt.get("raw_output", ""))
                base_name = f"attempt{attempt_idx}_{model_name}"
                lean_path = model_dir / f"{base_name}.lean"
                raw_path = model_dir / f"{base_name}.txt"
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
    parser.add_argument("kimina_json", type=Path, help="Path to kimina attempts JSON")
    parser.add_argument("deepseek_json", type=Path, help="Path to deepseekv2 attempts JSON")
    parser.add_argument("goedel_json", type=Path, help="Path to goedelv2 attempts JSON")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional output directory (default: <kimina_json_stem>_models).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output directory and zip file.",
    )
    args = parser.parse_args()

    output_dir, zip_path = export_attempts(
        args.kimina_json,
        args.deepseek_json,
        args.goedel_json,
        args.overwrite,
        args.output_dir,
    )
    print(f"Wrote attempts to {output_dir}")
    print(f"Wrote zip to {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
