from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class BrandIdentity(BaseModel):
    name: str = ""
    core_promise: str = ""
    tone_of_voice: List[str] = []
    manifesto_summary: str = ""

class StrategicAudience(BaseModel):
    primary_segment: str = ""
    secondary_segments: List[str] = []
    pain_points: List[str] = []
    desires: List[str] = []

class MarketPosition(BaseModel):
    category: str = ""
    differentiator: str = ""
    perceptual_quadrant: str = ""
    strategy_path: str = "" # safe, clever, bold

class BusinessContext(BaseModel):
    """Universal state for RaptorFlow onboarding."""
    ucid: str
    identity: BrandIdentity = Field(default_factory=BrandIdentity)
    audience: StrategicAudience = Field(default_factory=StrategicAudience)
    positioning: MarketPosition = Field(default_factory=MarketPosition)
    evidence_ids: List[str] = []
    noteworthy_insights: List[Dict[str, Any]] = []
    
    # Flexibility for "AI Presumed" steps
    metadata: Dict[str, Any] = Field(default_factory=dict)
