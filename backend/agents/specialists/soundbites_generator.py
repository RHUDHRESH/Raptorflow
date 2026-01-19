"""
Soundbites Generator Agent
Creates messaging library with taglines, value props, and soundbites
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import re

from ..base import BaseAgent
from ..config import ModelTier
from ..state import AgentState

logger = logging.getLogger(__name__)


class SoundbiteType(Enum):
    """Types of soundbites"""
    TAGLINE = "tagline"
    VALUE_PROP = "value_prop"
    HEADLINE = "headline"
    SUBHEADLINE = "subheadline"
    CTA = "cta"
    ELEVATOR_PITCH = "elevator_pitch"
    TWEET = "tweet"
    PAIN_STATEMENT = "pain_statement"
    SOLUTION_STATEMENT = "solution_statement"


class AudienceContext(Enum):
    """Audience context for soundbites"""
    DECISION_MAKER = "decision_maker"
    TECHNICAL = "technical"
    END_USER = "end_user"
    GENERAL = "general"


class EmotionalTone(Enum):
    """Emotional tone of soundbite"""
    CONFIDENT = "confident"
    URGENT = "urgent"
    ASPIRATIONAL = "aspirational"
    EMPATHETIC = "empathetic"
    PROVOCATIVE = "provocative"
    REASSURING = "reassuring"


@dataclass
class Soundbite:
    """A single soundbite/messaging element"""
    id: str
    type: SoundbiteType
    content: str
    audience: AudienceContext
    tone: EmotionalTone
    character_count: int
    word_count: int
    use_cases: List[str] = field(default_factory=list)
    variations: List[str] = field(default_factory=list)
    score: float = 0.0
    notes: str = ""

    def to_dict(self):
        d = asdict(self)
        d["type"] = self.type.value
        d["audience"] = self.audience.value
        d["tone"] = self.tone.value
        return d


@dataclass
class SoundbiteLibrary:
    """Complete soundbite library"""
    soundbites: List[Soundbite]
    by_type: Dict[str, List[Soundbite]]
    by_audience: Dict[str, List[Soundbite]]
    recommendations: List[str]
    summary: str

    def to_dict(self):
        return {
            "soundbites": [s.to_dict() for s in self.soundbites],
            "by_type": {k: [s.to_dict() for s in v] for k, v in self.by_type.items()},
            "by_audience": {k: [s.to_dict() for s in v] for k, v in self.by_audience.items()},
            "recommendations": self.recommendations,
            "summary": self.summary
        }


class SoundbitesGenerator(BaseAgent):
    """AI-powered soundbites and messaging library generator"""
    
    def __init__(self):
        super().__init__(
            name="SoundbitesGenerator",
            description="Generates high-impact soundbites and messaging library",
            model_tier=ModelTier.FLASH,
            tools=["database"],
            skills=["copywriting", "brand_voice_design", "messaging_architecture"]
        )
        self.soundbite_counter = 0

    def get_system_prompt(self) -> str:
        return """You are the SoundbitesGenerator.
        Your goal is to transform core strategy into 'Atomic Messaging' - short, punchy statements.
        Generate Taglines, Value Props, CTAs, and Elevator Pitches."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute soundbite generation using current state."""
        company_info = state.get("business_context", {}).get("identity", {})
        positioning = state.get("positioning", {})
        icp_profiles = state.get("icp_profiles", [])
        
        result = await self.generate_library(company_info, positioning, icp_profiles)
        return {"output": result.to_dict()}
    
    def _generate_soundbite_id(self) -> str:
        self.soundbite_counter += 1
        return f"SND-{self.soundbite_counter:03d}"

    async def generate_library(self, company_info: Dict[str, Any], positioning: Dict[str, Any], icp_profiles: List[Dict[str, Any]]) -> SoundbiteLibrary:
        """Generation logic"""
        # Basic generation
        s1 = Soundbite(
            id=self._generate_soundbite_id(),
            type=SoundbiteType.TAGLINE,
            content="Real-time security for modern teams.",
            audience=AudienceContext.GENERAL,
            tone=EmotionalTone.CONFIDENT,
            character_count=32,
            word_count=5,
            score=0.9
        )
        
        return SoundbiteLibrary(
            soundbites=[s1],
            by_type={"tagline": [s1]},
            by_audience={"general": [s1]},
            recommendations=["Use on website hero"],
            summary="Messaging library generated."
        )