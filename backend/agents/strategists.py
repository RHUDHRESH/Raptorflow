import logging
from typing import List, TypedDict, Optional
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

logger = logging.getLogger("raptorflow.strategists.icp")

class ICPDemographics(BaseModel):
    """SOTA structured representation of 'Who' the customer is."""
    target_role: str = Field(description="The job title or role (e.g., Early-stage founder).")
    company_size: str = Field(description="Size of the target organization.")
    industry_niche: str = Field(description="Specific sub-sector (e.g., B2B SaaS).")
    geographic_focus: List[str] = Field(description="Where they are located.")
    tech_stack_affinity: List[str] = Field(description="Tools they likely use.")

class ICPDemographicProfiler:
    """
    SOTA Demographic Analysis Node.
    Defines the 'Who' of the target audience with surgical precision using Gemini.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of market segmentation. "
                       "Based on the research evidence provided, define the "
                       "surgical DEMOGRAPHIC profile of the ideal customer."),
            ("user", "Research Evidence: {evidence}")
        ])
        self.chain = self.prompt | llm.with_structured_output(ICPDemographics)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Profiling target demographics...")
        
        profile = await self.chain.ainvoke({"evidence": str(evidence)})
        logger.info(f"Demographic profiling complete for: {profile.target_role}")
        
        return {"context_brief": {"icp_demographics": profile.model_dump()}}

class ICPPsychographics(BaseModel):
    """SOTA structured representation of 'Why' the customer buys."""
    core_motivations: List[str] = Field(description="Top 3 drivers (e.g., status, speed, security).")
    perceived_risks: List[str] = Field(description="Fear-based blockers (e.g., vendor lock-in).")
    values_alignment: List[str] = Field(description="What they care about (e.g., transparency).")
    buying_triggers: List[str] = Field(description="Events that spark a purchase.")

class ICPPsychographicProfiler:
    """
    SOTA Psychographic Analysis Node.
    Defines the 'Why' of the target audience with surgical precision using Gemini.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of consumer psychology. "
                       "Based on the research evidence provided, define the "
                       "surgical PSYCHOGRAPHIC profile of the ideal customer."),
            ("user", "Research Evidence: {evidence}")
        ])
        self.chain = self.prompt | llm.with_structured_output(ICPPsychographics)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Profiling target psychographics...")
        
        profile = await self.chain.ainvoke({"evidence": str(evidence)})
        logger.info(f"Psychographic profiling complete. Found {len(profile.core_motivations)} motivations.")
        
        return {"context_brief": {"icp_psychographics": profile.model_dump()}}

class PainPoint(BaseModel):
    """SOTA structured pain-point representation."""
    problem: str
    severity: float # 0 to 1
    quote_or_signal: str # Evidence

class PainPointAnalysis(BaseModel):
    burning_problems: List[PainPoint]

