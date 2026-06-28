from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .paths import DEFAULT_STATE_DIR, DEMO_DATA_DIR, REPO_ROOT


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AQTCConfig:
    demo_data_dir: Path = DEMO_DATA_DIR
    state_dir: Path = DEFAULT_STATE_DIR
    approval_policy_path: Path = REPO_ROOT / "examples" / "approval_policy.yaml"

    stripe_mode: str = os.getenv("AQTC_STRIPE_MODE", "mock")
    stripe_currency: str = os.getenv("AQTC_STRIPE_CURRENCY", "usd")
    report_price_usd: float = float(os.getenv("AQTC_REPORT_PRICE_USD", "19"))
    data_purchase_usd: float = float(os.getenv("AQTC_DATA_PURCHASE_USD", "2"))

    nvidia_mode: str = os.getenv("AQTC_NVIDIA_MODE", "mock")
    openrouter_model: str = os.getenv(
        "AQTC_OPENROUTER_MODEL",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
    )
    nvidia_model: str = os.getenv(
        "AQTC_NVIDIA_MODEL",
        "nvidia/nemotron-3-ultra-550b-a55b",
    )
    opencode_zen_model: str = os.getenv(
        "AQTC_OPENCODE_ZEN_MODEL",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
    )

    live_trading: bool = _bool_env("AQTC_LIVE_TRADING", False)
    daily_budget_usd: float = float(os.getenv("AQTC_DAILY_BUDGET_USD", "25"))
    require_approval_above_usd: float = float(os.getenv("AQTC_REQUIRE_APPROVAL_ABOVE_USD", "5"))

    def ensure_state(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
