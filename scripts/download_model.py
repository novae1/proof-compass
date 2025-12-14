#!/usr/bin/env python3
"""
Utility to download supported Hugging Face models into the proof_compass workspace.

Usage:
    python download_model.py Goedel-LM/Goedel-Prover-V2-8B
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from huggingface_hub import snapshot_download

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.model_registry import (
    allow_patterns as registry_allow_patterns,
    model_path as registry_model_path,
    supported_model_ids,
)


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a supported Hugging Face model into proof_compass/models/."
    )
    parser.add_argument(
        "model_id",
        choices=list(supported_model_ids()),
        help="One of the supported Hugging Face repo IDs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    models_dir = project_root() / "models"
    models_dir.mkdir(exist_ok=True)

    local_dir = registry_model_path(args.model_id)
    local_dir.mkdir(exist_ok=True)

    print(f"Downloading '{args.model_id}' into '{local_dir}'")

    # snapshot_download keeps a local snapshot; rerunning for the same model reuses
    # the existing files and only fetches updates, so repeated downloads do not
    # duplicate data on disk.
    snapshot_kwargs = {
        "repo_id": args.model_id,
        "local_dir": str(local_dir),
        "local_dir_use_symlinks": False,
        "resume_download": True,  # Allows interrupted downloads to pick up where they left off.
    }
    allow_patterns = registry_allow_patterns(args.model_id)
    if allow_patterns:
        snapshot_kwargs["allow_patterns"] = allow_patterns

    snapshot_download(**snapshot_kwargs)

    print("Download complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