class PainPointMapper:
    """
    SOTA Pain-Point Identification Node.
    Extracts the highest leverage 'burning' problems from research evidence.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master strategist. "
                       "Extract exactly 5-10 specific, surgical pain points "
                       "from the research evidence that are 'burning' for the ICP."),
            ("user", "Evidence: {evidence}")
        ])
        self.chain = self.prompt | llm.with_structured_output(PainPointAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Mapping customer pain points...")
        
        analysis = await self.chain.ainvoke({"evidence": str(evidence)})
        logger.info(f"Pain-point mapping complete. Found {len(analysis.burning_problems)} problems.")
        
        return {"context_brief": {"pain_points": analysis.model_dump()}}

class UVP(BaseModel):
    """SOTA structured UVP representation."""
    title: str
    description: str
    why_it_wins: str # Strategic reasoning

class UVPAnalysis(BaseModel):
    winning_positions: List[UVP]

class UVPArchitect:
    """
    SOTA Strategic Positioning Node.
    Drafts distinct 'Winning Positions' (UVPs) based on pain points and research.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master positioning architect. "
                       "Draft exactly 3 distinct 'Winning Positions' (UVPs) "
                       "that surgically address the identified pain points."),
            ("user", "Pain Points: {pain_points}\nResearch: {evidence}")
        ])
        self.chain = self.prompt | llm.with_structured_output(UVPAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        pain_points = state.get("context_brief", {}).get("pain_points", {})
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Architecting UVPs...")
        
        analysis = await self.chain.ainvoke({"pain_points": str(pain_points), "evidence": str(evidence)})
        logger.info(f"UVP architecture complete. Drafted {len(analysis.winning_positions)} positions.")
        
        return {"context_brief": {"uvps": analysis.model_dump()}}

class AlignmentResult(BaseModel):
    """SOTA structured alignment evaluation."""
    uvp_title: str
    is_aligned: bool
    score: float # 0 to 1
    feedback: str # How to fix if not aligned

class BrandVoiceAnalysis(BaseModel):
    alignments: List[AlignmentResult]

class BrandVoiceAligner:
    """
    SOTA Brand Kit Compliance Node.
    Ensures UVPs and strategy align perfectly with the RaptorFlow core voice.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a surgical brand guardian. "
                       "Compare the proposed UVPs against the provided Brand Kit. "
                       "Every output must be 'Calm, Expensive, and Decisive'."),
            ("user", "Brand Kit: {brand_kit}\nUVPs: {uvps}")
        ])
        self.chain = self.prompt | llm.with_structured_output(BrandVoiceAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        brand_kit = state.get("context_brief", {}).get("brand_kit", "Default RaptorFlow Kit")
        uvps = state.get("context_brief", {}).get("uvps", {})
        logger.info("Aligning UVPs with Brand Voice...")
        
        analysis = await self.chain.ainvoke({"brand_kit": str(brand_kit), "uvps": str(uvps)})
        logger.info(f"Brand alignment complete for {len(analysis.alignments)} UVPs.")
        
        return {"context_brief": {"brand_alignment": analysis.model_dump()}}

class AntiPersona(BaseModel):
    """SOTA structured representation of who the brand is NOT for."""
    persona_name: str
    why_to_avoid: str # Strategic reasoning
    common_signals: List[str] # Red flags

class AntiPersonaAnalysis(BaseModel):
    anti_personas: List[AntiPersona]

class AntiPersonaProfiler:
    """
    SOTA Focus Refinement Node.
    Defines the 'Anti-Persona' to ensure the brand doesn't waste energy on the wrong audience.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of strategic focus. "
                       "Based on the research and ICP, define exactly 2 'Anti-Personas' "
                       "that the brand should surgically avoid."),
            ("user", "Research: {evidence}\nICP: {icp}")
        ])
        self.chain = self.prompt | llm.with_structured_output(AntiPersonaAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        icp = state.get("context_brief", {}).get("icp_demographics", {})
        logger.info("Profiling Anti-Personas...")
        
        analysis = await self.chain.ainvoke({"evidence": str(evidence), "icp": str(icp)})
        logger.info(f"Anti-persona profiling complete. Defined {len(analysis.anti_personas)} segments to avoid.")
        
        return {"context_brief": {"anti_personas": analysis.model_dump()}}

class CategoryProposal(BaseModel):
    """SOTA structured category representation."""
    category_name: str
    rationale: str
    market_potential: float # 0 to 1

class CategoryAnalysis(BaseModel):
    proposals: List[CategoryProposal]

class CategoryArchitect:
    """
    SOTA Category Design Node.
    Proposes surgical 'One-Word' or 'Two-Word' category names to ensure the brand owns a niche.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of category design. "
                       "Based on the UVPs, propose exactly 3 surgical category names "
                       "that allow this brand to own a new market space."),
            ("user", "UVPs: {uvps}\nResearch: {evidence}")
        ])
        self.chain = self.prompt | llm.with_structured_output(CategoryAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        uvps = state.get("context_brief", {}).get("uvps", {})
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Architecting market categories...")
        
        analysis = await self.chain.ainvoke({"uvps": str(uvps), "evidence": str(evidence)})
        logger.info(f"Category architecture complete. Proposed {len(analysis.proposals)} names.")
        
        return {"context_brief": {"categories": analysis.model_dump()}}

class Tagline(BaseModel):
    """SOTA structured tagline representation."""
    text: str = Field(description="The 10-word brand hook.")
    vibe: str = Field(description="The emotional signal.")

class TaglineAnalysis(BaseModel):
    taglines: List[Tagline]

class TaglineGenerator:
    """
    SOTA Brand Hook Node.
    Generates surgical 10-word taglines that define the brand in seconds.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master copywriter. "
                       "Generate exactly 5 surgical brand taglines (max 10 words each) "
                       "that perfectly capture the brand's 'Calm, Expensive, Decisive' vibe."),
            ("user", "UVPs: {uvps}")
        ])
        self.chain = self.prompt | llm.with_structured_output(TaglineAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        uvps = state.get("context_brief", {}).get("uvps", {})
        logger.info("Generating surgical taglines...")
        
        analysis = await self.chain.ainvoke({"uvps": str(uvps)})
        logger.info(f"Tagline generation complete. Created {len(analysis.taglines)} hooks.")
        
        return {"context_brief": {"taglines": analysis.model_dump()}}

class StrategyReplanner:
    """
    SOTA Strategic Pivot Node.
    Analyzes alignment scores and decides if the UVP architecture needs a retry or pivot.
    """
    def __init__(self, llm: any):
        self.llm = llm

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        alignments = state.get("context_brief", {}).get("brand_alignment", {}).get("alignments", [])
        avg_score = sum(a["score"] for a in alignments) / len(alignments) if alignments else 0
        
        logger.info(f"Evaluating strategy consistency... Average Score: {avg_score}")
        
        if avg_score < 0.7:
            logger.warning("Strategy score low. Triggering pivot logic...")
            # Generate pivot instructions using LLM
            res = await self.llm.ainvoke("The current UVPs are not aligned with our 'Calm, Expensive' vibe. Generate a single surgical instruction to fix the positioning.")
            return {"next_node": "pivot", "context_brief": {"pivot_instruction": res.content}}
        
        logger.info("Strategy alignment passed.")
        return {"next_node": "finalize"}

class MonthPlan(BaseModel):
    """SOTA structured monthly strategic theme."""
    month_number: int
    theme: str
    key_objective: str

class CampaignArc(BaseModel):
    """The 90-day strategic arc."""
    campaign_title: str
    monthly_plans: List[MonthPlan]

from backend.core.prompts import CampaignPrompts

# ...

class CampaignArcDesigner:
    """
    SOTA War-Planning Node.
    Maps out the high-level 90-day strategic arc using Gemini Ultra Reasoning.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", CampaignPrompts.PLANNER_SYSTEM),
            ("user", CampaignPrompts.ARC_GENERATION)
        ])
        self.chain = self.prompt | llm.with_structured_output(CampaignArc)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        uvps = state.get("context_brief", {}).get("uvps", {})
        evidence = state.get("business_context", []) # Pull from injected RAG context
        logger.info("Designing 90-day campaign arc...")
        
        arc = await self.chain.ainvoke({"uvps": str(uvps), "evidence": "\n".join(evidence)})
        logger.info(f"Campaign arc designed: {arc.campaign_title}")
        
        return {"context_brief": {"campaign_arc": arc.model_dump()}}

class ExecutionMove(BaseModel):
    """SOTA structured representation of a weekly execution packet."""
    week_number: int
    title: str
    action_items: List[str]
    desired_outcome: str

class MoveSequence(BaseModel):
    """The granular weekly breakdown of a campaign."""
    moves: List[ExecutionMove]

class MoveSequencer:
    """
    SOTA Weekly Execution Node.
    Breaks 90-day arcs into granular, weekly 'Moves' using Gemini Ultra Reasoning.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of high-velocity marketing execution. "
                       "Decompose the 90-day arc into exactly 12 weekly 'Moves' "
                       "(discrete execution packets) with clear action items."),
            ("user", "Campaign Arc: {arc}")
        ])
        self.chain = self.prompt | llm.with_structured_output(MoveSequence)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        arc = state.get("context_brief", {}).get("campaign_arc", {})
        logger.info("Sequencing weekly execution moves...")
        
        sequence = await self.chain.ainvoke({"arc": str(arc)})
        logger.info(f"Move sequencing complete. Generated {len(sequence.moves)} weekly packets.")
        
        return {"context_brief": {"move_sequence": sequence.model_dump()}}

