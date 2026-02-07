"""
Integration package for RaptorFlow backend.

Keep this package lightweight: importing `backend.integration` should not
eagerly import all integration modules.
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = [
    "route_with_memory_context",
    "sync_database_to_memory",
    "invalidate_on_change",
    "persist_agent_state",
    "restore_agent_state",
    "wire_all_event_handlers",
    "deduct_from_budget",
    "refund_on_failure",
    "validate_workspace_consistency",
    "validate_agent_state",
    "build_full_context",
    "process_output",
    "run_integration_tests",
]

_EXPORTS: dict[str, tuple[str, str]] = {
    "route_with_memory_context": (".routing_memory", "route_with_memory_context"),
    "sync_database_to_memory": (".memory_database", "sync_database_to_memory"),
    "invalidate_on_change": (".memory_database", "invalidate_on_change"),
    "persist_agent_state": (".redis_sessions", "persist_agent_state"),
    "restore_agent_state": (".redis_sessions", "restore_agent_state"),
    "wire_all_event_handlers": (".events_all", "wire_all_event_handlers"),
    "deduct_from_budget": (".billing_usage", "deduct_from_budget"),
    "refund_on_failure": (".billing_usage", "refund_on_failure"),
    "validate_workspace_consistency": (".validation", "validate_workspace_consistency"),
    "validate_agent_state": (".validation", "validate_agent_state"),
    "build_full_context": (".context_builder", "build_full_context"),
    "process_output": (".output_pipeline", "process_output"),
    "run_integration_tests": (".test_harness", "run_integration_tests"),
}


def __getattr__(name: str) -> Any:
    if name in _EXPORTS:
        module_name, attr_name = _EXPORTS[name]
        module = import_module(module_name, package=__name__)
        return getattr(module, attr_name)
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(set(__all__) | set(globals().keys()))
