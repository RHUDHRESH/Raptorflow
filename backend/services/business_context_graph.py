"""
Business Context LangGraph Workflow
====================================

Orchestrates the generation of comprehensive business context using a multi-node 
LangGraph workflow with Gemini 1.5 Pro and strict Pydantic validation.
"""

import logging
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional, Union, Annotated, TypedDict

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

from backend.agents.state import AgentState
from backend.schemas import (
    BusinessContextState as BusinessContextSchemasState,
    CompanyProfile, MarketAnalysis, CompetitiveLandscape, 
    CustomerSegments, ValueProposition, BusinessModel, 
    GrowthStrategy, RiskFactors, SWOTAnalysis, 
    PESTELAnalysis, ValueChainAnalysis, BrandArchetypes, 
    CompetitorMatrix, EnhancedICP, MessagingStrategy,
    PsychographicInsights, BrandVoice, CoreMessagePillars,
    MessagingFramework, RICP
)
from .vertex_ai_client import get_vertex_ai_client

logger = logging.getLogger(__name__)

# Define the state for the graph, extending the base AgentState and our schema state
class BusinessContextWorkflowState(AgentState):
    """Internal state for the Business Context Graph."""
    # Data models from schemas.py
    context_data: BusinessContextSchemasState
    
    # Workflow control
    current_node: str
    retry_count: Dict[str, int]
    
    # Raw inputs
    foundation_data: Dict[str, Any]
    icp_list: List[Dict[str, Any]]

def create_initial_workflow_state(
    workspace_id: str, 
    user_id: str, 
    foundation_data: Dict[str, Any],
    icp_list: Optional[List[Dict[str, Any]]] = None,
    session_id: Optional[str] = None
) -> BusinessContextWorkflowState:
    """Initialize the workflow state."""
    from backend.agents.state import create_initial_state
    
    base_state = create_initial_state(workspace_id, user_id, session_id)
    
    return {
        **base_state,
        "context_data": BusinessContextSchemasState(),
        "current_node": "start",
        "retry_count": {},
        "foundation_data": foundation_data,
        "icp_list": icp_list or []
    }

import logging
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Annotated, TypedDict, Type, TypeVar

from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field, ValidationError

T = TypeVar("T", bound=BaseModel)

