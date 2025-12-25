import operator
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional, TypedDict
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from backend.memory.short_term import L1ShortTermMemory


class BudgetCaps(BaseModel):
    """SOTA budget limits for agentic execution."""

    token_cap: Optional[int] = None
    tool_call_cap: Optional[int] = None
    time_cap_seconds: Optional[int] = None
    concurrency_cap: Optional[int] = None


class BudgetUsage(BaseModel):
    """Tracks budget consumption during a run."""

    tokens_used: int = 0
    tool_calls: int = 0
    time_elapsed_seconds: float = 0.0
    active_tool_calls: int = 0
    started_at: Optional[datetime] = None


class ModelTier(str, Enum):
    ULTRA = "ultra"
    SMART = "reasoning"
    DRIVER = "driver"
    MUNDANE = "mundane"


class CognitiveStatus(str, Enum):
    IDLE = "idle"
    PLANNING = "planning"
    RESEARCHING = "researching"
    EXECUTING = "execution"
    REFINING = "refinement"
    AUDITING = "auditing"
    COMPLETE = "complete"
    ERROR = "error"
    FAILED = "failed"


class LifecycleState(str, Enum):
    IDLE = CognitiveStatus.IDLE.value
    PLANNING = CognitiveStatus.PLANNING.value
    RESEARCHING = CognitiveStatus.RESEARCHING.value
    EXECUTING = CognitiveStatus.EXECUTING.value
    REFINING = CognitiveStatus.REFINING.value
    AUDITING = CognitiveStatus.AUDITING.value
    COMPLETE = CognitiveStatus.COMPLETE.value
    ERROR = CognitiveStatus.ERROR.value
    FAILED = CognitiveStatus.FAILED.value


class CognitiveStep(BaseModel):
    """Represents a single reasoning step in the cognitive engine."""

    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    certainty: float = Field(ge=0.0, le=1.0)
    tier: ModelTier = ModelTier.DRIVER


class AgentMessage(BaseModel):
    """Represents a single message in an agent conversation."""

    id: UUID = Field(default_factory=uuid4)
    role: str  # researcher, strategist, creator, critic, human
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


# LangGraph State Schema
class CognitiveIntelligenceState(TypedDict):
    """
    Industrial-grade State Schema for the Cognitive Intelligence Engine.
    Orchestrates the entire marketing lifecycle from context to outcomes.
    """

    # 1. Core Context
    tenant_id: str
    workspace_id: Optional[str]
    raw_prompt: str

    #  strategic Brief
    brief: Dict[str, Any]  # ICPs, UVP, Tone, Goals
    research_bundle: Dict[str, Any]  # Verified sources, trends, gaps

    # 3. Execution (The 'Moves')
    current_plan: List[Dict[str, Any]]  # 90-day arc or weekly moves
    active_move: Optional[Dict[str, Any]]
    generated_assets: List[Dict[str, Any]]  # Copy, images, wireframes

    # 4. Agentic Intelligence
    messages: Annotated[
        List[AgentMessage], operator.add
    ]  # Chain of thought and dialogue
    last_agent: str
    reflection_log: Annotated[
        List[Dict[str, Any]], operator.add
    ]  # Critique and audit results

    # 5. MLOps & Governance
    status: CognitiveStatus
    lifecycle_state: LifecycleState
    lifecycle_transitions: Annotated[List[Dict[str, Any]], operator.add]
    quality_score: float  # Aggregate quality 0-1
    cost_accumulator: float  # Estimated USD burn
    token_usage: Dict[str, int]  # Input/Output counts
    tool_usage: Dict[str, int]
    budget_caps: Optional[BudgetCaps]
    budget_usage: Optional[BudgetUsage]

    # 6. Errors & Flow Control
    error: Optional[str]
    next_node: Optional[str]  # Manual override for complex routing

    # 7. Swarm Orchestration Metadata
    routing_metadata: "RoutingMetadata"
    shared_memory_handles: "SharedMemoryHandles"
    resource_budget: "ResourceBudget"


