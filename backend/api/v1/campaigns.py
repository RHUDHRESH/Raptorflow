"""
Campaigns API endpoints with AI processing
"""

from typing import Any, Dict, List, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.core.auth import get_auth_context, get_current_user, get_workspace_id
from backend.core.models import AuthContext, User
from backend.core.supabase_mgr import get_supabase_client
from backend.db.campaigns import CampaignRepository

# Import Vertex AI client for AI processing
try:
    from backend.services.vertex_ai_client import get_vertex_ai_client
    vertex_ai_client = get_vertex_ai_client()
except ImportError:
    logging.warning("Vertex AI client not available for campaigns")
    vertex_ai_client = None

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


# Pydantic models for request/response
class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    target_icps: Optional[List[str]] = []
    phases: Optional[List[Dict[str, Any]]] = []
    budget_usd: Optional[float] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_icps: Optional[List[str]] = None
    phases: Optional[List[Dict[str, Any]]] = None
    budget_usd: Optional[float] = None
    status: Optional[str] = None


@router.get("/")
async def list_campaigns(
    auth_context: AuthContext = Depends(get_auth_context),
    page: int = 0,
    page_size: int = 20,
    status: Optional[str] = None,
):
    """
    List all campaigns for the workspace
    """
    campaign_repo = CampaignRepository()

    if status:
        # Filter by status
        from db.pagination import Pagination

        pagination = Pagination(page=page, page_size=page_size)
        result = await campaign_repo.list_by_status(
            auth_context.workspace_id, status, pagination
        )
    else:
        # Get all campaigns
        from db.pagination import Pagination

        pagination = Pagination(page=page, page_size=page_size)
        result = await campaign_repo.get_by_workspace(
            auth_context.workspace_id, pagination
        )

    return {
        "campaigns": result.items,
        "pagination": {
            "page": result.page,
            "page_size": result.page_size,
            "total": result.total,
            "total_pages": result.total_pages,
        },
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Create a new campaign
    """
    supabase = get_supabase_client()

    # Validate target ICPs belong to workspace
    if campaign_data.target_icps:
        icp_result = (
            supabase.table("icp_profiles")
            .select("id")
            .eq("workspace_id", auth_context.workspace_id)
            .in_("id", campaign_data.target_icps)
            .execute()
        )

        if len(icp_result.data or []) != len(campaign_data.target_icps):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more target ICPs not found in workspace",
            )

    # Prepare campaign data
    campaign_insert = {
        "workspace_id": auth_context.workspace_id,
        "name": campaign_data.name,
        "description": campaign_data.description,
        "target_icps": campaign_data.target_icps or [],
        "phases": campaign_data.phases or [],
        "budget_usd": campaign_data.budget_usd,
        "status": "planning",
    }

    # Add AI-generated campaign strategy if Vertex AI is available
    if vertex_ai_client and campaign_data.description:
        try:
            # Get ICP data for context
            icp_context = ""
            if campaign_data.target_icps:
                icp_result = (
                    supabase.table("icp_profiles")
                    .select("name, description, psycholinguistics")
                    .eq("workspace_id", auth_context.workspace_id)
                    .in_("id", campaign_data.target_icps)
                    .execute()
                )
                
                if icp_result.data:
                    icp_context = "\nTarget ICPs:\n" + "\n".join([
                        f"- {icp.get('name', '')}: {icp.get('description', '')}"
                        for icp in icp_result.data[:3]  # Limit to 3 ICPs
                    ])

            # Generate AI campaign strategy
            ai_prompt = f"""
            You are an expert marketing strategist. Create a campaign strategy for:
            
            Campaign: {campaign_data.name}
            Description: {campaign_data.description}
            Budget: ${campaign_data.budget_usd or 'Not specified'}
            {icp_context}
            
            Provide:
            1. Key objectives (3-5)
            2. Target audience insights
            3. Recommended channels
            4. Success metrics
            5. Timeline suggestion
            
            Return as JSON with keys: objectives, audience_insights, channels, success_metrics, timeline
            """
            
            ai_response = await vertex_ai_client.generate_text(ai_prompt)
            
            if ai_response:
                import json
                try:
                    ai_strategy = json.loads(ai_response)
                    campaign_insert["ai_strategy"] = ai_strategy
                    campaign_insert["ai_generated_at"] = "now"
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    campaign_insert["ai_strategy"] = {"raw_response": ai_response[:500]}
                    campaign_insert["ai_generated_at"] = "now"
                    
        except Exception as e:
            logging.warning(f"AI strategy generation failed: {e}")

    # Create campaign
    result = supabase.table("campaigns").insert(campaign_insert).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign",
        )

    return result.data[0]


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Get a specific campaign with its moves
    """
    campaign_repo = CampaignRepository()

    campaign = await campaign_repo.get_with_moves(campaign_id)

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Verify workspace ownership
    if campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return campaign


@router.put("/{campaign_id}")
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    auth_context: AuthContext = Depends(get_auth_context),
):
    """
    Update a campaign
    """
    supabase = get_supabase_client()

    # Verify campaign exists and belongs to workspace
    campaign_result = (
        supabase.table("campaigns")
        .select("*")
        .eq("id", campaign_id)
        .eq("workspace_id", auth_context.workspace_id)
        .single()
        .execute()
    )

    if not campaign_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Validate target ICPs if provided
    if campaign_data.target_icps is not None:
        icp_result = (
            supabase.table("icp_profiles")
            .select("id")
            .eq("workspace_id", auth_context.workspace_id)
            .in_("id", campaign_data.target_icps)
            .execute()
        )

        if len(icp_result.data or []) != len(campaign_data.target_icps):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more target ICPs not found in workspace",
            )

    # Prepare update data
    update_data = {}
    if campaign_data.name is not None:
        update_data["name"] = campaign_data.name
    if campaign_data.description is not None:
        update_data["description"] = campaign_data.description
    if campaign_data.target_icps is not None:
        update_data["target_icps"] = campaign_data.target_icps
    if campaign_data.phases is not None:
        update_data["phases"] = campaign_data.phases
    if campaign_data.budget_usd is not None:
        update_data["budget_usd"] = campaign_data.budget_usd
    if campaign_data.status is not None:
        update_data["status"] = campaign_data.status

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    # Update campaign
    result = (
        supabase.table("campaigns").update(update_data).eq("id", campaign_id).execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update campaign",
        )

    return result.data[0]


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Delete a campaign
    """
    supabase = get_supabase_client()

    # Verify campaign exists and belongs to workspace
    campaign_result = (
        supabase.table("campaigns")
        .select("*")
        .eq("id", campaign_id)
        .eq("workspace_id", auth_context.workspace_id)
        .single()
        .execute()
    )

    if not campaign_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Delete campaign (cascade deletes should handle related moves)
    result = supabase.table("campaigns").delete().eq("id", campaign_id).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete campaign",
        )

    return {"message": "Campaign deleted successfully", "campaign_id": campaign_id}


@router.get("/{campaign_id}/moves")
async def get_campaign_moves(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Get all moves for a campaign
    """
    campaign_repo = CampaignRepository()

    campaign = await campaign_repo.get(campaign_id)

    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Verify workspace ownership
    if campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    campaign_with_moves = await campaign_repo.get_with_moves(campaign_id)

    return {
        "campaign_id": campaign_id,
        "moves": campaign_with_moves.get("moves", []),
        "total_moves": len(campaign_with_moves.get("moves", [])),
    }


