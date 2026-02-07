from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentSharedState(BaseModel):
    """
    SOTA Shared State Pool.
    Allows multiple agents in a swarm to share context, findings, and temporary artifacts.
    """

    session_id: str
    tenant_id: str
    context_pool: Dict[str, Any] = Field(default_factory=dict)
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    active_agent_ids: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)

    def update_context(self, key: str, value: Any):
        """Update a specific context key."""
        self.context_pool[key] = value
        self.last_updated = datetime.now()

    def add_finding(self, agent_id: str, content: str, metadata: Optional[Dict] = None):
        """Add a surgical finding to the pool."""
        self.findings.append(
            {
                "agent_id": agent_id,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.last_updated = datetime.now()
