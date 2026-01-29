"""
RaptorFlow Advanced ICP Generation Service
Phase 2.3.1: Advanced ICP Generation

AI-powered persona generation with psychographic profiling,
behavioral pattern analysis, market sophistication assessment, and fit scoring.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .config import get_settings
from .core.logging import get_logger
from .services.llm_service import ExtractionContext, LLMService

logger = get_logger(__name__)
settings = get_settings()


class ICPType(str, Enum):
    """Types of ICP profiles."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"


class PsychographicSegment(str, Enum):
    """Psychographic segments."""

    INNOVATORS = "innovators"
    EARLY_ADOPTERS = "early_adopters"
    EARLY_MAJORITY = "early_majority"
    LATE_MAJORITY = "late_majority"
    LAGGARDS = "laggards"


class BehavioralPattern(str, Enum):
    """Behavioral patterns."""

    PRICE_SENSITIVE = "price_sensitive"
    QUALITY_FOCUSED = "quality_focused"
    CONVENIENCE_SEEKER = "convenience_seeker"
    RESEARCH_DRIVEN = "research_driven"
    BRAND_LOYAL = "brand_loyal"
    RISK_AVERSE = "risk_averse"


@dataclass
class Demographics:
    """Demographic information."""

    age_range: Tuple[int, int]
    income_range: Tuple[float, float]
    education_level: str
    location: str
    company_size: str
    industry: str
    job_title: str


@dataclass
class Psychographics:
    """Psychographic profile."""

    values: List[str]
    interests: List[str]
    lifestyle: List[str]
    personality_traits: List[str]
    communication_style: str
    decision_factors: List[str]
    segment: PsychographicSegment


@dataclass
class BehavioralProfile:
    """Behavioral patterns."""

    buying_patterns: List[str]
    research_habits: List[str]
    preferred_channels: List[str]
    engagement_preferences: List[str]
    pain_points: List[str]
    pattern: BehavioralPattern


@dataclass
class ICPProfile:
    """Complete ICP profile."""

    id: str
    name: str
    type: ICPType
    demographics: Demographics
    psychographics: Psychographics
    behaviors: BehavioralProfile
    pain_points: List[str]
    goals: List[str]
    challenges: List[str]
    communication_preferences: Dict
    fit_score: float
    market_sophistication: str
    estimated_market_size: Optional[float] = None
    conversion_likelihood: float
    generated_at: datetime
    confidence_score: float


