#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(
        Path(__file__).resolve().parent / "scripts" / "inspect_tactic_sft_dataset.py",
        run_name="__main__",
    )
