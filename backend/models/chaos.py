"""
Chaos Models

Pydantic models for Chaos Engineering and Wargaming simulations.
Defines the structure for Chaos Events, Scenarios, and Resilience Scores.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
import uuid


class ChaosType(str, Enum):
    """Types of Chaos Events"""
    MARKET_CRASH = "market_crash"
    REPUTATION_SCANDAL = "reputation_scandal"
    COMPETITOR_MOVE = "competitor_move"
    REGULATORY_CHANGE = "regulatory_change"
    TECHNICAL_FAILURE = "technical_failure"
    BLACK_SWAN = "black_swan"


class ChaosSeverity(str, Enum):
    """Severity levels for Chaos Events"""
    LOW = "low"          # Minor inconvenience
    MEDIUM = "medium"    # Noticeable impact, requires adjustment
    HIGH = "high"        # Major disruption, requires pivot
    CRITICAL = "critical" # Existential threat


class ChaosEvent(BaseModel):
    """
    Represents a specific chaos event injected into the system.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: ChaosType = Field(..., description="Type of chaos event")
    name: str = Field(..., description="Name/Headline of the event")
    description: str = Field(..., description="Detailed description of the event scenario")
    severity: ChaosSeverity = Field(default=ChaosSeverity.MEDIUM)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Parameters specific to the event (e.g., "competitor_name", "price_drop_percent")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    # The expected impact on various metrics (0.0 to 1.0)
    expected_impact: Dict[str, float] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class WargameScenario(BaseModel):
    """
    A collection of Chaos Events forming a complete simulation scenario.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Name of the wargame scenario")
    description: str = Field(..., description="Description of the scenario theme")
    events: List[ChaosEvent] = Field(default_factory=list, description="Sequence of events")
    difficulty: str = Field(default="medium")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StrategyResilienceScore(BaseModel):
    """
    The result of a wargame simulation on a specific strategy.
    """
    strategy_id: str = Field(..., description="ID of the strategy being tested")
    scenario_id: str = Field(..., description="ID of the wargame scenario used")
    
    overall_score: float = Field(..., description="Resilience score (0-100)", ge=0, le=100)
    survival_probability: float = Field(..., description="Probability of strategy survival", ge=0, le=1)
    
    # Detailed breakdown
    weaknesses_exposed: List[str] = Field(default_factory=list)
    strengths_validated: List[str] = Field(default_factory=list)
    
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
