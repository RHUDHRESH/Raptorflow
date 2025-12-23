from enum import Enum
from typing import List, Optional, Dict, Any, TypedDict, Annotated
import operator
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

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
    brief: Dict[str, Any] # ICPs, UVP, Tone, Goals
    research_bundle: Dict[str, Any] # Verified sources, trends, gaps
    
    # 3. Execution (The 'Moves')
    current_plan: List[Dict[str, Any]] # 90-day arc or weekly moves
    active_move: Optional[Dict[str, Any]]
    generated_assets: List[Dict[str, Any]] # Copy, images, wireframes
    
    # 4. Agentic Intelligence
    messages: Annotated[List[AgentMessage], operator.add] # Chain of thought and dialogue
    last_agent: str
    reflection_log: Annotated[List[Dict[str, Any]], operator.add] # Critique and audit results
    
    # 5. MLOps & Governance
    status: CognitiveStatus
    quality_score: float # Aggregate quality 0-1
    cost_accumulator: float # Estimated USD burn
    token_usage: Dict[str, int] # Input/Output counts
    
    # 6. Errors & Flow Control
    error: Optional[str]
    next_node: Optional[str] # Manual override for complex routing

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
    active_locks: List[str] = Field(default_factory=list) # For resource coordination
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)