@router.post("/{campaign_id}/add-move")
async def add_move_to_campaign(
    campaign_id: str,
    move_id: str,
    auth_context: AuthContext = Depends(get_auth_context),
):
    """
    Add a move to a campaign
    """
    campaign_repo = CampaignRepository()

    # Verify campaign exists and belongs to workspace
    campaign = await campaign_repo.get(campaign_id)

    if not campaign or campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Verify move exists and belongs to workspace
    supabase = get_supabase_client()
    move_result = (
        supabase.table("moves")
        .select("*")
        .eq("id", move_id)
        .eq("workspace_id", auth_context.workspace_id)
        .single()
        .execute()
    )

    if not move_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Move not found"
        )

    # Add move to campaign
    success = await campaign_repo.add_move(campaign_id, move_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add move to campaign",
        )

    return {
        "message": "Move added to campaign successfully",
        "campaign_id": campaign_id,
        "move_id": move_id,
    }


@router.post("/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Launch a campaign
    """
    campaign_repo = CampaignRepository()

    # Verify campaign exists and belongs to workspace
    campaign = await campaign_repo.get(campaign_id)

    if not campaign or campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Update campaign status to active
    updated_campaign = await campaign_repo.update_status(campaign_id, "active")

    if not updated_campaign:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to launch campaign",
        )

    return {"message": "Campaign launched successfully", "campaign": updated_campaign}


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Pause a campaign
    """
    campaign_repo = CampaignRepository()

    # Verify campaign exists and belongs to workspace
    campaign = await campaign_repo.get(campaign_id)

    if not campaign or campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Update campaign status to paused
    updated_campaign = await campaign_repo.update_status(campaign_id, "paused")

    if not updated_campaign:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause campaign",
        )

    return {"message": "Campaign paused successfully", "campaign": updated_campaign}


