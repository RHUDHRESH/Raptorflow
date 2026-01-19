"""
Competitor Analyzer Agent
Full-featured competitive analysis with web scraping and AI insights
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import re
import asyncio

logger = logging.getLogger(__name__)


class CompetitorType(Enum):
    """Types of competitors"""
    DIRECT = "direct"  # Same product category, same target market
    INDIRECT = "indirect"  # Different product, same problem
    STATUS_QUO = "status_quo"  # Current solution (spreadsheets, manual, etc.)
    EMERGING = "emerging"  # New entrants to watch
    ADJACENT = "adjacent"  # Different market, same technology


class ThreatLevel(Enum):
    """Competitor threat level"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class MarketPosition(Enum):
    """Market positioning"""
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"
    NEW_ENTRANT = "new_entrant"


@dataclass
class CompetitorStrength:
    """A competitor strength or weakness"""
    description: str
    category: str  # product, brand, distribution, pricing, team, funding
    evidence: str
    confidence: float = 0.5


@dataclass
class CompetitorProfile:
    """Complete competitor profile"""
    id: str
    name: str
    website: str
    competitor_type: CompetitorType
    market_position: MarketPosition
    threat_level: ThreatLevel
    
    # Core positioning
    tagline: str
    core_claim: str
    target_audience: str
    value_proposition: str
    
    # Product analysis
    key_features: List[str] = field(default_factory=list)
    pricing_model: str = ""
    pricing_range: str = ""
    free_tier: bool = False
    
    # Strengths and weaknesses
    strengths: List[CompetitorStrength] = field(default_factory=list)
    weaknesses: List[CompetitorStrength] = field(default_factory=list)
    
    # Market data
    estimated_revenue: str = ""
    funding_raised: str = ""
    team_size: str = ""
    founded_year: int = 0
    
    # Sentiment
    sentiment_score: float = 0.0  # -1 to 1
    mention_count: int = 0
    
    # Discovery metadata
    discovered_by: str = "ai"
    discovery_source: str = ""
    analyzed_at: str = ""
    confidence_score: float = 0.5


@dataclass
class CompetitiveAdvantage:
    """Identified competitive advantage"""
    id: str
    description: str
    category: str  # speed, price, quality, feature, support, brand
    strength: str  # strong, moderate, weak
    evidence: List[str]
    competitors_lacking: List[str]


@dataclass
class CompetitorAnalysisResult:
    """Complete competitor analysis result"""
    competitors: List[CompetitorProfile]
    competitive_advantages: List[CompetitiveAdvantage]
    market_gaps: List[Dict[str, Any]]
    positioning_opportunities: List[Dict[str, Any]]
    threat_assessment: Dict[str, Any]
    recommendations: List[str]
    analysis_summary: str


