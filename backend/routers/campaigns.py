from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from backend.core.request_context import RequestContext, get_request_context
from backend.services.supabase_client import supabase_client
from backend.models.campaign import (
    Campaign, CampaignCreate, CampaignUpdate,
    CampaignChannel, CampaignCohortTarget,
    MovePlanSkeleton, MoveType
)
import structlog

router = APIRouter(prefix="/api/v1/campaigns", tags=["campaigns"])
logger = structlog.get_logger(__name__)

# --- Campaign CRUD ---

@router.get("", response_model=List[Campaign])
async def list_campaigns(
    ctx: RequestContext = Depends(get_request_context)
):
    """List all campaigns for the workspace."""
    campaigns = await supabase_client.fetch_all(
        "campaigns",
        {"workspace_id": str(ctx.workspace_id)}
    )
    return campaigns

@router.post("", response_model=Campaign)
async def create_campaign(
    campaign: CampaignCreate,
    ctx: RequestContext = Depends(get_request_context)
):
    """Create a new campaign with optional initial cohorts and channels."""
    
    # 1. Create Campaign
    campaign_data = campaign.dict(exclude={"cohorts", "channels"})
    campaign_data["workspace_id"] = str(ctx.workspace_id)
    campaign_data["status"] = "planning"
    
    created_campaign = await supabase_client.insert("campaigns", campaign_data)
    campaign_id = created_campaign["id"]
    
    # 2. Add Cohorts
    if campaign.cohorts:
        for cohort in campaign.cohorts:
            await supabase_client.insert("campaign_cohorts", {
                "workspace_id": str(ctx.workspace_id),
                "campaign_id": campaign_id,
                "cohort_id": str(cohort.cohort_id),
                "journey_stage_target": cohort.journey_stage_target,
                "priority": cohort.priority
            })
            
    # 3. Add Channels
    if campaign.channels:
        for channel in campaign.channels:
            await supabase_client.insert("campaign_channels", {
                "workspace_id": str(ctx.workspace_id),
                "campaign_id": campaign_id,
                "channel": channel.channel,
                "role": channel.role,
                "budget_allocation": channel.budget_allocation
            })
            
    return created_campaign

@router.get("/{campaign_id}", response_model=Campaign)
async def get_campaign(
    campaign_id: UUID,
    ctx: RequestContext = Depends(get_request_context)
):
    """Get campaign details including cohorts and channels."""
    campaign = await supabase_client.fetch_one(
        "campaigns",
        {"id": str(campaign_id), "workspace_id": str(ctx.workspace_id)}
    )
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    # Fetch related data
    cohorts_data = await supabase_client.fetch_all(
        "campaign_cohorts",
        {"campaign_id": str(campaign_id)}
    )
    channels_data = await supabase_client.fetch_all(
        "campaign_channels",
        {"campaign_id": str(campaign_id)}
    )
    
    campaign["cohorts"] = cohorts_data
    campaign["channels"] = channels_data
    
    return campaign

@router.patch("/{campaign_id}", response_model=Campaign)
async def update_campaign(
    campaign_id: UUID,
    update: CampaignUpdate,
    ctx: RequestContext = Depends(get_request_context)
):
    """Update campaign details."""
    update_data = update.dict(exclude_unset=True)
    updated = await supabase_client.update(
        "campaigns",
        {"id": str(campaign_id), "workspace_id": str(ctx.workspace_id)},
        update_data
    )
    return updated

# --- Auto-Planning ---

@router.post("/{campaign_id}/autoplan-moves", response_model=List[MovePlanSkeleton])
async def autoplan_moves(
    campaign_id: UUID,
    ctx: RequestContext = Depends(get_request_context)
):
    """
    Trigger the CampaignPlanner agent to generate a move sequence.
    Currently returns a mock plan for immediate UI integration.
    """
    logger.info("Auto-planning moves", campaign_id=str(campaign_id))
    
    # Fetch campaign context
    campaign = await get_campaign(campaign_id, ctx)
    
    # In a real implementation, we would call CampaignPlannerGraph here.
    # For now, we implement the "Auto-suggest Moves" logic deterministically 
    # based on the prompt's example.
    
    objective_type = campaign.get("objective_type", "conversion")
    
    plan = []
    
    # Example Logic: Authority -> Consideration -> Objection -> Conversion
    
    # Move 1: Authority
    plan.append(MovePlanSkeleton(
        name="Authority Sprint",
        move_type=MoveType.AUTHORITY,
        journey_stage_from="problem_aware",
        journey_stage_to="solution_aware",
        cohort_id=None, # Applies to all targeted cohorts
        channels=["linkedin", "email"],
        duration_weeks=2,
        focus_message="Chaos to Clarity"
    ))
    
    # Move 2: Consideration
    plan.append(MovePlanSkeleton(
        name="Consideration Sprint",
        move_type=MoveType.CONSIDERATION,
        journey_stage_from="solution_aware",
        journey_stage_to="product_aware",
        cohort_id=None,
        channels=["email", "retargeting"],
        duration_weeks=2,
        focus_message="Proof It Works"
    ))
    
    # Move 3: Objection
    plan.append(MovePlanSkeleton(
        name="Objection Crusher",
        move_type=MoveType.OBJECTION,
        journey_stage_from="product_aware",
        journey_stage_to="most_aware",
        cohort_id=None,
        channels=["email", "dm"],
        duration_weeks=2,
        focus_message="Risk Reversal"
    ))
    
    # Move 4: Conversion
    if objective_type == "conversion":
        plan.append(MovePlanSkeleton(
            name="Conversion Push",
            move_type=MoveType.CONVERSION,
            journey_stage_from="most_aware",
            journey_stage_to="customer",
            cohort_id=None,
            channels=["email", "sales"],
            duration_weeks=2,
            focus_message="Urgency & Offer"
        ))
        
    return plan
