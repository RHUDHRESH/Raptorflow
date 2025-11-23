"""
Integrations Router - API endpoints for managing platform connections.
Handles OAuth flows and integration status.
"""

import structlog
import os
from typing import Annotated, Optional
from uuid import UUID
from datetime import datetime, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from backend.main import get_current_user_and_workspace
from backend.services.supabase_client import supabase_client
from backend.utils.correlation import generate_correlation_id

router = APIRouter()
logger = structlog.get_logger(__name__)


# OAuth Configuration (should be in environment variables)
OAUTH_CONFIG = {
    "linkedin": {
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "client_id": os.getenv("LINKEDIN_CLIENT_ID", ""),
        "client_secret": os.getenv("LINKEDIN_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/oauth/linkedin/callback"),
        "scope": "r_liteprofile r_emailaddress w_member_social"
    },
    "twitter": {
        "authorize_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "client_id": os.getenv("TWITTER_CLIENT_ID", ""),
        "client_secret": os.getenv("TWITTER_CLIENT_SECRET", ""),
        "redirect_uri": os.getenv("TWITTER_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/oauth/twitter/callback"),
        "scope": "tweet.read tweet.write users.read offline.access"
    }
}


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


# --- OAuth Flow Endpoints ---
@router.get("/oauth/{platform}/authorize", summary="Start OAuth Flow", tags=["Integrations"])
async def start_oauth_flow(
    platform: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Initiates OAuth authorization flow for a platform (e.g., LinkedIn).
    Redirects user to platform's authorization page.
    """
    workspace_id = auth["workspace_id"]
    user_id = auth["user_id"]
    correlation_id = generate_correlation_id()

    logger.info("Starting OAuth flow",
                platform=platform,
                workspace_id=workspace_id,
                correlation_id=correlation_id)

    if platform not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth not supported for platform: {platform}"
        )

    config = OAUTH_CONFIG[platform]

    # Generate state parameter for CSRF protection
    state = f"{workspace_id}:{user_id}:{correlation_id}"

    # Build authorization URL
    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": config["scope"],
        "state": state
    }

    authorize_url = f"{config['authorize_url']}?{urlencode(params)}"

    logger.info("Redirecting to OAuth authorization",
                platform=platform,
                correlation_id=correlation_id)

    return {
        "authorization_url": authorize_url,
        "platform": platform,
        "correlation_id": correlation_id
    }


@router.get("/oauth/{platform}/callback", summary="OAuth Callback", tags=["Integrations"])
async def oauth_callback(
    platform: str,
    code: str = Query(..., description="Authorization code from OAuth provider"),
    state: str = Query(..., description="State parameter for CSRF protection"),
    error: Optional[str] = Query(None, description="Error from OAuth provider")
):
    """
    Handles OAuth callback from platform.
    Exchanges authorization code for access token and stores integration.
    """
    correlation_id = generate_correlation_id()
    logger.info("Handling OAuth callback",
                platform=platform,
                has_error=error is not None,
                correlation_id=correlation_id)

    if error:
        logger.error(f"OAuth error: {error}", platform=platform)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authorization failed: {error}"
        )

    if platform not in OAUTH_CONFIG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth not supported for platform: {platform}"
        )

    # Parse state to get workspace_id and user_id
    try:
        workspace_id, user_id, original_correlation_id = state.split(":")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )

    config = OAUTH_CONFIG[platform]

    try:
        # Exchange code for access token
        import httpx

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                config["token_url"],
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": config["redirect_uri"],
                    "client_id": config["client_id"],
                    "client_secret": config["client_secret"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if token_response.status_code != 200:
                logger.error(f"Token exchange failed: {token_response.text}",
                           platform=platform)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to exchange authorization code for token"
                )

            token_data = token_response.json()

        # Store integration
        integration_data = {
            "workspace_id": workspace_id,
            "platform": platform,
            "access_token": token_data.get("access_token"),
            "refresh_token": token_data.get("refresh_token"),
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "status": "active",
            "metadata": token_data,
            "connected_at": datetime.now(timezone.utc).isoformat()
        }

        # Check if integration already exists
        existing = await supabase_client.fetch_one(
            "integrations",
            {"workspace_id": workspace_id, "platform": platform}
        )

        if existing:
            # Update existing
            integration = await supabase_client.update(
                "integrations",
                {"id": existing["id"]},
                integration_data
            )
            logger.info("OAuth integration updated",
                       platform=platform,
                       workspace_id=workspace_id,
                       correlation_id=correlation_id)
        else:
            # Create new
            integration = await supabase_client.insert("integrations", integration_data)
            logger.info("OAuth integration created",
                       platform=platform,
                       workspace_id=workspace_id,
                       correlation_id=correlation_id)

        # Redirect to success page or return success response
        return {
            "status": "success",
            "platform": platform,
            "connected": True,
            "integration_id": integration["id"],
            "correlation_id": correlation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}",
                    platform=platform,
                    correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/connect/{platform}", response_model=dict, summary="Connect Platform", tags=["Integrations"])
async def connect_platform(
    platform: str,
    request: IntegrationConnectRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Connects a third-party platform (LinkedIn, Twitter, Instagram, etc.).
    Stores OAuth tokens securely. Manual connection with pre-obtained tokens.
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Connecting platform",
                platform=platform,
                workspace_id=workspace_id,
                correlation_id=correlation_id)
    
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
            "connected_at": datetime.now(timezone.utc).isoformat()
        }
        
        if existing:
            # Update existing
            integration = await supabase_client.update(
                "integrations",
                {"id": existing["id"]},
                integration_data
            )
            logger.info("Platform integration updated",
                       platform=platform,
                       workspace_id=workspace_id,
                       correlation_id=correlation_id)
        else:
            # Create new
            integration = await supabase_client.insert("integrations", integration_data)
            logger.info("Platform integration created",
                       platform=platform,
                       workspace_id=workspace_id,
                       correlation_id=correlation_id)

        return {
            **integration,
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to connect platform: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/disconnect/{platform}", summary="Disconnect Platform", tags=["Integrations"])
async def disconnect_platform(
    platform: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Disconnects a platform integration."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Disconnecting platform",
                platform=platform,
                workspace_id=workspace_id,
                correlation_id=correlation_id)

    try:
        await supabase_client.delete(
            "integrations",
            {"workspace_id": str(workspace_id), "platform": platform}
        )

        logger.info("Platform disconnected successfully",
                   platform=platform,
                   correlation_id=correlation_id)

        return {
            "status": "success",
            "message": f"{platform} disconnected",
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to disconnect platform: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status", response_model=dict, summary="Get Integration Status", tags=["Integrations"])
async def get_integration_status(auth: Annotated[dict, Depends(get_current_user_and_workspace)]):
    """Retrieves status of all platform integrations for the workspace."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Fetching integration status",
                workspace_id=workspace_id,
                correlation_id=correlation_id)

    try:
        integrations = await supabase_client.fetch_all(
            "integrations",
            {"workspace_id": str(workspace_id)}
        )

        logger.info(f"Retrieved {len(integrations)} integrations",
                   correlation_id=correlation_id)

        return {
            "integrations": [IntegrationResponse(**i).dict() for i in integrations],
            "total": len(integrations),
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to get integration status: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{platform}/status", response_model=dict, summary="Get Platform Status", tags=["Integrations"])
async def get_platform_status(
    platform: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """Checks if a specific platform is connected."""
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()
    logger.info("Checking platform status",
                platform=platform,
                workspace_id=workspace_id,
                correlation_id=correlation_id)

    try:
        integration = await supabase_client.fetch_one(
            "integrations",
            {"workspace_id": str(workspace_id), "platform": platform}
        )

        if not integration:
            logger.warning(f"Platform not connected: {platform}", correlation_id=correlation_id)
            return {
                "platform": platform,
                "connected": False,
                "message": f"{platform} not connected",
                "correlation_id": correlation_id
            }

        logger.info(f"Platform connected: {platform}", correlation_id=correlation_id)
        return {
            **IntegrationResponse(**integration).dict(),
            "connected": True,
            "correlation_id": correlation_id
        }

    except Exception as e:
        logger.error(f"Failed to get platform status: {e}", correlation_id=correlation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

