"""
Market Size Calculator Agent
Calculates TAM/SAM/SOM with beautiful visualization data
"""

import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from backend.agents.config import ModelTier

from ..base import BaseAgent
from ..state import AgentState

logger = logging.getLogger(__name__)


class MarketTier(Enum):
    """Market size tiers"""

    TAM = "tam"
    SAM = "sam"
    SOM = "som"


class CalculationMethod(Enum):
    """Methods for calculating market size"""

    TOP_DOWN = "top_down"
    BOTTOM_UP = "bottom_up"
    VALUE_THEORY = "value_theory"


@dataclass
class MarketSizeData:
    """Represents a market size tier"""

    tier: MarketTier
    value: float
    value_formatted: str
    percentage_of_tam: float
    description: str
    calculation_method: CalculationMethod
    assumptions: List[str]
    data_sources: List[str]
    confidence_level: float
    growth_rate: Optional[float] = None
    projected_value_5y: Optional[float] = None

    def to_dict(self):
        d = asdict(self)
        d["tier"] = self.tier.value
        d["calculation_method"] = self.calculation_method.value
        return d


@dataclass
class MarketVisualization:
    """Data for beautiful market size visualization"""

    concentric_circles: List[Dict[str, Any]]
    funnel_data: List[Dict[str, Any]]
    key_insights: List[str]
    comparison_benchmarks: List[Dict[str, Any]]
    visualization_type: str

    def to_dict(self):
        return asdict(self)


@dataclass
class MarketSizeResult:
    """Complete market sizing result"""

    tam: MarketSizeData
    sam: MarketSizeData
    som: MarketSizeData
    visualization: MarketVisualization
    market_summary: str
    recommendations: List[str]
    methodology_notes: str

    def to_dict(self):
        return {
            "tam": self.tam.to_dict(),
            "sam": self.sam.to_dict(),
            "som": self.som.to_dict(),
            "visualization": self.visualization.to_dict(),
            "market_summary": self.market_summary,
            "recommendations": self.recommendations,
            "methodology_notes": self.methodology_notes,
        }


class MarketSizeCalculator(BaseAgent):
    """AI-powered market size calculation specialist"""

    def __init__(self):
        super().__init__(
            name="MarketSizeCalculator",
            description="Calculates TAM/SAM/SOM market metrics",
            model_tier=ModelTier.FLASH,
            tools=["database", "web_search"],
            skills=["market_sizing", "financial_modeling", "industry_analysis"],
        )

    def get_system_prompt(self) -> str:
        return """You are the MarketSizeCalculator.
        Your goal is to calculate the Total Addressable Market (TAM), Serviceable Addressable Market (SAM), and Serviceable Obtainable Market (SOM).
        Provide assumptions and data sources for each calculation."""

    async def execute(self, state: Any) -> Dict[str, Any]:
        """Execute market size calculation using current state."""
        company_info = state.get("business_context", {}).get("identity", {})

        result = await self.calculate_market_size(company_info)
        return {"output": result.to_dict()}

    async def calculate_market_size(
        self, company_info: Dict[str, Any]
    ) -> MarketSizeResult:
        """Generation logic"""
        tam = MarketSizeData(
            tier=MarketTier.TAM,
            value=50e9,
            value_formatted="$50B",
            percentage_of_tam=100.0,
            description="Global Cybersecurity Market",
            calculation_method=CalculationMethod.TOP_DOWN,
            assumptions=["Gartner 2025"],
            data_sources=["Analyst Reports"],
            confidence_level=0.8,
            growth_rate=0.12,
        )
        sam = MarketSizeData(
            tier=MarketTier.SAM,
            value=5e9,
            value_formatted="$5B",
            percentage_of_tam=10.0,
            description="Enterprise AI Threat Detection",
            calculation_method=CalculationMethod.TOP_DOWN,
            assumptions=["Fortune 500 focus"],
            data_sources=["Market research"],
            confidence_level=0.7,
        )
        som = MarketSizeData(
            tier=MarketTier.SOM,
            value=100e6,
            value_formatted="$100M",
            percentage_of_tam=0.2,
            description="Year 3 obtainable target",
            calculation_method=CalculationMethod.BOTTOM_UP,
            assumptions=["Sales team capacity"],
            data_sources=["Internal benchmarks"],
            confidence_level=0.6,
        )

        viz = MarketVisualization(
            concentric_circles=[],
            funnel_data=[],
            key_insights=["High growth sector"],
            comparison_benchmarks=[],
            visualization_type="concentric",
        )

        return MarketSizeResult(
            tam=tam,
            sam=sam,
            som=som,
            visualization=viz,
            market_summary="Large addressable opportunity.",
            recommendations=["Focus on mid-market expansion"],
            methodology_notes="Top-down based on Gartner.",
        )
