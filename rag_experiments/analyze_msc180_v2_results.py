#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(
        Path(__file__).resolve().parent / "scripts/analyze/analyze_msc180_v2_results.py",
        run_name="__main__",
    )
