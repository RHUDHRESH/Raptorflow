"""
Integration package for RaptorFlow backend.
Provides cross-module integration and coordination.
"""

from .auth_all import inject_auth_context, verify_workspace_access
from .billing_usage import deduct_from_budget, refund_on_failure
from .context_builder import build_full_context
from .events_all import wire_all_event_handlers
from .memory_database import invalidate_on_change, sync_database_to_memory
from .output_pipeline import process_output
from .redis_sessions import persist_agent_state, restore_agent_state
from .routing_memory import route_with_memory_context
from .test_harness import run_integration_tests
from .validation import validate_agent_state, validate_workspace_consistency

__all__ = [
    "route_with_memory_context",
    "sync_database_to_memory",
    "invalidate_on_change",
    "inject_auth_context",
    "verify_workspace_access",
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
