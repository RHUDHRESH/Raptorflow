import operator
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field

from models.cognitive import CognitiveIntelligenceState


class CouncilThought(BaseModel):
    """Represents a single expert's contribution to the blackboard."""

    agent_id: str
    content: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    tool_observations: Dict[str, Any] = Field(default_factory=dict)
    proposed_actions: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class DebateTranscript(BaseModel):
    """Logs a specific round of the Council's debate."""

    round_number: int
    proposals: List[CouncilThought]
    critiques: List[Dict[str, Any]] = Field(default_factory=list)
    synthesis: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class CouncilBlackboardState(CognitiveIntelligenceState):
    """
    Enhanced LangGraph State for the Expert Council.
    Implements the 'Blackboard' pattern for shared Agent memory.
    """

    # 1. Council Specific State
    parallel_thoughts: Annotated[List[CouncilThought], operator.add]
    debate_history: Annotated[List[DebateTranscript], operator.add]
    consensus_metrics: Dict[str, float]  # alignment, confidence, risk

    # 2. Strategic Outcomes
    synthesis: Optional[str]
    rejected_paths: Annotated[List[Dict[str, Any]], operator.add]
    final_strategic_decree: Optional[str]

    # 3. Metadata
    reasoning_chain_id: Optional[str]
    radar_signals: Annotated[List[Dict[str, Any]], operator.add]
    campaign_id: Optional[str]
    suggested_moves: Annotated[List[Dict[str, Any]], operator.add]
    refined_moves: Annotated[List[Dict[str, Any]], operator.add]
    evaluated_moves: Annotated[List[Dict[str, Any]], operator.add]
    approved_moves: Annotated[List[Dict[str, Any]], operator.add]
    discarded_moves: Annotated[List[Dict[str, Any]], operator.add]
    move_ids: Annotated[List[str], operator.add]