class PsychographicAnalyzer:
    """Psychographic profiling and analysis."""

    def __init__(self):
        self.nlp = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not available for psychographic analysis")

    async def analyze(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> Psychographics:
        """
        Analyze psychographic profile from business and fact data.

        Args:
            business_data: Business information
            fact_data: Extracted facts

        Returns:
            Psychographic profile
        """
        # Extract values from business data and facts
        values = await self._extract_values(business_data, fact_data)

        # Analyze interests
        interests = await self._analyze_interests(business_data, fact_data)

        # Analyze lifestyle
        lifestyle = await self._analyze_lifestyle(business_data, fact_data)

        # Determine personality traits
        personality_traits = await self._analyze_personality_traits(
            business_data, fact_data
        )

        # Communication style analysis
        communication_style = await self._analyze_communication_style(
            business_data, fact_data
        )

        # Decision factors
        decision_factors = await self._analyze_decision_factors(
            business_data, fact_data
        )

        # Determine psychographic segment
        segment = await self._determine_segment(values, interests, lifestyle)

        return Psychographics(
            values=values,
            interests=interests,
            lifestyle=lifestyle,
            personality_traits=personality_traits,
            communication_style=communication_style,
            decision_factors=decision_factors,
            segment=segment,
        )

    async def _extract_values(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> List[str]:
        """Extract core values from data."""
        values = []

        # Business values from company info
        company_values = business_data.get("values", [])
        values.extend(company_values)

        # Values implied from business model
        business_model = business_data.get("business_model", "")
        if "innovation" in business_model.lower():
            values.extend(["innovation", "creativity", "forward-thinking"])
        if "quality" in business_model.lower():
            values.extend(["quality", "excellence", "reliability"])
        if "efficiency" in business_model.lower():
            values.extend(["efficiency", "productivity", "cost-effectiveness"])

        # Values from customer feedback/facts
        for fact in fact_data:
            if "customer" in fact.get("category", "").lower():
                statement = fact.get("statement", "").lower()
                if "trust" in statement:
                    values.append("trust")
                if "transparency" in statement:
                    values.append("transparency")
                if "community" in statement:
                    values.append("community")

        # Remove duplicates and limit
        unique_values = list(set(values))
        return unique_values[:10]

    async def _analyze_interests(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> List[str]:
        """Analyze customer interests."""
        interests = []

        # Industry-specific interests
        industry = business_data.get("industry", "").lower()
        industry_interests = {
            "technology": [
                "software development",
                "cloud computing",
                "AI/ML",
                "cybersecurity",
                "automation",
            ],
            "healthcare": [
                "wellness",
                "preventive care",
                "medical research",
                "health tech",
            ],
            "finance": [
                "investment",
                "financial planning",
                "risk management",
                "fintech",
            ],
            "retail": ["shopping", "product discovery", "deals", "customer experience"],
            "education": [
                "learning",
                "skill development",
                "certification",
                "knowledge sharing",
            ],
        }

        interests.extend(industry_interests.get(industry, []))

        # Interests from facts
        for fact in fact_data:
            if self.nlp:
                doc = self.nlp(fact.get("statement", ""))
                entities = [
                    ent.text
                    for ent in doc.ents
                    if ent.label_ in ["PRODUCT", "ORG", "EVENT"]
                ]
                interests.extend(entities)

        # Remove duplicates and limit
        unique_interests = list(set(interests))
        return unique_interests[:15]

    async def _analyze_lifestyle(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> List[str]:
        """Analyze lifestyle characteristics."""
        lifestyle = []

        # Business type implications
        business_model = business_data.get("business_model", "").lower()
        if "b2b" in business_model:
            lifestyle.extend(["professional", "career-focused", "efficiency-driven"])
        if "b2c" in business_model:
            lifestyle.extend(
                ["consumer-oriented", "convenience-focused", "experience-driven"]
            )

        # Price point implications
        price_point = business_data.get("price_point", "").lower()
        if "premium" in price_point:
            lifestyle.extend(["luxury", "quality-focused", "status-conscious"])
        if "budget" in price_point:
            lifestyle.extend(["value-conscious", "practical", "deal-seeking"])

        # Remove duplicates and limit
        unique_lifestyle = list(set(lifestyle))
        return unique_lifestyle[:10]

    async def _analyze_personality_traits(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> List[str]:
        """Analyze personality traits."""
        traits = []

        # Business culture implications
        company_culture = business_data.get("company_culture", "").lower()
        if "innovative" in company_culture:
            traits.extend(["open-minded", "adaptable", "creative"])
        if "traditional" in company_culture:
            traits.extend(["conservative", "structured", "reliable"])

        # Target audience implications
        target_audience = business_data.get("target_audience", "").lower()
        if "technical" in target_audience:
            traits.extend(["analytical", "detail-oriented", "logical"])
        if "creative" in target_audience:
            traits.extend(["imaginative", "expressive", "innovative"])

        # Remove duplicates and limit
        unique_traits = list(set(traits))
        return unique_traits[:10]

    async def _analyze_communication_style(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> str:
        """Analyze preferred communication style."""
        # Business communication style
        business_communication = business_data.get("communication_style", "").lower()

        # Target audience preferences
        target_audience = business_data.get("target_audience", "").lower()

        if "technical" in target_audience:
            return "technical_detailed"
        elif "executive" in target_audience:
            return "professional_concise"
        elif "creative" in target_audience:
            return "visual_informal"
        elif "general" in target_audience:
            return "simple_direct"
        else:
            return "professional_balanced"

    async def _analyze_decision_factors(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> List[str]:
        """Analyze key decision factors."""
        factors = []

        # Industry-specific factors
        industry = business_data.get("industry", "").lower()
        industry_factors = {
            "healthcare": [
                "safety",
                "efficacy",
                "recommendations",
                "regulatory_compliance",
            ],
            "finance": ["roi", "risk_assessment", "security", "compliance"],
            "technology": [
                "features",
                "integration",
                "scalability",
                "support",
                "innovation",
            ],
            "retail": [
                "price",
                "quality",
                "convenience",
                "brand_reputation",
                "availability",
            ],
        }

        factors.extend(industry_factors.get(industry, []))

        # Business model factors
        business_model = business_data.get("business_model", "").lower()
        if "subscription" in business_model:
            factors.extend(["long_term_value", "flexibility", "ease_of_cancellation"])
        if "transactional" in business_model:
            factors.extend(["immediate_value", "one_time_cost", "simplicity"])

        # Remove duplicates and limit
        unique_factors = list(set(factors))
        return unique_factors[:10]

    async def _determine_segment(
        self, values: List[str], interests: List[str], lifestyle: List[str]
    ) -> PsychographicSegment:
        """Determine psychographic segment."""
        # Innovation-oriented signals
        innovation_signals = 0
        if any(
            value in ["innovation", "creativity", "forward-thinking"]
            for value in values
        ):
            innovation_signals += 2
        if any(
            interest in ["AI/ML", "automation", "cloud computing"]
            for interest in interests
        ):
            innovation_signals += 2

        # Professional signals
        professional_signals = 0
        if any(
            value in ["efficiency", "productivity", "reliability"] for value in values
        ):
            professional_signals += 2
        if any(
            lifestyle in ["professional", "career-focused"] for lifestyle in lifestyle
        ):
            professional_signals += 2

        # Determine segment
        if innovation_signals >= 3:
            return PsychographicSegment.INNOVATORS
        elif innovation_signals >= 2:
            return PsychographicSegment.EARLY_ADOPTERS
        elif professional_signals >= 2:
            return PsychographicSegment.EARLY_MAJORITY
        else:
            return PsychographicSegment.LATE_MAJORITY


class BehavioralAnalyzer:
    """Behavioral pattern analysis."""

    def __init__(self):
        self.nlp = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not available for behavioral analysis")

    async def analyze(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> BehavioralProfile:
        """
        Analyze behavioral patterns.

        Args:
            business_data: Business information
            fact_data: Extracted facts

        Returns:
            Behavioral profile
        """
        # Analyze buying patterns
        buying_patterns = await self._analyze_buying_patterns(business_data, fact_data)

        # Analyze research habits
        research_habits = await self._analyze_research_habits(business_data, fact_data)

        # Preferred channels
        preferred_channels = await self._analyze_preferred_channels(
            business_data, fact_data
        )

        # Engagement preferences
        engagement_preferences = await self._analyze_engagement_preferences(
            business_data, fact_data
        )

        # Pain points
        pain_points = await self._analyze_pain_points(fact_data)

        # Determine pattern
        pattern = await self._determine_behavioral_pattern(
            buying_patterns, research_habits
        )

        return BehavioralProfile(
            buying_patterns=buying_patterns,
            research_habits=research_habits,
            preferred_channels=preferred_channels,
            engagement_preferences=engagement_preferences,
            pain_points=pain_points,
            pattern=pattern,
        )

    async def _analyze_buying_patterns(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> List[str]:
        """Analyze buying patterns."""
        patterns = []

        # Price sensitivity from business model
        price_point = business_data.get("price_point", "").lower()
        if "budget" in price_point:
            patterns.extend(["price_comparison", "deal_seeking", "bulk_purchasing"])
        elif "premium" in price_point:
            patterns.extend(["quality_focused", "brand_loyalty", "premium_features"])

        # Purchase frequency from business model
        business_model = business_data.get("business_model", "").lower()
        if "subscription" in business_model:
            patterns.extend(["recurring_purchases", "long_term_planning"])
        elif "transactional" in business_model:
            patterns.extend(["one_time_purchases", "impulse_buying"])

        # Research intensity
        patterns.append(["extensive_research", "comparison_shopping"])

        return list(set(patterns))[:8]

    async def _analyze_research_habits(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> List[str]:
        """Analyze research habits."""
        habits = []

        # Industry-specific research habits
        industry = business_data.get("industry", "").lower()
        industry_habits = {
            "technology": [
                "technical_documentation",
                "feature_comparison",
                "trial_usage",
                "peer_reviews",
            ],
            "healthcare": [
                "medical_research",
                "second_opinions",
                "regulatory_research",
            ],
            "finance": [
                "market_analysis",
                "due_diligence",
                "case_studies",
                "expert_consultation",
            ],
        }

        habits.extend(industry_habits.get(industry, []))

        # General research habits
        habits.extend(["online_research", "social_proof_checking", "word_of_mouth"])

        return list(set(habits))[:8]

    async def _analyze_preferred_channels(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> List[str]:
        """Analyze preferred communication channels."""
        channels = []

        # Business model channels
        business_model = business_data.get("business_model", "").lower()
        if "b2b" in business_model:
            channels.extend(
                ["email", "linkedin", "professional_networks", "trade_shows"]
            )
        elif "b2c" in business_model:
            channels.extend(
                ["social_media", "mobile_apps", "online_marketplaces", "reviews"]
            )

        # Target audience channels
        target_audience = business_data.get("target_audience", "").lower()
        if "technical" in target_audience:
            channels.extend(["technical_blogs", "documentation", "forums"])
        elif "executive" in target_audience:
            channels.extend(["executive_briefings", "professional_networks"])

        # Digital preference
        channels.extend(["digital_first", "mobile_first"])

        return list(set(channels))[:8]

    async def _analyze_engagement_preferences(
        self, business_data: Dict, fact_data: List[Dict]
    ) -> List[str]:
        """Analyze engagement preferences."""
        preferences = []

        # Content preferences
        preferences.extend(["data_driven", "personalization", "self_service"])

        # Communication preferences
        preferences.extend(
            ["quick_responses", "multi_channel_support", "proactive_communication"]
        )

        # Community preferences
        preferences.extend(
            ["community_engagement", "user_generated_content", "social_proof"]
        )

        return list(set(preferences))[:8]

    async def _analyze_pain_points(self, fact_data: List[Dict]) -> List[str]:
        """Analyze pain points from facts."""
        pain_points = []

        # Common business pain points
        common_pains = [
            "cost_management",
            "efficiency_challenges",
            "integration_complexity",
            "security_concerns",
            "scalability_issues",
            "user_experience",
            "support_quality",
            "feature_limitations",
            "time_constraints",
        ]

        # Extract pain points from facts
        for fact in fact_data:
            if "pain_point" in fact.get("category", "").lower():
                pain_points.append(fact.get("statement", ""))
            if "challenge" in fact.get("statement", "").lower():
                pain_points.append(fact.get("statement", ""))
            if "problem" in fact.get("statement", "").lower():
                pain_points.append(fact.get("statement", ""))

        # Add common pains if not enough from facts
        if len(pain_points) < 5:
            pain_points.extend(common_pains[:5])

        return list(set(pain_points))[:10]

    async def _determine_behavioral_pattern(
        self, buying_patterns: List[str], research_habits: List[str]
    ) -> BehavioralPattern:
        """Determine behavioral pattern."""
        # Price sensitivity analysis
        price_sensitive = any(
            pattern in ["price_comparison", "deal_seeking", "bulk_purchasing"]
            for pattern in buying_patterns
        )

        # Research intensity analysis
        research_intensive = any(
            habit
            in ["extensive_research", "technical_documentation", "feature_comparison"]
            for habit in research_habits
        )

        # Determine pattern
        if price_sensitive and research_intensive:
            return BehavioralPattern.RESEARCH_DRIVEN
        elif price_sensitive:
            return BehavioralPattern.PRICE_SENSITIVE
        elif research_intensive:
            return BehavioralPattern.QUALITY_FOCUSED
        elif "brand_loyalty" in buying_patterns:
            return BehavioralPattern.BRAND_LOYAL
        elif "quick_responses" in [
            pref
            for pref in ["quick_responses", "multi_channel_support"]
            for pref in ["quick_responses", "multi_channel_support"]
        ]:
            return BehavioralPattern.CONVENIENCE_SEEKER
        else:
            return BehavioralPattern.RISK_AVERSE


class ICPGenerationService:
    """Main ICP generation service."""

    def __init__(self):
        self.llm_service = LLMService()
        self.psychographic_analyzer = PsychographicAnalyzer()
        self.behavioral_analyzer = BehavioralAnalyzer()

    async def generate_icp_profiles(self, business_data: Dict) -> Dict:
        """
        Generate comprehensive ICP profiles.

        Args:
            business_data: Business information

        Returns:
            ICP generation result
        """
        try:
            # Analyze business context
            business_analysis = await self._analyze_business_context(business_data)

            # Generate base personas using LLM
            base_personas = await self.llm_service.generate_icp_profiles(business_data)

            if "icp_profiles" not in base_personas:
                return {"icp_profiles": []}

            # Enhance with psychographics and behavioral analysis
            enhanced_personas = []

            for persona in base_personas["icp_profiles"]:
                # Analyze psychographics
                psychographics = await self.psychographic_analyzer.analyze(
                    business_data, []
                )

                # Analyze behaviors
                behaviors = await self.behavioral_analyzer.analyze(business_data, [])

                # Calculate fit scores
                fit_scores = await self._calculate_fit_scores(
                    persona, business_analysis
                )

                # Assess market sophistication
                market_sophistication = await self._assess_market_sophistication(
                    persona, business_data
                )

                enhanced_persona = ICPProfile(
                    id=str(uuid.uuid4()),
                    name=persona.get("name", ""),
                    type=ICCPType.PRIMARY,
                    demographics=Demographics(
                        age_range=persona.get("demographics", {}).get(
                            "age_range", (25, 65)
                        ),
                        income_range=persona.get("demographics", {}).get(
                            "income_range", (50000, 200000)
                        ),
                        education_level=persona.get("demographics", {}).get(
                            "education_level", "Bachelor"
                        ),
                        location=persona.get("demographics", {}).get(
                            "location", "United States"
                        ),
                        company_size=persona.get("demographics", {}).get(
                            "company_size", "Medium"
                        ),
                        industry=business_data.get("industry", ""),
                        job_title=persona.get("demographics", {}).get(
                            "job_title", "Manager"
                        ),
                    ),
                    psychographics=psychographics,
                    behaviors=behaviors,
                    pain_points=persona.get("pain_points", []),
                    goals=persona.get("goals", []),
                    challenges=persona.get("challenges", []),
                    communication_preferences={
                        "tone": persona.get("communication", {}).get(
                            "tone", "professional"
                        ),
                        "channels": persona.get("communication", {}).get(
                            "channels", ["email"]
                        ),
                        "frequency": persona.get("communication", {}).get(
                            "frequency", "weekly"
                        ),
                    },
                    fit_score=np.mean(fit_scores) if fit_scores else 0.5,
                    market_sophistication=market_sophistication,
                    estimated_market_size=persona.get("estimated_market_size", 0),
                    conversion_likelihood=persona.get("conversion_likelihood", 0.5),
                    generated_at=datetime.utcnow(),
                    confidence_score=persona.get("confidence", 0.7),
                )

                enhanced_personas.append(enhanced_persona)

            # Rank and select top profiles
            ranked_profiles = await self._rank_profiles(enhanced_personas)

            return {
                "icp_profiles": ranked_profiles[:5],  # Top 5 profiles
                "primary_recommendation": (
                    ranked_profiles[0] if ranked_profiles else None
                ),
                "generation_metadata": {
                    "total_generated": len(enhanced_personas),
                    "business_context_score": business_analysis.get(
                        "confidence_score", 0.5
                    ),
                    "processing_time": datetime.utcnow().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"ICP generation failed: {e}")
            return {"icp_profiles": []}

    async def _analyze_business_context(self, business_data: Dict) -> Dict:
        """Analyze business context for ICP generation."""
        return {
            "industry": business_data.get("industry", ""),
            "business_model": business_data.get("business_model", ""),
            "price_point": business_data.get("price_point", ""),
            "target_audience": business_data.get("target_audience", ""),
            "company_stage": business_data.get("company_stage", ""),
            "confidence_score": 0.5,  # Default confidence
        }

    async def _calculate_fit_scores(
        self, persona: Dict, business_analysis: Dict
    ) -> List[float]:
        """Calculate fit scores for persona."""
        scores = []

        # Industry alignment score
        industry_match = persona.get("industry_match", 0.5)
        scores.append(industry_match)

        # Business model alignment score
        model_match = persona.get("model_match", 0.5)
        scores.append(model_match)

        # Size alignment score
        size_match = persona.get("size_match", 0.5)
        scores.append(size_match)

        # Value alignment score
        value_match = persona.get("value_match", 0.5)
        scores.append(value_match)

        return scores

    async def _assess_market_sophistication(
        self, persona: Dict, business_data: Dict
    ) -> str:
        """Assess market sophistication level."""
        # Business complexity
        business_complexity = business_data.get("complexity_score", 0.5)

        # Target sophistication
        target_sophistication = persona.get("target_sophistication", 0.5)

        # Product complexity
        product_complexity = persona.get("product_complexity", 0.5)

        avg_sophistication = (
            business_complexity + target_sophistication + product_complexity
        ) / 3

        if avg_sophistication >= 0.8:
            return "enterprise"
        elif avg_sophistication >= 0.6:
            return "business"
        elif avg_sophistication >= 0.4:
            return "professional"
        else:
            return "consumer"

    async def _rank_profiles(self, profiles: List[ICPProfile]) -> List[ICPProfile]:
        """Rank ICP profiles by fit score and other criteria."""
        # Sort by fit score (primary), then by confidence
        return sorted(
            profiles, key=lambda x: (x.fit_score, x.confidence_score), reverse=True
        )


# Pydantic models for API responses
class ICPProfileResponse(BaseModel):
    """Response model for ICP profile."""

    id: str
    name: str
    type: str
    demographics: Dict
    psychographics: Dict
    behaviors: Dict
    pain_points: List[str]
    goals: List[str]
    challenges: List[str]
    communication_preferences: Dict
    fit_score: float
    market_sophistication: str
    estimated_market_size: Optional[float] = None
    conversion_likelihood: float
    confidence_score: float


class ICPGenerationResponse(BaseModel):
    """Response model for ICP generation."""

    icp_profiles: List[ICPProfileResponse]
    primary_recommendation: Optional[ICPProfileResponse] = None
    total_generated: int
    generation_metadata: Dict


# Error classes
class ICPGenerationError(Exception):
    """Base ICP generation error."""

    pass


class AnalysisError(ICPGenerationError):
    """Analysis error during ICP generation."""

    pass