class ChannelBudget(BaseModel):
    """SOTA structured representation of channel spend."""
    channel: str
    allocation_percentage: float
    reasoning: str

class BudgetAnalysis(BaseModel):
    """The total budget distribution for a campaign."""
    suggested_total: str
    distribution: List[ChannelBudget]

class BudgetAllocator:
    """
    SOTA Financial Planning Node.
    Suggests surgical spend across channels using Gemini Ultra Reasoning.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master performance marketer. "
                       "Suggest a surgical budget allocation across relevant channels "
                       "for the 90-day campaign based on the ICP and research."),
            ("user", "Research: {evidence}\nICP: {icp}")
        ])
        self.chain = self.prompt | llm.with_structured_output(BudgetAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        icp = state.get("context_brief", {}).get("icp_demographics", {})
        logger.info("Allocating marketing budget...")
        
        analysis = await self.chain.ainvoke({"evidence": str(evidence), "icp": str(icp)})
        logger.info("Budget allocation complete.")
        
        return {"context_brief": {"budget_plan": analysis.model_dump()}}

class SelectedChannel(BaseModel):
    """SOTA structured representation of a distribution channel."""
    channel_name: str
    priority: str # primary, secondary, experimental
    relevance_score: float # 0 to 1

class ChannelSelection(BaseModel):
    selected_channels: List[SelectedChannel]

class ChannelSelector:
    """
    SOTA Distribution Node.
    Decides the optimal mix of channels based on ICP demographics and psychographics.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of distribution strategy. "
                       "Based on the ICP and research, select the top 3-5 channels "
                       "where the brand should focus its energy."),
            ("user", "ICP: {icp}\nResearch: {evidence}")
        ])
        self.chain = self.prompt | llm.with_structured_output(ChannelSelection)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        icp = state.get("context_brief", {}).get("icp_demographics", {})
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Selecting optimal distribution channels...")
        
        analysis = await self.chain.ainvoke({"icp": str(icp), "evidence": str(evidence)})
        logger.info(f"Channel selection complete. Selected {len(analysis.selected_channels)} channels.")
        
        return {"context_brief": {"channels": analysis.model_dump()}}

