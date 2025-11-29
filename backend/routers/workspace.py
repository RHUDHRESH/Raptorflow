"""
Workspace Management API Router
Handles workspace creation, membership, and initialization.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from uuid import uuid4
import structlog

from backend.services.supabase_client import supabase_client
from backend.services.agent_registry import agent_registry
from backend.services.audit_log import log_workspace_created, log_agents_seeded
from backend.utils.logging_config import get_logger
from backend.core.errors import PermissionDeniedError
from backend.core.request_context import RequestContext
from backend.api.deps import require_workspace_member, require_workspace_role
from backend.utils.auth import get_current_user_and_workspace

logger = get_logger("workspace_router")

router = APIRouter()


# ==================== REQUEST/RESPONSE MODELS ====================

class CreateWorkspaceRequest(BaseModel):
    """Workspace creation request"""
    name: str
    slug: Optional[str] = None  # Auto-generated if not provided


class CreateWorkspaceResponse(BaseModel):
    """Workspace creation response"""
    workspace_id: str
    name: str
    slug: str
    agents_created: int


class WorkspaceInfo(BaseModel):
    """Workspace information"""
    id: str
    name: str
    slug: str
    owner_id: str
    plan: str
    is_active: bool
    created_at: str
    updated_at: str


class InviteMemberRequest(BaseModel):
    """Invite member request"""
    email: str
    role: str = "member"


class InviteMemberResponse(BaseModel):
    """Invite member response"""
    invite_id: str
    email: str
    workspace_id: str
    status: str


# ==================== WORKSPACE ENDPOINTS ====================

@router.post("/", response_model=CreateWorkspaceResponse)
async def create_workspace(request: CreateWorkspaceRequest, user_auth: dict = Depends(get_current_user_and_workspace)):
    """
    Create a new workspace.

    Initializes the workspace with the canonical Council of Lords and core infrastructure.

    Args:
        request: Workspace creation parameters
        user_auth: Authenticated user info

    Returns:
        Workspace creation result with agent seeding status
    """
    try:
        user_id = user_auth["user_id"]

        # Generate slug if not provided
        slug = request.slug or f"{request.name.lower().replace(' ', '-').replace('_', '-')}-{str(uuid4())[:8]}"

        # Create workspace in database
        workspace_id = str(uuid4())
        workspace_data = {
            "id": workspace_id,
            "name": request.name,
            "slug": slug,
            "owner_id": user_id,
            "plan": "free",
            "is_active": True,
        }

        result = await supabase_client.insert("workspaces", workspace_data)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create workspace")

        # Add owner as member
        member_data = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "role": "owner",
        }
        await supabase_client.insert("workspace_members", member_data)

        logger.info(
            "Workspace created",
            workspace_id=workspace_id,
            name=request.name,
            slug=slug,
            owner_id=user_id
        )

        # Audit log workspace creation
        await log_workspace_created(workspace_id, user_id, request.name)

        # Initialize core agents
        await agent_registry.ensure_core_agents_for_workspace(workspace_id)

        # Verify agents were created (optional - for response)
        agents = await agent_registry.list_workspace_agents(workspace_id)
        agents_created = len(agents)

        logger.info(
            "Workspace initialized with core agents",
            workspace_id=workspace_id,
            agents_created=agents_created,
            lords_available=len(agent_registry.get_canonical_lords())
        )

        # Audit log agent seeding
        await log_agents_seeded(workspace_id, user_id, agents_created)

        return CreateWorkspaceResponse(
            workspace_id=workspace_id,
            name=request.name,
            slug=slug,
            agents_created=agents_created
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workspace creation failed: {e}", exc_info=True)
        await supabase_client.client.table("workspaces").delete().eq("id", workspace_id)  # Cleanup on failure
        raise HTTPException(status_code=500, detail="Workspace creation failed")


@router.get("/", response_model=list[WorkspaceInfo])
async def get_my_workspaces(user_auth: dict = Depends(get_current_user_and_workspace)):
    """
    Get all workspaces the authenticated user has access to.
    """
    try:
        user_id = user_auth["user_id"]

        # Join workspaces through workspace_members
        result = await supabase_client.client.table("workspace_members").select(
            "workspace_id, workspaces(*)"
        ).eq("user_id", user_id).execute()

        workspaces = []
        for membership in result.data:
            workspace = membership.get("workspaces", {})
            if workspace:  # Ensure workspace data exists
                workspaces.append(WorkspaceInfo(**workspace))

        logger.info(
            "Workspaces retrieved",
            user_id=user_id,
            count=len(workspaces)
        )

        return workspaces

    except Exception as e:
        logger.error(f"Failed to get workspaces: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve workspaces")


@router.get("/{workspace_id}", response_model=WorkspaceInfo)
async def get_workspace_details(
    workspace_id: str,
    ctx: RequestContext = Depends(require_workspace_member)
):
    """
    Get details of a specific workspace.
    RLS protected via require_workspace_member dependency.
    """
    try:
        result = await supabase_client.client.table("workspaces").select("*").eq("id", workspace_id).single().execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Workspace not found")

        return WorkspaceInfo(**result.data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workspace details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve workspace details")


@router.post("/{workspace_id}/invite", response_model=InviteMemberResponse)
async def invite_member(
    workspace_id: str,
    request: InviteMemberRequest,
    ctx: RequestContext = Depends(require_workspace_role("owner", "admin"))
):
    """
    Invite a new member to the workspace.
    Only owners and admins can invite.
    """
    try:
        # Check if user already member (optional but good UX)
        # For now, just insert into invites table
        
        invite_data = {
            "workspace_id": workspace_id,
            "email": request.email,
            "role": request.role,
            "status": "pending"
        }
        
        result = await supabase_client.insert("workspace_invites", invite_data)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create invite")
            
        # In a real system, we would send an email here
        
        logger.info(
            "Member invited",
            workspace_id=workspace_id,
            email=request.email,
            role=request.role,
            actor_id=ctx.user_id
        )
        
        return InviteMemberResponse(
            invite_id=result[0]["id"],
            email=result[0]["email"],
            workspace_id=result[0]["workspace_id"],
            status=result[0]["status"]
        )

    except Exception as e:
        logger.error(f"Failed to invite member: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to invite member")


@router.get("/{workspace_id}/agents")
async def get_workspace_agents(
    workspace_id: str,
    ctx: RequestContext = Depends(require_workspace_member)
):
    """
    Get all agents in a workspace.

    SECURITY: User must be a member of the workspace.
    Uses the new request context system for authentication and authorization.
    """
    try:
        # Context already validated - user is authenticated and member of workspace
        agents = await agent_registry.list_workspace_agents(workspace_id)

        logger.info(
            "Workspace agents retrieved",
            workspace_id=workspace_id,
            user_id=ctx.user_id,
            agent_count=len(agents)
        )

        return {"agents": agents, "count": len(agents)}

    except Exception as e:
        logger.error(f"Failed to get workspace agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve agents")


@router.post("/{workspace_id}/seed-agents")
async def seed_workspace_agents(workspace_id: str, user_auth: dict = Depends(get_current_user_and_workspace)):
    """
    Manually seed workspace with core agents (idempotent).

    Useful for workspaces that were created before agent registry existed.
    """
    try:
        user_id = user_auth["user_id"]

        # Verify user is member and has admin privileges
        member_check = await supabase_client.client.table("workspace_members").select("role").eq("workspace_id", workspace_id).eq("user_id", user_id).execute()
        if not member_check.data or member_check.data[0]["role"] not in ["owner", "admin"]:
            raise PermissionDeniedError("Insufficient permissions")

        # Seed agents
        await agent_registry.ensure_core_agents_for_workspace(workspace_id)

        # Report results
        agents = await agent_registry.list_workspace_agents(workspace_id)

        logger.info(
            "Workspace manually seeded with agents",
            workspace_id=workspace_id,
            user_id=user_id,
            agents_count=len(agents)
        )

        return {
            "message": "Workspace seeded with core agents",
            "agents_created": len(agents),
            "lords_available": len(agent_registry.get_canonical_lords())
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to seed workspace agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to seed agents")
