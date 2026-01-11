"""
Sessions API endpoints for working memory and session management.

This module provides REST API endpoints for managing working memory
sessions and agent context in the Raptorflow backend.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...auth.dependencies import get_current_user, get_workspace_access
from ...memory.working_memory import MemorySession, WorkingMemory
from ...models import User, Workspace

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


# Pydantic models for API requests/responses
class SessionCreateRequest(BaseModel):
    workspace_id: str = Field(..., description="Workspace ID")
    user_id: str = Field(..., description="User ID")
    agent_type: Optional[str] = Field(None, description="Initial agent type")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Initial context")


class SessionResponse(BaseModel):
    session_id: str
    workspace_id: str
    user_id: str
    created_at: str
    last_activity: str
    agent_type: Optional[str]
    context: Dict[str, Any]
    message_count: int
    is_active: bool


class SessionUpdateRequest(BaseModel):
    agent_type: Optional[str] = Field(None, description="Agent type")
    context: Optional[Dict[str, Any]] = Field(None, description="Session context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Session metadata")


class ContextWindowRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    content: str = Field(..., description="Content to add")
    content_type: str = Field("message", description="Type of content")
    workspace_id: str = Field(..., description="Workspace ID")


class ScratchPadRequest(BaseModel):
    session_id: str = Field(..., description="Session ID")
    key: str = Field(..., description="Key for scratch pad item")
    value: Any = Field(..., description="Value for scratch pad item")
    workspace_id: str = Field(..., description="Workspace ID")


# Dependency to get working memory
async def get_working_memory() -> WorkingMemory:
    """Get working memory instance."""
    return WorkingMemory()


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    workspace_id: str = Query(..., description="Workspace ID"),
    active_only: bool = Query(False, description="Filter active sessions only"),
    limit: int = Query(50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    List sessions for a workspace.

    Args:
        workspace_id: Workspace ID
        active_only: Filter active sessions only
        limit: Maximum number of results
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        List of sessions
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # List sessions
        sessions = await working_memory.list_sessions(
            workspace_id=workspace_id, active_only=active_only, limit=limit
        )

        # Convert to response format
        return [
            SessionResponse(
                session_id=session.session_id,
                workspace_id=session.workspace_id,
                user_id=session.user_id,
                created_at=session.created_at.isoformat(),
                last_activity=session.last_activity.isoformat(),
                agent_type=session.context.get("agent_type"),
                context=session.context,
                message_count=len(session.agent_history),
                is_active=session.expires_at is None
                or session.expires_at > datetime.now(),
            )
            for session in sessions
        ]

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=SessionResponse)
async def create_session(
    request: SessionCreateRequest,
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Create a new session.

    Args:
        request: Session creation request
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Created session
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Create session
        session_id = await working_memory.create_session(
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            agent_type=request.agent_type,
            initial_context=request.context,
        )

        # Get created session
        session = await working_memory.get_session(session_id)

        return SessionResponse(
            session_id=session.session_id,
            workspace_id=session.workspace_id,
            user_id=session.user_id,
            created_at=session.created_at.isoformat(),
            last_activity=session.last_activity.isoformat(),
            agent_type=session.context.get("agent_type"),
            context=session.context,
            message_count=len(session.agent_history),
            is_active=session.expires_at is None or session.expires_at > datetime.now(),
        )

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Get a specific session by ID.

    Args:
        session_id: Session ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Session
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get session
        session = await working_memory.get_session(session_id)

        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return SessionResponse(
            session_id=session.session_id,
            workspace_id=session.workspace_id,
            user_id=session.user_id,
            created_at=session.created_at.isoformat(),
            last_activity=session.last_activity.isoformat(),
            agent_type=session.context.get("agent_type"),
            context=session.context,
            message_count=len(session.agent_history),
            is_active=session.expires_at is None or session.expires_at > datetime.now(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    request: SessionUpdateRequest,
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Update a session.

    Args:
        session_id: Session ID
        request: Session update request
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Updated session
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Update session
        updates = {}
        if request.agent_type is not None:
            updates["agent_type"] = request.agent_type
        if request.context is not None:
            updates["context"] = request.context
        if request.metadata is not None:
            updates["metadata"] = request.metadata

        await working_memory.update_session(session_id, **updates)

        # Get updated session
        session = await working_memory.get_session(session_id)

        return SessionResponse(
            session_id=session.session_id,
            workspace_id=session.workspace_id,
            user_id=session.user_id,
            created_at=session.created_at.isoformat(),
            last_activity=session.last_activity.isoformat(),
            agent_type=session.context.get("agent_type"),
            context=session.context,
            message_count=len(session.agent_history),
            is_active=session.expires_at is None or session.expires_at > datetime.now(),
        )

    except Exception as e:
        logger.error(f"Error updating session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Delete a session.

    Args:
        session_id: Session ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Success message
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Delete session
        success = await working_memory.delete_session(session_id)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"message": "Session deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{session_id}/context")
async def get_session_context(
    session_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    limit: int = Query(20, description="Maximum number of context items"),
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Get context window for a session.

    Args:
        session_id: Session ID
        workspace_id: Workspace ID
        limit: Maximum number of context items
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Context window data
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get context window
        context = await working_memory.get_context_window(
            session_id=session_id, limit=limit
        )

        return {
            "session_id": session_id,
            "context_items": context,
            "item_count": len(context),
        }

    except Exception as e:
        logger.error(f"Error getting session context: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{session_id}/context")
async def add_to_context_window(
    session_id: str,
    request: ContextWindowRequest,
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Add content to session context window.

    Args:
        session_id: Session ID
        request: Context window request
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Success message
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Add to context window
        await working_memory.add_to_context_window(
            session_id=session_id,
            content=request.content,
            content_type=request.content_type,
        )

        return {"message": "Content added to context window"}

    except Exception as e:
        logger.error(f"Error adding to context window: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{session_id}/scratch")
async def get_scratch_pad(
    session_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Get scratch pad data for a session.

    Args:
        session_id: Session ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Scratch pad data
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get scratch pad
        scratch_pad = await working_memory.get_scratch_pad(session_id)

        return {
            "session_id": session_id,
            "scratch_pad": scratch_pad,
            "item_count": len(scratch_pad),
        }

    except Exception as e:
        logger.error(f"Error getting scratch pad: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{session_id}/scratch")
async def write_to_scratch_pad(
    session_id: str,
    request: ScratchPadRequest,
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Write to scratch pad for a session.

    Args:
        session_id: Session ID
        request: Scratch pad request
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Success message
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Write to scratch pad
        await working_memory.write_to_scratch_pad(
            session_id=session_id, key=request.key, value=request.value
        )

        return {"message": "Scratch pad item written"}

    except Exception as e:
        logger.error(f"Error writing to scratch pad: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{session_id}/history")
async def get_session_history(
    session_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    limit: int = Query(50, description="Maximum number of history items"),
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Get agent history for a session.

    Args:
        session_id: Session ID
        workspace_id: Workspace ID
        limit: Maximum number of history items
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Agent history
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get session
        session = await working_memory.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get history (limited)
        history = (
            session.agent_history[-limit:]
            if len(session.agent_history) > limit
            else session.agent_history
        )

        return {
            "session_id": session_id,
            "history": history,
            "total_items": len(session.agent_history),
            "returned_items": len(history),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session history: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{session_id}/refresh")
async def refresh_session(
    session_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    working_memory: WorkingMemory = Depends(get_working_memory),
):
    """
    Refresh session TTL and activity.

    Args:
        session_id: Session ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        working_memory: Working memory instance

    Returns:
        Success message
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Refresh session
        await working_memory.refresh_session(session_id)

        return {"message": "Session refreshed"}

    except Exception as e:
        logger.error(f"Error refreshing session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
