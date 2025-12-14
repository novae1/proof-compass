#!/usr/bin/env python3
"""
Download a Hugging Face model snapshot into proof-compass/models/.

Usage:
    python scripts/download_model.py Goedel-LM/Goedel-Prover-V2-8B
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from huggingface_hub import snapshot_download


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a Hugging Face model snapshot into proof-compass/models/."
    )
    parser.add_argument(
        "model_id",
        help="Hugging Face repo id like 'org/model-name'.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    model_id = args.model_id.strip("/")
    if not model_id:
        raise ValueError("model_id must be non-empty (e.g. 'org/model-name').")

    local_dir = project_root() / "models" / model_id
    local_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading '{model_id}' into '{local_dir}'")
    snapshot_download(repo_id=model_id, local_dir=str(local_dir), local_dir_use_symlinks=False)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
