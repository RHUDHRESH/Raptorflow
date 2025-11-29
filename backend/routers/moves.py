from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from backend.core.request_context import RequestContext, get_request_context
from backend.services.supabase_client import supabase_client
from backend.models.campaign import (
    Move, MoveCreate, MoveUpdate, MoveType,
    Asset, AssetCreate, AssetStatus,
    PreflightResult, PreflightIssue
)
import structlog

router = APIRouter(prefix="/api/v1/moves", tags=["moves"])
logger = structlog.get_logger(__name__)

# --- Move CRUD ---

@router.get("/{move_id}", response_model=Move)
async def get_move(
    move_id: UUID,
    ctx: RequestContext = Depends(get_request_context)
):
    """Get move details."""
    move = await supabase_client.fetch_one(
        "moves",
        {"id": str(move_id), "workspace_id": str(ctx.workspace_id)}
    )
    if not move:
        raise HTTPException(status_code=404, detail="Move not found")
    return move

@router.post("", response_model=Move)
async def create_move(
    move: MoveCreate,
    ctx: RequestContext = Depends(get_request_context)
):
    """Create a new move."""
    move_data = move.dict()
    move_data["workspace_id"] = str(ctx.workspace_id)
    move_data["status"] = "planned"
    
    # Convert UUIDs to strings
    if move_data.get("cohort_id"):
        move_data["cohort_id"] = str(move_data["cohort_id"])
    if move_data.get("campaign_id"):
        move_data["campaign_id"] = str(move_data["campaign_id"])
    if move_data.get("message_variant_id"):
        move_data["message_variant_id"] = str(move_data["message_variant_id"])
    
    created_move = await supabase_client.insert("moves", move_data)
    return created_move

@router.patch("/{move_id}", response_model=Move)
async def update_move(
    move_id: UUID,
    update: MoveUpdate,
    ctx: RequestContext = Depends(get_request_context)
):
    """Update move details."""
    update_data = update.dict(exclude_unset=True)
    updated = await supabase_client.update(
        "moves",
        {"id": str(move_id), "workspace_id": str(ctx.workspace_id)},
        update_data
    )
    return updated

# --- Preflight ---

@router.post("/{move_id}/preflight", response_model=PreflightResult)
async def run_preflight_check(
    move_id: UUID,
    ctx: RequestContext = Depends(get_request_context)
):
    """Run pre-flight checks for the move."""
    move = await get_move(move_id, ctx)
    
    # Mock Preflight Logic based on Move Type
    issues = []
    status = "pass"
    
    # Example Logic
    if move.get("move_type") == MoveType.CONVERSION:
        # Simulate missing landing page or offer
        # In real app, we'd check 'assets' table
        assets = await supabase_client.fetch_all("assets", {"move_id": str(move_id)})
        landing_pages = [a for a in assets if a["format"] == "landing_page"]
        
        if not landing_pages:
            issues.append(PreflightIssue(
                code="NO_LANDING_PAGE",
                message="Conversion move requires a landing page destination.",
                severity="warn",
                recommendation="Generate a landing page asset."
            ))
            status = "warn"
            
    if not move.get("cohort_id"):
         issues.append(PreflightIssue(
            code="NO_COHORT",
            message="No target cohort defined.",
            severity="fail",
            recommendation="Select a cohort in Move settings."
        ))
         status = "fail"

    return PreflightResult(status=status, issues=issues)

# --- Assets & Briefs ---

@router.get("/{move_id}/assets", response_model=List[Asset])
async def list_move_assets(
    move_id: UUID,
    ctx: RequestContext = Depends(get_request_context)
):
    """List all assets for a move."""
    assets = await supabase_client.fetch_all(
        "assets",
        {"move_id": str(move_id), "workspace_id": str(ctx.workspace_id)}
    )
    return assets

@router.post("/{move_id}/generate-briefs", response_model=List[Asset])
async def generate_briefs(
    move_id: UUID,
    ctx: RequestContext = Depends(get_request_context)
):
    """
    Trigger BriefFactory agent to generate asset placeholders and creative briefs.
    """
    move = await get_move(move_id, ctx)
    move_type = move.get("move_type")
    
    # Mock Logic: Determine required assets based on move type
    required_assets = []
    
    if move_type == MoveType.AUTHORITY:
        required_assets = [
            {"format": "post", "channel": "linkedin", "name": "Authority Post 1"},
            {"format": "post", "channel": "linkedin", "name": "Authority Post 2"},
            {"format": "email", "channel": "email", "name": "Value Add Email"}
        ]
    elif move_type == MoveType.CONSIDERATION:
        required_assets = [
             {"format": "email", "channel": "email", "name": "Case Study Email"},
             {"format": "post", "channel": "linkedin", "name": "Social Proof Carousel"}
        ]
    elif move_type == MoveType.OBJECTION:
        required_assets = [
             {"format": "email", "channel": "email", "name": "Myth Buster Email"},
             {"format": "post", "channel": "linkedin", "name": "FAQ Post"}
        ]
    elif move_type == MoveType.CONVERSION:
        required_assets = [
             {"format": "email", "channel": "email", "name": "Offer Email"},
             {"format": "landing_page", "channel": "web", "name": "Campaign LP"}
        ]
    
    created_assets = []
    for asset_def in required_assets:
        asset_data = {
            "workspace_id": str(ctx.workspace_id),
            "move_id": str(move_id),
            "name": asset_def["name"],
            "format": asset_def["format"],
            "channel": asset_def["channel"],
            "status": AssetStatus.DRAFT,
            "creative_brief": {
                "single_minded_proposition": f"Generated SMP for {asset_def['name']}",
                "tone": "Professional yet bold"
            }
        }
        # check if already exists to avoid dupes in this mock
        # In real app, we'd be smarter
        existing = await supabase_client.fetch_all("assets", {
            "move_id": str(move_id), 
            "name": asset_def["name"]
        })
        if not existing:
            new_asset = await supabase_client.insert("assets", asset_data)
            created_assets.append(new_asset)
        else:
            created_assets.append(existing[0])
            
    return created_assets
