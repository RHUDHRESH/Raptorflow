from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from business_context import BrandIdentity, StrategicAudience, MarketPosition


class EventType(str, Enum):
    STRATEGIC_SHIFT = "STRATEGIC_SHIFT"
    MOVE_COMPLETED = "MOVE_COMPLETED"
    USER_INTERACTION = "USER_INTERACTION"
    AI_REFINEMENT = "AI_REFINEMENT"
    SYSTEM_CHECKPOINT = "SYSTEM_CHECKPOINT"


class InteractionRecord(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: str
    payload: Dict[str, Any] = {}


class EvolutionHistory(BaseModel):
    total_events: int = 0
    last_event_id: Optional[str] = None
    significant_milestones: List[str] = []
    evolution_index: float = 1.0  # Indicator of strategic depth


class TelemetryData(BaseModel):
    recent_interactions: List[InteractionRecord] = []
    total_interactions: int = 0
    top_search_queries: List[str] = []


class BusinessContextEverything(BaseModel):
    """
    The 'Everything' BCM Schema.
    An exhaustive, dynamic state that evolves based on every ledger event.
    """

    ucid: str
    identity: BrandIdentity = Field(default_factory=BrandIdentity)
    audience: StrategicAudience = Field(default_factory=StrategicAudience)
    positioning: MarketPosition = Field(default_factory=MarketPosition)

    # New Everything Fields
    history: EvolutionHistory = Field(default_factory=EvolutionHistory)
    telemetry: TelemetryData = Field(default_factory=TelemetryData)

    # The 'Current Logic' that has evolved from history
    evolved_insights: List[str] = []
    contradiction_log: List[Dict[str, Any]] = []

    metadata: Dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
