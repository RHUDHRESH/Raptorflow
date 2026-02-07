import operator
import random
from typing import Annotated, List, Optional, TypedDict

from pydantic import BaseModel, Field

from models.queue_controller import CapabilityProfile, QueueController


class FortressTask(BaseModel):
    """SOTA structured task representation."""

    id: str = Field(default_factory=lambda: "t-" + str(random.randint(1000, 9999)))
    crew: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    output: Optional[str] = None


class FortressState(TypedDict):
    """
    The Global State for the RaptorFlow Fortress.
    Uses Annotated with operator.add for append-only message/log history.
    """

    # Identifiers
    workspace_id: str
    thread_id: str
    user_id: str

    # Input/Output
    raw_prompt: str
    final_output: Optional[str]

    # Brain (Supervisor & Planner)
    task_queue: Annotated[List[FortressTask], operator.add]
    current_task_id: Optional[str]
    next_node: str  # The routing signal
    capability_profile: CapabilityProfile
    queue_controller: QueueController

    # Memory & Context
    messages: Annotated[List[any], operator.add]
    context_brief: dict

    # Quality & Stats
    quality_score: float
    iteration_count: int
    telemetry: Annotated[List[dict], operator.add]
