"""
Customer Intelligence Graph - Orchestrates ICP building and enrichment.
Coordinates: ICP Builder → Persona Narrative → Pain Point Miner → Psychographic Profiler
"""

from typing import Dict, List, Optional, Any, TypedDict
from uuid import UUID
import logging

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.agents.research.icp_builder import icp_builder
from backend.agents.research.persona_narrative import persona_narrative
from backend.agents.research.pain_point_miner import pain_point_miner
from backend.agents.research.psychographic_profiler import psychographic_profiler
from backend.models.persona import ICPProfile
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import get_correlation_id

logger = logging.getLogger(__name__)


# Define state schema
class CustomerIntelligenceState(TypedDict):
    """State for the customer intelligence workflow."""
    workspace_id: str
    persona_input: Dict[str, Any]
    icp: Optional[Dict[str, Any]]
    narrative: Optional[str]
    pain_points: List[str]
    triggers: List[str]
    psychographics: Optional[Dict[str, Any]]
    decision_structure: Optional[str]
    depth: str  # "quick" or "deep"
    error: Optional[str]
    completed: bool


class CustomerIntelligenceGraph:
    """
    Orchestrates the customer intelligence workflow.
    
    Workflow:
    1. Build ICP → Assign tags and structure data
    2. Generate Narrative → Create human story
    3. Mine Pain Points → Discover from web sources
    4. Enrich Psychographics → Apply B=MAP framework
    5. Save to Database
    """
    
    def __init__(self):
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile(checkpointer=MemorySaver())
    
    def _build_workflow(self) -> StateGraph:
        """Builds the LangGraph workflow."""
        workflow = StateGraph(CustomerIntelligenceState)
        
        # Add nodes
        workflow.add_node("build_icp", self._build_icp_node)
        workflow.add_node("generate_narrative", self._generate_narrative_node)
        workflow.add_node("mine_pain_points", self._mine_pain_points_node)
        workflow.add_node("enrich_psychographics", self._enrich_psychographics_node)
        workflow.add_node("save_icp", self._save_icp_node)
        
        # Define edges (sequential workflow)
        workflow.set_entry_point("build_icp")
        workflow.add_edge("build_icp", "generate_narrative")
        workflow.add_edge("generate_narrative", "mine_pain_points")
        workflow.add_edge("mine_pain_points", "enrich_psychographics")
        workflow.add_edge("enrich_psychographics", "save_icp")
        workflow.add_edge("save_icp", END)
        
        return workflow
    
    async def _build_icp_node(self, state: CustomerIntelligenceState) -> CustomerIntelligenceState:
        """Builds initial ICP with tags."""
        try:
            logger.info("Building ICP with tags")
            
            icp = await icp_builder.build_icp(
                workspace_id=UUID(state["workspace_id"]),
                persona_input=state["persona_input"]
            )
            
            state["icp"] = icp.model_dump()
            return state
            
        except Exception as e:
            logger.error(f"ICP building failed: {e}")
            state["error"] = str(e)
            return state
    
    async def _generate_narrative_node(self, state: CustomerIntelligenceState) -> CustomerIntelligenceState:
        """Generates persona narrative."""
        try:
            logger.info("Generating persona narrative")
            
            # Reconstruct ICP object
            icp = ICPProfile(**state["icp"])
            
            narrative = await persona_narrative.generate_narrative(icp)
            
            state["narrative"] = narrative
            state["icp"]["narrative"] = narrative  # Add to ICP
            
            return state
            
        except Exception as e:
            logger.error(f"Narrative generation failed: {e}")
            state["error"] = str(e)
            return state
    
    async def _mine_pain_points_node(self, state: CustomerIntelligenceState) -> CustomerIntelligenceState:
        """Mines pain points from web sources."""
        try:
            logger.info("Mining pain points")
            
            # Reconstruct ICP object
            icp = ICPProfile(**state["icp"])
            
            # Mine pain points
            discovered_pain_points = await pain_point_miner.mine_pain_points(
                icp=icp,
                depth=state.get("depth", "quick")
            )
            
            # Merge with existing pain points
            all_pain_points = list(set(icp.pain_points + discovered_pain_points))
            state["pain_points"] = all_pain_points
            state["icp"]["pain_points"] = all_pain_points
            
            # Extract triggers
            triggers = await pain_point_miner.extract_triggers(all_pain_points)
            state["triggers"] = triggers
            state["icp"]["behavioral_triggers"] = triggers
            
            return state
            
        except Exception as e:
            logger.error(f"Pain point mining failed: {e}")
            state["error"] = str(e)
            return state
    
    async def _enrich_psychographics_node(self, state: CustomerIntelligenceState) -> CustomerIntelligenceState:
        """Enriches with psychographic attributes."""
        try:
            logger.info("Enriching psychographics")
            
            # Reconstruct ICP object
            icp = ICPProfile(**state["icp"])
            
            # Enrich psychographics
            psychographics = await psychographic_profiler.enrich_psychographics(icp)
            state["psychographics"] = psychographics.model_dump()
            state["icp"]["psychographics"] = psychographics.model_dump()
            
            # Determine decision structure
            decision_structure = await psychographic_profiler.assess_decision_structure(icp)
            state["decision_structure"] = decision_structure
            state["icp"]["decision_structure"] = decision_structure
            
            # Determine buying triggers (additional)
            buying_triggers = await psychographic_profiler.determine_buying_triggers(icp)
            state["icp"]["behavioral_triggers"] = list(set(
                state["icp"]["behavioral_triggers"] + buying_triggers
            ))
            
            state["completed"] = True
            return state
            
        except Exception as e:
            logger.error(f"Psychographic enrichment failed: {e}")
            state["error"] = str(e)
            return state
    
    async def _save_icp_node(self, state: CustomerIntelligenceState) -> CustomerIntelligenceState:
        """Saves completed ICP to database."""
        try:
            logger.info("Saving ICP to database")
            
            icp_data = state["icp"]
            icp_data["workspace_id"] = state["workspace_id"]
            
            # Save to cohorts table
            saved_icp = await supabase_client.insert("cohorts", icp_data)
            state["icp"]["id"] = saved_icp["id"]
            
            logger.info(f"ICP saved with ID: {saved_icp['id']}")
            return state
            
        except Exception as e:
            logger.error(f"ICP save failed: {e}")
            state["error"] = str(e)
            return state
    
    async def create_icp(
        self,
        workspace_id: UUID,
        persona_input: Dict[str, Any],
        depth: str = "quick"
    ) -> Dict[str, Any]:
        """
        Creates a complete ICP from basic persona input.
        
        Args:
            workspace_id: User's workspace ID
            persona_input: Basic persona info (nickname, role, pain_point, known_attributes)
            depth: "quick" or "deep" research
            
        Returns:
            Complete ICP with all enrichments
        """
        correlation_id = get_correlation_id()
        logger.info(
            f"Creating ICP: {persona_input.get('nickname')}",
            extra={"correlation_id": correlation_id}
        )
        
        # Initialize state
        initial_state: CustomerIntelligenceState = {
            "workspace_id": str(workspace_id),
            "persona_input": persona_input,
            "icp": None,
            "narrative": None,
            "pain_points": [],
            "triggers": [],
            "psychographics": None,
            "decision_structure": None,
            "depth": depth,
            "error": None,
            "completed": False
        }
        
        # Run workflow
        config = {"configurable": {"thread_id": correlation_id}}
        result = await self.app.ainvoke(initial_state, config)
        
        if result.get("error"):
            logger.error(f"ICP creation failed: {result['error']}")
            return {
                "success": False,
                "error": result["error"]
            }
        
        logger.info("ICP creation completed successfully")
        return {
            "success": True,
            "icp": result["icp"],
            "narrative": result["narrative"],
            "pain_points": result["pain_points"],
            "triggers": result["triggers"],
            "correlation_id": correlation_id
        }
    
    async def enrich_existing_icp(
        self,
        icp_id: UUID,
        depth: str = "deep"
    ) -> Dict[str, Any]:
        """
        Enriches an existing ICP with additional research.
        
        Args:
            icp_id: Existing ICP ID
            depth: Research depth
            
        Returns:
            Updated ICP
        """
        logger.info(f"Enriching existing ICP: {icp_id}")
        
        try:
            # Fetch existing ICP
            existing_icp_data = await supabase_client.fetch_one("cohorts", {"id": str(icp_id)})
            
            if not existing_icp_data:
                return {
                    "success": False,
                    "error": f"ICP not found: {icp_id}"
                }
            
            # Reconstruct ICP
            existing_icp = ICPProfile(**existing_icp_data)
            
            # Mine additional pain points
            new_pain_points = await pain_point_miner.mine_pain_points(existing_icp, depth=depth)
            all_pain_points = list(set(existing_icp.pain_points + new_pain_points))
            
            # Extract new triggers
            new_triggers = await pain_point_miner.extract_triggers(new_pain_points)
            all_triggers = list(set(existing_icp.behavioral_triggers + new_triggers))
            
            # Re-enrich psychographics
            enriched_psychographics = await psychographic_profiler.enrich_psychographics(existing_icp)
            
            # Update in database
            updates = {
                "pain_points": all_pain_points,
                "behavioral_triggers": all_triggers,
                "psychographics": enriched_psychographics.model_dump()
            }
            
            updated_icp = await supabase_client.update("cohorts", {"id": str(icp_id)}, updates)
            
            return {
                "success": True,
                "icp": updated_icp
            }
            
        except Exception as e:
            logger.error(f"ICP enrichment failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
customer_intelligence_graph = CustomerIntelligenceGraph()

