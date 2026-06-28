"""
Tool Registry — Central registry for all harness tools.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Type
from .base import FeatureTool, RiskTool, ExecutionTool

if TYPE_CHECKING:
    from .base import Harness, HarnessGenotype


class ToolRegistry:
    """Central registry for all harness tools."""
    
    _features: Dict[str, Type[FeatureTool]] = {}
    _risk: Dict[str, Type[RiskTool]] = {}
    _execution: Dict[str, Type[ExecutionTool]] = {}
    _controller: Dict[str, Type] = {}
    
    @classmethod
    def register_feature(cls, name: str, tool_class: Type[FeatureTool]):
        cls._features[name] = tool_class
    
    @classmethod
    def register_risk(cls, name: str, tool_class: Type[RiskTool]):
        cls._risk[name] = tool_class
    
    @classmethod
    def register_execution(cls, name: str, tool_class: Type[ExecutionTool]):
        cls._execution[name] = tool_class
    
    @classmethod
    def register_controller(cls, name: str, tool_class: Type):
        cls._controller[name] = tool_class
    
    @classmethod
    def get_feature(cls, name: str) -> Type[FeatureTool] | None:
        return cls._features.get(name)
    
    @classmethod
    def get_risk(cls, name: str) -> Type[RiskTool] | None:
        return cls._risk.get(name)
    
    @classmethod
    def get_execution(cls, name: str) -> Type[ExecutionTool] | None:
        return cls._execution.get(name)
    
    @classmethod
    def get_controller(cls, name: str) -> Type | None:
        return cls._controller.get(name)
    
    @classmethod
    def list_features(cls) -> Dict[str, Type[FeatureTool]]:
        return dict(cls._features)
    
    @classmethod
    def list_risk(cls) -> Dict[str, Type[RiskTool]]:
        return dict(cls._risk)
    
    @classmethod
    def list_execution(cls) -> Dict[str, Type[ExecutionTool]]:
        return dict(cls._execution)
    
    @classmethod
    def list_controller(cls) -> Dict[str, Type]:
        return dict(cls._controller)

# Import build_harness from harness module to avoid circular imports
def build_harness(genotype: 'HarnessGenotype') -> 'Harness':
    """Build a complete harness from genotype."""
    from .harness import build_harness as _build_harness
    return _build_harness(genotype)