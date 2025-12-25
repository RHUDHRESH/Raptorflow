from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CapabilityProfile(BaseModel):
    """Defines per-agent concurrency capabilities."""

    default_concurrency: int = 1
    per_agent_concurrency: Dict[str, int] = Field(default_factory=dict)

    def limit_for(self, agent_type: str) -> int:
        limit = self.per_agent_concurrency.get(agent_type, self.default_concurrency)
        return max(1, limit)


class QueuedTask(BaseModel):
    """Represents a queued or in-flight agent task."""

    task_id: str
    agent_type: str
    metadata: Optional[Dict[str, str]] = None


class QueueController(BaseModel):
    """Caps in-flight agent tasks and manages a FIFO queue."""

    capability_profile: CapabilityProfile = Field(default_factory=CapabilityProfile)
    inflight_by_agent: Dict[str, int] = Field(default_factory=dict)
    queue: List[QueuedTask] = Field(default_factory=list)

    def can_dispatch(self, agent_type: str) -> bool:
        return self.inflight_by_agent.get(agent_type, 0) < self.capability_profile.limit_for(
            agent_type
        )

    def enqueue(self, task: QueuedTask) -> bool:
        if self.can_dispatch(task.agent_type):
            self._increment_inflight(task.agent_type)
            return True
        self.queue.append(task)
        return False

    def complete(self, agent_type: str) -> List[QueuedTask]:
        self._decrement_inflight(agent_type)
        return self.dispatch_ready()

    def dispatch_ready(self) -> List[QueuedTask]:
        dispatched: List[QueuedTask] = []
        remaining: List[QueuedTask] = []
        for task in self.queue:
            if self.can_dispatch(task.agent_type):
                self._increment_inflight(task.agent_type)
                dispatched.append(task)
            else:
                remaining.append(task)
        self.queue = remaining
        return dispatched

    def _increment_inflight(self, agent_type: str) -> None:
        self.inflight_by_agent[agent_type] = self.inflight_by_agent.get(agent_type, 0) + 1

    def _decrement_inflight(self, agent_type: str) -> None:
        current = self.inflight_by_agent.get(agent_type, 0)
        if current <= 1:
            self.inflight_by_agent.pop(agent_type, None)
        else:
            self.inflight_by_agent[agent_type] = current - 1
