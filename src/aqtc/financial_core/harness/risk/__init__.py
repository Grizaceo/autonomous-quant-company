"""
Risk Tools — Position sizing, exposure limits, stop losses.
"""

from __future__ import annotations

from typing import Dict
import numpy as np

from ..base import BaseRiskTool
from ..registry import ToolRegistry


class MaxGrossTool(BaseRiskTool):
    """Maximum gross exposure constraint."""

    def _apply_impl(self, raw_action: np.ndarray, portfolio_state: Dict) -> np.ndarray:
        max_gross = self.params.get("max_gross", 10.0)
        current_gross = np.sum(np.abs(raw_action))

        if current_gross > max_gross:
            # Scale down proportionally
            scale = max_gross / current_gross
            return raw_action * scale
        return raw_action


class MaxActiveTool(BaseRiskTool):
    """Maximum number of active positions."""

    def _apply_impl(self, raw_action: np.ndarray, portfolio_state: Dict) -> np.ndarray:
        max_active = int(self.params.get("max_active", 6))
        n_assets = len(raw_action)

        if n_assets <= max_active:
            return raw_action

        # Keep top max_active by absolute weight
        abs_weights = np.abs(raw_action)
        top_indices = np.argsort(abs_weights)[-max_active:]

        constrained = np.zeros_like(raw_action)
        constrained[top_indices] = raw_action[top_indices]
        return constrained


class StopLossTool(BaseRiskTool):
    """Stop-loss on individual positions."""

    def _apply_impl(self, raw_action: np.ndarray, portfolio_state: Dict) -> np.ndarray:
        stop_loss_pct = self.params.get("stop_loss_pct", 0.02)
        positions = portfolio_state.get("positions", {})

        action = raw_action.copy()
        tickers = portfolio_state.get("tickers", [])

        for i, ticker in enumerate(tickers):
            if ticker in positions:
                pos = positions[ticker]
                avg_cost = pos.get("avg_cost", 0)
                current_price = pos.get("current_price", 0)

                if avg_cost > 0 and current_price > 0:
                    pnl_pct = (current_price - avg_cost) / avg_cost
                    # If long and below stop loss, force sell
                    if pnl_pct < -stop_loss_pct and raw_action[i] > 0:
                        action[i] = -abs(raw_action[i])  # Flip to sell

        return action


class VolTargetTool(BaseRiskTool):
    """Volatility targeting — scale positions to target portfolio vol."""

    def _apply_impl(self, raw_action: np.ndarray, portfolio_state: Dict) -> np.ndarray:
        vol_target = self.params.get("vol_target", 0.15)
        # Estimate current portfolio vol from recent returns
        recent_returns = portfolio_state.get("recent_returns", [])

        if len(recent_returns) < 20:
            return raw_action

        current_vol = np.std(recent_returns) * np.sqrt(252)

        if current_vol > 0:
            scale = vol_target / current_vol
            scale = np.clip(scale, 0.5, 2.0)  # Clamp scaling
            return raw_action * scale

        return raw_action


class CorrelationLimitTool(BaseRiskTool):
    """Limit correlation between positions."""

    def _apply_impl(self, raw_action: np.ndarray, portfolio_state: Dict) -> np.ndarray:
        corr_limit = self.params.get("correlation_limit", 0.7)
        corr_matrix = portfolio_state.get("correlation_matrix")

        if corr_matrix is None:
            return raw_action

        # Simple greedy: if adding position would exceed corr limit with existing, reduce
        n = len(raw_action)
        action = raw_action.copy()

        for i in range(n):
            if action[i] == 0:
                continue
            for j in range(i):
                if action[j] != 0 and abs(corr_matrix[i, j]) > corr_limit:
                    # Reduce smaller position
                    if abs(action[i]) < abs(action[j]):
                        action[i] *= 0.5
                    else:
                        action[j] *= 0.5

        return action


# Register risk tools
ToolRegistry.register_risk("max_gross", MaxGrossTool)
ToolRegistry.register_risk("max_active", MaxActiveTool)
ToolRegistry.register_risk("stop_loss", StopLossTool)
ToolRegistry.register_risk("vol_target", VolTargetTool)
ToolRegistry.register_risk("correlation_limit", CorrelationLimitTool)
