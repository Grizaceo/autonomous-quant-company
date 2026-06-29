from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .paths import DEFAULT_STATE_DIR, DEMO_DATA_DIR, REPO_ROOT


def _bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in {"1", "true", "yes", "on"}


def _env_str(name: str, default: str) -> str:
    raw = os.getenv(name)
    return raw if raw is not None else default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    return float(raw) if raw is not None else default


def _env_path(name: str, default: Path) -> Path:
    raw = os.getenv(name)
    return Path(raw).expanduser() if raw is not None else default


@dataclass(frozen=True)
class AQTCConfig:
    demo_data_dir: Path = field(default_factory=lambda: DEMO_DATA_DIR)
    state_dir: Path = field(default_factory=lambda: _env_path("AQTC_STATE_DIR", DEFAULT_STATE_DIR))
    approval_policy_path: Path = field(
        default_factory=lambda: REPO_ROOT / "examples" / "approval_policy.yaml"
    )

    stripe_mode: str = field(default_factory=lambda: _env_str("AQTC_STRIPE_MODE", "mock"))
    stripe_currency: str = field(default_factory=lambda: _env_str("AQTC_STRIPE_CURRENCY", "usd"))
    report_price_usd: float = field(
        default_factory=lambda: _env_float("AQTC_REPORT_PRICE_USD", 19.0)
    )
    data_purchase_usd: float = field(
        default_factory=lambda: _env_float("AQTC_DATA_PURCHASE_USD", 2.0)
    )

    nvidia_mode: str = field(default_factory=lambda: _env_str("AQTC_NVIDIA_MODE", "mock"))
    openrouter_model: str = field(
        default_factory=lambda: _env_str(
            "AQTC_OPENROUTER_MODEL",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
        )
    )
    nvidia_model: str = field(
        default_factory=lambda: _env_str(
            "AQTC_NVIDIA_MODEL",
            "nvidia/nemotron-3-ultra-550b-a55b",
        )
    )
    opencode_zen_model: str = field(
        default_factory=lambda: _env_str(
            "AQTC_OPENCODE_ZEN_MODEL",
            "nvidia/nemotron-3-ultra-550b-a55b:free",
        )
    )
    opencode_zen_base_url: str = field(
        default_factory=lambda: _env_str(
            "AQTC_OPENCODE_ZEN_BASE_URL",
            "https://openrouter.ai/api/v1",
        )
    )

    live_trading: bool = field(default_factory=lambda: _bool_env("AQTC_LIVE_TRADING", False))
    auto_approve_spend: bool = field(
        default_factory=lambda: _bool_env("AQTC_AUTO_APPROVE_SPEND", False)
    )

    def ensure_state(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
