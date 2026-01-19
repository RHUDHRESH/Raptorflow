"""
Competitive Analysis Automation
Advanced competitive intelligence and analysis for Raptorflow
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import asyncio
import re
from collections import defaultdict, Counter

# Import AI services
try:
    from services.vertex_ai_service import vertex_ai_service
except ImportError:
    vertex_ai_service = None

logger = logging.getLogger(__name__)


class CompetitorSize(str, Enum):
    """Competitor company sizes"""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class CompetitorType(str, Enum):
    """Types of competitors"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    SUBSTITUTE = "substitute"
    POTENTIAL = "potential"


class AnalysisDimension(str, Enum):
    """Dimensions for competitive analysis"""
    PRODUCT = "product"
    PRICING = "pricing"
    MARKETING = "marketing"
    SALES = "sales"
    CUSTOMER_SERVICE = "customer_service"
    TECHNOLOGY = "technology"
    BRAND = "brand"
    MARKET_POSITION = "market_position"


@dataclass
class Competitor:
    """Competitor information"""
    id: str
    name: str
    website: str
    description: str
    size: CompetitorSize
    type: CompetitorType
    founded_year: Optional[int] = None
    employee_count: Optional[int] = None
    revenue: Optional[float] = None
    funding: Optional[float] = None
    headquarters: Optional[str] = None
    target_market: str = ""
    key_products: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    market_share: float = 0.0
    growth_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "website": self.website,
            "description": self.description,
            "size": self.size.value,
            "type": self.type.value,
            "founded_year": self.founded_year,
            "employee_count": self.employee_count,
            "revenue": self.revenue,
            "funding": self.funding,
            "headquarters": self.headquarters,
            "target_market": self.target_market,
            "key_products": self.key_products,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "market_share": self.market_share,
            "growth_rate": self.growth_rate,
            "metadata": self.metadata
        }


@dataclass
class CompetitiveInsight:
    """Competitive analysis insight"""
    dimension: AnalysisDimension
    insight: str
    evidence: List[str]
    confidence: float
    impact_score: float
    urgency_score: float
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SWOTAnalysis:
    """SWOT analysis for competitive positioning"""
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    confidence_score: float
    analysis_date: datetime = field(default_factory=datetime.now)


