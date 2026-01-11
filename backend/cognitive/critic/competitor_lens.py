"""
Competitor Lens for Adversarial Critic

Analyzes content from competitor perspective.
Implements PROMPT 59 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..models import Entity, EntityType


class CompetitorAnalysisType(Enum):
    """Types of competitor analysis."""
    WEAKNESS_IDENTIFICATION = "weakness_identification"
    DIFFERENTIATION_OPPORTUNITIES = "differentiation_opportunities"
    MARKET_POSITIONING = "market_positioning"
    COMPETITIVE_ADVANTAGE = "competitive_advantage"
    THREAT_ASSESSMENT = "threat_assessment"
    STRATEGIC_RECOMMENDATIONS = "strategic_recommendations"


class CompetitorPerspective(Enum):
    """Perspectives to analyze from."""
    CUSTOMER = "customer"
    INVESTOR = "investor"
    EMPLOYEE = "employee"
    PARTNER = "partner"
    REGULATOR = "regulator"
    COMPETITOR = "competitor"


@dataclass
class CompetitorInsight:
    """An insight from competitor perspective."""
    id: str
    perspective: CompetitorPerspective
    insight_type: str
    description: str
    severity: str  # "low", "medium", "high", "critical"
    confidence: float  # 0-1 scale
    evidence: List[str]
    recommendations: List[str]


@dataclass
class CompetitiveWeakness:
    """A weakness identified from competitor perspective."""
    area: str
    description: str
    impact_level: str  # "low", "medium", "high", "critical"
    exploitability: float  # 0-1 scale
    mitigation_difficulty: float  # 0-1 scale
    examples: List[str]


@dataclass
class DifferentiationOpportunity:
    """An opportunity to differentiate from competitors."""
    area: str
    description: str
    market_gap: str
    implementation_complexity: str  # "low", "medium", "high"
    potential_impact: str  # "low", "medium", "high", "critical"
    time_to_market: str


@dataclass
class CompetitorCritique:
    """Complete competitor critique analysis."""
    content_id: str
    competitors_analyzed: List[str]
    analysis_date: datetime
    insights: List[CompetitorInsight]
    weaknesses: List[CompetitiveWeakness]
    opportunities: List[DifferentiationOpportunity]
    overall_threat_level: str  # "low", "medium", "high", "critical"
    competitive_score: float  # 0-100 scale
    strategic_recommendations: List[str]
    analysis_time_ms: int


class CompetitorLens:
    """
    Analyzes content from competitor perspective.

    Identifies weaknesses, opportunities, and threats as competitors would see them.
    """

    def __init__(self, llm_client=None, market_data=None):
        """
        Initialize the competitor lens.

        Args:
            llm_client: LLM client for analysis
            market_data: Market data for context
        """
        self.llm_client = llm_client
        self.market_data = market_data

        # Competitor analysis frameworks
        self.swot_framework = {
            "strengths": [
                "What advantages do we have?",
                "What unique capabilities do we possess?",
                "What do competitors see as our strengths?"
            ],
            "weaknesses": [
                "What could competitors exploit?",
                "Where are we vulnerable?",
                "What do competitors see as our weaknesses?"
            ],
            "opportunities": [
                "What gaps can we exploit?",
                "What trends can we leverage?",
                "Where are competitors weak?"
            ],
            "threats": [
                "What are competitors doing?",
                "What market changes threaten us?",
                "How could competitors attack us?"
            ]
        }

        # Porter's Five Forces for competitive analysis
        self.porter_forces = {
            "competitive_rivalry": [
                "How intense is competition?",
                "What are competitor strengths?",
                "How can competitors differentiate?"
            ],
            "threat_of_new_entries": [
                "What barriers to entry exist?",
                "How could new competitors enter?",
                "What makes us vulnerable to new entrants?"
            ],
            "threat_of_substitutes": [
                "What alternatives exist?",
                "How easily can customers switch?",
                "What makes substitutes attractive?"
            ],
            "bargaining_power_of_buyers": [
                "How much power do customers have?",
                "What can competitors offer customers?",
                "How can competitors win our customers?"
            ],
            "bargaining_power_of_suppliers": [
                "How dependent are we on suppliers?",
                "Can competitors work with our suppliers?",
                "What supply chain vulnerabilities exist?"
            ]
        }

        # Common competitor attack vectors
        self.attack_vectors = [
            "price competition",
            "feature differentiation",
            "customer service superiority",
            "marketing and branding",
            "distribution channels",
            "technology innovation",
            "partnership ecosystems",
            "regulatory compliance",
            "supply chain disruption",
            "talent acquisition"
        ]

    async def critique_as_competitor(self, content: str, competitors: List[str]) -> CompetitorCritique:
        """
        Analyze content from competitor perspective.

        Args:
            content: Content to analyze
            competitors: List of competitor names

        Returns:
            Complete competitor critique analysis
        """
        import time
        start_time = time.time()

        # Extract key information from content
        content_analysis = await self._analyze_content(content)

        # Generate insights from different perspectives
        insights = await self._generate_perspective_insights(content, content_analysis, competitors)

        # Identify competitive weaknesses
        weaknesses = await self._identify_weaknesses(content, content_analysis, competitors)

        # Find differentiation opportunities
        opportunities = await self._identify_opportunities(content, content_analysis, competitors)

        # Assess overall threat level
        threat_level = await self._assess_threat_level(insights, weaknesses)

        # Calculate competitive score
        competitive_score = self._calculate_competitive_score(insights, weaknesses, opportunities)

        # Generate strategic recommendations
        recommendations = await self._generate_strategic_recommendations(
            insights, weaknesses, opportunities, threat_level
        )

        analysis_time_ms = int((time.time() - start_time) * 1000)

        return CompetitorCritique(
            content_id=self._generate_content_id(content),
            competitors_analyzed=competitors,
            analysis_date=datetime.now(),
            insights=insights,
            weaknesses=weaknesses,
            opportunities=opportunities,
            overall_threat_level=threat_level,
            competitive_score=competitive_score,
            strategic_recommendations=recommendations,
            analysis_time_ms=analysis_time_ms
        )

    async def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze content for competitive intelligence."""
        analysis = {
            "key_features": [],
            "value_propositions": [],
            "target_markets": [],
            "pricing_mentioned": [],
            "technology_mentions": [],
            "partnerships": [],
            "strengths_claimed": [],
            "weaknesses_revealed": []
        }

        # Extract key features
        feature_patterns = [
            r"(?:feature|capability|functionality|offers?|provides?)\s*[:\-]?\s*([^.!?]+)",
            r"(?:we|our)\s+(?:offer|provide|have|include)\s+([^.!?]+)",
            r"(?:key|main|primary)\s+(?:feature|benefit|advantage)s?\s*[:\-]?\s*([^.!?]+)"
        ]

        for pattern in feature_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis["key_features"].extend(matches)

        # Extract value propositions
        value_patterns = [
            r"(?:value\s+proposition|benefit|advantage)\s*[:\-]?\s*([^.!?]+)",
            r"(?:why|because|due to)\s+([^.!?]+)",
            r"(?:helps?|enables?|allows?)\s+(?:you|customers?)\s+([^.!?]+)"
        ]

        for pattern in value_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis["value_propositions"].extend(matches)

        # Extract pricing information
        pricing_patterns = [
            r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:dollars?|USD)",
            r"(?:price|cost|pricing)\s*[:\-]?\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)"
        ]

        for pattern in pricing_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis["pricing_mentioned"].extend(matches)

        # Extract technology mentions
        tech_patterns = [
            r"\b(AI|ML|machine learning|artificial intelligence|blockchain|cloud|SaaS|API|SDK)\b",
            r"\b(Python|JavaScript|React|Node\.js|AWS|Azure|GCP)\b",
            r"\b(technology|platform|system|software|application)\s+([^.!?]+)"
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if isinstance(matches[0], tuple) if matches else False:
                analysis["technology_mentions"].extend([match[0] for match in matches])
            else:
                analysis["technology_mentions"].extend(matches)

        # Extract partnerships
        partnership_patterns = [
            r"(?:partner|partnership|collaborate|integration)\s+(?:with|of)\s+([^.!?]+)",
            r"(?:work|integrates?|connects?)\s+with\s+([^.!?]+)",
            r"(?:powered by|using|built on)\s+([^.!?]+)"
        ]

        for pattern in partnership_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            analysis["partnerships"].extend(matches)

        return analysis

    async def _generate_perspective_insights(self, content: str, content_analysis: Dict[str, Any],
                                           competitors: List[str]) -> List[CompetitorInsight]:
        """Generate insights from different competitor perspectives."""
        insights = []

        for perspective in CompetitorPerspective:
            perspective_insights = await self._analyze_from_perspective(
                perspective, content, content_analysis, competitors
            )
            insights.extend(perspective_insights)

        return insights

    async def _analyze_from_perspective(self, perspective: CompetitorPerspective, content: str,
                                      content_analysis: Dict[str, Any], competitors: List[str]) -> List[CompetitorInsight]:
        """Analyze content from a specific perspective."""
        insights = []

        if perspective == CompetitorPerspective.CUSTOMER:
            insights.extend(await self._customer_perspective_analysis(content, content_analysis))
        elif perspective == CompetitorPerspective.INVESTOR:
            insights.extend(await self._investor_perspective_analysis(content, content_analysis))
        elif perspective == CompetitorPerspective.EMPLOYEE:
            insights.extend(await self._employee_perspective_analysis(content, content_analysis))
        elif perspective == CompetitorPerspective.PARTNER:
            insights.extend(await self._partner_perspective_analysis(content, content_analysis))
        elif perspective == CompetitorPerspective.REGULATOR:
            insights.extend(await self._regulator_perspective_analysis(content, content_analysis))
        elif perspective == CompetitorPerspective.COMPETITOR:
            insights.extend(await self._competitor_perspective_analysis(content, content_analysis, competitors))

        return insights

    async def _customer_perspective_analysis(self, content: str, content_analysis: Dict[str, Any]) -> List[CompetitorInsight]:
        """Analyze from customer perspective."""
        insights = []

        # Value proposition assessment
        if content_analysis["value_propositions"]:
            insights.append(CompetitorInsight(
                id="customer_value_assessment",
                perspective=CompetitorPerspective.CUSTOMER,
                insight_type="value_assessment",
                description=f"Customers see {len(content_analysis['value_propositions'])} value propositions",
                severity="medium",
                confidence=0.7,
                evidence=content_analysis["value_propositions"][:3],
                recommendations=["Strengthen unique value propositions", "Quantify customer benefits"]
            ))

        # Pricing assessment
        if content_analysis["pricing_mentioned"]:
            insights.append(CompetitorInsight(
                id="customer_pricing_sensitivity",
                perspective=CompetitorPerspective.CUSTOMER,
                insight_type="pricing_analysis",
                description="Pricing information may attract price-sensitive competitors",
                severity="medium",
                confidence=0.8,
                evidence=content_analysis["pricing_mentioned"],
                recommendations=["Consider value-based pricing", "Highlight ROI over price"]
            ))

        return insights

    async def _investor_perspective_analysis(self, content: str, content_analysis: Dict[str, Any]) -> List[CompetitorInsight]:
        """Analyze from investor perspective."""
        insights = []

        # Technology assessment
        if content_analysis["technology_mentions"]:
            insights.append(CompetitorInsight(
                id="investor_tech_assessment",
                perspective=CompetitorPerspective.INVESTOR,
                insight_type="technology_analysis",
                description="Technology stack may reveal competitive advantages to investors",
                severity="medium",
                confidence=0.6,
                evidence=content_analysis["technology_mentions"][:3],
                recommendations=["Protect IP and technology", "Highlight innovation"]
            ))

        # Partnership assessment
        if content_analysis["partnerships"]:
            insights.append(CompetitorInsight(
                id="investor_partnership_assessment",
                perspective=CompetitorPerspective.INVESTOR,
                insight_type="partnership_analysis",
                description="Partnerships may indicate market validation or dependencies",
                severity="low",
                confidence=0.5,
                evidence=content_analysis["partnerships"][:2],
                recommendations=["Diversify partnership portfolio", "Secure exclusive partnerships"]
            ))

        return insights

    async def _employee_perspective_analysis(self, content: str, content_analysis: Dict[str, Any]) -> List[CompetitorInsight]:
        """Analyze from employee perspective."""
        insights = []

        # Feature complexity assessment
        if len(content_analysis["key_features"]) > 5:
            insights.append(CompetitorInsight(
                id="employee_complexity_assessment",
                perspective=CompetitorPerspective.EMPLOYEE,
                insight_type="complexity_analysis",
                description="Complex feature set may require specialized talent",
                severity="medium",
                confidence=0.6,
                evidence=[f"{len(content_analysis['key_features'])} features identified"],
                recommendations=["Simplify product architecture", "Invest in talent development"]
            ))

        return insights

    async def _partner_perspective_analysis(self, content: str, content_analysis: Dict[str, Any]) -> List[CompetitorInsight]:
        """Analyze from partner perspective."""
        insights = []

        # Integration opportunities
        if content_analysis["technology_mentions"]:
            insights.append(CompetitorInsight(
                id="partner_integration_opportunities",
                perspective=CompetitorPerspective.PARTNER,
                insight_type="integration_analysis",
                description="Technology stack presents integration opportunities for partners",
                severity="low",
                confidence=0.5,
                evidence=content_analysis["technology_mentions"][:2],
                recommendations=["Develop partner API", "Create integration marketplace"]
            ))

        return insights

    async def _regulator_perspective_analysis(self, content: str, content_analysis: Dict[str, Any]) -> List[CompetitorInsight]:
        """Analyze from regulator perspective."""
        insights = []

        # Compliance considerations
        if any(term in content.lower() for term in ["data", "privacy", "security", "financial"]):
            insights.append(CompetitorInsight(
                id="regulator_compliance_assessment",
                perspective=CompetitorPerspective.REGULATOR,
                insight_type="compliance_analysis",
                description="Content may trigger regulatory compliance requirements",
                severity="medium",
                confidence=0.7,
                evidence=["Mentions of sensitive data areas"],
                recommendations=["Ensure compliance frameworks", "Document compliance processes"]
            ))

        return insights

    async def _competitor_perspective_analysis(self, content: str, content_analysis: Dict[str, Any],
                                            competitors: List[str]) -> List[CompetitorInsight]:
        """Analyze from direct competitor perspective."""
        insights = []

        # Feature comparison
        if content_analysis["key_features"]:
            insights.append(CompetitorInsight(
                id="competitor_feature_analysis",
                perspective=CompetitorPerspective.COMPETITOR,
                insight_type="feature_analysis",
                description=f"Features reveal potential competitive advantages or gaps",
                severity="high",
                confidence=0.8,
                evidence=content_analysis["key_features"][:3],
                recommendations=["Conduct feature gap analysis", "Develop competitive differentiation"]
            ))

        # Market positioning
        if content_analysis["value_propositions"]:
            insights.append(CompetitorInsight(
                id="competitor_positioning_analysis",
                perspective=CompetitorPerspective.COMPETITOR,
                insight_type="positioning_analysis",
                description="Value propositions indicate market positioning strategy",
                severity="high",
                confidence=0.7,
                evidence=content_analysis["value_propositions"][:2],
                recommendations=["Analyze competitive positioning", "Develop counter-positioning"]
            ))

        return insights

    async def _identify_weaknesses(self, content: str, content_analysis: Dict[str, Any],
                                 competitors: List[str]) -> List[CompetitiveWeakness]:
        """Identify competitive weaknesses."""
        weaknesses = []

        # Feature complexity weakness
        if len(content_analysis["key_features"]) > 8:
            weaknesses.append(CompetitiveWeakness(
                area="Feature Complexity",
                description="Large feature set may indicate complexity and maintenance challenges",
                impact_level="medium",
                exploitability=0.6,
                mitigation_difficulty=0.7,
                examples=["Competitor could offer simpler solution", "Higher maintenance costs"]
            ))

        # Pricing transparency weakness
        if content_analysis["pricing_mentioned"]:
            weaknesses.append(CompetitiveWeakness(
                area="Pricing Transparency",
                description="Public pricing information enables competitor price competition",
                impact_level="medium",
                exploitability=0.8,
                mitigation_difficulty=0.4,
                examples=["Price undercutting", "Value-based pricing attacks"]
            ))

        # Technology dependency weakness
        if content_analysis["technology_mentions"]:
            weaknesses.append(CompetitiveWeakness(
                area="Technology Dependencies",
                description="Technology stack reveals potential dependencies and vulnerabilities",
                impact_level="medium",
                exploitability=0.5,
                mitigation_difficulty=0.6,
                examples["Competitor could target technology gaps", "Supply chain attacks"]
            ))

        return weaknesses

    async def _identify_opportunities(self, content: str, content_analysis: Dict[str, Any],
                                    competitors: List[str]) -> List[DifferentiationOpportunity]:
        """Identify differentiation opportunities."""
        opportunities = []

        # Feature gap opportunities
        if content_analysis["key_features"]:
            opportunities.append(DifferentiationOpportunity(
                area="Feature Innovation",
                description="Identify gaps in current feature set for differentiation",
                market_gap="Underserved customer needs",
                implementation_complexity="medium",
                potential_impact="high",
                time_to_market="6-12 months"
            ))

        # Value proposition opportunities
        if content_analysis["value_propositions"]:
            opportunities.append(DifferentiationOpportunity(
                area="Value Proposition Enhancement",
                description="Strengthen and differentiate value propositions",
                market_gap="Weak or generic value messaging",
                implementation_complexity="low",
                potential_impact="medium",
                time_to_market="3-6 months"
            ))

        # Partnership opportunities
        if not content_analysis["partnerships"]:
            opportunities.append(DifferentiationOpportunity(
                area="Strategic Partnerships",
                description="Develop partnerships to create competitive moat",
                market_gap="Lack of ecosystem partnerships",
                implementation_complexity="high",
                potential_impact="critical",
                time_to_market="12-18 months"
            ))

        return opportunities

    async def _assess_threat_level(self, insights: List[CompetitorInsight],
                                 weaknesses: List[CompetitiveWeakness]) -> str:
        """Assess overall competitive threat level."""
        threat_score = 0

        # Score insights
        for insight in insights:
            severity_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            threat_score += severity_scores.get(insight.severity, 1) * insight.confidence

        # Score weaknesses
        for weakness in weaknesses:
            impact_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
            threat_score += impact_scores.get(weakness.impact_level, 1) * weakness.exploitability

        # Normalize to threat level
        avg_threat_score = threat_score / (len(insights) + len(weaknesses)) if (insights or weaknesses) else 0

        if avg_threat_score >= 3.0:
            return "critical"
        elif avg_threat_score >= 2.0:
            return "high"
        elif avg_threat_score >= 1.0:
            return "medium"
        else:
            return "low"

    def _calculate_competitive_score(self, insights: List[CompetitorInsight],
                                   weaknesses: List[CompetitiveWeakness],
                                   opportunities: List[DifferentiationOpportunity]) -> float:
        """Calculate overall competitive score."""
        base_score = 50.0

        # Adjust based on insights
        for insight in insights:
            if insight.severity in ["high", "critical"]:
                base_score -= 10 * insight.confidence
            elif insight.severity == "medium":
                base_score -= 5 * insight.confidence

        # Adjust based on weaknesses
        for weakness in weaknesses:
            base_score -= 15 * weakness.exploitability

        # Adjust based on opportunities
        for opportunity in opportunities:
            impact_scores = {"low": 5, "medium": 10, "high": 15, "critical": 20}
            base_score += impact_scores.get(opportunity.potential_impact, 10)

        return max(0.0, min(100.0, base_score))

    async def _generate_strategic_recommendations(self, insights: List[CompetitorInsight],
                                               weaknesses: List[CompetitiveWeakness],
                                               opportunities: List[DifferentiationOpportunity],
                                               threat_level: str) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []

        # Threat-based recommendations
        if threat_level in ["high", "critical"]:
            recommendations.extend([
                "Implement competitive intelligence monitoring",
                "Develop rapid response capabilities",
                "Strengthen competitive barriers"
            ])

        # Weakness-based recommendations
        critical_weaknesses = [w for w in weaknesses if w.impact_level in ["high", "critical"]]
        if critical_weaknesses:
            recommendations.append("Address critical competitive weaknesses immediately")

        # Opportunity-based recommendations
        high_impact_opportunities = [o for o in opportunities if o.potential_impact in ["high", "critical"]]
        if high_impact_opportunities:
            recommendations.append("Pursue high-impact differentiation opportunities")

        # General recommendations
        recommendations.extend([
            "Conduct regular competitive analysis",
            "Develop competitive response strategies",
            "Monitor competitor moves and market changes",
            "Build sustainable competitive advantages"
        ])

        return recommendations[:6]  # Return top 6 recommendations

    def _generate_content_id(self, content: str) -> str:
        """Generate content ID for analysis."""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def get_competitor_analysis_stats(self, critiques: List[CompetitorCritique]) -> Dict[str, Any]:
        """Get statistics about competitor analyses."""
        if not critiques:
            return {}

        total_analyses = len(critiques)
        total_insights = sum(len(c.insights) for c in critiques)
        total_weaknesses = sum(len(c.weaknesses) for c in critiques)
        total_opportunities = sum(len(c.opportunities) for c in critiques)

        # Perspective distribution
        perspective_counts = {}
        for critique in critiques:
            for insight in critique.insights:
                perspective = insight.perspective.value
                perspective_counts[perspective] = perspective_counts.get(perspective, 0) + 1

        # Threat level distribution
        threat_counts = {}
        for critique in critiques:
            threat = critique.overall_threat_level
            threat_counts[threat] = threat_counts.get(threat, 0) + 1

        # Average competitive score
        avg_competitive_score = sum(c.competitive_score for c in critiques) / total_analyses

        return {
            'total_analyses': total_analyses,
            'total_insights_generated': total_insights,
            'total_weaknesses_identified': total_weaknesses,
            'total_opportunities_found': total_opportunities,
            'perspective_distribution': perspective_counts,
            'threat_level_distribution': threat_counts,
            'average_competitive_score': avg_competitive_score,
            'average_analysis_time_ms': sum(c.analysis_time_ms for c in critiques) / total_analyses
        }
