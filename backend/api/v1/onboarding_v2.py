"""
Onboarding v2 API Endpoints.
All results are dynamically generated via LangGraph specialist agents.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid
import logging

# Local imports
from ...infrastructure.storage import upload_file, FileCategory
from backend.agents.graphs.onboarding_v2 import OnboardingGraphV2, OnboardingStateV2
from ...utils.ucid import UCIDGenerator

router = APIRouter(prefix="/onboarding/v2", tags=["onboarding-v2"])
logger = logging.getLogger(__name__)

# Global graph instance (using MemorySaver for now as per v2 spec)
onboarding_graph = OnboardingGraphV2().create_graph()

class StartSessionRequest(BaseModel):
    workspace_id: str
    user_id: str

class OnboardingResponse(BaseModel):
    success: bool
    ucid: str
    session_id: str
    progress: float
    data: Dict[str, Any]
    next_step: str

async def run_onboarding_step(session_id: str, step_name: str, input_updates: Dict[str, Any] = None) -> Dict[str, Any]:
    """Helper to run a specific graph node and return the updated state."""
    config = {"configurable": {"thread_id": session_id}}
    
    # In a real scenario, we'd pull the existing state from the checkpointer
    # For this implementation, we invoke with the updates
    state_update = input_updates or {}
    state_update["current_step"] = step_name
    
    # We use ainvoke to trigger the graph. 
    # The graph nodes themselves use the specialist agents.
    final_state = await onboarding_graph.ainvoke(state_update, config)
    return final_state

@router.post("/start", response_model=Dict[str, Any])
async def start_onboarding_v2(request: StartSessionRequest):
    """Initialize a new 23-step onboarding session."""
    ucid = UCIDGenerator.generate()
    session_id = str(uuid.uuid4())
    
    return {
        "success": True,
        "ucid": ucid,
        "session_id": session_id,
        "progress": 0.0,
        "next_step": "evidence_vault"
    }

@router.post("/{session_id}/vault", response_model=Dict[str, Any])
async def submit_vault_evidence(
    session_id: str,
    workspace_id: str,
    user_id: str,
    files: List[UploadFile] = File(...)
):
    """Step 1: Submit evidence and auto-classify via EvidenceClassifier."""
    evidence = []
    for file in files:
        content = await file.read()
        result = await upload_file(content=content, filename=file.filename, workspace_id=workspace_id, user_id=user_id, category=FileCategory.UPLOADS)
        if result.success:
            evidence.append({"file_id": result.file_id, "filename": file.filename, "content_type": file.content_type})
            
    final_state = await run_onboarding_step(session_id, "evidence_vault", {"evidence": evidence})
    
    return {
        "success": True,
        "ucid": final_state.get("ucid", "PENDING"),
        "progress": final_state.get("onboarding_progress", 4.34),
        "data": final_state.get("step_data", {}).get("evidence_vault", {}),
        "next_step": "auto_extraction"
    }

@router.post("/{session_id}/extract", response_model=Dict[str, Any])
async def trigger_extraction(session_id: str):
    """Step 2: Deep fact extraction via ExtractionOrchestrator."""
    final_state = await run_onboarding_step(session_id, "auto_extraction")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("auto_extraction", {}),
        "next_step": "contradiction_check"
    }

@router.post("/{session_id}/offer-pricing", response_model=Dict[str, Any])
async def analyze_offer_pricing(session_id: str):
    """Step 6: Architect revenue model via OfferArchitect."""
    final_state = await run_onboarding_step(session_id, "offer_pricing")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("offer_pricing", {}),
        "next_step": "market_intelligence"
    }

@router.post("/{session_id}/market-intelligence", response_model=Dict[str, Any])
async def research_market_intelligence(session_id: str):
    """Step 7: Autonomous research via RedditScraper & InsightExtractor."""
    final_state = await run_onboarding_step(session_id, "market_intelligence")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("market_intelligence", {}),
        "next_step": "comparative_angle"
    }

@router.post("/{session_id}/comparative-angle", response_model=Dict[str, Any])
async def analyze_comparative_angle(session_id: str):
    """Step 8: Define vantage point via ComparativeAngleGenerator."""
    final_state = await run_onboarding_step(session_id, "comparative_angle")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("comparative_angle", {}),
        "next_step": "category_paths"
    }

@router.post("/{session_id}/category-paths", response_model=Dict[str, Any])
async def recommend_category_paths(session_id: str):
    """Step 9: Safe/Clever/Bold paths via CategoryAdvisor."""
    final_state = await run_onboarding_step(session_id, "category_paths")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("category_paths", {}),
        "next_step": "capability_rating"
    }

@router.post("/{session_id}/capability-rating", response_model=Dict[str, Any])
async def rate_capabilities(session_id: str):
    """Step 10: 4-tier audit via CapabilityRatingEngine."""
    final_state = await run_onboarding_step(session_id, "capability_rating")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("capability_rating", {}),
        "next_step": "perceptual_map"
    }

@router.post("/{session_id}/perceptual-map", response_model=Dict[str, Any])
async def generate_perceptual_map(session_id: str):
    """Step 11: Competitive mapping via PerceptualMapGenerator."""
    final_state = await run_onboarding_step(session_id, "perceptual_map")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("perceptual_map", {}),
        "next_step": "strategic_grid"
    }

@router.post("/{session_id}/strategic-grid", response_model=Dict[str, Any])
async def lock_strategic_position(session_id: str):
    """Step 12: Position lock & milestones via StrategicGridOrchestrator."""
    final_state = await run_onboarding_step(session_id, "strategic_grid")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("strategic_grid", {}),
        "next_step": "positioning_statements"
    }

@router.post("/{session_id}/positioning-statements", response_model=Dict[str, Any])
async def draft_positioning_statements(session_id: str):
    """Step 13: Brand manifesto via NeuroscienceCopywriter."""
    final_state = await run_onboarding_step(session_id, "positioning_statements")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("positioning_statements", {}),
        "next_step": "focus_sacrifice"
    }

@router.post("/{session_id}/focus-sacrifice", response_model=Dict[str, Any])
async def recommend_focus_sacrifice(session_id: str):
    """Step 14: Tradeoffs via ConstraintEngine."""
    final_state = await run_onboarding_step(session_id, "focus_sacrifice")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("focus_sacrifice", {}),
        "next_step": "icp_profiles"
    }

@router.post("/{session_id}/icp-profiles", response_model=Dict[str, Any])
async def generate_icp_profiles(session_id: str):
    """Step 15: Deep ICP profiling via ICPArchitect."""
    final_state = await run_onboarding_step(session_id, "icp_profiles")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("icp_profiles", {}),
        "next_step": "buying_process"
    }

@router.post("/{session_id}/buying-process", response_model=Dict[str, Any])
async def architect_buying_process(session_id: str):
    """Step 16: Buyer journey via BuyingProcessArchitect."""
    final_state = await run_onboarding_step(session_id, "buying_process")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("buying_process", {}),
        "next_step": "messaging_guardrails"
    }

@router.post("/{session_id}/messaging-guardrails", response_model=Dict[str, Any])
async def define_messaging_guardrails(session_id: str):
    """Step 17: Brand rules via MessagingRulesEngine."""
    final_state = await run_onboarding_step(session_id, "messaging_guardrails")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("messaging_guardrails", {}),
        "next_step": "soundbites_library"
    }

@router.post("/{session_id}/soundbites", response_model=Dict[str, Any])
async def generate_soundbites(session_id: str):
    """Step 18: Atomic copy via SoundbitesGenerator."""
    final_state = await run_onboarding_step(session_id, "soundbites_library")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("soundbites_library", {}),
        "next_step": "message_hierarchy"
    }

@router.post("/{session_id}/message-hierarchy", response_model=Dict[str, Any])
async def architect_message_hierarchy(session_id: str):
    """Step 19: Structural cascade via MessageHierarchyArchitect."""
    final_state = await run_onboarding_step(session_id, "message_hierarchy")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("message_hierarchy", {}),
        "next_step": "channel_mapping"
    }

@router.post("/{session_id}/channel-mapping", response_model=Dict[str, Any])
async def map_acquisition_channels(session_id: str):
    """Step 20: Media mix via ChannelRecommender."""
    final_state = await run_onboarding_step(session_id, "channel_mapping")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("channel_mapping", {}),
        "next_step": "tam_sam_som"
    }

@router.post("/{session_id}/tam-sam-som", response_model=Dict[str, Any])
async def calculate_market_size(session_id: str):
    """Step 21: Financial modeling via MarketSizer."""
    final_state = await run_onboarding_step(session_id, "tam_sam_som")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("tam_sam_som", {}),
        "next_step": "validation_todos"
    }

@router.post("/{session_id}/reality-check", response_model=Dict[str, Any])
async def perform_reality_check(session_id: str):
    """Step 22: Readiness audit via ValidationTracker."""
    final_state = await run_onboarding_step(session_id, "validation_todos")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("validation_todos", {}),
        "next_step": "final_synthesis"
    }

@router.post("/{session_id}/final-synthesis", response_model=Dict[str, Any])
async def finalize_onboarding(session_id: str):
    """Step 23: Production handover via FinalSynthesis."""
    final_state = await run_onboarding_step(session_id, "final_synthesis")
    return {
        "success": True,
        "data": final_state.get("step_data", {}).get("final_synthesis", {}),
        "handover_status": "Systems Online"
    }