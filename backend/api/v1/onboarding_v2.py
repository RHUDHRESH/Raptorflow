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

@router.post("/{session_id}/market-intelligence", response_model=Dict[str, Any])
async def research_market_intelligence(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 7: Autonomous research via Reddit."""
    return {
        "success": True,
        "dossier": {
            "pain_points": [
                {"category": "Pricing", "description": "Current tools are too expensive for small teams."}
            ],
            "discovered_competitors": ["Hubspot", "Salesforce"],
            "sentiment_score": -0.45
        },
        "next_step": "comparative_angle"
    }

@router.post("/{session_id}/comparative-angle", response_model=Dict[str, Any])
async def analyze_comparative_angle(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 8: Define competitive vantage point and leverage."""
    return {
        "success": True,
        "positioning": {
            "vantage_point": "Surgical Simplicity",
            "leverage": "AI-first native UX",
            "differentiation_score": 88.5
        },
        "next_step": "category_paths"
    }

@router.post("/{session_id}/category-paths", response_model=Dict[str, Any])
async def recommend_category_paths(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 9: Recommend Safe/Clever/Bold category paths."""
    return {
        "success": True,
        "paths": {
            "safe": {"category": "Marketing Automation", "effort": "Low"},
            "clever": {"category": "Autonomous Growth Engine", "effort": "Medium"},
            "bold": {"category": "Founder OS", "effort": "High"},
            "recommended": "clever"
        },
        "next_step": "capability_rating"
    }

@router.post("/{session_id}/capability-rating", response_model=Dict[str, Any])
async def rate_capabilities(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 10: Audit and rate unique capabilities."""
    return {
        "success": True,
        "ratings": [
            {"capability": "Agent Swarm", "tier": 4, "status": "Verified Unique"}
        ],
        "next_step": "perceptual_map"
    }

@router.post("/{session_id}/strategic-grid", response_model=Dict[str, Any])
async def lock_strategic_position(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 12: Lock strategic position and synthesize milestones."""
    return {
        "success": True,
        "lock": {
            "selected_position": "The Surgical Operator",
            "milestones": [
                {"name": "Swarm Core Alpha", "timeline": "Week 2"}
            ],
            "threats": [" incumbents adding shallow AI features"],
            "opportunities": ["First-mover advantage in specialized swarm logic"]
        },
        "next_step": "positioning_statements"
    }

@router.post("/{session_id}/positioning-statements", response_model=Dict[str, Any])
async def draft_positioning_statements(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 13: Draft brand manifesto and headlines using neuroscience."""
    return {
        "success": True,
        "copy": {
            "manifesto": "In a world of noise, we bring silence. Surgical. Precise. RaptorFlow.",
            "limbic_score": 0.95,
            "headlines": ["End Complexity.", "The Surgical Operator is here."]
        },
        "next_step": "focus_sacrifice"
    }

@router.post("/{session_id}/focus-sacrifice", response_model=Dict[str, Any])
async def recommend_focus_sacrifice(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 14: Strategic tradeoffs and 'Lightbulb' logic."""
    return {
        "success": True,
        "constraints": {
            "focus_areas": ["Founders"],
            "sacrifices": [
                {"target": "Enterprise", "rationale": "High friction", "lightbulb": "Speed is your edge."}
            ]
        },
        "next_step": "icp_profiles"
    }

@router.post("/{session_id}/icp-profiles", response_model=Dict[str, Any])
async def generate_icp_profiles(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 15: Deep ICP profiling and psychographic mapping."""
    return {
        "success": True,
        "profiles": [
            {
                "name": "The High-Growth Founder",
                "tagline": "Relentless growth at all costs",
                "who_they_want_to_become": "Market Leader",
                "sophistication_level": 4
            }
        ],
        "next_step": "buying_process"
    }

@router.post("/{session_id}/buying-process", response_model=Dict[str, Any])
async def architect_buying_process(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 16: Architect the buying journey and cognitive shifts."""
    return {
        "success": True,
        "journey": [
            {"stage": "Problem Aware", "shift": "I have a problem -> I need a surgical solution"},
            {"stage": "Solution Aware", "shift": "Looking for tools -> RaptorFlow is the specific tool"}
        ],
        "chasm_logic": "Leverage educational whitepapers to bridge the trust gap.",
        "next_step": "messaging_guardrails"
    }

@router.post("/{session_id}/perceptual-map", response_model=Dict[str, Any])
async def generate_perceptual_map(
    session_id: str,
    workspace_id: str,
    user_id: str
):
    """Step 11: Map competitors and identify 'Only You' quadrant."""
    return {
        "success": True,
        "map": {
            "primary_axis": {"name": "Simplicity", "low": "Complex", "high": "Surgical"},
            "secondary_axis": {"name": "Speed", "low": "Slow", "high": "Instant"},
            "competitors": [{"name": "Hubspot", "x": 0.2, "y": 0.5}],
            "only_you_quadrant": "Top Right (Surgical + Instant)"
        },
        "next_step": "strategic_grid"
    }
