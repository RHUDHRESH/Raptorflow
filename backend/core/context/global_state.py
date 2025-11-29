
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class GlobalContext(BaseModel):
    """
    Shared state across the entire RaptorFlow system.
    """
    workspace_id: str
    active_campaign_ids: list[str] = Field(default_factory=list)
    active_agent_tasks: Dict[str, Any] = Field(default_factory=dict)
    system_health: float = 1.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Shared Memory (Short-term)
    blackboard: Dict[str, Any] = Field(default_factory=dict)

class ContextManager:
    """
    Manages the global context, potentially backed by Redis.
    """
    
    def __init__(self):
        self._context: Dict[str, GlobalContext] = {}

    async def get_context(self, workspace_id: str) -> GlobalContext:
        if workspace_id not in self._context:
            self._context[workspace_id] = GlobalContext(workspace_id=workspace_id)
        return self._context[workspace_id]

    async def update_context(self, workspace_id: str, updates: Dict[str, Any]):
        ctx = await self.get_context(workspace_id)
        updated_data = ctx.dict()
        updated_data.update(updates)
        updated_data["last_updated"] = datetime.utcnow()
        self._context[workspace_id] = GlobalContext(**updated_data)

# Global Instance
context_manager = ContextManager()
