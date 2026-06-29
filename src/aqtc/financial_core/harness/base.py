"""
Base classes for Tool Harness — plugins that the HGAT controller can use/configure.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Protocol
import numpy as np
import pandas as pd


# ─── Tool Protocols ────────────────────────────────────────────────────────


class FeatureTool(Protocol):
    """Transforms raw market data into features."""

    name: str
    enabled: bool
    params: Dict[str, Any]

    def compute(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        """Return feature matrix [n_assets, n_features] for current window."""
        ...


class RiskTool(Protocol):
    """Applies risk constraints to raw model actions."""

    name: str
    enabled: bool
    params: Dict[str, Any]

    def apply(self, raw_action: np.ndarray, portfolio_state: Dict) -> np.ndarray:
        """Return constrained action."""
        ...


class ExecutionTool(Protocol):
    """Simulates or executes orders."""

    name: str
    enabled: bool
    params: Dict[str, Any]

    def simulate(self, action: np.ndarray, market_state: Dict) -> Dict[str, Any]:
        """Return execution result: fills, costs, slippage."""
        ...


# ─── Base Implementations ──────────────────────────────────────────────────


class BaseFeatureTool(ABC):
    def __init__(self, name: str, params: Dict[str, Any] = None, enabled: bool = True):
        self.name = name
        self.params = params or {}
        self.enabled = enabled

    def compute(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        if not self.enabled:
            return np.array([])
        return self._compute_impl(data)

    @abstractmethod
    def _compute_impl(self, data: Dict[str, pd.DataFrame]) -> np.ndarray:
        pass


class BaseRiskTool(ABC):
    def __init__(self, name: str, params: Dict[str, Any] = None, enabled: bool = True):
        self.name = name
        self.params = params or {}
        self.enabled = enabled

    def apply(self, raw_action: np.ndarray, portfolio_state: Dict) -> np.ndarray:
        if not self.enabled:
            return raw_action
        return self._apply_impl(raw_action, portfolio_state)

    @abstractmethod
    def _apply_impl(self, raw_action: np.ndarray, portfolio_state: Dict) -> np.ndarray:
        pass


class BaseExecutionTool(ABC):
    def __init__(self, name: str, params: Dict[str, Any] = None, enabled: bool = True):
        self.name = name
        self.params = params or {}
        self.enabled = enabled

    def simulate(self, action: np.ndarray, market_state: Dict) -> Dict[str, Any]:
        if not self.enabled:
            return {"fills": action, "costs": 0.0, "slippage": 0.0}
        return self._simulate_impl(action, market_state)

    @abstractmethod
    def _simulate_impl(self, action: np.ndarray, market_state: Dict) -> Dict[str, Any]:
        pass


# ─── Harness Genotype (what ES optimizes) ──────────────────────────────────


@dataclass
class HarnessGenotype:
    """Genotype φ — ES evolves this, not raw weights."""

    # Feature tools: {tool_name: {param: value, "enabled": bool}}
    features: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: {
            "rsi": {"window": 14, "enabled": True},
            "macd": {"fast": 12, "slow": 26, "signal": 9, "enabled": True},
            "zscore": {"window": 20, "enabled": True},
            "pca": {"k": 5, "enabled": False},
            "wavelet": {"level": 3, "enabled": False},
            "cross_sectional": {"enabled": True},
        }
    )

    # Risk tools config
    risk: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_gross": 10.0,
            "max_active": 6,
            "stop_loss_pct": 0.02,
            "vol_target": 0.15,
            "correlation_limit": 0.7,
        }
    )

    # Execution tools config
    execution: Dict[str, Any] = field(
        default_factory=lambda: {
            "order_type": "limit",
            "participation_rate": 0.1,
            "slippage_bps": 5,
        }
    )

    # Controller (HGAT) hyperparams
    controller: Dict[str, Any] = field(
        default_factory=lambda: {
            "d_model": 64,  # genotype seed; production run uses d_model=128 (data/demo/production.toml)
            "n_layers": 3,
            "dropout": 0.2,
            "attention_heads": 4,
            "attention_temp": 1.0,
        }
    )

    def to_flat(self) -> np.ndarray:
        """Flatten to vector for ES (only continuous params)."""
        vec = []
        # Features: only continuous params
        for tool, params in self.features.items():
            for k, v in params.items():
                if k != "enabled" and isinstance(v, (int, float)):
                    vec.append(float(v))
        # Risk
        for k, v in self.risk.items():
            if isinstance(v, (int, float)):
                vec.append(float(v))
        # Execution
        for k, v in self.execution.items():
            if isinstance(v, (int, float)):
                vec.append(float(v))
        # Controller
        for k, v in self.controller.items():
            if isinstance(v, (int, float)):
                vec.append(float(v))
        return np.array(vec)

    @classmethod
    def from_flat(cls, vec: np.ndarray) -> "HarnessGenotype":
        """Reconstruct from flat vector (inverse of to_flat)."""
        idx = 0
        genotype = cls()

        # Features
        for tool, params in genotype.features.items():
            for k in params:
                if k != "enabled" and isinstance(params[k], (int, float)):
                    genotype.features[tool][k] = type(params[k])(vec[idx])
                    idx += 1

        # Risk
        for k in genotype.risk:
            if isinstance(genotype.risk[k], (int, float)):
                genotype.risk[k] = type(genotype.risk[k])(vec[idx])
                idx += 1

        # Execution
        for k in genotype.execution:
            if isinstance(genotype.execution[k], (int, float)):
                genotype.execution[k] = type(genotype.execution[k])(vec[idx])
                idx += 1

        # Controller
        for k in genotype.controller:
            if isinstance(genotype.controller[k], (int, float)):
                genotype.controller[k] = type(genotype.controller[k])(vec[idx])
                idx += 1

        return genotype

    def dim(self) -> int:
        """Dimensionality of flat vector."""
        return len(self.to_flat())


# ─── Harness Builder ───────────────────────────────────────────────────────


@dataclass
class Harness:
    """Built harness from genotype — ready to use in env."""

    features: Dict[str, BaseFeatureTool]
    risk: Any  # CompositeRiskTool
    execution: Any  # CompositeExecutionTool
    controller_config: Dict[str, Any]
    genotype: HarnessGenotype
