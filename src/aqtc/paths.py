from __future__ import annotations

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[2]
DEMO_DATA_DIR = REPO_ROOT / "data" / "demo"
DEFAULT_STATE_DIR = REPO_ROOT / ".aqtc_state"
