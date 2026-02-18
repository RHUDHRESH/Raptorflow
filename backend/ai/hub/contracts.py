"""
Contracts for the AI Hub kernel.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RunStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class SafetyDecision(str, Enum):
    ALLOW = "allow"
    REVIEW = "review"
    BLOCK = "block"


@dataclass
class BudgetPolicy:
    max_steps: int = 8
    max_repair_rounds: int = 1
    max_tokens: int = 2000
    max_cost_usd: float = 0.15
    max_wall_time_s: int = 30

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ToolPolicy:
    allowed_tools: set[str] = field(default_factory=set)
    allow_mutating_external: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed_tools": sorted(self.allowed_tools),
            "allow_mutating_external": self.allow_mutating_external,
        }


@dataclass
class TaskRequestV1:
    workspace_id: str
    intent: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    policy_profile: str = "balanced"
    idempotency_key: str = ""
    mode: str = "single"
    intensity: str = "medium"
    max_tokens: int = 900
    temperature: float = 0.7
    content_type: str = "general"
    requested_tools: List[str] = field(default_factory=list)
    retrieval_evidence: List[Dict[str, Any]] = field(default_factory=list)
    system_prompt: Optional[str] = None
    tool_policy: ToolPolicy = field(default_factory=ToolPolicy)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["tool_policy"] = self.tool_policy.to_dict()
        return payload


@dataclass
class ContextNodeV1:
    node_id: str
    layer: str
    content: Dict[str, Any]
    source_event_ids: List[str] = field(default_factory=list)
    confidence: float = 1.0
    freshness_seconds: int = 0
    token_weight: int = 0
    policy_label: str = "default"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContextBundleV1:
    workspace_id: str
    nodes: List[ContextNodeV1] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "node_count": len(self.nodes),
            "nodes": [node.to_dict() for node in self.nodes],
        }


@dataclass
class PlanStepV1:
    step_id: str
    name: str
    kind: str
    input_keys: List[str] = field(default_factory=list)
    risk: str = "low"
    tool: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanV1:
    plan_id: str
    steps: List[PlanStepV1] = field(default_factory=list)
    estimated_tokens: int = 0
    estimated_cost_usd: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "estimated_tokens": self.estimated_tokens,
            "estimated_cost_usd": self.estimated_cost_usd,
            "steps": [step.to_dict() for step in self.steps],
        }


@dataclass
class UsageV1:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionTraceV1:
    trace_id: str
    state_transitions: List[str] = field(default_factory=list)
    model_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    fallbacks: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""
    memory_candidate_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TaskResultV1:
    status: RunStatus
    output: str
    plan_summary: Dict[str, Any]
    safety_decision: SafetyDecision
    evidence_refs: List[str] = field(default_factory=list)
    usage: UsageV1 = field(default_factory=UsageV1)
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "output": self.output,
            "plan_summary": self.plan_summary,
            "safety_decision": self.safety_decision.value,
            "evidence_refs": self.evidence_refs,
            "usage": self.usage.to_dict(),
            "metadata": self.metadata,
            "trace_id": self.trace_id,
        }

