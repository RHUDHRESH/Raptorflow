"""
Market Size Calculator Agent
Calculates TAM/SAM/SOM with beautiful visualization data
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class MarketTier(Enum):
    """Market size tiers"""
    TAM = "tam"  # Total Addressable Market
    SAM = "sam"  # Serviceable Addressable Market
    SOM = "som"  # Serviceable Obtainable Market


class CalculationMethod(Enum):
    """Methods for calculating market size"""
    TOP_DOWN = "top_down"
    BOTTOM_UP = "bottom_up"
    VALUE_THEORY = "value_theory"


class MarketDataSource(Enum):
    """Sources for market data"""
    INDUSTRY_REPORT = "industry_report"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    CUSTOMER_RESEARCH = "customer_research"
    ESTIMATION = "estimation"


@dataclass
class MarketSizeData:
    """Represents a market size tier"""
    tier: MarketTier
    value: float  # In dollars
    value_formatted: str
    percentage_of_tam: float
    description: str
    calculation_method: CalculationMethod
    assumptions: List[str]
    data_sources: List[str]
    confidence_level: float
    growth_rate: Optional[float] = None
    projected_value_5y: Optional[float] = None


@dataclass
class MarketVisualization:
    """Data for beautiful market size visualization"""
    concentric_circles: List[Dict[str, Any]]
    funnel_data: List[Dict[str, Any]]
    key_insights: List[str]
    comparison_benchmarks: List[Dict[str, Any]]
    visualization_type: str  # concentric, funnel, bubble


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


class MarketSizeCalculator:
    """AI-powered market size calculation specialist"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.multipliers = self._load_multipliers()
    
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """Load industry benchmark data"""
        return {
            "saas": {
                "average_tam": 50_000_000_000,  # $50B
                "sam_percentage": 0.15,  # 15% of TAM
                "som_percentage": 0.02,  # 2% of SAM
                "growth_rate": 0.12,  # 12% YoY
                "arpu_range": (100, 50000)  # Annual revenue per user
            },
            "fintech": {
                "average_tam": 100_000_000_000,
                "sam_percentage": 0.10,
                "som_percentage": 0.01,
                "growth_rate": 0.15,
                "arpu_range": (500, 100000)
            },
            "martech": {
                "average_tam": 30_000_000_000,
                "sam_percentage": 0.20,
                "som_percentage": 0.03,
                "growth_rate": 0.10,
                "arpu_range": (200, 25000)
            },
            "ecommerce": {
                "average_tam": 200_000_000_000,
                "sam_percentage": 0.05,
                "som_percentage": 0.005,
                "growth_rate": 0.08,
                "arpu_range": (50, 5000)
            },
            "healthcare": {
                "average_tam": 80_000_000_000,
                "sam_percentage": 0.08,
                "som_percentage": 0.01,
                "growth_rate": 0.14,
                "arpu_range": (1000, 200000)
            },
            "default": {
                "average_tam": 20_000_000_000,
                "sam_percentage": 0.15,
                "som_percentage": 0.02,
                "growth_rate": 0.10,
                "arpu_range": (100, 10000)
            }
        }
    
    def _load_multipliers(self) -> Dict[str, float]:
        """Load calculation multipliers"""
        return {
            "enterprise_focus": 2.5,  # Higher ARPU
            "smb_focus": 0.5,  # Lower ARPU, higher volume
            "global_market": 1.5,
            "regional_market": 0.3,
            "niche_market": 0.1,
            "emerging_market": 0.7,
            "mature_market": 1.0
        }
    
    def _format_currency(self, value: float) -> str:
        """Format currency value for display"""
        if value >= 1_000_000_000_000:
            return f"${value / 1_000_000_000_000:.1f}T"
        elif value >= 1_000_000_000:
            return f"${value / 1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"${value / 1_000_000:.1f}M"
        elif value >= 1_000:
            return f"${value / 1_000:.1f}K"
        else:
            return f"${value:.0f}"
    
    def _determine_industry(self, company_info: Dict[str, Any]) -> str:
        """Determine industry from company info"""
        industry = company_info.get("industry", "").lower()
        product_desc = company_info.get("product_description", "").lower()
        
        keywords = {
            "saas": ["saas", "software", "platform", "subscription", "cloud"],
            "fintech": ["fintech", "payment", "banking", "finance", "money"],
            "martech": ["marketing", "advertising", "growth", "analytics", "campaign"],
            "ecommerce": ["ecommerce", "commerce", "retail", "shopping", "store"],
            "healthcare": ["health", "medical", "patient", "clinical", "care"]
        }
        
        for ind, words in keywords.items():
            if any(word in industry or word in product_desc for word in words):
                return ind
        
        return "default"
    
    def _calculate_tam(self, company_info: Dict[str, Any], industry: str) -> MarketSizeData:
        """Calculate Total Addressable Market"""
        benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks["default"])
        
        # Start with industry benchmark
        base_tam = benchmarks["average_tam"]
        
        # Apply multipliers based on market scope
        market_scope = company_info.get("market_scope", "regional").lower()
        if "global" in market_scope:
            base_tam *= self.multipliers["global_market"]
        elif "regional" in market_scope:
            base_tam *= self.multipliers["regional_market"]
        
        # Adjust for market maturity
        market_maturity = company_info.get("market_maturity", "mature").lower()
        if "emerging" in market_maturity:
            base_tam *= self.multipliers["emerging_market"]
        
        # Growth rate
        growth_rate = benchmarks["growth_rate"]
        projected_5y = base_tam * ((1 + growth_rate) ** 5)
        
        return MarketSizeData(
            tier=MarketTier.TAM,
            value=base_tam,
            value_formatted=self._format_currency(base_tam),
            percentage_of_tam=100.0,
            description="Total market demand for the entire product category globally",
            calculation_method=CalculationMethod.TOP_DOWN,
            assumptions=[
                f"Based on {industry} industry benchmarks",
                f"Market scope: {market_scope}",
                f"Annual growth rate: {growth_rate:.1%}"
            ],
            data_sources=["Industry reports", "Market research", "Competitor analysis"],
            confidence_level=0.6,
            growth_rate=growth_rate,
            projected_value_5y=projected_5y
        )
    
    def _calculate_sam(self, company_info: Dict[str, Any], tam: MarketSizeData, industry: str) -> MarketSizeData:
        """Calculate Serviceable Addressable Market"""
        benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks["default"])
        
        # Base SAM percentage
        sam_percentage = benchmarks["sam_percentage"]
        
        # Adjust for target market focus
        target_market = company_info.get("target_market", "").lower()
        if "enterprise" in target_market:
            sam_percentage *= 0.8  # Smaller but higher value
        elif "smb" in target_market or "small" in target_market:
            sam_percentage *= 1.2  # Larger addressable base
        
        # Adjust for geographic focus
        geography = company_info.get("target_geography", "").lower()
        if "north america" in geography or "us" in geography:
            sam_percentage *= 0.4  # ~40% of global market
        elif "europe" in geography:
            sam_percentage *= 0.3
        elif "asia" in geography:
            sam_percentage *= 0.35
        
        sam_value = tam.value * sam_percentage
        
        return MarketSizeData(
            tier=MarketTier.SAM,
            value=sam_value,
            value_formatted=self._format_currency(sam_value),
            percentage_of_tam=sam_percentage * 100,
            description="Market segment you can realistically target with your product and go-to-market",
            calculation_method=CalculationMethod.TOP_DOWN,
            assumptions=[
                f"Target market: {company_info.get('target_market', 'General')}",
                f"Geographic focus: {company_info.get('target_geography', 'Global')}",
                f"Product fit: {sam_percentage:.1%} of TAM"
            ],
            data_sources=["Target market analysis", "Product-market fit assessment"],
            confidence_level=0.7,
            growth_rate=tam.growth_rate,
            projected_value_5y=sam_value * ((1 + (tam.growth_rate or 0.1)) ** 5)
        )
    
    def _calculate_som(self, company_info: Dict[str, Any], sam: MarketSizeData, industry: str) -> MarketSizeData:
        """Calculate Serviceable Obtainable Market"""
        benchmarks = self.industry_benchmarks.get(industry, self.industry_benchmarks["default"])
        
        # Base SOM percentage of SAM
        som_percentage = benchmarks["som_percentage"]
        
        # Adjust for competitive position
        market_position = company_info.get("market_position", "").lower()
        if "leader" in market_position:
            som_percentage *= 3.0
        elif "challenger" in market_position:
            som_percentage *= 1.5
        elif "niche" in market_position:
            som_percentage *= 0.5
        
        # Adjust for sales capacity
        team_size = company_info.get("sales_team_size", 0)
        if team_size > 20:
            som_percentage *= 2.0
        elif team_size > 5:
            som_percentage *= 1.2
        
        # Cap at reasonable percentage
        som_percentage = min(som_percentage, 0.15)  # Max 15% of SAM
        
        som_value = sam.value * som_percentage
        
        return MarketSizeData(
            tier=MarketTier.SOM,
            value=som_value,
            value_formatted=self._format_currency(som_value),
            percentage_of_tam=som_value / (sam.value / (sam.percentage_of_tam / 100)) * 100,
            description="Realistic market share achievable in the next 1-3 years",
            calculation_method=CalculationMethod.BOTTOM_UP,
            assumptions=[
                f"Market position: {company_info.get('market_position', 'Challenger')}",
                f"Sales capacity: {team_size} team members",
                f"Capture rate: {som_percentage:.1%} of SAM"
            ],
            data_sources=["Sales capacity analysis", "Competitive positioning", "Historical growth data"],
            confidence_level=0.8,
            growth_rate=sam.growth_rate,
            projected_value_5y=som_value * ((1 + ((sam.growth_rate or 0.1) + 0.05)) ** 5)  # Faster growth for SOM
        )
    
    def _generate_visualization(self, tam: MarketSizeData, sam: MarketSizeData, som: MarketSizeData) -> MarketVisualization:
        """Generate visualization data for beautiful TAM/SAM/SOM display"""
        
        # Concentric circles data (most common beautiful viz)
        concentric_circles = [
            {
                "tier": "TAM",
                "label": "Total Addressable Market",
                "value": tam.value,
                "formatted": tam.value_formatted,
                "radius": 100,  # Outermost circle
                "color": "#E8F4F8",
                "border_color": "#94C4D4"
            },
            {
                "tier": "SAM",
                "label": "Serviceable Addressable Market",
                "value": sam.value,
                "formatted": sam.value_formatted,
                "radius": 65,  # Middle circle
                "color": "#B8D4E3",
                "border_color": "#6BA3C4"
            },
            {
                "tier": "SOM",
                "label": "Serviceable Obtainable Market",
                "value": som.value,
                "formatted": som.value_formatted,
                "radius": 30,  # Inner circle
                "color": "#4A90A4",
                "border_color": "#2C5F7C"
            }
        ]
        
        # Funnel data (alternative viz)
        funnel_data = [
            {
                "tier": "TAM",
                "label": "Total Market",
                "value": tam.value,
                "formatted": tam.value_formatted,
                "width": 100,
                "color": "#E8F4F8"
            },
            {
                "tier": "SAM",
                "label": "Addressable",
                "value": sam.value,
                "formatted": sam.value_formatted,
                "width": int(sam.percentage_of_tam),
                "color": "#B8D4E3"
            },
            {
                "tier": "SOM",
                "label": "Obtainable",
                "value": som.value,
                "formatted": som.value_formatted,
                "width": int(som.percentage_of_tam),
                "color": "#4A90A4"
            }
        ]
        
        # Key insights
        key_insights = [
            f"Your total market opportunity is {tam.value_formatted}",
            f"You can realistically address {sam.value_formatted} ({sam.percentage_of_tam:.1f}% of TAM)",
            f"Target capture: {som.value_formatted} in the next 1-3 years",
            f"Market growing at {(tam.growth_rate or 0.1) * 100:.0f}% annually"
        ]
        
        if som.projected_value_5y:
            key_insights.append(f"5-year projection: {self._format_currency(som.projected_value_5y)} SOM potential")
        
        # Comparison benchmarks
        comparison_benchmarks = [
            {
                "name": "Typical SaaS startup Year 1",
                "value": 1_000_000,
                "formatted": "$1M"
            },
            {
                "name": "Series A company",
                "value": 10_000_000,
                "formatted": "$10M"
            },
            {
                "name": "Unicorn threshold",
                "value": 100_000_000,
                "formatted": "$100M ARR"
            }
        ]
        
        return MarketVisualization(
            concentric_circles=concentric_circles,
            funnel_data=funnel_data,
            key_insights=key_insights,
            comparison_benchmarks=comparison_benchmarks,
            visualization_type="concentric"  # Recommended for beautiful non-grid viz
        )
    
    async def calculate_market_size(self, company_info: Dict[str, Any]) -> MarketSizeResult:
        """
        Calculate complete TAM/SAM/SOM with visualization data
        
        Args:
            company_info: Company information including industry, target market, etc.
        
        Returns:
            MarketSizeResult with all tiers and visualization data
        """
        # Determine industry
        industry = self._determine_industry(company_info)
        
        # Calculate all tiers
        tam = self._calculate_tam(company_info, industry)
        sam = self._calculate_sam(company_info, tam, industry)
        som = self._calculate_som(company_info, sam, industry)
        
        # Generate visualization data
        visualization = self._generate_visualization(tam, sam, som)
        
        # Market summary
        market_summary = f"The {industry} market represents a {tam.value_formatted} opportunity. "
        market_summary += f"Based on your target market and positioning, you can address {sam.value_formatted} "
        market_summary += f"({sam.percentage_of_tam:.1f}% of TAM). "
        market_summary += f"With current resources, target capturing {som.value_formatted} in 1-3 years."
        
        # Recommendations
        recommendations = []
        
        if som.value < 10_000_000:
            recommendations.append("Consider expanding target market or geography to increase SOM")
        
        if sam.percentage_of_tam < 10:
            recommendations.append("Explore adjacent market segments to increase SAM")
        
        if tam.growth_rate and tam.growth_rate > 0.15:
            recommendations.append("Fast-growing market - prioritize market share capture over profitability")
        
        recommendations.append(f"Focus on {som.value_formatted} achievable market before expanding")
        
        # Methodology notes
        methodology_notes = "Market sizing uses a combination of top-down (TAM, SAM) and bottom-up (SOM) approaches. "
        methodology_notes += "TAM is derived from industry benchmarks and market research. "
        methodology_notes += "SAM factors in your specific target market and geographic focus. "
        methodology_notes += "SOM is calculated based on competitive position and go-to-market capacity."
        
        return MarketSizeResult(
            tam=tam,
            sam=sam,
            som=som,
            visualization=visualization,
            market_summary=market_summary,
            recommendations=recommendations,
            methodology_notes=methodology_notes
        )
    
    def get_visualization_config(self, result: MarketSizeResult) -> Dict[str, Any]:
        """Get configuration for rendering the visualization"""
        return {
            "type": result.visualization.visualization_type,
            "circles": result.visualization.concentric_circles,
            "funnel": result.visualization.funnel_data,
            "insights": result.visualization.key_insights,
            "benchmarks": result.visualization.comparison_benchmarks,
            "animation": {
                "duration": 1000,
                "easing": "easeOutQuart",
                "stagger": 200
            },
            "colors": {
                "tam": "#E8F4F8",
                "sam": "#B8D4E3", 
                "som": "#4A90A4",
                "text": "#1a1a1a",
                "accent": "#2C5F7C"
            }
        }