@router.post("/{campaign_id}/complete")
async def complete_campaign(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Complete a campaign
    """
    campaign_repo = CampaignRepository()

    # Verify campaign exists and belongs to workspace
    campaign = await campaign_repo.get(campaign_id)

    if not campaign or campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    # Update campaign status to completed
    updated_campaign = await campaign_repo.update_status(campaign_id, "completed")

    if not updated_campaign:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete campaign",
        )

    return {"message": "Campaign completed successfully", "campaign": updated_campaign}


@router.get("/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Get campaign statistics
    """
    campaign_repo = CampaignRepository()

    # Verify campaign exists and belongs to workspace
    campaign = await campaign_repo.get(campaign_id)

    if not campaign or campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    stats = await campaign_repo.get_campaign_stats(campaign_id)

    return {"campaign_id": campaign_id, "stats": stats}


@router.get("/{campaign_id}/roi")
async def get_campaign_roi(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Get campaign ROI analysis
    """
    campaign_repo = CampaignRepository()

    # Verify campaign exists and belongs to workspace
    campaign = await campaign_repo.get(campaign_id)

    if not campaign or campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    roi_data = await campaign_repo.calculate_roi(campaign_id)

    return {"campaign_id": campaign_id, "roi": roi_data}


@router.get("/{campaign_id}/timeline")
async def get_campaign_timeline(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Get campaign timeline
    """
    campaign_repo = CampaignRepository()

    # Verify campaign exists and belongs to workspace
    campaign = await campaign_repo.get(campaign_id)

    if not campaign or campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    timeline = await campaign_repo.get_campaign_timeline(campaign_id)

    return {"campaign_id": campaign_id, "timeline": timeline}


@router.post("/{campaign_id}/duplicate")
async def duplicate_campaign(
    campaign_id: str,
    new_name: str,
    auth_context: AuthContext = Depends(get_auth_context),
):
    """
    Duplicate a campaign
    """
    campaign_repo = CampaignRepository()

    # Verify campaign exists and belongs to workspace
    campaign = await campaign_repo.get(campaign_id)

    if not campaign or campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    duplicated_campaign = await campaign_repo.duplicate_campaign(campaign_id, new_name)

    if not duplicated_campaign:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate campaign",
        )

    return {
        "message": "Campaign duplicated successfully",
        "original_campaign_id": campaign_id,
        "new_campaign": duplicated_campaign,
    }


@router.post("/{campaign_id}/archive")
async def archive_campaign(
    campaign_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Archive a campaign
    """
    campaign_repo = CampaignRepository()

    # Verify campaign exists and belongs to workspace
    campaign = await campaign_repo.get(campaign_id)

    if not campaign or campaign.get("workspace_id") != auth_context.workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found"
        )

    success = await campaign_repo.archive_campaign(campaign_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to archive campaign",
        )

    return {"message": "Campaign archived successfully", "campaign_id": campaign_id}
