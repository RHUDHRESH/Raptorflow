"""
AI Hub kernel package.

This package provides a product-agnostic AI runtime with:
- BCM-first layered context assembly
- deterministic plan/execution state machine
- bounded tool calling
- critique and repair loop
"""

from backend.ai.hub.runtime import AIHubRuntime
from backend.ai.hub.policy import (
    build_tool_policy,
    describe_policy_profiles,
    normalize_policy_profile,
)
from backend.ai.hub.contracts import (
    BudgetPolicy,
    ContextBundleV1,
    ContextNodeV1,
    ExecutionTraceV1,
    PlanStepV1,
    PlanV1,
    SafetyDecision,
    TaskRequestV1,
    TaskResultV1,
    ToolPolicy,
    UsageV1,
)

__all__ = [
    "AIHubRuntime",
    "BudgetPolicy",
    "ContextBundleV1",
    "ContextNodeV1",
    "ExecutionTraceV1",
    "PlanStepV1",
    "PlanV1",
    "SafetyDecision",
    "TaskRequestV1",
    "TaskResultV1",
    "ToolPolicy",
    "UsageV1",
    "build_tool_policy",
    "describe_policy_profiles",
    "normalize_policy_profile",
]
