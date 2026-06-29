"""
Tool Registry — Central registry for all harness tools.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import BaseExecutionTool, BaseFeatureTool, BaseRiskTool

if TYPE_CHECKING:
    from .base import Harness, HarnessGenotype


class ToolRegistry:
    """Central registry for all harness tools."""

    _features: dict[str, type[BaseFeatureTool]] = {}
    _risk: dict[str, type[BaseRiskTool]] = {}
    _execution: dict[str, type[BaseExecutionTool]] = {}
    _controller: dict[str, type[Any]] = {}

    @classmethod
    def register_feature(cls, name: str, tool_class: type[BaseFeatureTool]) -> None:
        cls._features[name] = tool_class

    @classmethod
    def register_risk(cls, name: str, tool_class: type[BaseRiskTool]) -> None:
        cls._risk[name] = tool_class

    @classmethod
    def register_execution(cls, name: str, tool_class: type[BaseExecutionTool]) -> None:
        cls._execution[name] = tool_class

    @classmethod
    def register_controller(cls, name: str, tool_class: type[Any]) -> None:
        cls._controller[name] = tool_class

    @classmethod
    def get_feature(cls, name: str) -> type[BaseFeatureTool] | None:
        return cls._features.get(name)

    @classmethod
    def get_risk(cls, name: str) -> type[BaseRiskTool] | None:
        return cls._risk.get(name)

    @classmethod
    def get_execution(cls, name: str) -> type[BaseExecutionTool] | None:
        return cls._execution.get(name)

    @classmethod
    def get_controller(cls, name: str) -> type[Any] | None:
        return cls._controller.get(name)

    @classmethod
    def list_features(cls) -> dict[str, type[BaseFeatureTool]]:
        return dict(cls._features)

    @classmethod
    def list_risk(cls) -> dict[str, type[BaseRiskTool]]:
        return dict(cls._risk)

    @classmethod
    def list_execution(cls) -> dict[str, type[BaseExecutionTool]]:
        return dict(cls._execution)

    @classmethod
    def list_controller(cls) -> dict[str, type[Any]]:
        return dict(cls._controller)


# Import build_harness from harness module to avoid circular imports
def build_harness(genotype: HarnessGenotype) -> Harness:
    """Build a complete harness from genotype."""
    from .harness import build_harness as _build_harness

    return _build_harness(genotype)
