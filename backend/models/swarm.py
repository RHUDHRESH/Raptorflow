import operator
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.models.cognitive import CognitiveIntelligenceState
from backend.models.queue_controller import CapabilityProfile, QueueController

__all__ = [
    "SwarmSubtaskSpec",
    "SwarmTask",
    "SwarmTaskStatus",
    "SwarmState",
]


class SwarmTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class SwarmSubtaskSpec(BaseModel):
    """Structured specification for a swarm subtask."""

    id: str
    specialist_type: str
    objective: str
    success_criteria: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    inputs: Dict[str, Any] = Field(default_factory=dict)


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

    subtask_specs: Annotated[List[SwarmSubtaskSpec], operator.add]

    # List of delegated sub-tasks
    swarm_tasks: Annotated[List[SwarmTask], operator.add]

    # Shared pool of knowledge discovered during the run
    shared_knowledge: Annotated[Dict[str, Any], dict]

    # History of delegations and specialist interactions
    delegation_history: Annotated[List[Dict[str, Any]], operator.add]

    # Concurrency management
    capability_profile: CapabilityProfile
    queue_controller: QueueController
