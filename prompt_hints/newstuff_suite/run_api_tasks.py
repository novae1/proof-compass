#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    runpy.run_path(
        Path(__file__).resolve().parents[2]
        / "theorem_guidance"
        / "scripts"
        / "run"
        / "run_api_tasks.py",
        run_name="__main__",
    )
