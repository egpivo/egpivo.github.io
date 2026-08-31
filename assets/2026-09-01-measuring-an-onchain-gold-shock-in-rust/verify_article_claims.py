#!/usr/bin/env python3
"""Blog-side wrapper: run the shock-to-migration article claim verifier."""

from __future__ import annotations

import runpy
from pathlib import Path

ENGINE_VERIFY = (
    Path(__file__).resolve().parents[3]
    / "shock-to-migration"
    / "artifacts"
    / "articles"
    / "2026-09-01"
    / "verify_claims.py"
)

if __name__ == "__main__":
    runpy.run_path(str(ENGINE_VERIFY), run_name="__main__")
