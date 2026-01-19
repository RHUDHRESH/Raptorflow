"""
Onboarding v2 API Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import uuid

# Local imports
from ...infrastructure.storage import upload_file, FileCategory
from ...agents.graphs.onboarding_v2 import OnboardingGraphV2, OnboardingStateV2
from ...utils.ucid import UCIDGenerator

router = APIRouter(prefix="/onboarding/v2", tags=["onboarding-v2"])

class StartSessionRequest(BaseModel):
    workspace_id: str
    user_id: str

class VaultSubmissionResponse(BaseModel):
    ucid: str
    session_id: str
    progress: float
    next_step: str

@router.post("/start", response_model=VaultSubmissionResponse)
async def start_onboarding_v2(request: StartSessionRequest):
    """Initialize a new 23-step onboarding session."""
    ucid = UCIDGenerator.generate()
    session_id = str(uuid.uuid4())
    
    # In a real app, we would store this in Supabase/Postgres
    return {
        "ucid": ucid,
        "session_id": session_id,
        "progress": 0.0,
        "next_step": "evidence_vault"
    }

@router.post("/{session_id}/vault", response_model=VaultSubmissionResponse)
async def submit_vault_evidence(
    session_id: str,
    workspace_id: str,
    user_id: str,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """Step 1: Submit evidence to the vault."""
    evidence = []
    
    for file in files:
        content = await file.read()
        result = await upload_file(
            content=content,
            filename=file.filename,
            workspace_id=workspace_id,
            user_id=user_id,
            category=FileCategory.UPLOADS
        )
        
        if result.success:
            evidence.append({
                "file_id": result.file_id,
                "filename": file.filename,
                "content_type": file.content_type,
                "size": result.size_bytes
            })
            
    # Trigger Graph processing
    # graph = OnboardingGraphV2().create_graph()
    # config = {"configurable": {"thread_id": session_id}}
    # background_tasks.add_task(graph.ainvoke, {"evidence": evidence, "ucid": "PENDING"}, config)

    return {
        "ucid": "RF-2026-PENDING",
        "session_id": session_id,
        "progress": 4.34,
        "next_step": "auto_extraction"
    }

@router.post("/{session_id}/offer-pricing", response_model=Dict[str, Any])
async def analyze_offer_pricing(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 6: Architect revenue model and pricing logic."""
    # In a real scenario, we would load the state from Supabase checkpointer
    # For now, we mock the graph execution for this specific step
    from ...agents.graphs.onboarding_v2 import OnboardingGraphV2
    
    # Mocking graph invoke for Step 6
    # This would normally be handled by a more generic 'next_step' trigger
    return {
        "success": True,
        "analysis": {
            "revenue_model": "Subscription",
            "pricing_logic": "Value-based",
            "risk_reversal": {
                "score": 0.85,
                "feedback": "Highly effective guarantee detected."
            }
        },
        "next_step": "market_intelligence"
    }
