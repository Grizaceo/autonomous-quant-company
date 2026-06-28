from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .paths import DEFAULT_STATE_DIR, DEMO_DATA_DIR


@dataclass(frozen=True)
class AQTCConfig:
    demo_data_dir: Path = DEMO_DATA_DIR
    state_dir: Path = DEFAULT_STATE_DIR
    stripe_mode: str = os.getenv("AQTC_STRIPE_MODE", "mock")
    nvidia_mode: str = os.getenv("AQTC_NVIDIA_MODE", "mock")
    live_trading: bool = os.getenv("AQTC_LIVE_TRADING", "false").lower() == "true"
    daily_budget_usd: float = float(os.getenv("AQTC_DAILY_BUDGET_USD", "25"))
    require_approval_above_usd: float = float(os.getenv("AQTC_REQUIRE_APPROVAL_ABOVE_USD", "5"))

    def ensure_state(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
