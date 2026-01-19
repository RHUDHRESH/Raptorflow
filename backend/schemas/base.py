#!/usr/bin/env python3
"""
Node schemas for type-safe communication
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, UTC

class NodeInput(BaseModel):
    """Standard input for all nodes"""
    task: str = Field(..., description="Primary task or request")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context data")
    user_id: str = Field(..., description="User ID")
    workspace_id: str = Field(..., description="Workspace ID")
    session_id: Optional[str] = Field(None, description="Session ID for persistence")

class NodeOutput(BaseModel):
    """Standard output from all nodes"""
    status: str = Field(..., description="Execution status: success/error")
    data: Dict[str, Any] = Field(default_factory=dict, description="Result data")
    next_step: Optional[str] = Field(None, description="Suggested next node")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")

class FlowState(BaseModel):
    """Persistent flow state"""
    flow_id: str
    status: str
    current_step: int
    total_steps: int
    context: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class MoveSequence(BaseModel):
    """Definition of a move sequence"""
    move_id: str
    name: str
    description: str
    node_sequence: List[str]
    estimated_duration_hours: float
    triggers: List[str]  # time, event, manual

# --- Business Context Overhaul Models ---

class CompanyProfile(BaseModel):
    """Core company identity and positioning analysis."""
    name: str = Field(default="Unknown")
    mission: str = Field(default="")
    vision: str = Field(default="")
    market_position: str = Field(default="")
    industry: str = Field(default="Unknown")
    stage: str = Field(default="Unknown")
    description: str = Field(default="")
    team_size: str = Field(default="Unknown")
    revenue: str = Field(default="Unknown")

class MarketAnalysis(BaseModel):
    """Detailed market size, trends, and opportunity assessment."""
    overview: str = Field(default="Market analysis not available")
    size: str = Field(default="Unknown")
    trends: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)

class CompetitiveLandscape(BaseModel):
    """Key competitors and differentiation points."""
    overview: str = Field(default="Competitive analysis not available")
    competitors: List[str] = Field(default_factory=list)
    differentiation: List[str] = Field(default_factory=list)
    advantages: List[str] = Field(default_factory=list)

class CustomerSegments(BaseModel):
    """Primary and secondary customer profiles."""
    primary: str = Field(default="Unknown")
    secondary: List[str] = Field(default_factory=list)
    demographics: Dict[str, Any] = Field(default_factory=dict)
    psychographics: Dict[str, Any] = Field(default_factory=dict)

class ValueProposition(BaseModel):
    """Core value proposition and unique selling points."""
    core: str = Field(default="")
    unique_points: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)

class BusinessModel(BaseModel):
    """How the company makes money."""
    type: str = Field(default="Unknown")
    revenue_streams: List[str] = Field(default_factory=list)
    cost_structures: List[str] = Field(default_factory=list)
    profitability_mechanisms: List[str] = Field(default_factory=list)

class GrowthStrategy(BaseModel):
    """Key growth drivers and strategies."""
    overview: str = Field(default="Growth strategy not available")
    drivers: List[str] = Field(default_factory=list)
    initiatives: List[str] = Field(default_factory=list)

class RiskFactors(BaseModel):
    """Potential risks and challenges."""
    overview: str = Field(default="Risk analysis not available")
    risks: List[str] = Field(default_factory=list)
    mitigations: List[str] = Field(default_factory=list)

class SWOTAnalysis(BaseModel):
    """Strengths, Weaknesses, Opportunities, Threats."""
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)

class PESTELAnalysis(BaseModel):
    """Political, Economic, Social, Technological, Environmental, Legal factors."""
    political: List[str] = Field(default_factory=list)
    economic: List[str] = Field(default_factory=list)
    social: List[str] = Field(default_factory=list)
    technological: List[str] = Field(default_factory=list)
    environmental: List[str] = Field(default_factory=list)
    legal: List[str] = Field(default_factory=list)

class ValueChainAnalysis(BaseModel):
    """Primary and support activities breakdown."""
    primary_activities: Dict[str, List[str]] = Field(default_factory=dict)
    support_activities: Dict[str, List[str]] = Field(default_factory=dict)

class BrandArchetypes(BaseModel):
    """Jungian archetype classification."""
    primary: str = Field(default="Unknown")
    secondary: Optional[str] = None
    traits: List[str] = Field(default_factory=list)

class CompetitorMatrix(BaseModel):
    """Feature-by-feature comparison matrix."""
    competitors: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    comparison: Dict[str, Dict[str, str]] = Field(default_factory=dict)

class PsychographicInsights(BaseModel):
    """Deep psychological drivers and motivations."""
    drivers: List[str] = Field(default_factory=list)
    motivations: List[str] = Field(default_factory=list)
    behavioral_patterns: List[str] = Field(default_factory=list)

class PainPointAnalysis(BaseModel):
    """Pain point severity scoring."""
    pain_point: str
    severity: int = Field(..., ge=1, le=10)
    description: str = ""

class BuyingTriggers(BaseModel):
    """Events or conditions that trigger purchase decisions."""
    internal_triggers: List[str] = Field(default_factory=list)
    external_triggers: List[str] = Field(default_factory=list)

class ObjectionHandlers(BaseModel):
    """Responses to common customer objections."""
    objections: Dict[str, str] = Field(default_factory=dict)

class MessagingAngles(BaseModel):
    """Recommended messaging approaches."""
    angles: List[str] = Field(default_factory=list)

class ChannelPreferences(BaseModel):
    """Most effective channels to reach segments."""
    channels: List[str] = Field(default_factory=list)
    rationale: Dict[str, str] = Field(default_factory=dict)

class RICPDemographics(BaseModel):
    """Detailed demographics for an RICP."""
    age_range: str = Field(default="Unknown", description="e.g., 32-45 years old")
    income: str = Field(default="Unknown", description="e.g., $150,000 - $400,000")
    location: str = Field(default="Unknown", description="e.g., Urban tech hubs")
    role: str = Field(default="Unknown", description="e.g., Founder/CEO")
    stage: str = Field(default="Unknown", description="e.g., Seed to Series A")

class RICPPsychographics(BaseModel):
    """Deep psychographics for an RICP."""
    beliefs: str = Field(default="", description="Core mindset/beliefs")
    identity: str = Field(default="", description="How they see themselves")
    becoming: str = Field(default="", description="Who they want to become")
    fears: str = Field(default="", description="Primary fears or anxieties")
    values: List[str] = Field(default_factory=list, description="Core values")
    hangouts: List[str] = Field(default_factory=list, description="Digital/physical hangouts")
    content_consumed: List[str] = Field(default_factory=list, description="Podcasts, newsletters, etc.")
    who_they_follow: List[str] = Field(default_factory=list, description="Influencers, leaders")
    language: List[str] = Field(default_factory=list, description="Specific terminology/slang")
    timing: List[str] = Field(default_factory=list, description="When they are most reachable")
    triggers: List[str] = Field(default_factory=list, description="Purchase or action triggers")

class RICP(BaseModel):
    """Rich Ideal Customer Profile - The 'Cohort' entity."""
    id: str = Field(default_factory=lambda: "cohort_" + datetime.now(UTC).strftime("%Y%m%d%H%M%S"))
    name: str = Field(..., description="Cohort name (e.g., 'Ambitious SaaS Founder')")
    persona_name: Optional[str] = Field(None, description="Human persona name (e.g., 'Sarah')")
    avatar: str = Field(default="👤", description="Emoji avatar")
    demographics: RICPDemographics = Field(default_factory=RICPDemographics)
    psychographics: RICPPsychographics = Field(default_factory=RICPPsychographics)
    market_sophistication: int = Field(default=3, ge=1, le=5)
    confidence: int = Field(default=0, ge=0, le=100)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class EnhancedICP(BaseModel):
    """DEPRECATED: Use RICP/Cohort model. Maintained for legacy compatibility."""
    archetype_name: str = Field(default="General Archetype", description="AI-generated descriptive name for this persona archetype")
    original_data: Dict[str, Any] = Field(default_factory=dict)
    psychographics: PsychographicInsights = Field(default_factory=PsychographicInsights)
    pain_points: List[PainPointAnalysis] = Field(default_factory=list)
    buying_triggers: BuyingTriggers = Field(default_factory=BuyingTriggers)
    objection_handlers: ObjectionHandlers = Field(default_factory=ObjectionHandlers)
    messaging_angles: MessagingAngles = Field(default_factory=MessagingAngles)
    channel_preferences: ChannelPreferences = Field(default_factory=ChannelPreferences)
    ai_enhanced: bool = True
    enhanced_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class BrandVoice(BaseModel):
    """Tone, personality, and communication style."""
    tone: str = "Professional"
    personality: str = "Helpful and knowledgeable"
    guidelines: List[str] = Field(default_factory=list)

class CoreMessagePillars(BaseModel):
    """Foundational message pillars."""
    pillars: List[str] = Field(default_factory=list)

class MessagingFramework(BaseModel):
    """Structured messaging approach."""
    structure: str = "Problem-Solution-Benefit"
    elements: List[str] = Field(default_factory=list)

class ChannelMessaging(BaseModel):
    """Tailored messages per channel."""
    channel_specific: Dict[str, str] = Field(default_factory=dict)

class StoryBrand(BaseModel):
    """StoryBrand framework elements."""
    character: str = Field(default="", description="The hero of the story")
    problem_external: str = Field(default="", description="The physical challenge")
    problem_internal: str = Field(default="", description="How the hero feels")
    problem_philosophical: str = Field(default="", description="Why it's wrong")
    guide: str = Field(default="", description="The brand as the guide")
    plan: List[str] = Field(default_factory=list, description="3-step plan")
    call_to_action: str = Field(default="Start Now")
    avoid_failure: List[str] = Field(default_factory=list)
    success: List[str] = Field(default_factory=list)

class SocialProof(BaseModel):
    """Recommended social proof elements."""
    recommendations: List[str] = Field(default_factory=list)

class CallToAction(BaseModel):
    """Primary and secondary CTAs."""
    primary: str = "Learn More"
    secondary: str = "Contact Us"

class MessagingStrategy(BaseModel):
    """Comprehensive messaging strategy."""
    one_liner: str = Field(default="", description="High-impact mission-driven one-liner")
    positioning_statement: Optional[Dict[str, str]] = Field(default=None, description="Structured positioning (Target, Situation, Category, etc.)")
    brand_voice: BrandVoice = Field(default_factory=BrandVoice)
    core_messages: CoreMessagePillars = Field(default_factory=CoreMessagePillars)
    framework: MessagingFramework = Field(default_factory=MessagingFramework)
    story_brand: StoryBrand = Field(default_factory=StoryBrand)
    channel_messaging: ChannelMessaging = Field(default_factory=ChannelMessaging)
    objection_responses: ObjectionHandlers = Field(default_factory=ObjectionHandlers)
    social_proof: SocialProof = Field(default_factory=SocialProof)
    ctas: CallToAction = Field(default_factory=CallToAction)
    target_icps: List[str] = Field(default_factory=list)
    confidence: int = Field(default=0, ge=0, le=100)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source: str = "none"

class BusinessContextState(BaseModel):
    """LangGraph state for business context generation."""
    company_profile: Optional[CompanyProfile] = None
    market_analysis: Optional[MarketAnalysis] = None
    competitive_landscape: Optional[CompetitiveLandscape] = None
    customer_segments: Optional[CustomerSegments] = None
    value_proposition: Optional[ValueProposition] = None
    business_model: Optional[BusinessModel] = None
    growth_strategy: Optional[GrowthStrategy] = None
    risk_factors: Optional[RiskFactors] = None
    swot_analysis: Optional[SWOTAnalysis] = None
    pestel_analysis: Optional[PESTELAnalysis] = None
    value_chain_analysis: Optional[ValueChainAnalysis] = None
    brand_archetypes: Optional[BrandArchetypes] = None
    competitor_matrix: Optional[CompetitorMatrix] = None
    personas: Optional[List[Dict[str, Any]]] = None
    ricps: List[RICP] = Field(default_factory=list, description="Unified Cohort/ICP/Persona entities")
    icp_enhancements: Dict[str, EnhancedICP] = Field(default_factory=dict)
    messaging_strategy: Optional[MessagingStrategy] = None
    metadata: Dict[str, Any] = Field(default_factory=lambda: {
        "generated_at": datetime.now(UTC).isoformat(),
        "source": "none",
        "version": "1.0.0"
    })

# --- Expert Council Models ---

class CouncilAgent(BaseModel):
    """Definition of an agent within the Expert Council."""
    id: str
    name: str
    role: str
    avatar: str
    description: str
    specialization: str
    personality: str

class CouncilContribution(BaseModel):
    """A single contribution or message from an agent in the council."""
    agent_id: str
    agent_name: str
    content: str
    type: str = "suggestion" # suggestion, critique, refinement, decision
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

class CouncilDiscussion(BaseModel):
    """The full discussion history of a council session."""
    session_id: str
    mission: str
    contributions: List[CouncilContribution] = Field(default_factory=list)
    consensus_reached: bool = False
    final_output: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

class CouncilState(BaseModel):
    """LangGraph state for Expert Council collaboration."""
    mission: str
    workspace_context: Dict[str, Any]
    current_agent_id: Optional[str] = None
    discussion: CouncilDiscussion
    iteration_count: int = 0
    max_iterations: int = 5
    metadata: Dict[str, Any] = Field(default_factory=dict)

# --- Infinite Skill System Models ---

class SkillDefinition(BaseModel):
    """Definition of a dynamic skill."""
    name: str
    category: str
    description: str
    tools_required: List[str] = Field(default_factory=list)
    level: str = "intermediate"

class AgentSkillSet(BaseModel):
    """Dynamically loaded skill set for an agent."""
    agent_id: str
    active_skills: List[SkillDefinition] = Field(default_factory=list)
    available_tools: List[str] = Field(default_factory=list)
