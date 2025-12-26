import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from agents.base import BaseCognitiveAgent
from models.swarm import (
    SwarmState,
    CompetitorProfile,
    CompetitorGroup,
    CompetitorInsight,
    CompetitorAnalysis,
    CompetitorType,
    CompetitorThreatLevel,
)

logger = logging.getLogger("raptorflow.agents.swarm_competitor_intelligence")


class CompetitorResearchOutput(BaseModel):
    """Structured output for competitor research tasks."""
    
    discovered_competitors: List[CompetitorProfile] = Field(default_factory=list)
    market_insights: List[str] = Field(default_factory=list)
    competitive_gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    research_summary: str


class CompetitorAnalysisOutput(BaseModel):
    """Structured output for competitor analysis tasks."""
    
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_type: str
    competitor_ids: List[str] = Field(default_factory=list)
    swot_analysis: Dict[str, List[str]] = Field(default_factory=dict)
    competitive_positioning: str
    threat_assessment: CompetitorThreatLevel
    strategic_recommendations: List[str] = Field(default_factory=list)
    market_opportunities: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    analyzed_at: datetime = Field(default_factory=datetime.now)


class SwarmCompetitorIntelligenceAgent(BaseCognitiveAgent):
    """
    Swarm Competitor Intelligence Specialist.
    Focuses on discovering, analyzing, and tracking competitors within swarm operations.
    Integrates competitive intelligence into swarm decision-making processes.
    """

    def __init__(self):
        system_prompt = (
            "You are the Swarm Competitor Intelligence Specialist, an expert in competitive analysis "
            "and market intelligence. Your role is to:\n"
            "1. Discover and profile competitors relevant to the swarm's objectives\n"
            "2. Analyze competitor strategies, positioning, and movements\n"
            "3. Identify competitive threats and opportunities\n"
            "4. Provide actionable intelligence to guide swarm decision-making\n"
            "5. Track competitor activities and maintain up-to-date intelligence\n"
            "6. Group competitors by characteristics for strategic analysis\n"
            "Always provide structured, data-driven insights with confidence scores."
        )
        
        super().__init__(
            name="SwarmCompetitorIntelligence",
            role="competitor_intelligence",
            system_prompt=system_prompt,
            model_tier="reasoning",
            output_schema=CompetitorResearchOutput,
        )

    async def discover_competitors(self, state: SwarmState) -> Dict[str, Any]:
        """Discover new competitors based on market analysis."""
        logger.info("SwarmCompetitorIntelligence discovering competitors...")
        
        context = self._build_competitor_context(state)
        prompt = (
            f"Based on the following context, discover and profile competitors:\n\n"
            f"Context: {context}\n\n"
            "Identify key competitors in the market. For each competitor, provide:\n"
            "- Company name and website\n"
            "- Competitor type (direct, indirect, emerging, market leader, niche player)\n"
            "- Threat level assessment\n"
            "- Key products/services and features\n"
            "- Pricing model information\n"
            "- Target audience and market positioning\n"
            "- Strengths and weaknesses\n"
            "- Market share if known\n"
            "Return your findings as a structured competitor analysis."
        )
        
        try:
            response = await self._call_llm(prompt, CompetitorResearchOutput)
            
            # Update swarm state with discovered competitors
            updated_state = state.copy()
            competitor_profiles = updated_state.get("competitor_profiles", {})
            
            for competitor in response.discovered_competitors:
                competitor_profiles[competitor.id] = competitor
                
            updated_state["competitor_profiles"] = competitor_profiles
            updated_state["shared_knowledge"]["latest_competitor_discovery"] = {
                "timestamp": datetime.now().isoformat(),
                "competitors_found": len(response.discovered_competitors),
                "summary": response.research_summary
            }
            
            return {
                "discovered_competitors": [c.model_dump() for c in response.discovered_competitors],
                "market_insights": response.market_insights,
                "competitive_gaps": response.competitive_gaps,
                "recommendations": response.recommendations,
                "confidence_score": response.confidence_score,
                "research_summary": response.research_summary,
                "updated_state": updated_state
            }
            
        except Exception as e:
            logger.error(f"Competitor discovery failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def analyze_competitors(self, state: SwarmState, competitor_ids: List[str]) -> Dict[str, Any]:
        """Perform deep analysis on specific competitors."""
        logger.info(f"SwarmCompetitorIntelligence analyzing competitors: {competitor_ids}")
        
        competitor_profiles = state.get("competitor_profiles", {})
        target_competitors = [competitor_profiles[cid] for cid in competitor_ids if cid in competitor_profiles]
        
        if not target_competitors:
            return {"error": "No valid competitor profiles found", "status": "failed"}
        
        context = {
            "competitors": [c.model_dump() for c in target_competitors],
            "swarm_objectives": state.get("shared_knowledge", {}),
            "market_context": state.get("competitive_landscape_summary", "")
        }
        
        prompt = (
            f"Perform a comprehensive competitive analysis on the following competitors:\n\n"
            f"Competitor Data: {context}\n\n"
            "Provide:\n"
            "1. SWOT analysis for each competitor\n"
            "2. Competitive positioning assessment\n"
            "3. Threat level evaluation\n"
            "4. Strategic recommendations for dealing with these competitors\n"
            "5. Market opportunities identified through the analysis\n"
            "6. Overall confidence in your analysis"
        )
        
        try:
            response = await self._call_llm(prompt, CompetitorAnalysisOutput)
            
            # Create competitor analysis record
            analysis = CompetitorAnalysis(
                id=response.analysis_id,
                analysis_type=response.analysis_type,
                competitor_ids=competitor_ids,
                summary=response.competitive_positioning,
                key_findings=[f"SWOT: {k} - {', '.join(v)}" for k, v in response.swot_analysis.items()],
                recommendations=response.strategic_recommendations,
                competitive_gaps=[],  # To be filled by additional analysis
                market_opportunities=response.market_opportunities,
                threat_level=response.threat_assessment,
                confidence_score=response.confidence_score,
                analyzed_at=response.analyzed_at
            )
            
            # Update swarm state
            updated_state = state.copy()
            competitor_analyses = updated_state.get("competitor_analyses", [])
            competitor_analyses.append(analysis)
            updated_state["competitor_analyses"] = competitor_analyses
            
            return {
                "analysis": analysis.model_dump(),
                "swot_analysis": response.swot_analysis,
                "competitive_positioning": response.competitive_positioning,
                "threat_assessment": response.threat_assessment,
                "strategic_recommendations": response.strategic_recommendations,
                "market_opportunities": response.market_opportunities,
                "confidence_score": response.confidence_score,
                "updated_state": updated_state
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def track_competitor_insights(self, state: SwarmState, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Track and categorize new competitor insights."""
        logger.info("SwarmCompetitorIntelligence tracking competitor insights...")
        
        try:
            insight = CompetitorInsight(
                id=str(uuid.uuid4()),
                competitor_id=insight_data.get("competitor_id"),
                insight_type=insight_data.get("insight_type", "general"),
                title=insight_data.get("title", "New Competitor Insight"),
                description=insight_data.get("description", ""),
                impact_assessment=insight_data.get("impact_assessment", "medium"),
                confidence=insight_data.get("confidence", 0.5),
                source=insight_data.get("source", "swarm_intelligence"),
                tags=insight_data.get("tags", [])
            )
            
            # Update swarm state with new insight
            updated_state = state.copy()
            competitor_insights = updated_state.get("competitor_insights", [])
            competitor_insights.append(insight)
            updated_state["competitor_insights"] = competitor_insights
            
            # Update competitor profile if insight affects it
            competitor_id = insight.competitor_id
            if competitor_id in updated_state.get("competitor_profiles", {}):
                profile = updated_state["competitor_profiles"][competitor_id]
                profile.last_updated = datetime.now()
                profile.data_sources.append(insight.source)
            
            return {
                "insight": insight.model_dump(),
                "updated_state": updated_state,
                "status": "tracked"
            }
            
        except Exception as e:
            logger.error(f"Competitor insight tracking failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def group_competitors(self, state: SwarmState, grouping_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Group competitors based on specified criteria."""
        logger.info("SwarmCompetitorIntelligence grouping competitors...")
        
        competitor_profiles = state.get("competitor_profiles", {})
        if not competitor_profiles:
            return {"error": "No competitor profiles available", "status": "failed"}
        
        try:
            # Create competitor groups based on criteria
            groups = {}
            criteria_type = grouping_criteria.get("type", "market_segment")
            
            if criteria_type == "market_segment":
                for comp_id, profile in competitor_profiles.items():
                    segment = profile.competitor_type.value
                    if segment not in groups:
                        groups[segment] = {
                            "id": f"group_{segment}",
                            "name": f"{segment.title()} Competitors",
                            "description": f"Group of {segment} competitors",
                            "competitor_ids": [],
                            "common_characteristics": [],
                            "market_segment": segment
                        }
                    groups[segment]["competitor_ids"].append(comp_id)
            
            elif criteria_type == "threat_level":
                for comp_id, profile in competitor_profiles.items():
                    threat = profile.threat_level.value
                    if threat not in groups:
                        groups[threat] = {
                            "id": f"group_{threat}",
                            "name": f"{threat.title()} Threat Competitors",
                            "description": f"Group of {threat} threat level competitors",
                            "competitor_ids": [],
                            "common_characteristics": [f"threat_level: {threat}"],
                            "market_segment": "threat_based"
                        }
                    groups[threat]["competitor_ids"].append(comp_id)
            
            # Convert to CompetitorGroup objects
            competitor_groups = {}
            for group_key, group_data in groups.items():
                group = CompetitorGroup(**group_data)
                competitor_groups[group.id] = group
            
            # Update swarm state
            updated_state = state.copy()
            updated_state["competitor_groups"] = competitor_groups
            
            return {
                "groups": [g.model_dump() for g in competitor_groups.values()],
                "grouping_criteria": grouping_criteria,
                "updated_state": updated_state,
                "status": "grouped"
            }
            
        except Exception as e:
            logger.error(f"Competitor grouping failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def __call__(self, state: SwarmState) -> Dict[str, Any]:
        """Main entry point for competitor intelligence operations."""
        logger.info("SwarmCompetitorIntelligence agent called...")
        
        # Determine operation type based on state
        operation = state.get("competitor_operation", "discover")
        
        if operation == "discover":
            return await self.discover_competitors(state)
        elif operation == "analyze":
            competitor_ids = state.get("target_competitors", [])
            return await self.analyze_competitors(state, competitor_ids)
        elif operation == "track_insight":
            insight_data = state.get("insight_data", {})
            return await self.track_competitor_insights(state, insight_data)
        elif operation == "group":
            grouping_criteria = state.get("grouping_criteria", {"type": "market_segment"})
            return await self.group_competitors(state, grouping_criteria)
        else:
            return {"error": f"Unknown operation: {operation}", "status": "failed"}

    def _build_competitor_context(self, state: SwarmState) -> str:
        """Build context for competitor discovery from swarm state."""
        context_parts = []
        
        # Add swarm objectives
        if "shared_knowledge" in state:
            context_parts.append(f"Swarm Objectives: {state['shared_knowledge']}")
        
        # Add existing competitor info
        if "competitor_profiles" in state and state["competitor_profiles"]:
            existing_comp = [f"{p.name} ({p.competitor_type.value})" 
                           for p in state["competitor_profiles"].values()]
            context_parts.append(f"Known Competitors: {', '.join(existing_comp)}")
        
        # Add market context
        if "competitive_landscape_summary" in state:
            context_parts.append(f"Market Context: {state['competitive_landscape_summary']}")
        
        return "\n".join(context_parts) if context_parts else "No specific context available"

    async def _call_llm(self, prompt: str, output_schema: type) -> Any:
        """Helper method to call LLM with structured output."""
        # This would use the actual LLM calling mechanism from the base agent
        # For now, we'll simulate the call
        logger.info(f"Calling LLM with prompt: {prompt[:100]}...")
        
        # In a real implementation, this would call the actual LLM
        # For demonstration, we'll return a mock response
        if output_schema == CompetitorResearchOutput:
            return CompetitorResearchOutput(
                discovered_competitors=[],
                market_insights=["Mock insight"],
                competitive_gaps=["Mock gap"],
                recommendations=["Mock recommendation"],
                confidence_score=0.8,
                research_summary="Mock research summary"
            )
        elif output_schema == CompetitorAnalysisOutput:
            return CompetitorAnalysisOutput(
                analysis_type="swot",
                swot_analysis={
                    "strengths": ["Mock strength"],
                    "weaknesses": ["Mock weakness"],
                    "opportunities": ["Mock opportunity"],
                    "threats": ["Mock threat"]
                },
                competitive_positioning="Mock positioning",
                threat_assessment=CompetitorThreatLevel.MEDIUM,
                strategic_recommendations=["Mock strategy"],
                market_opportunities=["Mock opportunity"],
                confidence_score=0.75
            )
