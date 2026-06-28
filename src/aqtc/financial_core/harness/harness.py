"""
Harness — Complete tool harness built from genotype.
"""
from __future__ import annotations

from typing import Any, Dict
import numpy as np

from .base import HarnessGenotype, Harness, BaseRiskTool, BaseExecutionTool
from .registry import ToolRegistry


class CompositeRiskTool:
    """Applies all enabled risk tools in sequence."""
    
    def __init__(self, risk_tools: Dict[str, BaseRiskTool]):
        self.risk_tools = risk_tools
    
    def apply(self, raw_action: np.ndarray, portfolio_state: Dict) -> np.ndarray:
        action = raw_action
        for tool in self.risk_tools.values():
            action = tool.apply(action, portfolio_state)
        return action


class CompositeExecutionTool:
    """Applies all enabled execution tools in sequence."""
    
    def __init__(self, execution_tools: Dict[str, BaseExecutionTool]):
        self.execution_tools = execution_tools
    
    def simulate(self, action: np.ndarray, market_state: Dict) -> Dict[str, Any]:
        result = {"fills": action, "costs": 0.0, "slippage": 0.0}
        for tool in self.execution_tools.values():
            step_result = tool.simulate(result["fills"], market_state)
            result["fills"] = step_result.get("fills", result["fills"])
            result["costs"] += step_result.get("costs", 0.0)
            result["slippage"] += step_result.get("slippage", 0.0)
        return result


def build_harness(genotype: HarnessGenotype) -> Harness:
    """Build complete harness from genotype."""
    
    # Build feature tools
    features = {}
    for name, config in genotype.features.items():
        tool_class = ToolRegistry.get_feature(name)
        if tool_class:
            params = {k: v for k, v in config.items() if k != "enabled"}
            enabled = config.get("enabled", True)
            features[name] = tool_class(name, params, enabled)
    
    # Build risk tools
    risk_tools = {}
    for name in ["max_gross", "max_active", "stop_loss", "vol_target", "correlation_limit"]:
        config = genotype.risk
        tool_class = ToolRegistry.get_risk(name)
        if tool_class:
            risk_tools[name] = tool_class(name, config, True)
    
    # Build execution tools
    execution_tools = {}
    for name in ["market", "limit", "twap", "vwap", "iceberg"]:
        tool_class = ToolRegistry.get_execution(name)
        if tool_class:
            config = genotype.execution
            execution_tools[name] = tool_class(name, config, True)
    
    # Create composites
    risk = CompositeRiskTool(risk_tools)
    execution = CompositeExecutionTool(execution_tools)
    
    return Harness(
        features=features,
        risk=risk,
        execution=execution,
        controller_config=genotype.controller,
        genotype=genotype,
    )


# Alias for backward compatibility
def make_harness(genotype: HarnessGenotype) -> Harness:
    return build_harness(genotype)