class Metric(BaseModel):
    """SOTA structured representation of a success metric."""
    name: str
    target_value: str
    measurement_method: str

class KPIAnalysis(BaseModel):
    kpis: List[Metric]

class KPIDefiner:
    """
    SOTA Performance Measurement Node.
    Defines exactly what to track for the 90-day campaign using Gemini Ultra Reasoning.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a surgical data analyst. "
                       "Define the top 3-5 high-leverage KPIs for the campaign "
                       "based on the selected channels and objectives."),
            ("user", "Channels: {channels}\nObjectives: {arc}")
        ])
        self.chain = self.prompt | llm.with_structured_output(KPIAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        channels = state.get("context_brief", {}).get("channels", {})
        arc = state.get("context_brief", {}).get("campaign_arc", {})
        logger.info("Defining success metrics (KPIs)...")
        
        analysis = await self.chain.ainvoke({"channels": str(channels), "arc": str(arc)})
        logger.info(f"KPI definition complete. Identified {len(analysis.kpis)} metrics.")
        
        return {"context_brief": {"kpis": analysis.model_dump()}}

class FunnelStage(BaseModel):
    """SOTA structured representation of a funnel stage."""
    stage_name: str # e.g., TOFU, MOFU, BOFU
    content_type: str
    conversion_goal: str

class FunnelAnalysis(BaseModel):
    stages: List[FunnelStage]

class FunnelDesigner:
    """
    SOTA Journey Architecture Node.
    Maps the customer funnel from first touch to final sale using Gemini Ultra Reasoning.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of conversion rate optimization. "
                       "Architect a surgical multi-stage funnel for this campaign."),
            ("user", "Objectives: {arc}\nChannels: {channels}")
        ])
        self.chain = self.prompt | llm.with_structured_output(FunnelAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        arc = state.get("context_brief", {}).get("campaign_arc", {})
        channels = state.get("context_brief", {}).get("channels", {})
        logger.info("Designing conversion funnel...")
        
        analysis = await self.chain.ainvoke({"arc": str(arc), "channels": str(channels)})
        logger.info(f"Funnel design complete. Created {len(analysis.stages)} stages.")
        
        return {"context_brief": {"funnel": analysis.model_dump()}}

class StrategicConflict(BaseModel):
    """SOTA structured representation of a plan conflict."""
    description: str
    severity: float # 0 to 1
    resolution_suggestion: str

class ConflictAnalysis(BaseModel):
    conflicts: List[StrategicConflict]
    is_safe_to_proceed: bool

class StrategicConflictResolver:
    """
    SOTA Continuity Node.
    Checks if the new campaign contradicts past brand moves or historical research.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a surgical brand continuity lead. "
                       "Analyze the new campaign arc against the brand's historical context "
                       "and identify any strategic conflicts."),
            ("user", "New Arc: {arc}\nHistorical Context: {history}")
        ])
        self.chain = self.prompt | llm.with_structured_output(ConflictAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        arc = state.get("context_brief", {}).get("campaign_arc", {})
        history = state.get("research_bundle", {}).get("historical_context", [])
        logger.info("Checking for strategic conflicts...")
        
        analysis = await self.chain.ainvoke({"arc": str(arc), "history": str(history)})
        logger.info(f"Strategic conflict check complete. Safe to proceed: {analysis.is_safe_to_proceed}")
        
        return {"context_brief": {"conflicts": analysis.model_dump()}}

class StrategyRefreshHook:
    """
    SOTA Dynamic Planning Hook.
    Allows the Strategist to request 'More Research' or 'Reset Plan' 
    if the evidence bundle is surgically thin.
    """
    def __init__(self, llm: any):
        self.llm = llm

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        
        logger.info("Evaluating strategic data sufficiency...")
        
        # Heuristic: if key_findings < 2, we need more data
        if len(evidence.get("key_findings", [])) < 2:
            logger.warning("Strategic evidence too thin. Requesting research refresh...")
            res = await self.llm.ainvoke("The research is insufficient. Generate a specific query to find more competitive data.")
            return {"next_node": "research_refresh", "context_brief": {"refresh_instruction": res.content}}
        
        return {"next_node": "continue"}

def create_strategy_refresh_hook(llm: any):
    return StrategyRefreshHook(llm)

from backend.db import save_entity

class FounderProfile(BaseModel):
    """SOTA structured founder archetype representation."""
    personality_traits: List[str]
    strategic_goals: List[str]
    preferred_communication_style: str

class FounderArchetypeProfiler:
    """
    SOTA Entity Memory Node.
    Identifies and stores founder preferences to inform future agent backstories.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a world-class executive coach. "
                       "Based on the user's research and interactions, define the "
                       "surgical personality and strategic profile of the founder."),
            ("user", "Research: {evidence}")
        ])
        self.chain = self.prompt | llm.with_structured_output(FounderProfile)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        workspace_id = state.get("workspace_id")
        evidence = state.get("research_bundle", {}).get("final_evidence", {})
        logger.info("Profiling founder archetype...")
        
        profile = await self.chain.ainvoke({"evidence": str(evidence)})
        logger.info("Founder profiling complete.")
        
        # In production, we generate a real embedding
        dummy_embedding = [0.1] * 768
        
        await save_entity(
            workspace_id=workspace_id,
            name="Primary Founder",
            entity_type="founder",
            description=f"Strategic profile for the primary founder.",
            embedding=dummy_embedding,
            metadata=profile.model_dump()
        )
        
        return {"context_brief": {"founder_profile": profile.model_dump()}}

