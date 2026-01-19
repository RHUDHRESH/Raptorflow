"""
ICPArchitect - Creates and manages Ideal Customer Profiles using cognitive psychology models.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..base import BaseAgent
from backend.agents.config import ModelTier
from ..exceptions import ValidationError
from ..state import AgentState, add_message, update_state

logger = logging.getLogger(__name__)


class ICPType(Enum):
    """Types of ICPs that can be created."""

    B2B_ENTERPRISE = "b2b_enterprise"
    B2B_SMB = "b2b_smb"
    B2C_CONSUMER = "b2c_consumer"
    B2C_PROFESSIONAL = "b2c_professional"
    NONPROFIT = "nonprofit"
    GOVERNMENT = "government"


class PsychographicProfile(Enum):
    """Psychographic profiles for ICPs."""

    ANALYTICAL = "analytical"
    DRIVER = "driver"
    AMIABLE = "amiable"
    EXPRESSIVE = "expressive"
    INNOVATOR = "innovator"
    TRADITIONALIST = "traditionalist"


@dataclass
class ICPDemographics:
    """Demographic information for ICP."""

    age_range: Tuple[int, int]
    income_range: Tuple[float, float]
    education_level: str
    geographic_location: str
    company_size: Optional[str] = None
    industry: Optional[str] = None
    job_title: Optional[str] = None


@dataclass
class ICPPsychographics:
    """Psychographic information for ICP."""

    personality_type: PsychographicProfile
    values: List[str]
    motivations: List[str]
    fears: List[str]
    communication_style: str
    decision_factors: List[str]


@dataclass
class ICPBehavior:
    """Behavioral patterns for ICP."""

    information_sources: List[str]
    purchase_triggers: List[str]
    buying_process: str
    pain_points: List[str]
    success_metrics: List[str]
    preferred_channels: List[str]


@dataclass
class IdealCustomerProfile:
    """Complete Ideal Customer Profile."""

    name: str
    tagline: str
    icp_type: ICPType
    is_primary: bool
    demographics: ICPDemographics
    psychographics: ICPPsychographics
    behavior: ICPBehavior
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class ICPGenerationResult:
    """Result of ICP generation process."""

    generated_icps: List[IdealCustomerProfile]
    primary_icp: Optional[IdealCustomerProfile]
    synthesis_summary: str
    confidence_score: float
    recommendations: List[str]


class ICPArchitect(BaseAgent):
    """Specialist agent for creating Ideal Customer Profiles."""

    def __init__(self):
        super().__init__(
            name="ICPArchitect",
            description="Creates and manages Ideal Customer Profiles using cognitive psychology models",
            model_tier=ModelTier.FLASH,
            tools=["web_search", "database", "content_gen"],
        )

        # Cognitive psychology models
        self.personality_models = {
            PsychographicProfile.ANALYTICAL: {
                "traits": ["logical", "data-driven", "cautious", "thorough"],
                "communication": "detailed, factual, evidence-based",
                "decision_factors": ["ROI", "data", "proof", "specifications"],
            },
            PsychographicProfile.DRIVER: {
                "traits": ["results-oriented", "decisive", "competitive", "efficient"],
                "communication": "direct, concise, action-focused",
                "decision_factors": ["results", "speed", "control", "winning"],
            },
            PsychographicProfile.AMIABLE: {
                "traits": [
                    "relationship-focused",
                    "supportive",
                    "collaborative",
                    "patient",
                ],
                "communication": "warm, personal, relationship-building",
                "decision_factors": ["relationships", "trust", "harmony", "support"],
            },
            PsychographicProfile.EXPRESSIVE: {
                "traits": ["enthusiastic", "creative", "persuasive", "spontaneous"],
                "communication": "engaging, visionary, story-driven",
                "decision_factors": [
                    "vision",
                    "innovation",
                    "recognition",
                    "excitement",
                ],
            },
        }

        # Industry-specific patterns
        self.industry_patterns = {
            "Technology": {
                "common_roles": [
                    "CTO",
                    "Engineering Manager",
                    "Product Manager",
                    "DevOps Lead",
                ],
                "pain_points": [
                    "scalability",
                    "security",
                    "integration",
                    "talent shortage",
                ],
                "values": ["innovation", "efficiency", "scalability", "reliability"],
            },
            "Healthcare": {
                "common_roles": [
                    "Hospital Administrator",
                    "Medical Director",
                    "IT Manager",
                    "Compliance Officer",
                ],
                "pain_points": [
                    "regulatory compliance",
                    "patient outcomes",
                    "cost control",
                    "data security",
                ],
                "values": ["patient care", "compliance", "efficiency", "innovation"],
            },
            "Finance": {
                "common_roles": [
                    "CFO",
                    "Finance Manager",
                    "Risk Officer",
                    "Compliance Manager",
                ],
                "pain_points": [
                    "regulatory compliance",
                    "risk management",
                    "digital transformation",
                    "fraud",
                ],
                "values": ["security", "compliance", "efficiency", "accuracy"],
            },
            "Retail": {
                "common_roles": [
                    "Store Manager",
                    "Marketing Director",
                    "E-commerce Manager",
                    "Supply Chain Manager",
                ],
                "pain_points": [
                    "inventory management",
                    "customer experience",
                    "competition",
                    "omnichannel",
                ],
                "values": [
                    "customer satisfaction",
                    "efficiency",
                    "growth",
                    "innovation",
                ],
            },
        }

    def get_system_prompt(self) -> str:
        """Get the system prompt for the ICPArchitect."""
        return """
