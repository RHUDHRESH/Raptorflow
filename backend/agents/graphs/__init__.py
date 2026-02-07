"""
LangGraph workflows for Raptorflow agent orchestration.

This package contains multiple graphs that may depend on optional heavy
dependencies. Keep imports lazy to avoid breaking unrelated endpoints at
startup.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "create_raptorflow_graph",
    "OnboardingGraph",
    "MoveExecutionGraph",
    "ContentGraph",
    "ResearchGraph",
    "HITLGraph",
    "ReflectionGraph",
    "DailyWinsGraph",
]

_EXPORTS: dict[str, tuple[str, str]] = {
    "create_raptorflow_graph": (".main", "create_raptorflow_graph"),
    "OnboardingGraph": (".onboarding", "OnboardingGraph"),
    "MoveExecutionGraph": (".move_execution", "MoveExecutionGraph"),
    "ContentGraph": (".content", "ContentGraph"),
    "ResearchGraph": (".research", "ResearchGraph"),
    "HITLGraph": (".hitl", "HITLGraph"),
    "ReflectionGraph": (".reflection", "ReflectionGraph"),
    "DailyWinsGraph": (".daily_wins", "DailyWinsGraph"),
}


def __getattr__(name: str) -> Any:
    if name in _EXPORTS:
        module_name, attr_name = _EXPORTS[name]
        module = import_module(module_name, package=__name__)
        return getattr(module, attr_name)
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(globals().keys()))