class BusinessContextGraph:
    """Manages the LangGraph for Business Context generation."""
    
    def __init__(self):
        self.vertex_ai_client = get_vertex_ai_client()
        self.workflow = self._build_graph()
        self.max_retries = 3
    
    def _build_graph(self) -> StateGraph:
        """Construct the LangGraph workflow with parallel processing."""
        builder = StateGraph(BusinessContextWorkflowState)
        
        # 1. Foundation Nodes (Linear)
        builder.add_node("generate_profile", self.generate_profile_node)
        builder.add_node("analyze_market", self.analyze_market_node)
        
        # 2. Parallel Intelligence Nodes (Fan-out)
        builder.add_node("analyze_competitors", self.analyze_competitors_node)
        builder.add_node("analyze_competitor_matrix", self.analyze_competitor_matrix_node)
        builder.add_node("analyze_customer_segments", self.analyze_customer_segments_node)
        builder.add_node("analyze_value_proposition", self.analyze_value_proposition_node)
        builder.add_node("generate_swot", self.generate_swot_node)
        builder.add_node("generate_pestel", self.generate_pestel_node)
        
        # 3. Structural Analysis Nodes (Linear after fan-in)
        builder.add_node("analyze_business_model", self.analyze_business_model_node)
        builder.add_node("derive_initial_cohorts", self.derive_initial_cohorts_node)
        builder.add_node("analyze_value_chain", self.analyze_value_chain_node)
        builder.add_node("identify_brand_archetypes", self.identify_brand_archetypes_node)
        
        # 4. Strategy Generation Nodes
        builder.add_node("formulate_growth_strategy", self.formulate_growth_strategy_node)
        builder.add_node("assess_risk_factors", self.assess_risk_factors_node)
        builder.add_node("enhance_icp", self.enhance_icp_node)
        builder.add_node("generate_messaging", self.generate_messaging_node)
        builder.add_node("synthesize_strategy", self.synthesize_strategy_node)
        
        # Define Edges with Parallelism
        builder.set_entry_point("generate_profile")
        builder.add_edge("generate_profile", "analyze_market")
        
        # Fan-out from Market Analysis
        builder.add_edge("analyze_market", "analyze_competitors")
        builder.add_edge("analyze_market", "analyze_customer_segments")
        builder.add_edge("analyze_market", "analyze_value_proposition")
        builder.add_edge("analyze_market", "generate_swot")
        builder.add_edge("analyze_market", "generate_pestel")
        
        # Matrix depends on Competitors
        builder.add_edge("analyze_competitors", "analyze_competitor_matrix")
        
        # Fan-in / Join point (Using analyze_business_model as the join)
        builder.add_edge("analyze_competitor_matrix", "analyze_business_model")
        builder.add_edge("analyze_customer_segments", "analyze_business_model")
        builder.add_edge("analyze_value_proposition", "analyze_business_model")
        builder.add_edge("generate_swot", "analyze_business_model")
        builder.add_edge("generate_pestel", "analyze_business_model")
        
        # Post-join flow
        builder.add_edge("analyze_business_model", "derive_initial_cohorts")
        builder.add_edge("derive_initial_cohorts", "analyze_value_chain")
        builder.add_edge("analyze_value_chain", "identify_brand_archetypes")
        builder.add_edge("identify_brand_archetypes", "formulate_growth_strategy")
        builder.add_edge("formulate_growth_strategy", "assess_risk_factors")
        builder.add_edge("assess_risk_factors", "enhance_icp")
        builder.add_edge("enhance_icp", "generate_messaging")
        builder.add_edge("generate_messaging", "synthesize_strategy")
        builder.add_edge("synthesize_strategy", END)
        
        return builder.compile()

    async def _safe_generate(
        self, 
        prompt: str, 
        model_class: Type[T], 
        node_name: str,
        state: BusinessContextWorkflowState
    ) -> T:
        """
        Safely generate structured output using Vertex AI and Pydantic validation.
        Implements retries and graceful degradation.
        """
        retries = state["retry_count"].get(node_name, 0)
        
        while retries < self.max_retries:
            try:
                response_text = await self.vertex_ai_client.generate_text(prompt)
                if not response_text:
                    raise ValueError("Empty response from AI")
                
                # JSON Parsing Safety
                try:
                    # Clean response text if it has markdown blocks
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                    data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON decode error in {node_name} (attempt {retries + 1}): {e}")
                    retries += 1
                    state["retry_count"][node_name] = retries
                    continue

                # Pydantic Validation
                try:
                    validated_data = model_class(**data)
                    return validated_data
                except ValidationError as e:
                    logger.warning(f"Validation error in {node_name} (attempt {retries + 1}): {e}")
                    retries += 1
                    state["retry_count"][node_name] = retries
                    continue
                    
            except Exception as e:
                logger.error(f"Unexpected error in {node_name} (attempt {retries + 1}): {e}")
                retries += 1
                state["retry_count"][node_name] = retries
        
        # Graceful Degradation: Return a default/fallback object if all retries fail
        logger.error(f"All retries failed for {node_name}. Using fallback.")
        return model_class()

    def _update_metadata(self, state: BusinessContextWorkflowState, source: str = "vertex_ai"):
        """
        Update metadata with latest generation timestamp and AI enhancement status.
        
        Args:
            state: The current workflow state.
            source: The source of the generation (default: vertex_ai).
        """
        state["context_data"].metadata["generated_at"] = datetime.now(UTC).isoformat()
        state["context_data"].metadata["source"] = source
        state["context_data"].metadata["ai_enhanced"] = True if source != "fallback" else False
        state["updated_at"] = datetime.now()

    def get_fallback_context(self, foundation_data: Dict[str, Any]) -> BusinessContextSchemasState:
        """Generate basic business context without AI."""
        context = BusinessContextSchemasState(
            company_profile=CompanyProfile(
                name=foundation_data.get('company_name', 'Unknown'),
                industry=foundation_data.get('industry', 'Unknown'),
                stage=foundation_data.get('stage', 'Unknown'),
                description=foundation_data.get('description', '')
            ),
            market_analysis=MarketAnalysis(overview="Market analysis unavailable (fallback mode)"),
            competitive_landscape=CompetitiveLandscape(overview="Competitive intelligence unavailable (fallback mode)"),
            customer_segments=CustomerSegments(primary="Primary segment details unavailable"),
            value_proposition=ValueProposition(core=foundation_data.get("description", "Value proposition unavailable")),
            swot_analysis=SWOTAnalysis(strengths=["Existing business context"]),
            pestel_analysis=PESTELAnalysis(political=["Regulatory compliance"]),
            brand_archetypes=BrandArchetypes(primary="The Sage")
        )
        context.metadata["source"] = "fallback"
        return context

    def get_fallback_icp(self, original_data: Dict[str, Any]) -> EnhancedICP:
        """Provide a non-AI fallback for ICP enhancement."""
        return EnhancedICP(
            archetype_name=f"Standard {original_data.get('name', 'Segment')}",
            original_data=original_data,
            psychographics=PsychographicInsights(
                drivers=["Efficiency", "Growth", "Stability"],
                motivations=["Risk reduction", "Competitive advantage"],
                behavioral_patterns=["Methodical decision making"]
            ),
            ai_enhanced=False
        )

    def get_fallback_messaging(self) -> MessagingStrategy:
        """Generate fallback messaging strategy."""
        return MessagingStrategy(
            one_liner="RaptorFlow provides clarity and control for founder marketing.",
            positioning_statement={
                "target": "Founders",
                "situation": "who want control",
                "product": "RaptorFlow",
                "category": "Marketing OS",
                "key_benefit": "Clarity",
                "alternatives": "Chaos",
                "differentiator": "Surgical precision"
            },
            brand_voice=BrandVoice(tone="Professional", personality="Helpful"),
            core_messages=CoreMessagePillars(pillars=["Quality service", "Customer first"]),
            framework=MessagingFramework(structure="Problem-Solution-Benefit"),
            source="fallback"
        )

    async def generate_profile_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to generate core company profile."""
        prompt = f"""
        You are a SOTA Business Strategy Agent. Your task is to analyze the raw foundation data and extract a surgical company profile.
        
        Foundation Data: {json.dumps(state['foundation_data'], indent=2)}
        
        Guidelines:
        - Think step-by-step about the company's core mission and long-term vision.
        - Determine the exact market position based on industry and stage.
        - Ensure all fields align with the "Quiet Luxury" brand identity of RaptorFlow (Calm, Precise, Surgical).
        
        Return a JSON object matching the CompanyProfile schema:
        {{
            "name": "Company Name",
            "mission": "Surgical mission statement",
            "vision": "Ambitious 5-year vision",
            "market_position": "Precise market positioning description",
            "industry": "Extracted industry",
            "stage": "Extracted stage",
            "description": "Professional description",
            "team_size": "Extracted team size",
            "revenue": "Extracted revenue"
        }}
        """
        profile = await self._safe_generate(prompt, CompanyProfile, "generate_profile", state)
        state["context_data"].company_profile = profile
        self._update_metadata(state)
        return state

    async def analyze_market_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to analyze market size and trends."""
        prompt = f"""
        You are an Industrial Intelligence Analyst. Analyze the market landscape for:
        Company: {state['context_data'].company_profile.name if state['context_data'].company_profile else 'Unknown'}
        Industry Context: {state['foundation_data'].get('industry', '')}
        
        Task:
        1. Assess current market size and CAGRs if applicable.
        2. Identify high-signal trends (Technological, Behavioral, Regulatory).
        3. Pinpoint specific "Blue Ocean" opportunities.
        
        Return a JSON object matching the MarketAnalysis schema:
        {{
            "overview": "Data-driven market assessment",
            "size": "Market size with units (e.g., $10B)",
            "trends": ["Trend 1", "Trend 2", "Trend 3"],
            "opportunities": ["Opportunity 1", "Opportunity 2"]
        }}
        """
        analysis = await self._safe_generate(prompt, MarketAnalysis, "analyze_market", state)
        state["context_data"].market_analysis = analysis
        self._update_metadata(state)
        return state

    async def analyze_competitors_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to map the competitive landscape."""
        prompt = f"""
        You are a Competitive Intelligence Agent. Map the battlefield for:
        Company: {state['context_data'].company_profile.name if state['context_data'].company_profile else 'Unknown'}
        
        Task:
        - Identify direct and indirect competitors.
        - Detail the primary differentiation vectors.
        - Surface the "Unfair Advantages" (Moats).
        
        Return a JSON object matching the CompetitiveLandscape schema:
        {{
            "overview": "Surgical competitive summary",
            "competitors": ["Competitor A", "Competitor B"],
            "differentiation": ["Vector 1", "Vector 2"],
            "advantages": ["Moat 1", "Moat 2"]
        }}
        """
        landscape = await self._safe_generate(prompt, CompetitiveLandscape, "analyze_competitors", state)
        state["context_data"].competitive_landscape = landscape
        self._update_metadata(state)
        return state

    async def analyze_competitor_matrix_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to generate a feature comparison matrix."""
        competitors = state['context_data'].competitive_landscape.competitors if state['context_data'].competitive_landscape else []
        
        prompt = f"""
        You are a Product Strategist. Create a feature-by-feature comparison matrix for:
        Company: {state['context_data'].company_profile.name if state['context_data'].company_profile else 'Unknown'}
        Competitors: {', '.join(competitors)}
        
        Task:
        - Identify 5 key high-value features/dimensions for comparison.
        - For each competitor (and the target company), evaluate their implementation (High, Medium, Low, or Absent).
        
        Return a JSON object matching the CompetitorMatrix schema:
        {{
            "competitors": ["Company", "Competitor A", "..."],
            "features": ["Feature 1", "Feature 2", "..."],
            "comparison": {{
                "Company": {{"Feature 1": "High", "Feature 2": "Medium", "..."}},
                "Competitor A": {{"Feature 1": "Low", "Feature 2": "High", "..."}}
            }}
        }}
        """
        matrix = await self._safe_generate(prompt, CompetitorMatrix, "analyze_competitor_matrix", state)
        state["context_data"].competitor_matrix = matrix
        self._update_metadata(state)
        return state

    async def analyze_customer_segments_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to define customer segments."""
        prompt = f"""
        You are a Behavioral Segmentation Specialist. Define the customer segments for:
        Company Profile: {json.dumps(state['context_data'].company_profile.model_dump() if state['context_data'].company_profile else {}, indent=2)}
        
        Task:
        - Define the "North Star" primary segment.
        - List high-potential secondary segments.
        - Provide high-density demographic and psychographic markers.
        
        Return a JSON object matching the CustomerSegments schema:
        {{
            "primary": "Detailed primary segment description",
            "secondary": ["Segment A", "Segment B"],
            "demographics": {{"age": "...", "roles": "...", "etc": "..."}},
            "psychographics": {{"motivations": "...", "values": "...", "etc": "..."}}
        }}
        """
        segments = await self._safe_generate(prompt, CustomerSegments, "analyze_customer_segments", state)
        state["context_data"].customer_segments = segments
        self._update_metadata(state)
        return state

    async def analyze_value_proposition_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to analyze the value proposition."""
        prompt = f"""
        You are a Value Proposition Designer. Articulate the core value for:
        Foundation Data: {json.dumps(state['foundation_data'], indent=2)}
        
        Task:
        - Draft a surgical core value proposition statement.
        - List 3-5 unique selling points (USPs) that are hard to replicate.
        - Map these to tangible customer benefits (Functional, Emotional, Social).
        
        Return a JSON object matching the ValueProposition schema:
        {{
            "core": "High-impact value statement",
            "unique_points": ["USP 1", "USP 2"],
            "benefits": ["Benefit 1", "Benefit 2"]
        }}
        """
        proposition = await self._safe_generate(prompt, ValueProposition, "analyze_value_proposition", state)
        state["context_data"].value_proposition = proposition
        self._update_metadata(state)
        return state

    async def analyze_business_model_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to analyze the business model."""
        prompt = f"""
        You are a Business Model Architect. Deconstruct the mechanics for:
        Company: {state['context_data'].company_profile.name if state['context_data'].company_profile else 'Unknown'}
        Value Prop: {state['context_data'].value_proposition.core if state['context_data'].value_proposition else 'Unknown'}
        
        Task:
        - Classify the business model type.
        - Identify all primary and auxiliary revenue streams.
        - Detail the primary cost drivers (COGS, OpEx).
        - Explain the core profitability engine.
        
        Return a JSON object matching the BusinessModel schema:
        {{
            "type": "e.g., Enterprise SaaS, B2B Marketplace",
            "revenue_streams": ["Stream 1", "Stream 2"],
            "cost_structures": ["Cost 1", "Cost 2"],
            "profitability_mechanisms": ["Mechanism 1", "Mechanism 2"]
        }}
        """
        model = await self._safe_generate(prompt, BusinessModel, "analyze_business_model", state)
        state["context_data"].business_model = model
        self._update_metadata(state)
        return state

    async def derive_initial_cohorts_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """
        Node to automatically suggest/derive initial cohorts if none are provided.
        Uses the CustomerSegments results to populate icp_list.
        """
        if state["icp_list"]:
            logger.info("ICP list already populated, skipping initial cohort derivation.")
            return state

        segments = state["context_data"].customer_segments
        if not segments:
            logger.warning("No customer segments found, cannot derive initial cohorts.")
            return state

        prompt = f"""
        You are a Marketing Strategist. Suggest 3 high-potential initial cohorts (target segments) for:
        Primary Segment Overview: {segments.primary}
        Secondary Segments: {', '.join(segments.secondary)}
        
        Task:
        - Define 3 specific cohorts that should be targeted first.
        - For each, provide a name and a brief description.
        
        Return a JSON array of objects with "name" and "description" keys.
        """
        
        try:
            # We use _safe_generate with a list type or handle it manually
            # For simplicity, we'll request a wrapped object
            class CohortList(BaseModel):
                cohorts: List[Dict[str, str]]

            suggested = await self._safe_generate(prompt, CohortList, "derive_initial_cohorts", state)
            state["icp_list"] = suggested.cohorts
            logger.info(f"Derived {len(suggested.cohorts)} initial cohorts.")
        except Exception as e:
            logger.error(f"Failed to derive initial cohorts: {e}")
            # Fallback to just the primary segment as a single cohort
            state["icp_list"] = [{"name": "Primary Segment", "description": segments.primary}]

        return state

    async def formulate_growth_strategy_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to formulate growth strategy."""
        prompt = f"""
        You are a Growth Intelligence Lead. Formulate the expansion plan for:
        Market Analysis: {json.dumps(state['context_data'].market_analysis.model_dump() if state['context_data'].market_analysis else {}, indent=2)}
        
        Task:
        - Define the overarching growth strategy (Product-led, Sales-led, Ecosystem-led).
        - List the primary growth drivers (Engines of Growth).
        - Detail 3 high-priority strategic initiatives.
        
        Return a JSON object matching the GrowthStrategy schema:
        {{
            "overview": "Surgical growth overview",
            "drivers": ["Driver 1", "Driver 2"],
            "initiatives": ["Initiative 1", "Initiative 2"]
        }}
        """
        strategy = await self._safe_generate(prompt, GrowthStrategy, "formulate_growth_strategy", state)
        state["context_data"].growth_strategy = strategy
        self._update_metadata(state)
        return state

    async def assess_risk_factors_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to assess risks and mitigations."""
        prompt = f"""
        You are a Risk & Resilience Officer. Identify potential failure modes for:
        Business Model: {json.dumps(state['context_data'].business_model.model_dump() if state['context_data'].business_model else {}, indent=2)}
        
        Task:
        - Assess the risk landscape (Market, Execution, Financial, Technical).
        - List the top "Black Swan" risks.
        - Propose specific, surgical mitigations for each.
        
        Return a JSON object matching the RiskFactors schema:
        {{
            "overview": "Risk assessment summary",
            "risks": ["Risk 1", "Risk 2"],
            "mitigations": ["Mitigation 1", "Mitigation 2"]
        }}
        """
        risks = await self._safe_generate(prompt, RiskFactors, "assess_risk_factors", state)
        state["context_data"].risk_factors = risks
        self._update_metadata(state)
        return state

    async def generate_swot_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to generate SWOT analysis."""
        prompt = f"""
        Perform a surgical SWOT analysis for:
        Company: {state['context_data'].company_profile.name if state['context_data'].company_profile else 'Unknown'}
        Market Context: {state['context_data'].market_analysis.overview if state['context_data'].market_analysis else 'Unknown'}
        
        Think step-by-step about internal capabilities vs external pressures.
        
        Return a JSON object matching the SWOTAnalysis schema:
        {{
            "strengths": ["...", "..."],
            "weaknesses": ["...", "..."],
            "opportunities": ["...", "..."],
            "threats": ["...", "..."]
        }}
        """
        swot = await self._safe_generate(prompt, SWOTAnalysis, "generate_swot", state)
        state["context_data"].swot_analysis = swot
        self._update_metadata(state)
        return state

    async def generate_pestel_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to generate PESTEL analysis."""
        prompt = f"""
        Perform a comprehensive PESTEL analysis for the industry:
        Industry: {state['foundation_data'].get('industry', 'Unknown')}
        Market Context: {state['context_data'].market_analysis.overview if state['context_data'].market_analysis else 'Unknown'}
        
        Return a JSON object matching the PESTELAnalysis schema:
        {{
            "political": ["...", "..."],
            "economic": ["...", "..."],
            "social": ["...", "..."],
            "technological": ["...", "..."],
            "environmental": ["...", "..."],
            "legal": ["...", "..."]
        }}
        """
        pestel = await self._safe_generate(prompt, PESTELAnalysis, "generate_pestel", state)
        state["context_data"].pestel_analysis = pestel
        self._update_metadata(state)
        return state

    async def analyze_value_chain_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to analyze the value chain."""
        prompt = f"""
        Conduct a Michael Porter style Value Chain Analysis for:
        Business Model: {state['context_data'].business_model.type if state['context_data'].business_model else 'Unknown'}
        
        Break down:
        1. primary_activities: (Inbound Logistics, Operations, Outbound Logistics, Marketing & Sales, Service)
        2. support_activities: (Firm Infrastructure, HR Management, Tech Development, Procurement)
        
        Return a JSON object matching the ValueChainAnalysis schema:
        {{
            "primary_activities": {{
                "logistics": ["...", "..."],
                "operations": ["...", "..."],
                "marketing": ["...", "..."],
                "service": ["...", "..."]
            }},
            "support_activities": {{
                "infrastructure": ["...", "..."],
                "hr": ["...", "..."],
                "technology": ["...", "..."],
                "procurement": ["...", "..."]
            }}
        }}
        """
        chain = await self._safe_generate(prompt, ValueChainAnalysis, "analyze_value_chain", state)
        state["context_data"].value_chain_analysis = chain
        self._update_metadata(state)
        return state

    async def identify_brand_archetypes_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to identify brand archetypes."""
        prompt = f"""
        You are a Brand Identity Strategist. Identify the Jungian archetypes for:
        Company: {state['context_data'].company_profile.name if state['context_data'].company_profile else 'Unknown'}
        Mission: {state['context_data'].company_profile.mission if state['context_data'].company_profile else 'Unknown'}
        
        Task:
        - Select the Primary and Secondary archetypes (e.g., The Hero, The Creator, The Sage, The Rebel).
        - Detail the personality traits that define this archetype in the brand's context.
        
        Return a JSON object matching the BrandArchetypes schema:
        {{
            "primary": "Archetype Name",
            "secondary": "Archetype Name",
            "traits": ["Trait 1", "Trait 2", "Trait 3"]
        }}
        """
        archetypes = await self._safe_generate(prompt, BrandArchetypes, "identify_brand_archetypes", state)
        state["context_data"].brand_archetypes = archetypes
        self._update_metadata(state)
        return state

    async def enhance_icp_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """
        Orchestrator node for RICP (Cohort/ICP/Persona) generation. 
        Iterates through the icp_list and generates deep insights for each.
        """
        if not state["icp_list"]:
            logger.info("No ICPs provided for enhancement.")
            return state

        # Limit to 3 ICPs as per original implementation requirements
        for icp in state["icp_list"][:3]:
            icp_id = icp.get("id") or icp.get("name")
            if not icp_id:
                continue

            prompt = f"""
            You are a Behavioral Economics & Marketing Scientist. Generate a Rich ICP (RICP) which is a unified 
            Cohort + ICP + Persona entity for:
            
            Input Data: {json.dumps(icp, indent=2)}
            Company Context: {json.dumps(state['context_data'].company_profile.model_dump() if state['context_data'].company_profile else {}, indent=2)}
            
            Guidelines:
            - name: The Cohort name (e.g., "Seed-Stage B2B Founders")
            - persona_name: A human name for the persona (e.g., "Sarah")
            - avatar: A single emoji representing the persona.
            - demographics: Surgical demographic data (age_range, income, location, role, stage).
            - psychographics: Deep psychological drivers (beliefs, identity, becoming, fears, values, hangouts, content_consumed, who_they_follow, language, timing, triggers).
            - market_sophistication: 1-5 score (1=Unaware, 5=Most Aware).
            - confidence: 0-100 score of your assessment.
            
            Return a JSON object matching the RICP schema.
            """
            
            try:
                # 1. Generate Unified RICP
                ricp_entity = await self._safe_generate(prompt, RICP, f"generate_ricp_{icp_id}", state)
                state["context_data"].ricps.append(ricp_entity)
                
                # 2. Maintain legacy EnhancedICP for backward compatibility
                legacy_prompt = f"""
                Convert this RICP into the legacy EnhancedICP format:
                RICP: {ricp_entity.model_dump_json()}
                """
                enhanced = await self._safe_generate(legacy_prompt, EnhancedICP, f"enhance_icp_{icp_id}", state)
                if not enhanced.original_data:
                    enhanced = self.get_fallback_icp(icp)
                
                enhanced.original_data = icp
                enhanced.ai_enhanced = True
                enhanced.enhanced_at = datetime.now(UTC)
                state["context_data"].icp_enhancements[icp_id] = enhanced
                
            except Exception as e:
                logger.error(f"Error in enhance_icp_{icp_id}: {e}")
                state["context_data"].ricps.append(RICP(name=icp.get("name", "Unknown Segment")))
                state["context_data"].icp_enhancements[icp_id] = self.get_fallback_icp(icp)
            
        self._update_metadata(state)
        return state

    async def generate_messaging_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Node to generate comprehensive messaging strategy using StoryBrand."""
        icp_summary = ""
        for ricp in state["context_data"].ricps:
            icp_summary += f"\n- {ricp.name} ({ricp.persona_name}): {ricp.psychographics.identity}"

        prompt = f"""
        You are a SOTA Messaging Architect and StoryBrand Certified Guide. Construct the communication spine for:
        Company: {state['context_data'].company_profile.name if state['context_data'].company_profile else 'Unknown'}
        Value Prop: {state['context_data'].value_proposition.core if state['context_data'].value_proposition else 'Unknown'}
        Archetypes: {state['context_data'].brand_archetypes.primary if state['context_data'].brand_archetypes else 'Unknown'}
        Target RICPs: {icp_summary}
        
        Task:
        1. Create a high-impact mission-driven one_liner.
        2. Draft a structured positioning_statement (keys: target, situation, product, category, key_benefit, alternatives, differentiator).
        3. Establish the Brand Voice (Tone & Personality).
        4. Develop 3 foundational Core Message Pillars.
        5. Create a structured Messaging Framework (Problem-Solution-Benefit).
        6. Tailor messages for primary digital channels.
        7. Build the StoryBrand Framework (Character, Problem, Guide, Plan, CTA, Success/Failure).
        
        Return a JSON object matching the MessagingStrategy schema.
        """
        try:
            strategy = await self._safe_generate(prompt, MessagingStrategy, "generate_messaging", state)
            strategy.target_icps = [r.id for r in state["context_data"].ricps]
            strategy.source = "vertex_ai"
            strategy.confidence = 85 # Initial assessment
            
            state["context_data"].messaging_strategy = strategy
        except Exception as e:
            logger.error(f"Error in generate_messaging: {e}")
            state["context_data"].messaging_strategy = self.get_fallback_messaging()
            
        self._update_metadata(state)
        return state

    async def synthesize_strategy_node(self, state: BusinessContextWorkflowState) -> BusinessContextWorkflowState:
        """Final node to synthesize the full strategy and update state results."""
        logger.info("Synthesizing full business context strategy.")
        
        # Final formatting/cleaning of the overall state output if needed
        state["output"] = state["context_data"].model_dump()
        state["current_agent"] = "BusinessContextGenerator"
        
        self._update_metadata(state)

        # Record in BCM Ledger
        try:
            from backend.services.bcm_integration import bcm_evolution
            await bcm_evolution.record_strategic_shift(
                workspace_id=state.get("workspace_id"),
                ucid=state["context_data"].ucid or "RF-STRATEGY-REBUILD",
                reason="Business Context Graph Reconstruction",
                updates=state["output"]
            )
        except Exception as e:
            logger.error(f"Failed to ledger strategy synthesis: {e}")

        return state

# Global singleton pattern
_business_context_graph: Optional[BusinessContextGraph] = None

def get_business_context_graph() -> BusinessContextGraph:
    """Get the singleton instance of the Business Context Graph."""
    global _business_context_graph
    if _business_context_graph is None:
        _business_context_graph = BusinessContextGraph()
    return _business_context_graph