class CompetitorAnalyzer:
    """AI-powered comprehensive competitor analysis agent"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.competitor_counter = 0
        self.advantage_counter = 0
        self.industry_signals = self._load_industry_signals()
    
    def _load_industry_signals(self) -> Dict[str, List[str]]:
        """Load industry-specific competitor signals"""
        return {
            "saas": ["pricing page", "free trial", "enterprise", "API", "integrations"],
            "fintech": ["compliance", "security", "instant", "fees", "banking partner"],
            "martech": ["ROI", "attribution", "campaign", "automation", "personalization"],
            "ecommerce": ["shipping", "returns", "checkout", "payment options"],
            "default": ["pricing", "features", "customers", "integrations"]
        }
    
    def _generate_competitor_id(self) -> str:
        """Generate unique competitor ID"""
        self.competitor_counter += 1
        return f"COMP-{self.competitor_counter:03d}"
    
    def _generate_advantage_id(self) -> str:
        """Generate unique advantage ID"""
        self.advantage_counter += 1
        return f"ADV-{self.advantage_counter:03d}"
    
    def _determine_competitor_type(self, competitor_info: Dict[str, Any], company_info: Dict[str, Any]) -> CompetitorType:
        """Determine competitor type based on product and market overlap"""
        product_overlap = competitor_info.get("product_overlap", 0.5)
        market_overlap = competitor_info.get("market_overlap", 0.5)
        
        if product_overlap > 0.7 and market_overlap > 0.7:
            return CompetitorType.DIRECT
        elif product_overlap < 0.3 and market_overlap > 0.5:
            return CompetitorType.INDIRECT
        elif competitor_info.get("is_status_quo", False):
            return CompetitorType.STATUS_QUO
        elif competitor_info.get("founded_year", 2020) >= datetime.now().year - 2:
            return CompetitorType.EMERGING
        else:
            return CompetitorType.ADJACENT
    
    def _determine_threat_level(self, competitor: Dict[str, Any], company_info: Dict[str, Any]) -> ThreatLevel:
        """Determine threat level based on various factors"""
        score = 0
        
        # Funding factor
        funding = competitor.get("funding_raised", "").lower()
        if "series c" in funding or "series d" in funding:
            score += 3
        elif "series b" in funding:
            score += 2
        elif "series a" in funding:
            score += 1
        
        # Market position factor
        position = competitor.get("market_position", "").lower()
        if "leader" in position:
            score += 3
        elif "challenger" in position:
            score += 2
        
        # Feature overlap
        if competitor.get("feature_overlap", 0) > 0.7:
            score += 2
        
        # Target market overlap
        if competitor.get("market_overlap", 0) > 0.8:
            score += 2
        
        if score >= 6:
            return ThreatLevel.HIGH
        elif score >= 3:
            return ThreatLevel.MEDIUM
        elif score >= 1:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.UNKNOWN
    
    def _determine_market_position(self, competitor: Dict[str, Any]) -> MarketPosition:
        """Determine market positioning"""
        indicators = competitor.get("position_indicators", {})
        
        if indicators.get("is_leader", False) or competitor.get("market_share", 0) > 30:
            return MarketPosition.LEADER
        elif indicators.get("is_challenger", False) or competitor.get("growth_rate", 0) > 50:
            return MarketPosition.CHALLENGER
        elif competitor.get("niche_focus", False):
            return MarketPosition.NICHE
        elif competitor.get("founded_year", 2020) >= datetime.now().year - 2:
            return MarketPosition.NEW_ENTRANT
        else:
            return MarketPosition.FOLLOWER
    
    def _analyze_strengths_weaknesses(self, competitor: Dict[str, Any]) -> Tuple[List[CompetitorStrength], List[CompetitorStrength]]:
        """Analyze competitor strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        # Analyze based on available data
        features = competitor.get("features", [])
        pricing = competitor.get("pricing", {})
        reviews = competitor.get("reviews", {})
        
        # Feature strengths
        if len(features) > 10:
            strengths.append(CompetitorStrength(
                description="Comprehensive feature set",
                category="product",
                evidence=f"Offers {len(features)}+ features",
                confidence=0.8
            ))
        
        # Pricing analysis
        if pricing.get("free_tier"):
            strengths.append(CompetitorStrength(
                description="Free tier available",
                category="pricing",
                evidence="Offers freemium model",
                confidence=0.9
            ))
        
        # Review-based analysis
        avg_rating = reviews.get("average_rating", 0)
        if avg_rating > 4.5:
            strengths.append(CompetitorStrength(
                description="High customer satisfaction",
                category="brand",
                evidence=f"Average rating: {avg_rating}/5",
                confidence=0.85
            ))
        elif avg_rating < 3.5 and avg_rating > 0:
            weaknesses.append(CompetitorStrength(
                description="Customer satisfaction issues",
                category="brand",
                evidence=f"Average rating: {avg_rating}/5",
                confidence=0.85
            ))
        
        # Funding as strength
        if competitor.get("funding_raised"):
            strengths.append(CompetitorStrength(
                description="Well-funded",
                category="funding",
                evidence=f"Raised {competitor.get('funding_raised')}",
                confidence=0.9
            ))
        
        return strengths, weaknesses
    
    def _identify_competitive_advantages(self, company_info: Dict[str, Any], competitors: List[CompetitorProfile]) -> List[CompetitiveAdvantage]:
        """Identify competitive advantages over competitors"""
        advantages = []
        
        company_features = set(company_info.get("features", []))
        company_strengths = company_info.get("strengths", [])
        
        # Speed advantage
        if company_info.get("implementation_time") and company_info["implementation_time"] < 30:
            advantages.append(CompetitiveAdvantage(
                id=self._generate_advantage_id(),
                description="Faster implementation and time-to-value",
                category="speed",
                strength="strong",
                evidence=[f"Implementation in {company_info['implementation_time']} minutes"],
                competitors_lacking=[c.name for c in competitors if c.threat_level == ThreatLevel.HIGH]
            ))
        
        # Pricing advantage
        if company_info.get("pricing_advantage"):
            advantages.append(CompetitiveAdvantage(
                id=self._generate_advantage_id(),
                description="More competitive pricing structure",
                category="price",
                strength="moderate",
                evidence=["Lower entry price point", "Transparent pricing"],
                competitors_lacking=[]
            ))
        
        # Feature uniqueness
        unique_features = company_info.get("unique_features", [])
        if unique_features:
            advantages.append(CompetitiveAdvantage(
                id=self._generate_advantage_id(),
                description=f"Unique capabilities: {', '.join(unique_features[:3])}",
                category="feature",
                strength="strong",
                evidence=unique_features,
                competitors_lacking=[c.name for c in competitors]
            ))
        
        return advantages
    
    def _identify_market_gaps(self, company_info: Dict[str, Any], competitors: List[CompetitorProfile]) -> List[Dict[str, Any]]:
        """Identify gaps in the market"""
        gaps = []
        
        # Analyze competitor weaknesses for gap opportunities
        all_weaknesses = []
        for comp in competitors:
            for weakness in comp.weaknesses:
                all_weaknesses.append(weakness.description)
        
        # Common weakness patterns = market gaps
        if len([w for w in all_weaknesses if "support" in w.lower()]) > len(competitors) / 2:
            gaps.append({
                "id": "GAP-001",
                "description": "Customer support and success",
                "opportunity": "White-glove onboarding and support",
                "competitors_failing": [c.name for c in competitors],
                "difficulty": "medium"
            })
        
        # Default gap based on category path
        if company_info.get("category_path") == "bold":
            gaps.append({
                "id": "GAP-002",
                "description": "New category creation",
                "opportunity": "Define a new market category",
                "competitors_failing": [],
                "difficulty": "high"
            })
        
        return gaps
    
    def _generate_threat_assessment(self, competitors: List[CompetitorProfile]) -> Dict[str, Any]:
        """Generate overall threat assessment"""
        high_threats = [c for c in competitors if c.threat_level == ThreatLevel.HIGH]
        medium_threats = [c for c in competitors if c.threat_level == ThreatLevel.MEDIUM]
        
        overall_threat = "low"
        if len(high_threats) >= 2:
            overall_threat = "high"
        elif len(high_threats) >= 1 or len(medium_threats) >= 3:
            overall_threat = "medium"
        
        return {
            "overall_threat_level": overall_threat,
            "high_threat_count": len(high_threats),
            "medium_threat_count": len(medium_threats),
            "primary_threats": [c.name for c in high_threats],
            "monitoring_recommended": [c.name for c in medium_threats],
            "assessment": f"Competitive landscape shows {overall_threat} overall threat with {len(high_threats)} direct competitors requiring active monitoring."
        }
    
    async def analyze_competitors(self, company_info: Dict[str, Any], discovered_competitors: List[Dict[str, Any]] = None) -> CompetitorAnalysisResult:
        """
        Perform comprehensive competitor analysis
        
        Args:
            company_info: Company information including product, market, positioning
            discovered_competitors: Pre-discovered competitor data (optional)
        
        Returns:
            CompetitorAnalysisResult with full analysis
        """
        competitors_data = discovered_competitors or []
        
        # If no competitors provided, generate based on industry
        if not competitors_data:
            industry = company_info.get("industry", "saas").lower()
            competitors_data = self._generate_demo_competitors(company_info, industry)
        
        # Build competitor profiles
        competitor_profiles = []
        for comp_data in competitors_data:
            comp_type = self._determine_competitor_type(comp_data, company_info)
            threat_level = self._determine_threat_level(comp_data, company_info)
            market_position = self._determine_market_position(comp_data)
            strengths, weaknesses = self._analyze_strengths_weaknesses(comp_data)
            
            profile = CompetitorProfile(
                id=self._generate_competitor_id(),
                name=comp_data.get("name", "Unknown"),
                website=comp_data.get("website", ""),
                competitor_type=comp_type,
                market_position=market_position,
                threat_level=threat_level,
                tagline=comp_data.get("tagline", ""),
                core_claim=comp_data.get("core_claim", ""),
                target_audience=comp_data.get("target_audience", ""),
                value_proposition=comp_data.get("value_proposition", ""),
                key_features=comp_data.get("features", []),
                pricing_model=comp_data.get("pricing_model", ""),
                pricing_range=comp_data.get("pricing_range", ""),
                free_tier=comp_data.get("free_tier", False),
                strengths=strengths,
                weaknesses=weaknesses,
                estimated_revenue=comp_data.get("estimated_revenue", ""),
                funding_raised=comp_data.get("funding_raised", ""),
                team_size=comp_data.get("team_size", ""),
                founded_year=comp_data.get("founded_year", 0),
                sentiment_score=comp_data.get("sentiment_score", 0.0),
                mention_count=comp_data.get("mention_count", 0),
                discovered_by="ai",
                discovery_source=comp_data.get("source", "analysis"),
                analyzed_at=datetime.now().isoformat(),
                confidence_score=0.75
            )
            competitor_profiles.append(profile)
        
        # Identify advantages
        advantages = self._identify_competitive_advantages(company_info, competitor_profiles)
        
        # Identify market gaps
        gaps = self._identify_market_gaps(company_info, competitor_profiles)
        
        # Generate positioning opportunities
        positioning_opportunities = [
            {
                "id": "POS-001",
                "opportunity": "Speed and simplicity positioning",
                "description": "Position as the fastest, simplest solution",
                "viability": 0.8
            },
            {
                "id": "POS-002", 
                "opportunity": "Specialist positioning",
                "description": f"Position as the specialist for {company_info.get('target_market', 'your niche')}",
                "viability": 0.75
            }
        ]
        
        # Threat assessment
        threat_assessment = self._generate_threat_assessment(competitor_profiles)
        
        # Recommendations
        recommendations = [
            f"Monitor {len([c for c in competitor_profiles if c.threat_level == ThreatLevel.HIGH])} high-threat competitors closely",
            "Differentiate on speed and customer success",
            "Consider category creation strategy to avoid direct competition"
        ]
        
        if gaps:
            recommendations.append(f"Capitalize on identified market gap: {gaps[0]['description']}")
        
        # Summary
        analysis_summary = f"Analyzed {len(competitor_profiles)} competitors. "
        analysis_summary += f"Threat level: {threat_assessment['overall_threat_level']}. "
        analysis_summary += f"Identified {len(advantages)} competitive advantages and {len(gaps)} market gaps."
        
        return CompetitorAnalysisResult(
            competitors=competitor_profiles,
            competitive_advantages=advantages,
            market_gaps=gaps,
            positioning_opportunities=positioning_opportunities,
            threat_assessment=threat_assessment,
            recommendations=recommendations,
            analysis_summary=analysis_summary
        )
    
    def _generate_demo_competitors(self, company_info: Dict[str, Any], industry: str) -> List[Dict[str, Any]]:
        """Generate demo competitors based on industry"""
        templates = {
            "saas": [
                {
                    "name": "Established Leader",
                    "website": "https://leader.example.com",
                    "tagline": "The industry standard",
                    "core_claim": "Trusted by Fortune 500",
                    "target_audience": "Enterprise",
                    "features": ["Feature A", "Feature B", "Feature C", "Enterprise SSO"],
                    "pricing_model": "Per seat",
                    "pricing_range": "$50-200/user/mo",
                    "free_tier": False,
                    "funding_raised": "Series D - $150M",
                    "market_position": "leader",
                    "product_overlap": 0.8,
                    "market_overlap": 0.6
                },
                {
                    "name": "Fast Challenger",
                    "website": "https://challenger.example.com",
                    "tagline": "The modern alternative",
                    "core_claim": "Built for speed",
                    "target_audience": "Growth teams",
                    "features": ["Feature A", "Feature B", "Integrations"],
                    "pricing_model": "Usage-based",
                    "pricing_range": "$29-99/mo",
                    "free_tier": True,
                    "funding_raised": "Series B - $40M",
                    "market_position": "challenger",
                    "product_overlap": 0.9,
                    "market_overlap": 0.8
                },
                {
                    "name": "Spreadsheets",
                    "website": "",
                    "tagline": "The status quo",
                    "core_claim": "Everyone knows it",
                    "target_audience": "Everyone",
                    "features": ["Flexibility", "Familiarity"],
                    "pricing_model": "Free/Bundled",
                    "pricing_range": "$0-20/mo",
                    "free_tier": True,
                    "is_status_quo": True,
                    "product_overlap": 0.3,
                    "market_overlap": 1.0
                }
            ],
            "default": [
                {
                    "name": "Industry Incumbent",
                    "website": "https://incumbent.example.com",
                    "tagline": "Trusted for decades",
                    "core_claim": "Reliable and proven",
                    "target_audience": "Enterprise",
                    "features": ["Core Feature"],
                    "pricing_model": "Enterprise",
                    "pricing_range": "Contact sales",
                    "free_tier": False,
                    "product_overlap": 0.7,
                    "market_overlap": 0.5
                }
            ]
        }
        
        return templates.get(industry, templates["default"])
    
    def get_competitor_summary(self, result: CompetitorAnalysisResult) -> Dict[str, Any]:
        """Get summary for display"""
        return {
            "competitor_count": len(result.competitors),
            "threat_level": result.threat_assessment["overall_threat_level"],
            "high_threats": result.threat_assessment["high_threat_count"],
            "advantages_found": len(result.competitive_advantages),
            "gaps_found": len(result.market_gaps),
            "summary": result.analysis_summary,
            "top_recommendations": result.recommendations[:3]
        }
