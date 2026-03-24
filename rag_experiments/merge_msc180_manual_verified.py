#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(
        Path(__file__).resolve().parent / "scripts/tools/merge_msc180_manual_verified.py",
        run_name="__main__",
    )
