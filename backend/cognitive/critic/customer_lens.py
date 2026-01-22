"""
Customer Lens for Adversarial Critic

Analyzes content from customer perspective.
Implements PROMPT 60 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..models import Entity, EntityType


class CustomerSegment(Enum):
    """Customer segments for analysis."""

    ENTERPRISE = "enterprise"
    SMB = "smb"  # Small and Medium Business
    STARTUP = "startup"
    CONSUMER = "consumer"
    DEVELOPER = "developer"
    STUDENT = "student"
    GOVERNMENT = "government"
    NONPROFIT = "nonprofit"


class CustomerPersona(Enum):
    """Customer personas for detailed analysis."""

    DECISION_MAKER = "decision_maker"
    TECHNICAL_USER = "technical_user"
    BUSINESS_USER = "business_user"
    END_USER = "end_user"
    INFLUENCER = "influencer"
    BUDGET_HOLDER = "budget_holder"


class CustomerReaction(Enum):
    """Types of customer reactions."""

    ENTHUSIASTIC = "enthusiastic"
    INTERESTED = "interested"
    NEUTRAL = "neutral"
    SKEPTICAL = "skeptical"
    CONFUSED = "confused"
    CONCERNED = "concerned"
    REJECTED = "rejected"


@dataclass
class CustomerInsight:
    """An insight from customer perspective."""

    id: str
    segment: CustomerSegment
    persona: CustomerPersona
    insight_type: str
    description: str
    reaction: CustomerReaction
    confidence: float  # 0-1 scale
    reasoning: str
    quotes: List[str]  # What customers might say
    concerns: List[str]
    questions: List[str]


@dataclass
class ValuePropositionMatch:
    """How well content matches customer value propositions."""

    customer_need: str
    content_addressal: str
    match_score: float  # 0-1 scale
    gaps: List[str]
    strengths: List[str]


@dataclass
class CustomerJourneyImpact:
    """Impact on customer journey stages."""

    journey_stage: (
        str  # awareness, consideration, decision, purchase, onboarding, usage, advocacy
    )
    impact_type: str  # positive, negative, neutral
    description: str
    action_required: str


@dataclass
class CustomerCritique:
    """Complete customer perspective analysis."""

    content_id: str
    analysis_date: datetime
    segments_analyzed: List[CustomerSegment]
    personas_analyzed: List[CustomerPersona]
    insights: List[CustomerInsight]
    value_matches: List[ValuePropositionMatch]
    journey_impacts: List[CustomerJourneyImpact]
    overall_customer_sentiment: CustomerReaction
    trust_score: float  # 0-100 scale
    purchase_likelihood: float  # 0-100 scale
    recommendations: List[str]
    analysis_time_ms: int


class CustomerLens:
    """
    Analyzes content from customer perspective.

    Evaluates how customers would perceive, trust, and act on content.
    """

    def __init__(self, llm_client=None, customer_data=None):
        """
        Initialize the customer lens.

        Args:
            llm_client: LLM client for analysis
            customer_data: Customer data and personas
        """
        self.llm_client = llm_client
        self.customer_data = customer_data

        # Customer needs and pain points by segment
        self.customer_needs = {
            CustomerSegment.ENTERPRISE: [
                "Scalability and reliability",
                "Security and compliance",
                "ROI and cost justification",
                "Integration with existing systems",
                "Support and service level agreements",
                "Data privacy and governance",
            ],
            CustomerSegment.SMB: [
                "Affordability and value",
                "Ease of use and implementation",
                "Quick time to value",
                "Flexibility and adaptability",
                "Customer support",
                "Growth potential",
            ],
            CustomerSegment.STARTUP: [
                "Speed and agility",
                "Cost effectiveness",
                "Scalability for growth",
                "Developer-friendly",
                "Modern technology stack",
                "Minimal overhead",
            ],
            CustomerSegment.CONSUMER: [
                "Simplicity and intuitiveness",
                "Trust and credibility",
                "Personalization",
                "Social proof",
                "Mobile accessibility",
                "Privacy protection",
            ],
            CustomerSegment.DEVELOPER: [
                "Documentation and clarity",
                "API quality and consistency",
                "Performance and reliability",
                "Community and support",
                "Flexibility and extensibility",
                "Modern practices",
            ],
        }

        # Customer journey stages
        self.journey_stages = [
            "awareness",
            "consideration",
            "decision",
            "purchase",
            "onboarding",
            "usage",
            "advocacy",
        ]

        # Trust indicators
        self.trust_indicators = [
            "social_proof",
            "testimonials",
            "case_studies",
            "certifications",
            "security_badges",
            "money_back_guarantee",
            "free_trial",
            "transparent_pricing",
            "professional_design",
            "contact_information",
            "privacy_policy",
            "terms_of_service",
        ]

        # Red flags that reduce trust
        self.trust_red_flags = [
            "vague_claims",
            "missing_pricing",
            "no_contact_info",
            "grammar_errors",
            "unrealistic_promises",
            "pressure_tactics",
            "hidden_costs",
            "lack_of_social_proof",
            "outdated_information",
            "technical_jargon",
            "inconsistent_messaging",
        ]

    async def critique_as_customer(
        self, content: str, icp: Dict[str, Any]
    ) -> CustomerCritique:
        """
        Analyze content from customer perspective.

        Args:
            content: Content to analyze
            icp: Ideal Customer Profile data

        Returns:
            Complete customer critique analysis
        """
        import time

        start_time = time.time()

        # Determine target segments and personas
        segments = await self._determine_target_segments(content, icp)
        personas = await self._determine_target_personas(content, icp)

        # Generate insights from different perspectives
        insights = await self._generate_customer_insights(content, segments, personas)

        # Analyze value proposition matches
        value_matches = await self._analyze_value_propositions(content, segments)

        # Assess customer journey impacts
        journey_impacts = await self._analyze_journey_impacts(content, segments)

        # Calculate overall sentiment and scores
        overall_sentiment = await self._determine_overall_sentiment(insights)
        trust_score = await self._calculate_trust_score(content, insights)
        purchase_likelihood = await self._calculate_purchase_likelihood(
            insights, trust_score
        )

        # Generate recommendations
        recommendations = await self._generate_customer_recommendations(
            insights, value_matches, journey_impacts, trust_score, purchase_likelihood
        )

        analysis_time_ms = int((time.time() - start_time) * 1000)

        return CustomerCritique(
            content_id=self._generate_content_id(content),
            analysis_date=datetime.now(),
            segments_analyzed=segments,
            personas_analyzed=personas,
            insights=insights,
            value_matches=value_matches,
            journey_impacts=journey_impacts,
            overall_customer_sentiment=overall_sentiment,
            trust_score=trust_score,
            purchase_likelihood=purchase_likelihood,
            recommendations=recommendations,
            analysis_time_ms=analysis_time_ms,
        )

    async def _determine_target_segments(
        self, content: str, icp: Dict[str, Any]
    ) -> List[CustomerSegment]:
        """Determine target customer segments from content and ICP."""
        segments = []

        # Extract segment indicators from content
        content_lower = content.lower()

        # Enterprise indicators
        enterprise_keywords = [
            "enterprise",
            "large organization",
            "fortune",
            "corporate",
            "scale",
        ]
        if any(keyword in content_lower for keyword in enterprise_keywords):
            segments.append(CustomerSegment.ENTERPRISE)

        # SMB indicators
        smb_keywords = ["small business", "medium business", "smb", "growing business"]
        if any(keyword in content_lower for keyword in smb_keywords):
            segments.append(CustomerSegment.SMB)

        # Startup indicators
        startup_keywords = ["startup", "early stage", "venture", "seed", "series a"]
        if any(keyword in content_lower for keyword in startup_keywords):
            segments.append(CustomerSegment.STARTUP)

        # Developer indicators
        dev_keywords = ["api", "sdk", "developer", "code", "programming", "integration"]
        if any(keyword in content_lower for keyword in dev_keywords):
            segments.append(CustomerSegment.DEVELOPER)

        # Consumer indicators
        consumer_keywords = ["individual", "personal", "consumer", "user", "customer"]
        if any(keyword in content_lower for keyword in consumer_keywords):
            segments.append(CustomerSegment.CONSUMER)

        # Default to segments from ICP if no clear indicators
        if not segments and icp:
            icp_segments = icp.get("segments", [])
            for seg in icp_segments:
                if seg.lower() in [s.value for s in CustomerSegment]:
                    segments.append(CustomerSegment(seg.lower()))

        # Default to CONSUMER if still no segments
        if not segments:
            segments.append(CustomerSegment.CONSUMER)

        return segments

    async def _determine_target_personas(
        self, content: str, icp: Dict[str, Any]
    ) -> List[CustomerPersona]:
        """Determine target customer personas."""
        personas = []

        content_lower = content.lower()

        # Decision maker indicators
        decision_keywords = [
            "decision",
            "approve",
            "budget",
            "purchase",
            "buy",
            "invest",
        ]
        if any(keyword in content_lower for keyword in decision_keywords):
            personas.append(CustomerPersona.DECISION_MAKER)

        # Technical user indicators
        tech_keywords = [
            "technical",
            "developer",
            "engineer",
            "api",
            "integration",
            "code",
        ]
        if any(keyword in content_lower for keyword in tech_keywords):
            personas.append(CustomerPersona.TECHNICAL_USER)

        # Business user indicators
        business_keywords = [
            "business",
            "productivity",
            "efficiency",
            "workflow",
            "process",
        ]
        if any(keyword in content_lower for keyword in business_keywords):
            personas.append(CustomerPersona.BUSINESS_USER)

        # End user indicators
        end_user_keywords = [
            "use",
            "experience",
            "interface",
            "easy",
            "simple",
            "intuitive",
        ]
        if any(keyword in content_lower for keyword in end_user_keywords):
            personas.append(CustomerPersona.END_USER)

        # Default personas from ICP
        if not personas and icp:
            icp_personas = icp.get("personas", [])
            for persona in icp_personas:
                if persona.lower() in [p.value for p in CustomerPersona]:
                    personas.append(CustomerPersona(persona.lower()))

        # Default to END_USER if still no personas
        if not personas:
            personas.append(CustomerPersona.END_USER)

        return personas

    async def _generate_customer_insights(
        self,
        content: str,
        segments: List[CustomerSegment],
        personas: List[CustomerPersona],
    ) -> List[CustomerInsight]:
        """Generate insights from customer perspectives."""
        insights = []

        # Generate insights for each segment-persona combination
        for segment in segments:
            for persona in personas:
                segment_insights = await self._analyze_segment_persona_perspective(
                    content, segment, persona
                )
                insights.extend(segment_insights)

        return insights

    async def _analyze_segment_persona_perspective(
        self, content: str, segment: CustomerSegment, persona: CustomerPersona
    ) -> List[CustomerInsight]:
        """Analyze content from specific segment-persona perspective."""
        insights = []

        # Get customer needs for this segment
        needs = self.customer_needs.get(segment, [])

        # Analyze how well content addresses needs
        content_lower = content.lower()
        addressed_needs = []
        unaddressed_needs = []

        for need in needs:
            need_keywords = need.lower().split()
            if any(keyword in content_lower for keyword in need_keywords):
                addressed_needs.append(need)
            else:
                unaddressed_needs.append(need)

        # Generate insight based on need addressing
        if addressed_needs:
            insights.append(
                CustomerInsight(
                    id=f"{segment.value}_{persona.value}_needs_met",
                    segment=segment,
                    persona=persona,
                    insight_type="needs_analysis",
                    description=f"Content addresses {len(addressed_needs)} key needs",
                    reaction=CustomerReaction.INTERESTED,
                    confidence=0.7,
                    reasoning=f"Found references to: {', '.join(addressed_needs[:2])}",
                    quotes=[f"This addresses our {addressed_needs[0].lower()} needs"],
                    concerns=[],
                    questions=[f"How does this compare to alternatives?"],
                )
            )

        if unaddressed_needs:
            insights.append(
                CustomerInsight(
                    id=f"{segment.value}_{persona.value}_needs_gap",
                    segment=segment,
                    persona=persona,
                    insight_type="needs_gap",
                    description=f"Content doesn't address {len(unaddressed_needs)} important needs",
                    reaction=CustomerReaction.CONCERNED,
                    confidence=0.6,
                    reasoning=f"Missing references to: {', '.join(unaddressed_needs[:2])}",
                    quotes=[f"What about {unaddressed_needs[0].lower()}?"],
                    concerns=unaddressed_needs[:2],
                    questions=[f"How do you handle {unaddressed_needs[0].lower()}?"],
                )
            )

        # Analyze language and complexity for persona
        complexity_insight = await self._analyze_content_complexity(
            content, segment, persona
        )
        if complexity_insight:
            insights.append(complexity_insight)

        # Analyze trust factors
        trust_insight = await self._analyze_trust_factors(content, segment, persona)
        if trust_insight:
            insights.append(trust_insight)

        return insights

    async def _analyze_content_complexity(
        self, content: str, segment: CustomerSegment, persona: CustomerPersona
    ) -> Optional[CustomerInsight]:
        """Analyze content complexity for persona."""
        # Calculate complexity metrics
        sentences = re.split(r"[.!?]+", content)
        avg_sentence_length = (
            sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        )

        technical_terms = len(
            re.findall(r"\b(API|SDK|SaaS|B2B|B2C|ROI|KPI|SLA)\b", content)
        )

        # Determine appropriate complexity for persona
        if persona == CustomerPersona.TECHNICAL_USER:
            if technical_terms < 2:
                return CustomerInsight(
                    id=f"{segment.value}_{persona.value}_too_simple",
                    segment=segment,
                    persona=persona,
                    insight_type="complexity_analysis",
                    description="Content may be too simple for technical users",
                    reaction=CustomerReaction.SKEPTICAL,
                    confidence=0.5,
                    reasoning="Low technical term usage",
                    quotes=["Where are the technical details?"],
                    concerns=["Lacks technical depth"],
                    questions=["What's the architecture?"],
                )
        elif persona in [CustomerPersona.END_USER, CustomerPersona.BUSINESS_USER]:
            if avg_sentence_length > 20 or technical_terms > 5:
                return CustomerInsight(
                    id=f"{segment.value}_{persona.value}_too_complex",
                    segment=segment,
                    persona=persona,
                    insight_type="complexity_analysis",
                    description="Content may be too complex for this audience",
                    reaction=CustomerReaction.CONFUSED,
                    confidence=0.6,
                    reasoning=f"High complexity: {avg_sentence_length:.1f} avg words, {technical_terms} technical terms",
                    quotes=["This is too technical for me"],
                    concerns=["Too complex to understand"],
                    questions=["Can you explain this in simple terms?"],
                )

        return None

    async def _analyze_trust_factors(
        self, content: str, segment: CustomerSegment, persona: CustomerPersona
    ) -> Optional[CustomerInsight]:
        """Analyze trust factors in content."""
        trust_score = 0
        red_flags = 0

        # Check for trust indicators
        for indicator in self.trust_indicators:
            if indicator.replace("_", " ") in content.lower():
                trust_score += 1

        # Check for red flags
        for flag in self.trust_red_flags:
            if flag.replace("_", " ") in content.lower():
                red_flags += 1

        # Generate insight based on trust analysis
        if red_flags > trust_score:
            return CustomerInsight(
                id=f"{segment.value}_{persona.value}_trust_concerns",
                segment=segment,
                persona=persona,
                insight_type="trust_analysis",
                description="Content has trust concerns that may reduce credibility",
                reaction=CustomerReaction.SKEPTICAL,
                confidence=0.7,
                reasoning=f"Found {red_flags} red flags vs {trust_score} trust indicators",
                quotes=["I'm not sure I can trust this"],
                concerns=["Lacks credibility indicators"],
                questions=["Can you provide proof or testimonials?"],
            )
        elif trust_score > red_flags + 2:
            return CustomerInsight(
                id=f"{segment.value}_{persona.value}_trust_positive",
                segment=segment,
                persona=persona,
                insight_type="trust_analysis",
                description="Content shows good trust indicators",
                reaction=CustomerReaction.INTERESTED,
                confidence=0.6,
                reasoning=f"Found {trust_score} trust indicators vs {red_flags} red flags",
                quotes=["This looks trustworthy"],
                concerns=[],
                questions=[],
            )

        return None

    async def _analyze_value_propositions(
        self, content: str, segments: List[CustomerSegment]
    ) -> List[ValuePropositionMatch]:
        """Analyze how well content matches customer value propositions."""
        matches = []

        for segment in segments:
            needs = self.customer_needs.get(segment, [])

            for need in needs:
                # Check if content addresses this need
                need_keywords = need.lower().split()
                content_lower = content.lower()

                addressed = any(keyword in content_lower for keyword in need_keywords)

                if addressed:
                    # Calculate match score
                    match_score = min(
                        1.0,
                        sum(1 for keyword in need_keywords if keyword in content_lower)
                        / len(need_keywords),
                    )

                    matches.append(
                        ValuePropositionMatch(
                            customer_need=need,
                            content_addressal=f"Found references to {need}",
                            match_score=match_score,
                            gaps=[],
                            strengths=[f"Addresses {need}"],
                        )
                    )
                else:
                    matches.append(
                        ValuePropositionMatch(
                            customer_need=need,
                            content_addressal="No direct addressing found",
                            match_score=0.0,
                            gaps=[f"Doesn't address {need}"],
                            strengths=[],
                        )
                    )

        return matches

    async def _analyze_journey_impacts(
        self, content: str, segments: List[CustomerSegment]
    ) -> List[CustomerJourneyImpact]:
        """Analyze impact on customer journey stages."""
        impacts = []

        content_lower = content.lower()

        for stage in self.journey_stages:
            # Determine impact type based on content characteristics
            impact_type = "neutral"
            description = "No clear impact on this stage"
            action_required = ""

            if stage == "awareness":
                if any(
                    word in content_lower
                    for word in ["new", "innovative", "first", "unique"]
                ):
                    impact_type = "positive"
                    description = "Content creates awareness through differentiation"
                    action_required = "Leverage unique messaging"
                elif any(
                    word in content_lower for word in ["generic", "similar", "like"]
                ):
                    impact_type = "negative"
                    description = "Content fails to differentiate in awareness stage"
                    action_required = "Strengthen unique value proposition"

            elif stage == "consideration":
                if any(
                    word in content_lower
                    for word in ["compare", "versus", "better than"]
                ):
                    impact_type = "positive"
                    description = "Content supports consideration through comparison"
                    action_required = "Highlight competitive advantages"
                elif any(
                    word in content_lower
                    for word in ["unclear", "confusing", "complicated"]
                ):
                    impact_type = "negative"
                    description = "Content may hinder consideration due to complexity"
                    action_required = "Simplify messaging"

            elif stage == "decision":
                if any(
                    word in content_lower
                    for word in ["buy", "purchase", "sign up", "get started"]
                ):
                    impact_type = "positive"
                    description = "Content includes clear call-to-action"
                    action_required = "Optimize conversion funnel"
                elif any(
                    word in content_lower for word in ["maybe", "perhaps", "consider"]
                ):
                    impact_type = "negative"
                    description = "Content lacks decisive messaging"
                    action_required = "Add stronger call-to-action"

            impacts.append(
                CustomerJourneyImpact(
                    journey_stage=stage,
                    impact_type=impact_type,
                    description=description,
                    action_required=action_required,
                )
            )

        return impacts

    async def _determine_overall_sentiment(
        self, insights: List[CustomerInsight]
    ) -> CustomerReaction:
        """Determine overall customer sentiment from insights."""
        if not insights:
            return CustomerReaction.NEUTRAL

        # Count reactions
        reaction_counts = {}
        for insight in insights:
            reaction = insight.reaction.value
            reaction_counts[reaction] = reaction_counts.get(reaction, 0) + 1

        # Weight by confidence
        weighted_scores = {}
        for insight in insights:
            reaction = insight.reaction.value
            score = self._reaction_score(insight.reaction)
            weighted_score = score * insight.confidence
            weighted_scores[reaction] = (
                weighted_scores.get(reaction, 0) + weighted_score
            )

        # Find dominant reaction
        if weighted_scores:
            dominant_reaction = max(weighted_scores.items(), key=lambda x: x[1])[0]
            return CustomerReaction(dominant_reaction)

        return CustomerReaction.NEUTRAL

    def _reaction_score(self, reaction: CustomerReaction) -> float:
        """Get numeric score for reaction."""
        scores = {
            CustomerReaction.ENTHUSIASTIC: 2.0,
            CustomerReaction.INTERESTED: 1.0,
            CustomerReaction.NEUTRAL: 0.0,
            CustomerReaction.SKEPTICAL: -0.5,
            CustomerReaction.CONFUSED: -1.0,
            CustomerReaction.CONCERNED: -1.5,
            CustomerReaction.REJECTED: -2.0,
        }
        return scores.get(reaction, 0.0)

    async def _calculate_trust_score(
        self, content: str, insights: List[CustomerInsight]
    ) -> float:
        """Calculate overall trust score (0-100)."""
        base_score = 50.0

        # Adjust based on trust-related insights
        for insight in insights:
            if insight.insight_type == "trust_analysis":
                if insight.reaction in [
                    CustomerReaction.INTERESTED,
                    CustomerReaction.ENTHUSIASTIC,
                ]:
                    base_score += 10 * insight.confidence
                elif insight.reaction in [
                    CustomerReaction.SKEPTICAL,
                    CustomerReaction.CONCERNED,
                ]:
                    base_score -= 15 * insight.confidence

        # Check for trust indicators in content
        content_lower = content.lower()
        trust_indicators_found = 0
        for indicator in self.trust_indicators:
            if indicator.replace("_", " ") in content_lower:
                trust_indicators_found += 1

        base_score += trust_indicators_found * 3

        # Check for red flags
        red_flags_found = 0
        for flag in self.trust_red_flags:
            if flag.replace("_", " ") in content_lower:
                red_flags_found += 1

        base_score -= red_flags_found * 5

        return max(0.0, min(100.0, base_score))

    async def _calculate_purchase_likelihood(
        self, insights: List[CustomerInsight], trust_score: float
    ) -> float:
        """Calculate purchase likelihood (0-100)."""
        base_score = trust_score * 0.6  # Trust is 60% of purchase decision

        # Adjust based on sentiment
        sentiment_score = 0.0
        for insight in insights:
            sentiment_score += (
                self._reaction_score(insight.reaction) * insight.confidence
            )

        if insights:
            avg_sentiment = sentiment_score / len(insights)
            # Convert sentiment score to 0-100 scale
            sentiment_percentage = (
                (avg_sentiment + 2) / 4
            ) * 100  # Normalize -2 to 2 range
            base_score += (
                sentiment_percentage * 0.4
            )  # Sentiment is 40% of purchase decision

        return max(0.0, min(100.0, base_score))

    async def _generate_customer_recommendations(
        self,
        insights: List[CustomerInsight],
        value_matches: List[ValuePropositionMatch],
        journey_impacts: List[CustomerJourneyImpact],
        trust_score: float,
        purchase_likelihood: float,
    ) -> List[str]:
        """Generate customer-focused recommendations."""
        recommendations = []

        # Trust-based recommendations
        if trust_score < 60:
            recommendations.extend(
                [
                    "Add trust indicators (testimonials, case studies, certifications)",
                    "Be more transparent about pricing and processes",
                    "Include contact information and support details",
                ]
            )

        # Value proposition recommendations
        low_matches = [m for m in value_matches if m.match_score < 0.3]
        if low_matches:
            recommendations.append(
                "Address key customer needs that are currently missing"
            )

        # Journey impact recommendations
        negative_impacts = [j for j in journey_impacts if j.impact_type == "negative"]
        if negative_impacts:
            recommendations.append(
                "Improve content for critical customer journey stages"
            )

        # Sentiment-based recommendations
        concerned_insights = [
            i
            for i in insights
            if i.reaction in [CustomerReaction.CONCERNED, CustomerReaction.SKEPTICAL]
        ]
        if concerned_insights:
            recommendations.append("Address customer concerns and questions directly")

        # General recommendations
        recommendations.extend(
            [
                "Test content with actual customers from target segments",
                "A/B test messaging for different personas",
                "Continuously gather customer feedback and iterate",
            ]
        )

        return recommendations[:6]  # Return top 6 recommendations

    def _generate_content_id(self, content: str) -> str:
        """Generate content ID for analysis."""
        import hashlib

        return hashlib.md5(content.encode()).hexdigest()[:16]

    def get_customer_analysis_stats(
        self, critiques: List[CustomerCritique]
    ) -> Dict[str, Any]:
        """Get statistics about customer analyses."""
        if not critiques:
            return {}

        total_analyses = len(critiques)
        total_insights = sum(len(c.insights) for c in critiques)

        # Segment distribution
        segment_counts = {}
        for critique in critiques:
            for segment in critique.segments_analyzed:
                segment = segment.value
                segment_counts[segment] = segment_counts.get(segment, 0) + 1

        # Sentiment distribution
        sentiment_counts = {}
        for critique in critiques:
            sentiment = critique.overall_customer_sentiment.value
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

        # Average scores
        avg_trust_score = sum(c.trust_score for c in critiques) / total_analyses
        avg_purchase_likelihood = (
            sum(c.purchase_likelihood for c in critiques) / total_analyses
        )

        return {
            "total_analyses": total_analyses,
            "total_insights_generated": total_insights,
            "segment_distribution": segment_counts,
            "sentiment_distribution": sentiment_counts,
            "average_trust_score": avg_trust_score,
            "average_purchase_likelihood": avg_purchase_likelihood,
            "average_analysis_time_ms": sum(c.analysis_time_ms for c in critiques)
            / total_analyses,
        }
