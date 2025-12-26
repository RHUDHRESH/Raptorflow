from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

DEFAULT_IMPORTANCE = "standard"


@dataclass(frozen=True)
class RetentionRule:
    max_items: int
    max_tokens: int
    ttl_seconds: int
    retention_days: int
    recall_limit: int

    def combine(self, other: "RetentionRule") -> "RetentionRule":
        return RetentionRule(
            max_items=max(self.max_items, other.max_items),
            max_tokens=max(self.max_tokens, other.max_tokens),
            ttl_seconds=max(self.ttl_seconds, other.ttl_seconds),
            retention_days=max(self.retention_days, other.retention_days),
            recall_limit=max(self.recall_limit, other.recall_limit),
        )


IMPORTANCE_RULES: Dict[str, RetentionRule] = {
    "low": RetentionRule(
        max_items=10,
        max_tokens=2000,
        ttl_seconds=1800,
        retention_days=30,
        recall_limit=3,
    ),
    "standard": RetentionRule(
        max_items=20,
        max_tokens=4000,
        ttl_seconds=3600,
        retention_days=90,
        recall_limit=5,
    ),
    "high": RetentionRule(
        max_items=40,
        max_tokens=8000,
        ttl_seconds=7200,
        retention_days=180,
        recall_limit=8,
    ),
    "critical": RetentionRule(
        max_items=60,
        max_tokens=12000,
        ttl_seconds=14400,
        retention_days=365,
        recall_limit=12,
    ),
}


class MemoryPolicy:
    """Shared memory policy keyed by workspace and agent importance."""

    def __init__(self, importance_rules: Dict[str, RetentionRule] | None = None):
        self.importance_rules = importance_rules or IMPORTANCE_RULES

    def resolve(
        self,
        workspace_importance: str = DEFAULT_IMPORTANCE,
        agent_importance: str = DEFAULT_IMPORTANCE,
    ) -> RetentionRule:
        workspace_rule = self.importance_rules.get(
            workspace_importance, self.importance_rules[DEFAULT_IMPORTANCE]
        )
        agent_rule = self.importance_rules.get(
            agent_importance, self.importance_rules[DEFAULT_IMPORTANCE]
        )
        return workspace_rule.combine(agent_rule)

    def retention_metadata(
        self, workspace_importance: str, agent_importance: str
    ) -> Dict[str, str | int]:
        rule = self.resolve(workspace_importance, agent_importance)
        return {
            "workspace_importance": workspace_importance,
            "agent_importance": agent_importance,
            "retention_days": rule.retention_days,
        }


_POLICY = MemoryPolicy()


def get_memory_policy() -> MemoryPolicy:
    return _POLICY
