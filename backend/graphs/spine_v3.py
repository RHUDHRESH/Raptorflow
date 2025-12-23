import logging
import os
import operator
from typing import Dict, Any, List, Optional, Annotated
from langgraph.graph import StateGraph, START, END
from backend.models.cognitive import CognitiveIntelligenceState, CognitiveStatus, AgentMessage
from backend.memory.semantic import SemanticMemory
from backend.memory.episodic import EpisodicMemory
from backend.memory.procedural import ProceduralMemory

# Specialists
from backend.agents.specialists.strategist import StrategistAgent
from backend.agents.specialists.brand_kit import BrandKitAgent
from backend.agents.specialists.icp_architect import ICPArchitectAgent
from backend.agents.specialists.competitor_intelligence import CompetitorIntelligenceAgent
from backend.agents.specialists.value_proposition import ValuePropositionAgent
from backend.agents.specialists.messaging_matrix import MessagingMatrixAgent
from backend.agents.specialists.swot_analyst import SWOTAnalystAgent

logger = logging.getLogger("raptorflow.graphs.spine_v3")

async def initialize_spine(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Initializes the cognitive spine state."""
    logger.info(f"Initializing spine for tenant: {state.get('tenant_id')}")
    updates = {"status": state.get("status") or CognitiveStatus.PLANNING}
    if not state.get("messages"):
        updates["messages"] = [AgentMessage(role="system", content="Cognitive Spine Initialized.")]
    return updates

def spine_router(state: CognitiveIntelligenceState) -> List[str]:
    """Dynamic routing for industrial orchestration."""
    if state.get("error"): return ["error"]
    
    status_map = {
        CognitiveStatus.PLANNING: ["brand_foundation"],
        CognitiveStatus.RESEARCHING: ["icp_architect", "competitor_intel"],
        CognitiveStatus.EXECUTING: ["execute"],
        CognitiveStatus.AUDITING: ["audit"],
        CognitiveStatus.COMPLETE: ["finalize"]
    }
    return status_map.get(state["status"], ["finalize"])

async def brand_foundation_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Phase 41/42: Brand Kit & Positioning."""
    logger.info("Spine: Executing Brand Foundation")
    bk_agent = BrandKitAgent()
    strat_agent = StrategistAgent()
    
    bk_res = await bk_agent(state)
    strat_res = await strat_agent(state)
    
    combined_messages = bk_res["messages"] + strat_res["messages"]
    return {
        "status": CognitiveStatus.RESEARCHING,
        "messages": combined_messages + [AgentMessage(role="system", content="Foundation set. Moving to Cohorts/Intel.")],
        "brief": {**bk_res.get("output", {}), **strat_res.get("output", {})}
    }

async def icp_architect_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Phase 43/44: ICP Intelligence."""
    agent = ICPArchitectAgent()
    return await agent(state)

async def competitor_intel_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Phase 45: Competitor Mapping."""
    agent = CompetitorIntelligenceAgent()
    return await agent(state)

async def research_aggregator(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Sync point for parallel research."""
    return {
        "status": CognitiveStatus.EXECUTING,
        "messages": [AgentMessage(role="system", content="Research phase complete. Transitioning to strategic mapping.")]
    }

async def execute_strategy_mapping(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    """Phase 46/47/48: Value Prop, Matrix, SWOT."""
    vp_agent = ValuePropositionAgent()
    mm_agent = MessagingMatrixAgent()
    swot_agent = SWOTAnalystAgent()
    
    vp_res = await vp_agent(state)
    mm_res = await mm_agent(state)
    swot_res = await swot_agent(state)
    
    return {
        "messages": vp_res["messages"] + mm_res["messages"] + swot_res["messages"],
        "status": CognitiveStatus.AUDITING
    }

async def placeholder_execute(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    # Phase 6 will replace this
    return await execute_strategy_mapping(state)

async def human_audit_node(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {"status": CognitiveStatus.COMPLETE, "messages": [AgentMessage(role="human", content="Audit complete.")]}

async def finalize_spine(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {"status": CognitiveStatus.COMPLETE, "messages": [AgentMessage(role="system", content="Cognitive Spine Execution Complete.")]}

async def handle_spine_error(state: CognitiveIntelligenceState) -> Dict[str, Any]:
    return {"status": CognitiveStatus.ERROR, "messages": [AgentMessage(role="system", content="CRITICAL ERROR in Spine.")]}

# Graph Assembly
workflow = StateGraph(CognitiveIntelligenceState)

workflow.add_node("init", initialize_spine)
workflow.add_node("brand_foundation", brand_foundation_node)
workflow.add_node("icp_architect", icp_architect_node)
workflow.add_node("competitor_intel", competitor_intel_node)
workflow.add_node("aggregate", research_aggregator)
workflow.add_node("execute", placeholder_execute)
workflow.add_node("audit", human_audit_node)
workflow.add_node("finalize", finalize_spine)
workflow.add_node("error", handle_spine_error)

workflow.add_edge(START, "init")
workflow.add_conditional_edges("init", spine_router, {
    "brand_foundation": "brand_foundation",
    "icp_architect": "icp_architect",
    "competitor_intel": "competitor_intel",
    "execute": "execute",
    "audit": "audit",
    "finalize": "finalize",
    "error": "error"
})

workflow.add_edge("brand_foundation", "init")
workflow.add_edge("icp_architect", "aggregate")
workflow.add_edge("competitor_intel", "aggregate")
workflow.add_edge("aggregate", "init")
workflow.add_edge("execute", "init")
workflow.add_edge("audit", "finalize")
workflow.add_edge("finalize", END)
workflow.add_edge("error", END)

from langgraph.checkpoint.memory import MemorySaver
from backend.db import SupabaseSaver, get_pool

def get_checkpointer():
    db_url = os.getenv("DATABASE_URL")
    if db_url and "supabase" in db_url: return SupabaseSaver(get_pool())
    return MemorySaver()

cognitive_spine_v3 = workflow.compile(checkpointer=get_checkpointer(), interrupt_before=["audit"])