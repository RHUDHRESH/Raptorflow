"""
Integrations Router - API endpoints for managing platform connections.
Handles OAuth flows and integration status.
"""

import structlog
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.main import get_current_user_and_workspace
from backend.services.supabase_client import supabase_client

router = APIRouter()
logger = structlog.get_logger(__name__)


# --- Request/Response Models ---
class IntegrationConnectRequest(BaseModel):
    platform: str
    access_token: str
    refresh_token: Optional[str] = None
    account_id: Optional[str] = None
    metadata: dict = {}


class IntegrationResponse(BaseModel):
    id: UUID
    workspace_id: UUID
    platform: str
    status: str
    connected_at: str
    account_id: Optional[str] = None


@router.post("/connect/{platform}", response_model=IntegrationResponse, summary="Connect Platform", tags=["Integrations"])
async def connect_platform(
    platform: str,
    request: IntegrationConnectRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Connects a third-party platform (LinkedIn, Twitter, Instagram, etc.).
    Stores OAuth tokens securely.
    """
    workspace_id = auth["workspace_id"]
    logger.info("Connecting platform", platform=platform, workspace_id=workspace_id)
    
    supported_platforms = ["linkedin", "twitter", "instagram", "youtube", "facebook", "canva", "email"]
    if platform not in supported_platforms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported platform. Supported: {', '.join(supported_platforms)}"
        )
    
    try:
        # Check if integration already exists
        existing = await supabase_client.fetch_one(
            "integrations",
            {"workspace_id": str(workspace_id), "platform": platform}
        )
        
        integration_data = {
            "workspace_id": str(workspace_id),
            "platform": platform,
            "access_token": request.access_token,
            "refresh_token": request.refresh_token,
            "account_id": request.account_id,
            "status": "active",
            "metadata": request.metadata,
            "connected_at": datetime.utcnow().isoformat()
        }
        
        if existing:
            # Update existing
            integration = await supabase_client.update(
                "integrations",
                {"id": existing["id"]},
                integration_data
            )
            logger.info("Platform integration updated", platform=platform, workspace_id=workspace_id)
        else:
            # Create new
            integration = await supabase_client.insert("integrations", integration_data)
            logger.info("Platform integration created", platform=platform, workspace_id=workspace_id)
        
        return IntegrationResponse(**integration)
        
    except Exception as e:
        logger.error(f"Failed to connect platform: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/disconnect/{platform}", summary="Disconnect Platform", tags=["Integrations"])
async def disconnect_platform(
    platform: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Disconnects a platform integration."""
    workspace_id = auth["workspace_id"]
    logger.info("Disconnecting platform", platform=platform, workspace_id=workspace_id)
    
    try:
        await supabase_client.delete(
            "integrations",
            {"workspace_id": str(workspace_id), "platform": platform}
        )
        
        return {"status": "success", "message": f"{platform} disconnected"}
        
    except Exception as e:
        logger.error(f"Failed to disconnect platform: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/status", response_model=list[IntegrationResponse], summary="Get Integration Status", tags=["Integrations"])
async def get_integration_status(auth: Annotated[dict, Depends(get_current_user_and_workspace)]):
    """Retrieves status of all platform integrations for the workspace."""
    workspace_id = auth["workspace_id"]
    
    try:
        integrations = await supabase_client.fetch_all(
            "integrations",
            {"workspace_id": str(workspace_id)}
        )
        
        return [IntegrationResponse(**i) for i in integrations]
        
    except Exception as e:
        logger.error(f"Failed to get integration status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{platform}/status", response_model=IntegrationResponse, summary="Get Platform Status", tags=["Integrations"])
async def get_platform_status(
    platform: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Checks if a specific platform is connected."""
    workspace_id = auth["workspace_id"]
    
    try:
        integration = await supabase_client.fetch_one(
            "integrations",
            {"workspace_id": str(workspace_id), "platform": platform}
        )
        
        if not integration:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{platform} not connected")
        
        return IntegrationResponse(**integration)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get platform status: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

