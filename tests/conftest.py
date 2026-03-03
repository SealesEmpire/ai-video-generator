"""Shared test fixtures."""

import sys
from pathlib import Path

# Ensure the backend package is importable from the tests/ directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