@dataclass
class CompetitiveAnalysis:
    """Complete competitive analysis"""
    company_info: Dict[str, Any]
    competitors: List[Competitor]
    insights: List[CompetitiveInsight]
    swot_analysis: SWOTAnalysis
    market_positioning: Dict[str, Any]
    competitive_gaps: List[str]
    recommendations: List[str]
    processing_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class CompetitiveAnalysisAutomation:
    """Advanced competitive analysis automation service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Known competitors database
        self.competitor_database = self._initialize_competitor_database()
        
        # Analysis frameworks
        self.analysis_frameworks = self._initialize_analysis_frameworks()
        
        # Competitive dimensions
        self.dimension_keywords = self._initialize_dimension_keywords()
    
    def _initialize_competitor_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize known competitor database"""
        return {
            "hubspot": {
                "name": "HubSpot",
                "website": "https://hubspot.com",
                "description": "Inbound marketing, sales, and service software",
                "size": CompetitorSize.ENTERPRISE,
                "type": CompetitorType.DIRECT,
                "founded_year": 2006,
                "employee_count": 7000,
                "revenue": 1.5,  # Billion USD
                "headquarters": "Cambridge, MA",
                "target_market": "Mid-market to Enterprise",
                "key_products": ["Marketing Hub", "Sales Hub", "Service Hub", "CMS Hub"],
                "market_share": 0.25
            },
            "salesforce": {
                "name": "Salesforce",
                "website": "https://salesforce.com",
                "description": "Customer relationship management platform",
                "size": CompetitorSize.ENTERPRISE,
                "type": CompetitorType.DIRECT,
                "founded_year": 1999,
                "employee_count": 70000,
                "revenue": 31.4,  # Billion USD
                "headquarters": "San Francisco, CA",
                "target_market": "Enterprise",
                "key_products": ["Sales Cloud", "Service Cloud", "Marketing Cloud", "Commerce Cloud"],
                "market_share": 0.35
            },
            "marketo": {
                "name": "Marketo",
                "website": "https://marketo.com",
                "description": "Marketing automation software",
                "size": CompetitorSize.LARGE,
                "type": CompetitorType.DIRECT,
                "founded_year": 2006,
                "employee_count": 1200,
                "revenue": 0.5,  # Billion USD
                "headquarters": "San Mateo, CA",
                "target_market": "Mid-market to Enterprise",
                "key_products": ["Engage", "Measure", "Advertise"],
                "market_share": 0.08
            },
            "pardot": {
                "name": "Pardot",
                "website": "https://pardot.com",
                "description": "B2B marketing automation",
                "size": CompetitorSize.LARGE,
                "type": CompetitorType.DIRECT,
                "founded_year": 2007,
                "employee_count": 500,
                "revenue": 0.3,  # Billion USD
                "headquarters": "Atlanta, GA",
                "target_market": "Mid-market",
                "key_products": ["Lead Generation", "Lead Nurturing", "ROI Reporting"],
                "market_share": 0.05
            },
            "activecampaign": {
                "name": "ActiveCampaign",
                "website": "https://activecampaign.com",
                "description": "Customer experience automation platform",
                "size": CompetitorSize.MEDIUM,
                "type": CompetitorType.DIRECT,
                "founded_year": 2003,
                "employee_count": 800,
                "revenue": 0.2,  # Billion USD
                "headquarters": "Chicago, IL",
                "target_market": "Small to Mid-market",
                "key_products": ["Email Marketing", "Marketing Automation", "Sales CRM", "Messaging"],
                "market_share": 0.04
            },
            "mailchimp": {
                "name": "Mailchimp",
                "website": "https://mailchimp.com",
                "description": "Email marketing and automation platform",
                "size": CompetitorSize.LARGE,
                "type": CompetitorType.INDIRECT,
                "founded_year": 2001,
                "employee_count": 1200,
                "revenue": 0.8,  # Billion USD
                "headquarters": "Atlanta, GA",
                "target_market": "Small Business",
                "key_products": ["Email Marketing", "Marketing Automation", "Website Builder"],
                "market_share": 0.12
            }
        }
    
    def _initialize_analysis_frameworks(self) -> Dict[str, List[str]]:
        """Initialize analysis frameworks"""
        return {
            "porter_five_forces": [
                "threat_of_new_entries",
                "bargaining_power_of_buyers",
                "bargaining_power_of_suppliers",
                "threat_of_substitute_products",
                "competitive_rivalry"
            ],
            "swot": [
                "strengths",
                "weaknesses", 
                "opportunities",
                "threats"
            ],
            "competitive_advantage": [
                "cost_leadership",
                "differentiation",
                "focus",
                "customer_intimacy",
                "product_leadership",
                "operational_excellence"
            ]
        }
    
    def _initialize_dimension_keywords(self) -> Dict[AnalysisDimension, List[str]]:
        """Initialize keywords for analysis dimensions"""
        return {
            AnalysisDimension.PRODUCT: [
                "features", "functionality", "capabilities", "product", "solution",
                "platform", "software", "tool", "system", "technology", "innovation"
            ],
            AnalysisDimension.PRICING: [
                "price", "cost", "pricing", "fee", "subscription", "license", "model",
                "affordable", "expensive", "value", "roi", "investment", "budget"
            ],
            AnalysisDimension.MARKETING: [
                "marketing", "brand", "advertising", "promotion", "campaign", "content",
                "social", "seo", "ppc", "leads", "conversion", "messaging", "positioning"
            ],
            AnalysisDimension.SALES: [
                "sales", "selling", "revenue", "deals", "pipeline", "crm", "process",
                "cycle", "conversion", "quota", "team", "strategy", "enablement"
            ],
            AnalysisDimension.CUSTOMER_SERVICE: [
                "support", "service", "customer", "help", "assistance", "success",
                "experience", "satisfaction", "retention", "churn", "ticket", "response"
            ],
            AnalysisDimension.TECHNOLOGY: [
                "technology", "tech", "infrastructure", "architecture", "integration",
                "api", "security", "scalability", "performance", "reliability", "stack"
            ],
            AnalysisDimension.BRAND: [
                "brand", "reputation", "recognition", "awareness", "perception",
                "image", "identity", "trust", "credibility", "authority", "presence"
            ],
            AnalysisDimension.MARKET_POSITION: [
                "market", "position", "share", "leader", "follower", "niche",
                "segment", "category", "industry", "vertical", "landscape"
            ]
        }
    
    async def analyze_competition(self, company_info: Dict[str, Any], evidence: List[Dict[str, Any]] = None) -> CompetitiveAnalysis:
        """Perform comprehensive competitive analysis"""
        start_time = datetime.now()
        
        # Identify relevant competitors
        competitors = await self._identify_competitors(company_info, evidence)
        
        # Analyze each dimension
        insights = []
        for dimension in AnalysisDimension:
            dimension_insights = await self._analyze_dimension(dimension, competitors, company_info)
            insights.extend(dimension_insights)
        
        # Perform SWOT analysis
        swot_analysis = await self._perform_swot_analysis(competitors, company_info)
        
        # Analyze market positioning
        market_positioning = await self._analyze_market_positioning(competitors, company_info)
        
        # Identify competitive gaps
        competitive_gaps = await self._identify_competitive_gaps(competitors, company_info)
        
        # Generate recommendations
        recommendations = self._generate_competitive_recommendations(insights, swot_analysis, competitive_gaps)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return CompetitiveAnalysis(
            company_info=company_info,
            competitors=competitors,
            insights=insights,
            swot_analysis=swot_analysis,
            market_positioning=market_positioning,
            competitive_gaps=competitive_gaps,
            recommendations=recommendations,
            processing_time=processing_time,
            metadata={
                "analysis_date": datetime.now().isoformat(),
                "competitors_analyzed": len(competitors),
                "insights_generated": len(insights)
            }
        )
    
    async def _identify_competitors(self, company_info: Dict[str, Any], evidence: List[Dict[str, Any]] = None) -> List[Competitor]:
        """Identify relevant competitors"""
        competitors = []
        
        # Get company industry and target market
        industry = company_info.get("industry", "marketing technology").lower()
        target_market = company_info.get("target_market", "mid-market").lower()
        
        # Filter competitors based on relevance
        for comp_key, comp_data in self.competitor_database.items():
            # Check industry relevance
            if industry in ["marketing", "sales", "crm", "automation"]:
                is_relevant = True
            else:
                is_relevant = False
            
            # Check target market overlap
            comp_target = comp_data.get("target_market", "").lower()
            market_overlap = any(market in comp_target for market in ["small", "mid", "enterprise"])
            
            if is_relevant and market_overlap:
                competitor = Competitor(
                    id=comp_key,
                    name=comp_data["name"],
                    website=comp_data["website"],
                    description=comp_data["description"],
                    size=comp_data["size"],
                    type=comp_data["type"],
                    founded_year=comp_data.get("founded_year"),
                    employee_count=comp_data.get("employee_count"),
                    revenue=comp_data.get("revenue"),
                    headquarters=comp_data.get("headquarters"),
                    target_market=comp_data.get("target_market", ""),
                    key_products=comp_data.get("key_products", []),
                    market_share=comp_data.get("market_share", 0.0)
                )
                
                # Analyze strengths and weaknesses
                competitor.strengths, competitor.weaknesses = await self._analyze_competitor_sw(comp_data)
                
                competitors.append(competitor)
        
        # Sort by market share
        competitors.sort(key=lambda x: x.market_share, reverse=True)
        
        return competitors[:10]  # Top 10 competitors
    
    async def _analyze_competitor_sw(self, comp_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Analyze competitor strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        # Size-based analysis
        size = comp_data.get("size", CompetitorSize.MEDIUM)
        if size in [CompetitorSize.LARGE, CompetitorSize.ENTERPRISE]:
            strengths.extend(["Market leader", "Extensive resources", "Brand recognition"])
            weaknesses.extend(["Slow innovation", "High prices", "Complex products"])
        elif size == CompetitorSize.STARTUP:
            strengths.extend(["Agile", "Innovative", "Customer-focused"])
            weaknesses.extend(["Limited resources", "Unproven", "Risky"])
        
        # Revenue-based analysis
        revenue = comp_data.get("revenue", 0)
        if revenue > 1.0:  # Billion USD
            strengths.append("Strong financial position")
        elif revenue < 0.1:
            weaknesses.append("Limited financial resources")
        
        # Product-based analysis
        products = comp_data.get("key_products", [])
        if len(products) > 4:
            strengths.append("Comprehensive product suite")
            weaknesses.append("Complex to implement")
        elif len(products) < 2:
            weaknesses.append("Limited product offerings")
        
        return strengths, weaknesses
    
    async def _analyze_dimension(self, dimension: AnalysisDimension, competitors: List[Competitor], company_info: Dict[str, Any]) -> List[CompetitiveInsight]:
        """Analyze specific competitive dimension"""
        insights = []
        
        if dimension == AnalysisDimension.PRODUCT:
            insights.append(await self._analyze_product_dimension(competitors, company_info))
        elif dimension == AnalysisDimension.PRICING:
            insights.append(await self._analyze_pricing_dimension(competitors, company_info))
        elif dimension == AnalysisDimension.MARKETING:
            insights.append(await self._analyze_marketing_dimension(competitors, company_info))
        elif dimension == AnalysisDimension.SALES:
            insights.append(await self._analyze_sales_dimension(competitors, company_info))
        elif dimension == AnalysisDimension.CUSTOMER_SERVICE:
            insights.append(await self._analyze_customer_service_dimension(competitors, company_info))
        elif dimension == AnalysisDimension.TECHNOLOGY:
            insights.append(await self._analyze_technology_dimension(competitors, company_info))
        elif dimension == AnalysisDimension.BRAND:
            insights.append(await self._analyze_brand_dimension(competitors, company_info))
        elif dimension == AnalysisDimension.MARKET_POSITION:
            insights.append(await self._analyze_market_position_dimension(competitors, company_info))
        
        return insights
    
    async def _analyze_product_dimension(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> CompetitiveInsight:
        """Analyze product dimension"""
        # Collect product information
        all_products = []
        for competitor in competitors:
            all_products.extend(competitor.key_products)
        
        # Identify product gaps
        product_counts = Counter(all_products)
        common_products = [product for product, count in product_counts.items() if count >= 2]
        
        # Generate insight
        if len(common_products) > 3:
            insight = "Market has standardized on core product features. Differentiation requires innovation beyond standard offerings."
            impact_score = 0.7
            urgency_score = 0.6
        else:
            insight = "Product landscape is fragmented. Opportunity to establish standard features."
            impact_score = 0.8
            urgency_score = 0.7
        
        recommendations = [
            "Focus on unique features not offered by major competitors",
            "Consider integration capabilities as differentiator",
            "Evaluate product gaps in competitor offerings"
        ]
        
        return CompetitiveInsight(
            dimension=AnalysisDimension.PRODUCT,
            insight=insight,
            evidence=common_products[:5],
            confidence=0.8,
            impact_score=impact_score,
            urgency_score=urgency_score,
            recommendations=recommendations
        )
    
    async def _analyze_pricing_dimension(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> CompetitiveInsight:
        """Analyze pricing dimension"""
        # Analyze pricing patterns
        enterprise_competitors = [c for c in competitors if c.size in [CompetitorSize.LARGE, CompetitorSize.ENTERPRISE]]
        smb_competitors = [c for c in competitors if c.size in [CompetitorSize.SMALL, CompetitorSize.STARTUP]]
        
        # Generate insight based on market structure
        if len(enterprise_competitors) > len(smb_competitors):
            insight = "Market dominated by enterprise players with premium pricing. Opportunity for mid-market solutions."
            impact_score = 0.8
            urgency_score = 0.5
        else:
            insight = "Competitive pricing environment with multiple price points. Value proposition critical."
            impact_score = 0.7
            urgency_score = 0.7
        
        recommendations = [
            "Develop tiered pricing strategy",
            "Emphasize ROI and value over price",
            "Consider freemium model for market entry"
        ]
        
        return CompetitiveInsight(
            dimension=AnalysisDimension.PRICING,
            insight=insight,
            evidence=[f"Enterprise competitors: {len(enterprise_competitors)}", f"SMB competitors: {len(smb_competitors)}"],
            confidence=0.7,
            impact_score=impact_score,
            urgency_score=urgency_score,
            recommendations=recommendations
        )
    
    async def _analyze_marketing_dimension(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> CompetitiveInsight:
        """Analyze marketing dimension"""
        # Analyze brand presence and marketing sophistication
        large_competitors = [c for c in competitors if c.size in [CompetitorSize.LARGE, CompetitorSize.ENTERPRISE]]
        
        if len(large_competitors) > 3:
            insight = "High marketing sophistication among major competitors. Requires strong brand differentiation."
            impact_score = 0.8
            urgency_score = 0.6
        else:
            insight = "Marketing landscape relatively open. Opportunity for strong brand building."
            impact_score = 0.7
            urgency_score = 0.5
        
        recommendations = [
            "Develop unique brand positioning",
            "Focus on content marketing and thought leadership",
            "Leverage digital channels efficiently"
        ]
        
        return CompetitiveInsight(
            dimension=AnalysisDimension.MARKETING,
            insight=insight,
            evidence=[f"Large competitors: {len(large_competitors)}"],
            confidence=0.7,
            impact_score=impact_score,
            urgency_score=urgency_score,
            recommendations=recommendations
        )
    
    async def _analyze_sales_dimension(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> CompetitiveInsight:
        """Analyze sales dimension"""
        # Analyze sales channel complexity
        enterprise_competitors = [c for c in competitors if c.target_market.lower() in ["enterprise", "mid-market to enterprise"]]
        
        if len(enterprise_competitors) > 2:
            insight = "Complex enterprise sales cycles with multiple stakeholders. Requires sophisticated sales strategy."
            impact_score = 0.8
            urgency_score = 0.6
        else:
            insight = "Simpler sales environment. Opportunity for direct sales and self-service."
            impact_score = 0.6
            urgency_score = 0.5
        
        recommendations = [
            "Develop sales process for target market",
            "Create sales enablement materials",
            "Consider channel partnerships"
        ]
        
        return CompetitiveInsight(
            dimension=AnalysisDimension.SALES,
            insight=insight,
            evidence=[f"Enterprise-focused competitors: {len(enterprise_competitors)}"],
            confidence=0.7,
            impact_score=impact_score,
            urgency_score=urgency_score,
            recommendations=recommendations
        )
    
    async def _analyze_customer_service_dimension(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> CompetitiveInsight:
        """Analyze customer service dimension"""
        # Analyze service expectations
        large_competitors = [c for c in competitors if c.size in [CompetitorSize.LARGE, CompetitorSize.ENTERPRISE]]
        
        if len(large_competitors) > 2:
            insight = "High customer service expectations set by enterprise players. Service quality is key differentiator."
            impact_score = 0.7
            urgency_score = 0.6
        else:
            insight = "Service standards vary. Opportunity to differentiate through superior support."
            impact_score = 0.8
            urgency_score = 0.5
        
        recommendations = [
            "Invest in customer success program",
            "Develop comprehensive support resources",
            "Implement proactive customer outreach"
        ]
        
        return CompetitiveInsight(
            dimension=AnalysisDimension.CUSTOMER_SERVICE,
            insight=insight,
            evidence=[f"Large competitors: {len(large_competitors)}"],
            confidence=0.7,
            impact_score=impact_score,
            urgency_score=urgency_score,
            recommendations=recommendations
        )
    
    async def _analyze_technology_dimension(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> CompetitiveInsight:
        """Analyze technology dimension"""
        # Analyze technology sophistication
        enterprise_competitors = [c for c in competitors if c.size in [CompetitorSize.LARGE, CompetitorSize.ENTERPRISE]]
        
        if len(enterprise_competitors) > 2:
            insight = "Advanced technology stack expected by enterprise customers. Integration capabilities critical."
            impact_score = 0.8
            urgency_score = 0.7
        else:
            insight = "Technology requirements vary. Opportunity for simplified, user-friendly solutions."
            impact_score = 0.7
            urgency_score = 0.5
        
        recommendations = [
            "Prioritize integration capabilities",
            "Invest in scalable infrastructure",
            "Focus on user experience and simplicity"
        ]
        
        return CompetitiveInsight(
            dimension=AnalysisDimension.TECHNOLOGY,
            insight=insight,
            evidence=[f"Enterprise competitors: {len(enterprise_competitors)}"],
            confidence=0.7,
            impact_score=impact_score,
            urgency_score=urgency_score,
            recommendations=recommendations
        )
    
    async def _analyze_brand_dimension(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> CompetitiveInsight:
        """Analyze brand dimension"""
        # Analyze brand strength
        market_leaders = [c for c in competitors if c.market_share > 0.2]
        
        if len(market_leaders) > 0:
            insight = "Strong brand dominance by market leaders. Requires niche positioning or brand differentiation."
            impact_score = 0.8
            urgency_score = 0.6
        else:
            insight = "No dominant brands. Opportunity to establish strong market presence."
            impact_score = 0.8
            urgency_score = 0.5
        
        recommendations = [
            "Develop clear brand positioning",
            "Invest in thought leadership content",
            "Build community around brand"
        ]
        
        return CompetitiveInsight(
            dimension=AnalysisDimension.BRAND,
            insight=insight,
            evidence=[f"Market leaders: {len(market_leaders)}"],
            confidence=0.7,
            impact_score=impact_score,
            urgency_score=urgency_score,
            recommendations=recommendations
        )
    
    async def _analyze_market_position_dimension(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> CompetitiveInsight:
        """Analyze market position dimension"""
        # Analyze market concentration
        total_market_share = sum(c.market_share for c in competitors)
        herfindahl_index = sum(c.market_share ** 2 for c in competitors)
        
        if herfindahl_index > 0.25:  # Highly concentrated
            insight = "Highly concentrated market with dominant players. Requires niche strategy."
            impact_score = 0.8
            urgency_score = 0.7
        elif herfindahl_index > 0.15:  # Moderately concentrated
            insight = "Moderately concentrated market. Opportunities for differentiation exist."
            impact_score = 0.7
            urgency_score = 0.6
        else:  # Fragmented
            insight = "Fragmented market with many players. Opportunity for consolidation."
            impact_score = 0.6
            urgency_score = 0.5
        
        recommendations = [
            "Identify underserved market segments",
            "Develop unique value proposition",
            "Consider partnership or acquisition opportunities"
        ]
        
        return CompetitiveInsight(
            dimension=AnalysisDimension.MARKET_POSITION,
            insight=insight,
            evidence=[f"Market concentration: {herfindahl_index:.2f}"],
            confidence=0.8,
            impact_score=impact_score,
            urgency_score=urgency_score,
            recommendations=recommendations
        )
    
    async def _perform_swot_analysis(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> SWOTAnalysis:
        """Perform SWOT analysis"""
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []
        
        # Analyze competitive landscape for opportunities and threats
        large_competitors = [c for c in competitors if c.size in [CompetitorSize.LARGE, CompetitorSize.ENTERPRISE]]
        small_competitors = [c for c in competitors if c.size in [CompetitorSize.SMALL, CompetitorSize.STARTUP]]
        
        # Opportunities
        if len(small_competitors) > len(large_competitors):
            opportunities.append("Market fragmentation allows for consolidation")
        
        if any("integration" in weakness.lower() for c in competitors for weakness in c.weaknesses):
            opportunities.append "Integration capabilities gap in market"
        
        opportunities.extend([
            "Growing demand for marketing automation",
            "AI and machine learning integration opportunities",
            "Mid-market underserved by enterprise solutions"
        ])
        
        # Threats
        if len(large_competitors) > 2:
            threats.append("Market consolidation by large players")
        
        if any(c.market_share > 0.3 for c in competitors):
            threats.append("Dominant market player controls pricing")
        
        threats.extend([
            "Rapid technology changes",
            "New market entrants with innovative solutions",
            "Customer expectations increasing"
        ])
        
        # Strengths (based on company info)
        company_size = company_info.get("size", "startup").lower()
        if company_size in ["startup", "small"]:
            strengths.extend(["Agility and speed", "Customer focus", "Innovation capability"])
        
        # Weaknesses
        if company_size in ["startup", "small"]:
            weaknesses.extend(["Limited resources", "Brand recognition", "Market presence"])
        
        return SWOTAnalysis(
            strengths=strengths[:5],
            weaknesses=weaknesses[:5],
            opportunities=opportunities[:5],
            threats=threats[:5],
            confidence_score=0.7
        )
    
    async def _analyze_market_positioning(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market positioning"""
        # Calculate market concentration
        total_share = sum(c.market_share for c in competitors)
        market_concentration = sum(c.market_share ** 2 for c in competitors)
        
        # Identify positioning gaps
        positioning_map = {
            "price_leader": None,
            "quality_leader": None,
            "innovation_leader": None,
            "service_leader": None
        }
        
        # Simple positioning analysis based on competitor characteristics
        for competitor in competitors:
            if "affordable" in competitor.description.lower() or competitor.size == CompetitorSize.SMALL:
                positioning_map["price_leader"] = competitor.name
            elif "enterprise" in competitor.target_market.lower() or competitor.size == CompetitorSize.ENTERPRISE:
                positioning_map["quality_leader"] = competitor.name
            elif "innovative" in competitor.description.lower() or competitor.size == CompetitorSize.STARTUP:
                positioning_map["innovation_leader"] = competitor.name
        
        return {
            "market_concentration": market_concentration,
            "total_addressable_market": total_share,
            "positioning_gaps": [pos for pos, leader in positioning_map.items() if leader is None],
            "recommended_positioning": self._recommend_positioning(positioning_map, company_info)
        }
    
    def _recommend_positioning(self, positioning_map: Dict[str, Optional[str]], company_info: Dict[str, Any]) -> str:
        """Recommend market positioning"""
        company_size = company_info.get("size", "startup").lower()
        
        if company_size in ["startup", "small"]:
            if positioning_map["innnovation_leader"] is None:
                return "Innovation leader - focus on cutting-edge features"
            elif positioning_map["price_leader"] is None:
                return "Price leader - focus on value and affordability"
            else:
                return "Niche specialist - focus on specific market segment"
        else:
            if positioning_map["quality_leader"] is None:
                return "Quality leader - focus on premium features and service"
            elif positioning_map["service_leader"] is None:
                return "Service leader - focus on customer success"
            else:
                return "Balanced approach - compete on multiple dimensions"
    
    async def _identify_competitive_gaps(self, competitors: List[Competitor], company_info: Dict[str, Any]) -> List[str]:
        """Identify competitive gaps"""
        gaps = []
        
        # Product gaps
        all_products = []
        for competitor in competitors:
            all_products.extend(competitor.key_products)
        
        common_products = [product for product, count in Counter(all_products).items() if count >= 3]
        potential_gaps = ["AI-powered insights", "Advanced analytics", "Mobile-first design", "Voice integration"]
        
        for gap in potential_gaps:
            if not any(gap.lower() in product.lower() for product in common_products):
                gaps.append(f"Product gap: {gap}")
        
        # Market gaps
        target_markets = [c.target_market.lower() for c in competitors]
        if "small business" not in " ".join(target_markets):
            gaps.append("Market gap: Small business segment underserved")
        
        # Service gaps
        if all(c.size != CompetitorSize.STARTUP for c in competitors):
            gaps.append("Service gap: Agile, startup-friendly approach")
        
        return gaps[:5]  # Top 5 gaps
    
    def _generate_competitive_recommendations(self, insights: List[CompetitiveInsight], swot_analysis: SWOTAnalysis, gaps: List[str]) -> List[str]:
        """Generate competitive recommendations"""
        recommendations = []
        
        # High-impact insights
        high_impact_insights = [insight for insight in insights if insight.impact_score > 0.7]
        for insight in high_impact_insights:
            recommendations.extend(insight.recommendations[:2])
        
        # SWOT-based recommendations
        if swot_analysis.opportunities:
            recommendations.append(f"Leverage opportunities: {', '.join(swot_analysis.opportunities[:2])}")
        
        if swot_analysis.threats:
            recommendations.append(f"Mitigate threats: {', '.join(swot_analysis.threats[:2])}")
        
        # Gap-based recommendations
        if gaps:
            recommendations.append(f"Address competitive gaps: {', '.join(gaps[:2])}")
        
        # Strategic recommendations
        recommendations.extend([
            "Develop clear competitive differentiation",
            "Monitor competitor moves regularly",
            "Build competitive intelligence capabilities"
        ])
        
        return recommendations[:10]  # Top 10 recommendations


# Export service
__all__ = ["CompetitiveAnalysisAutomation", "CompetitiveAnalysis", "Competitor", "CompetitiveInsight"]
