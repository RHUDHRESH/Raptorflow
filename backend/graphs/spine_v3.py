from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, START, END
from backend.agents.supervisor import create_team_supervisor
from backend.agents.planner import create_task_decomposer
from backend.agents.classifier import create_intent_classifier, create_ambiguity_resolver
from backend.agents.researchers import (
    create_reddit_analyst, create_linkedin_profiler, 
    create_competitor_tracker, create_trend_extractor,
    create_gap_finder, create_research_summarizer
)
from backend.agents.strategists import (
    create_icp_demographer, create_icp_psychographer,
    create_uvp_architect, create_brand_voice_aligner,
    create_campaign_designer, create_move_sequencer,
    create_founder_profiler
)
from backend.agents.creatives import (
    create_linkedin_architect, create_twitter_architect,
    create_tone_adjuster, create_formatting_filter
)
from backend.agents.quality import create_brand_guardian, create_quality_gate
from backend.inference import InferenceProvider
from backend.core.middleware import JSONRepair, SafetyFilter
import logging

logger = logging.getLogger("raptorflow.spine.v3")

# --- SOTA Production Tiering ---
def get_tiered_models():
    return {
        "intake": InferenceProvider.get_model(model_tier="kinda_mundane"), # 2.0 Flash
        "reasoning": InferenceProvider.get_model(model_tier="reasoning"), # 3 Flash
        "ultra": InferenceProvider.get_model(model_tier="ultra"),         # 3 Pro
        "driver": InferenceProvider.get_model(model_tier="driver"),       # 2.5 Flash
        "mundane": InferenceProvider.get_model(model_tier="mundane")      # 1.5 Flash
    }

# --- Node Implementation (Real SOTA Integration) ---

async def discovery_node(state: UltimateSpineState):
    """Surgical Intake using Gemini 2.0 Flash."""
    models = get_tiered_models()
    classifier = create_intent_classifier(models["intake"])
    return await classifier(state)

async def research_web_node(state: UltimateSpineState):
    """Deep Web Research using Gemini 3 Flash."""
    models = get_tiered_models()
    summarizer = create_research_summarizer(models["reasoning"])
    return await summarizer(state)

async def research_social_node(state: UltimateSpineState):
    """Social Listening using Reddit/LinkedIn specialized logic."""
    models = get_tiered_models()
    analyst = create_reddit_analyst(models["reasoning"])
    return await analyst(state)

async def strategy_node(state: UltimateSpineState):
    """Positioning & UVP Architecture using Gemini 3 Pro (Ultra)."""
    models = get_tiered_models()
    icp_gen = create_icp_demographer(models["ultra"])
    uvp_arch = create_uvp_architect(models["ultra"])
    
    # Execute strategy steps
    icp_res = await icp_gen(state)
    # Update state internally for UVP gen
    state.update(icp_res)
    uvp_res = await uvp_arch(state)
    
    return {**icp_res, **uvp_res, "status": "strategic_alignment"}

async def creative_node(state: UltimateSpineState):
    """Creative Production using Gemini 2.5 Flash (Driver)."""
    models = get_tiered_models()
    copy_gen = create_linkedin_architect(models["driver"])
    return await copy_gen(state)

async def surgical_editor_node(state: UltimateSpineState):
    """QA & Formatting using Gemini 1.5 Flash (Mundane)."""
    models = get_tiered_models()
    lint = create_formatting_filter(models["mundane"])
    return await lint(state)

# --- Final SOTA Assembly ---

def build_ultimate_spine():
    workflow = StateGraph(UltimateSpineState)
    
    # Adding nodes
    workflow.add_node("discover", discovery_node)
    workflow.add_node("research_web", research_web_node)
    workflow.add_node("research_social", research_social_node)
    workflow.add_node("strategy", strategy_node)
    workflow.add_node("creative", creative_node)
    workflow.add_node("qa", surgical_editor_node)
    
    # 1. Start -> Discover
    workflow.add_edge(START, "discover")
    
    # 2. Discover -> Parallel Research (SOTA)
    workflow.add_edge("discover", "research_web")
    workflow.add_edge("discover", "research_social")
    
    # 3. Research -> Strategy (Fan-in)
    workflow.add_edge("research_web", "strategy")
    workflow.add_edge("research_social", "strategy")
    
    # 4. Strategy -> Creative
    workflow.add_edge("strategy", "creative")
    
    # 5. Creative -> QA
    workflow.add_edge("creative", "qa")
    workflow.add_edge("qa", END)
    
    # Compile with persistence
    from backend.db import init_checkpointer
    # Since compile is sync but init_checkpointer is async, we'd handle this in main.py
    # For now, we use a placeholder or the MemorySaver for the shell
    from langgraph.checkpoint.memory import MemorySaver
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)