def create_founder_profiler(llm: any):
    return FounderArchetypeProfiler(llm)

def create_icp_demographer(llm: any):
    return ICPDemographicProfiler(llm)

def create_icp_psychographer(llm: any):
    return ICPPsychographicProfiler(llm)

def create_pain_point_mapper(llm: any):
    return PainPointMapper(llm)

def create_uvp_architect(llm: any):
    return UVPArchitect(llm)

def create_brand_voice_aligner(llm: any):
    return BrandVoiceAligner(llm)

def create_anti_persona_profiler(llm: any):
    return AntiPersonaProfiler(llm)

def create_category_architect(llm: any):
    return CategoryArchitect(llm)

def create_tagline_generator(llm: any):
    return TaglineGenerator(llm)

def create_strategy_replanner(llm: any):
    return StrategyReplanner(llm)

def create_campaign_designer(llm: any):
    return CampaignArcDesigner(llm)

def create_move_sequencer(llm: any):
    return MoveSequencer(llm)

def create_budget_allocator(llm: any):
    return BudgetAllocator(llm)

def create_channel_selector(llm: any):
    return ChannelSelector(llm)

def create_kpi_definer(llm: any):
    return KPIDefiner(llm)

def create_funnel_designer(llm: any):
    return FunnelDesigner(llm)

def create_conflict_resolver(llm: any):
    return StrategicConflictResolver(llm)
