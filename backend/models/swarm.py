import operator
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.models.cognitive import (
    CognitiveIntelligenceState,
    ResourceBudget,
    RoutingMetadata,
    SharedMemoryHandles,
)


class SwarmTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SwarmTask(BaseModel):
    """Represents a sub-task delegated to a swarm specialist."""

    id: str
    specialist_type: str  # researcher, architect, critic, etc.
    description: str
    status: SwarmTaskStatus = SwarmTaskStatus.PENDING
    result: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SwarmState(CognitiveIntelligenceState):
    """
    SOTA Swarm Intelligence State.
    Extends the base cognitive state with multi-agent coordination fields.
    """

    # List of delegated sub-tasks
    swarm_tasks: Annotated[List[SwarmTask], operator.add]

    # Shared pool of knowledge discovered during the run
    shared_knowledge: Annotated[Dict[str, Any], dict]

    # History of delegations and specialist interactions
    delegation_history: Annotated[List[Dict[str, Any]], operator.add]

    # Routing metadata for orchestration
    routing_metadata: RoutingMetadata

    # Shared memory handles for cross-agent state
    shared_memory_handles: SharedMemoryHandles

    # Resource budgets for the swarm run
    resource_budget: ResourceBudget
