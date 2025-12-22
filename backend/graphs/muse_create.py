from agents.shared.agents import IntentRouter, QualityGate, Intent
from agents.shared.memory_updater import MemoryUpdaterAgent
from agents.shared.context_assembler import ContextAssemblerAgent
from skills.executor import SkillExecutor
from core.toolbelt import Toolbelt

async def context_node(state: MuseState):
    """T01/T02/A03: Pulls full context including learned memories."""
    assembler = ContextAssemblerAgent()
    ctx = await assembler.assemble(state["workspace_id"], state["user_id"], state["prompt"])
    return {"context": ctx, "status": "drafting"}

async def memory_update_node(state: MuseState):
    """A06: Learns from the final result vs initial draft."""
    updater = MemoryUpdaterAgent()
    rule = await updater.extract_preference(state["drafts"][0], state["current_draft"])
    if rule and rule.confidence > 0.8:
        belt = Toolbelt(os.getenv("DATABASE_URL"))
        # Save rule to memories table
        pass 
    return {"status": "memory_updated"}

def build_muse_spine():
    workflow = StateGraph(MuseState)
    
    workflow.add_node("router", router_node)
    workflow.add_node("context", context_node)
    workflow.add_node("drafter", drafting_node)
    workflow.add_node("critic", reflection_node)
    workflow.add_node("refiner", refinement_node)
    workflow.add_node("finalizer", finalize_node)
    workflow.add_node("memory_update", memory_update_node)
    
    workflow.add_edge(START, "router")
    workflow.add_edge("router", "context")
    workflow.add_edge("context", "drafter")
    workflow.add_edge("drafter", "critic")
    
    workflow.add_conditional_edges(
        "critic",
        decide_refinement,
        {
            "refine": "refiner",
            "finalize": "finalizer"
        }
    )
    
    workflow.add_edge("refiner", "critic")
    workflow.add_edge("finalizer", "memory_update") # Run memory update after finalization
    workflow.add_edge("memory_update", END)
    
    return workflow.compile()