You are the ICPArchitect, a specialist agent for Raptorflow marketing automation platform.

Your role is to create detailed Ideal Customer Profiles (ICPs) using cognitive psychology models and industry research.

Key responsibilities:
1. Analyze business context and industry to identify target customer segments
2. Apply cognitive psychology models to understand customer behavior
3. Create comprehensive ICPs with demographics, psychographics, and behavioral patterns
4. Use evidence-based approaches to validate ICP assumptions
5. Generate actionable insights for marketing strategy

For each ICP, include:
- Clear identification (name, tagline, type)
- Demographic profile (age, income, education, location, etc.)
- Psychographic profile (personality, values, motivations, fears)
- Behavioral patterns (information sources, buying process, pain points)
- Actionable marketing recommendations

Always base your ICPs on real market research and psychological principles. Be specific and practical.
"""

    async def execute(self, state: AgentState) -> AgentState:
        """Execute ICP generation and management."""
        try:
            # Extract user request
            user_request = self._extract_user_input(state)
            if not user_request:
                return self._set_error(state, "No request provided for ICP generation")

            # Add system message about ICP generation
            state = self._add_system_message(
                state, f"Generating ICPs for request: {user_request[:100]}..."
            )

            # Analyze business context
            business_context = await self._analyze_business_context(state, user_request)

            # Generate ICPs
            icp_result = await self._generate_icps(business_context, state)

            # Validate ICPs
            validated_icps = await self._validate_icps(icp_result.generated_icps, state)

            # Create synthesis summary
            synthesis = await self._create_icp_synthesis(
                validated_icps, business_context
            )

            # Generate recommendations
            recommendations = await self._generate_icp_recommendations(
                validated_icps, business_context
            )

            # Update result
            icp_result.generated_icps = validated_icps
            icp_result.synthesis_summary = synthesis
            icp_result.recommendations = recommendations

            # Update state with results
            state = self._update_state(
                state,
                icp_generation_result=icp_result,
                generated_icps=validated_icps,
                icp_count=len(validated_icps),
                primary_icp=icp_result.primary_icp,
            )

            # Add summary message
            summary = self._create_icp_summary(icp_result)
            state = self._add_assistant_message(state, summary)

            # Set output
            return self._set_output(
                state,
                {
                    "icp_generation_result": icp_result,
                    "generated_icps": validated_icps,
                    "icp_count": len(validated_icps),
                    "synthesis_summary": synthesis,
                    "recommendations": recommendations,
                },
            )

        except Exception as e:
            logger.error(f"ICP generation failed: {e}")
            return self._set_error(state, f"ICP generation failed: {str(e)}")

    async def _analyze_business_context(
        self, state: AgentState, request: str
    ) -> Dict[str, Any]:
        """Analyze business context from state and request."""
        context = {
            "user_request": request,
            "foundation_summary": state.get("foundation_summary", ""),
            "brand_voice": state.get("brand_voice", ""),
            "industry": "Unknown",
            "company_size": "Unknown",
            "target_market": "Unknown",
            "business_model": "Unknown",
        }

        # Extract industry from foundation summary
        foundation = context["foundation_summary"].lower()
        for industry in self.industry_patterns.keys():
            if industry.lower() in foundation:
                context["industry"] = industry
                break

        # Extract company size clues
        size_indicators = {
            "small": ["startup", "small business", "smb", "small"],
            "medium": ["medium", "mid-size", "growing"],
            "large": ["enterprise", "large", "corporation", "fortune"],
        }

        for size, indicators in size_indicators.items():
            if any(indicator in foundation for indicator in indicators):
                context["company_size"] = size
                break

        # Determine ICP type based on business model
        if "b2b" in foundation or "business" in foundation:
            if context["company_size"] == "large":
                context["icp_type"] = ICPType.B2B_ENTERPRISE
            else:
                context["icp_type"] = ICPType.B2B_SMB
        elif "consumer" in foundation or "b2c" in foundation:
            if "professional" in foundation:
                context["icp_type"] = ICPType.B2C_PROFESSIONAL
            else:
                context["icp_type"] = ICPType.B2C_CONSUMER
        elif "nonprofit" in foundation:
            context["icp_type"] = ICPType.NONPROFIT
        elif "government" in foundation:
            context["icp_type"] = ICPType.GOVERNMENT
        else:
            context["icp_type"] = ICPType.B2B_SMB  # Default

        return context

    async def _generate_icps(
        self, business_context: Dict[str, Any], state: AgentState
    ) -> ICPGenerationResult:
        """Generate ICPs based on business context."""
        icps = []

        # Determine number of ICPs to generate (max 3)
        num_icps = min(3, self._determine_icp_count(business_context, state))

        # Generate different personality types for diversity
        personality_types = list(PsychographicProfile)[:num_icps]

        for i in range(num_icps):
            personality = personality_types[i]

            # Create items - either via Swarm Skill or internal logic
            # [SWARM INTEGRATION]
            persona_skill = self.skills_registry.get_skill("persona_builder")
            icp = None
            
            if persona_skill:
                try:
                    logger.info("Swarm: Building Persona...")
                    # We pass the personality context to guide the swarms generation
                    model = self.personality_models[personality] 
                    persona_res = await persona_skill.execute({
                        "agent": self,
                        "base_profile": business_context,
                        "personality_trait": personality.value
                    })
                    
                    if "persona" in persona_res:
                        p_data = persona_res["persona"]
                        # Map skill result to IdealCustomerProfile
                        
                        # Use demographic helper to get defaults, then override with skill data
                        demos = self._create_demographics(business_context, personality, i)
                        if "demographics" in p_data:
                            d_in = p_data["demographics"]
                            if "age_range" in d_in: demos.age_range = d_in["age_range"] # simplified mapping
                            if "title" in d_in: demos.job_title = d_in["title"]

                        # Use psychographic helper to get defaults, then override
                        psychos = self._create_psychographics(personality, business_context)
                        if "motivations" in p_data: psychos.motivations = p_data["motivations"]
                        if "frustrations" in p_data: psychos.fears = p_data["frustrations"]

                        # Create behavior profile
                        behaviors = self._create_behavior_profile(personality, business_context, demos)
                        if "goals" in p_data: behaviors.success_metrics = p_data["goals"]

                        icp = IdealCustomerProfile(
                            name=p_data.get("name", self._generate_icp_name(business_context, personality, i)),
                            tagline=p_data.get("role_description", self._generate_icp_tagline(business_context, personality, i)),
                            icp_type=business_context["icp_type"],
                            is_primary=(i == 0),
                            demographics=demos,
                            psychographics=psychos,
                            behavior=behaviors,
                            created_at=datetime.now(),
                            metadata={
                                "generation_method": "swarm_persona_builder",
                                "personality_type": personality.value,
                                "swarm_enhanced": True
                            }
                        )
                except Exception as e:
                    logger.warning(f"PersonaBuilderSkill failed: {e}")

            # Fallback to internal logic
            if not icp:
                demographics = self._create_demographics(business_context, personality, i)
                psychographics = self._create_psychographics(personality, business_context)
                behavior = self._create_behavior_profile(personality, business_context, demographics)

                icp = IdealCustomerProfile(
                    name=self._generate_icp_name(business_context, personality, i),
                    tagline=self._generate_icp_tagline(business_context, personality, i),
                    icp_type=business_context["icp_type"],
                    is_primary=(i == 0),
                    demographics=demographics,
                    psychographics=psychographics,
                    behavior=behavior,
                    created_at=datetime.now(),
                    metadata={
                        "generation_method": "cognitive_psychology_model",
                        "personality_type": personality.value,
                        "business_context": business_context,
                    }
                )

            icps.append(icp)

        # Set primary ICP
        primary_icp = icps[0] if icps else None

        # Calculate confidence score
        confidence_score = self._calculate_icp_confidence(icps, business_context)

        return ICPGenerationResult(
            generated_icps=icps,
            primary_icp=primary_icp,
            synthesis_summary="",
            confidence_score=confidence_score,
            recommendations=[],
        )

    def _determine_icp_count(
        self, business_context: Dict[str, Any], state: AgentState
    ) -> int:
        """Determine how many ICPs to generate."""
        # Check existing ICPs
        existing_icps = state.get("active_icps", [])

        if existing_icps:
            return max(1, 3 - len(existing_icps))

        # Default to 2-3 ICPs for comprehensive coverage
        return 2

    def _create_demographics(
        self,
        business_context: Dict[str, Any],
        personality: PsychographicProfile,
        index: int,
    ) -> ICPDemographics:
        """Create demographic profile for ICP."""
        industry = business_context["industry"]
        icp_type = business_context["icp_type"]

        # Set age range based on ICP type and personality
        if icp_type in [ICPType.B2B_ENTERPRISE, ICPType.B2B_SMB]:
            age_range = (35, 55)
        elif icp_type == ICPType.B2C_CONSUMER:
            age_range = (25, 45)
        elif icp_type == ICPType.B2C_PROFESSIONAL:
            age_range = (30, 50)
        else:
            age_range = (40, 60)

        # Set income range
        if icp_type in [ICPType.B2B_ENTERPRISE]:
            income_range = (150000, 500000)
        elif icp_type == ICPType.B2B_SMB:
            income_range = (80000, 200000)
        elif icp_type == ICPType.B2C_CONSUMER:
            income_range = (50000, 150000)
        elif icp_type == ICPType.B2C_PROFESSIONAL:
            income_range = (100000, 300000)
        else:
            income_range = (60000, 120000)

        # Set education level
        if personality == PsychographicProfile.ANALYTICAL:
            education_level = "Graduate Degree"
        elif personality in [
            PsychographicProfile.DRIVER,
            PsychographicProfile.EXPRESSIVE,
        ]:
            education_level = "Bachelor's Degree"
        else:
            education_level = "Some College"

        # Set geographic location (US-based default)
        geographic_location = "United States"

        # Set company size and industry for B2B
        company_size = None
        job_title = None

        if icp_type in [ICPType.B2B_ENTERPRISE, ICPType.B2B_SMB]:
            company_size = business_context["company_size"]

            # Set job title based on personality and industry
            if industry in self.industry_patterns:
                roles = self.industry_patterns[industry]["common_roles"]
                if personality == PsychographicProfile.ANALYTICAL:
                    job_title = roles[1] if len(roles) > 1 else roles[0]
                elif personality == PsychographicProfile.DRIVER:
                    job_title = roles[0]
                else:
                    job_title = roles[2] if len(roles) > 2 else roles[0]

        return ICPDemographics(
            age_range=age_range,
            income_range=income_range,
            education_level=education_level,
            geographic_location=geographic_location,
            company_size=company_size,
            industry=industry,
            job_title=job_title,
        )

    def _create_psychographics(
        self, personality: PsychographicProfile, business_context: Dict[str, Any]
    ) -> ICPPsychographics:
        """Create psychographic profile for ICP."""
        model = self.personality_models[personality]

        # Set values based on personality and business context
        values = model["traits"].copy()

        # Add industry-specific values
        industry = business_context["industry"]
        if industry in self.industry_patterns:
            values.extend(self.industry_patterns[industry]["values"])

        # Set motivations
        if personality == PsychographicProfile.ANALYTICAL:
            motivations = [
                "making informed decisions",
                "optimizing processes",
                "achieving measurable results",
            ]
        elif personality == PsychographicProfile.DRIVER:
            motivations = ["achieving goals", "winning", "efficiency", "control"]
        elif personality == PsychographicProfile.AMIABLE:
            motivations = [
                "building relationships",
                "helping others",
                "team success",
                "harmony",
            ]
        else:  # EXPRESSIVE
            motivations = [
                "innovation",
                "creativity",
                "recognition",
                "making an impact",
            ]

        # Set fears
        if personality == PsychographicProfile.ANALYTICAL:
            fears = ["making wrong decisions", "missing data", "being unprepared"]
        elif personality == PsychographicProfile.DRIVER:
            fears = ["losing control", "failure", "being inefficient"]
        elif personality == PsychographicProfile.AMIABLE:
            fears = ["conflict", "rejection", "letting others down"]
        else:  # EXPRESSIVE
            fears = ["being ignored", "boredom", "lack of recognition"]

        return ICPPsychographics(
            personality_type=personality,
            values=values,
            motivations=motivations,
            fears=fears,
            communication_style=model["communication"],
            decision_factors=model["decision_factors"],
        )

    def _create_behavior_profile(
        self,
        personality: PsychographicProfile,
        business_context: Dict[str, Any],
        demographics: ICPDemographics,
    ) -> ICPBehavior:
        """Create behavioral profile for ICP."""
        # Set information sources based on personality
        if personality == PsychographicProfile.ANALYTICAL:
            information_sources = [
                "industry reports",
                "data analysis",
                "expert opinions",
                "case studies",
            ]
        elif personality == PsychographicProfile.DRIVER:
            information_sources = [
                "executive summaries",
                "ROI data",
                "peer recommendations",
                "quick demos",
            ]
        elif personality == PsychographicProfile.AMIABLE:
            information_sources = [
                "colleague recommendations",
                "customer testimonials",
                "reviews",
                "social proof",
            ]
        else:  # EXPRESSIVE
            information_sources = [
                "social media",
                "industry events",
                "thought leaders",
                "innovative content",
            ]

        # Set purchase triggers
        if business_context["icp_type"] in [ICPType.B2B_ENTERPRISE, ICPType.B2B_SMB]:
            purchase_triggers = [
                "business growth",
                "competitive pressure",
                "efficiency needs",
                "regulatory changes",
            ]
        else:
            purchase_triggers = [
                "life changes",
                "recommendations",
                "trends",
                "promotions",
            ]

        # Set buying process
        if personality == PsychographicProfile.ANALYTICAL:
            buying_process = "Research-heavy, multiple evaluations, committee approval"
        elif personality == PsychographicProfile.DRIVER:
            buying_process = "Quick decision, focus on results, minimal bureaucracy"
        elif personality == PsychographicProfile.AMIABLE:
            buying_process = (
                "Relationship-based, trusted recommendations, consensus building"
            )
        else:  # EXPRESSIVE
            buying_process = (
                "Vision-driven, inspired by innovation, emotional connection"
            )

        # Set pain points
        industry = business_context["industry"]
        if industry in self.industry_patterns:
            pain_points = self.industry_patterns[industry]["pain_points"]
        else:
            pain_points = ["efficiency", "cost control", "competition", "growth"]

        # Set success metrics
        if business_context["icp_type"] in [ICPType.B2B_ENTERPRISE, ICPType.B2B_SMB]:
            success_metrics = [
                "ROI",
                "efficiency gains",
                "cost savings",
                "revenue growth",
            ]
        else:
            success_metrics = [
                "satisfaction",
                "convenience",
                "status",
                "personal growth",
            ]

        # Set preferred channels
        if personality == PsychographicProfile.ANALYTICAL:
            preferred_channels = ["email", "whitepapers", "webinars", "case studies"]
        elif personality == PsychographicProfile.DRIVER:
            preferred_channels = [
                "direct sales",
                "executive briefings",
                "ROI calculators",
                "demos",
            ]
        elif personality == PsychographicProfile.AMIABLE:
            preferred_channels = [
                "referrals",
                "social proof",
                "community events",
                "personal outreach",
            ]
        else:  # EXPRESSIVE
            preferred_channels = [
                "social media",
                "events",
                "video content",
                "influencers",
            ]

        return ICPBehavior(
            information_sources=information_sources,
            purchase_triggers=purchase_triggers,
            buying_process=buying_process,
            pain_points=pain_points,
            success_metrics=success_metrics,
            preferred_channels=preferred_channels,
        )

    def _generate_icp_name(
        self,
        business_context: Dict[str, Any],
        personality: PsychographicProfile,
        index: int,
    ) -> str:
        """Generate a name for the ICP."""
        industry = business_context["industry"]
        personality_name = personality.value.replace("_", " ").title()

        if industry != "Unknown":
            return f"{industry} {personality_name}"
        else:
            return f"{personality_name} Customer"

    def _generate_icp_tagline(
        self,
        business_context: Dict[str, Any],
        personality: PsychographicProfile,
        index: int,
    ) -> str:
        """Generate a tagline for the ICP."""
        model = self.personality_models[personality]
        traits = model["traits"][:2]  # Use first two traits

        return f"{' and '.join(traits).title()} decision-makers focused on {model['decision_factors'][0].lower()}"

    def _calculate_icp_confidence(
        self, icps: List[IdealCustomerProfile], business_context: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for generated ICPs."""
        if not icps:
            return 0.0

        # Base confidence on business context clarity
        context_score = 0.0

        if business_context["industry"] != "Unknown":
            context_score += 0.3

        if business_context["company_size"] != "Unknown":
            context_score += 0.2

        if business_context["foundation_summary"]:
            context_score += 0.2

        # Diversity bonus for multiple ICPs
        diversity_score = min(0.3, len(icps) * 0.1)

        # Total confidence
        total_confidence = context_score + diversity_score

        return min(total_confidence, 1.0)

    async def _validate_icps(
        self, icps: List[IdealCustomerProfile], state: AgentState
    ) -> List[IdealCustomerProfile]:
        """Validate generated ICPs."""
        validated_icps = []

        for icp in icps:
            # Check for duplicates with existing ICPs
            existing_icps = state.get("active_icps", [])
            is_duplicate = False

            for existing in existing_icps:
                if icp.name.lower() == existing.get("name", "").lower():
                    is_duplicate = True
                    break

            if not is_duplicate:
                # Validate ICP completeness
                if self._validate_icp_completeness(icp):
                    validated_icps.append(icp)
                else:
                    logger.warning(f"ICP {icp.name} failed validation")

        return validated_icps

    def _validate_icp_completeness(self, icp: IdealCustomerProfile) -> bool:
        """Validate that ICP has all required components."""
        required_fields = [
            icp.name,
            icp.tagline,
            icp.demographics.age_range,
            icp.psychographics.personality_type,
            icp.behavior.pain_points,
        ]

        return all(field is not None for field in required_fields)

    async def _create_icp_synthesis(
        self, icps: List[IdealCustomerProfile], business_context: Dict[str, Any]
    ) -> str:
        """Create synthesis summary of generated ICPs."""
        if not icps:
            return "No ICPs were generated."

        synthesis = f"Generated {len(icps)} Ideal Customer Profile(s) for {business_context['industry']}:\n\n"

        for i, icp in enumerate(icps, 1):
            synthesis += f"**{i}. {icp.name}**\n"
            synthesis += f"Tagline: {icp.tagline}\n"
            synthesis += f"Type: {icp.psychographics.personality_type.value}\n"
            synthesis += f"Key Pain Points: {', '.join(icp.behavior.pain_points[:3])}\n"
            synthesis += f"Preferred Channels: {', '.join(icp.behavior.preferred_channels[:3])}\n\n"

        return synthesis

    async def _generate_icp_recommendations(
        self, icps: List[IdealCustomerProfile], business_context: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on ICPs."""
        recommendations = []

        if not icps:
            return ["Generate at least one ICP to proceed with marketing strategy"]

        # General recommendations
        recommendations.append("Use the primary ICP for initial marketing campaigns")

        if len(icps) > 1:
            recommendations.append("Create targeted content for each secondary ICP")

        # Channel recommendations
        all_channels = []
        for icp in icps:
            all_channels.extend(icp.behavior.preferred_channels)

        channel_counts = {}
        for channel in all_channels:
            channel_counts[channel] = channel_counts.get(channel, 0) + 1

        top_channels = sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[
            :3
        ]
        if top_channels:
            recommendations.append(
                f"Focus on these top channels: {', '.join([c[0] for c in top_channels])}"
            )

        # Content recommendations
        recommendations.append(
            "Create content that addresses the primary pain points identified"
        )

        # Personalization recommendations
        if len(icps) > 1:
            recommendations.append(
                "Implement personalization to cater to different personality types"
            )

        return recommendations

    def _create_icp_summary(self, result: ICPGenerationResult) -> str:
        """Create a summary of ICP generation results."""
        summary = f"🎯 **ICP Generation Summary**\n\n"
        summary += f"**Generated ICPs:** {len(result.generated_icps)}\n"
        summary += f"**Confidence Score:** {result.confidence_score:.1%}\n\n"

        if result.generated_icps:
            summary += "**Generated Profiles:**\n"
            for i, icp in enumerate(result.generated_icps, 1):
                summary += f"{i}. **{icp.name}** ({icp.tagline})\n"
                summary += f"   - Type: {icp.psychographics.personality_type.value}\n"
                summary += f"   - Primary: {'Yes' if icp.is_primary else 'No'}\n"
            summary += "\n"

        if result.synthesis_summary:
            summary += "**Synthesis:**\n"
            summary += result.synthesis_summary + "\n\n"

        if result.recommendations:
            summary += "**Recommendations:**\n"
            for recommendation in result.recommendations:
                summary += f"• {recommendation}\n"

        return summary