class RoutingMetadata(TypedDict, total=False):
    """Explicit routing metadata for swarm orchestration."""

    current_node: Optional[str]
    next_node: Optional[str]
    intent: Optional[Dict[str, Any]]
    instructions: Optional[str]
    rationale: Optional[str]
    route_history: Annotated[List[Dict[str, Any]], operator.add]


class SharedMemoryHandles(TypedDict, total=False):
    """Shared memory identifiers for swarm execution."""

    workspace_memory_id: Optional[str]
    thread_memory_id: Optional[str]
    blackbox_memory_id: Optional[str]
    vector_index: Optional[str]


class ResourceBudget(TypedDict, total=False):
    """Resource budgets for a swarm run."""

    max_tokens: Optional[int]
    max_cost: Optional[float]
    max_rounds: Optional[int]
    max_time_s: Optional[int]


class AgentThread(BaseModel):
    """Represents a persistent conversation thread for an agentic run."""

    id: str
    tenant_id: UUID
    move_id: Optional[UUID] = None
    messages: List[AgentMessage] = Field(default_factory=list)
    state: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)


class AgentSharedState(BaseModel):
    """
    SOTA Shared State for workspace-wide agent coordination.
    Acts as a common context pool accessible by multiple agents across different threads.
    """

    workspace_id: str
    context_pool: Dict[str, Any] = Field(default_factory=dict)
    learning_artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    active_locks: List[str] = Field(default_factory=list)  # For resource coordination
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)

    def add_learning_artifacts(
        self,
        artifacts: List[Dict[str, Any]],
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append learning artifacts with provenance metadata."""
        timestamp = datetime.now().isoformat()
        payload = metadata or {}
        for artifact in artifacts:
            self.learning_artifacts.append(
                {
                    "source": source,
                    "artifact": artifact,
                    "metadata": payload,
                    "timestamp": timestamp,
                }
            )
        self.context_pool["learning_artifacts"] = self.learning_artifacts
        self.updated_at = datetime.now()

    def apply_to_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Merge shared learnings into an agent state payload."""
        state.setdefault("shared_state", {})
        state["shared_state"].update(self.model_dump())
        state.setdefault("shared_learnings", self.learning_artifacts)
        context_brief = state.setdefault("context_brief", {})
        context_brief.setdefault("shared_learnings", self.learning_artifacts)
        return state


class LearningBroadcastPipeline:
    """Broadcasts strategic learnings into the workspace shared state."""

    def __init__(self, memory: Optional[L1ShortTermMemory] = None) -> None:
        self.memory = memory or L1ShortTermMemory()

    async def publish(
        self,
        workspace_id: str,
        artifacts: List[Dict[str, Any]],
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentSharedState:
        shared_state = await self._load_shared_state(workspace_id)
        if shared_state is None:
            shared_state = AgentSharedState(workspace_id=workspace_id)
        shared_state.add_learning_artifacts(artifacts, source, metadata)
        await self._store_shared_state(shared_state)
        return shared_state

    async def subscribe(self, workspace_id: str) -> Optional[AgentSharedState]:
        return await self._load_shared_state(workspace_id)

    async def _load_shared_state(self, workspace_id: str) -> Optional[AgentSharedState]:
        if not self.memory.client:
            return None
        raw = await self.memory.retrieve(f"shared_state:{workspace_id}")
        if not raw:
            return None
        return AgentSharedState(**raw)

    async def _store_shared_state(self, shared_state: AgentSharedState) -> None:
        if not self.memory.client:
            return
        await self.memory.store(
            f"shared_state:{shared_state.workspace_id}",
            shared_state.model_dump(mode="json"),
        )


async def hydrate_shared_learnings(state: Dict[str, Any]) -> Dict[str, Any]:
    """Attach shared learnings to the agent state if available."""
    workspace_id = state.get("workspace_id")
    if not workspace_id:
        return state
    pipeline = LearningBroadcastPipeline()
    shared_state = await pipeline.subscribe(workspace_id)
    if shared_state is None:
        return state
    return shared_state.apply_to_state(state)
