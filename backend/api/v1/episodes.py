"""
Episodes API endpoints for episodic memory operations.

This module provides REST API endpoints for accessing and manipulating
episodic memory (conversation episodes and turns) in the Raptorflow backend.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ...auth.dependencies import get_current_user, get_workspace_access
from ...memory.episodic.models import ConversationTurn, Episode
from ...memory.episodic.store import EpisodicMemory
from ...models import User, Workspace

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/episodes", tags=["episodes"])


# Pydantic models for API requests/responses
class EpisodeCreateRequest(BaseModel):
    workspace_id: str = Field(..., description="Workspace ID")
    user_id: str = Field(..., description="User ID")
    session_id: str = Field(..., description="Session ID")
    episode_type: str = Field("conversation", description="Episode type")
    title: Optional[str] = Field(None, description="Episode title")
    content: str = Field("", description="Episode content")
    metadata: Optional[Dict[str, Any]] = Field(
        default={}, description="Episode metadata"
    )


class EpisodeResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    session_id: str
    episode_type: str
    title: Optional[str]
    content: str
    summary: str
    key_decisions: List[Dict[str, Any]]
    entities_mentioned: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    importance: float
    tags: List[str]
    started_at: str
    ended_at: Optional[str]
    token_count: int
    message_count: int
    duration_seconds: Optional[int]


class TurnCreateRequest(BaseModel):
    episode_id: str = Field(..., description="Episode ID")
    role: str = Field("user", description="Turn role")
    content: str = Field(..., description="Turn content")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=[], description="Tool calls"
    )
    tool_results: Optional[List[Dict[str, Any]]] = Field(
        default=[], description="Tool results"
    )
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Turn metadata")


class TurnResponse(BaseModel):
    id: str
    episode_id: str
    role: str
    content: str
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    turn_index: int
    timestamp: str
    metadata: Dict[str, Any]
    token_count: int
    processing_time_ms: Optional[int]
    model_used: Optional[str]


class EpisodeSummaryResponse(BaseModel):
    episode_id: str
    summary: str
    key_decisions: List[Dict[str, Any]]
    action_items: List[Dict[str, Any]]
    entities_mentioned: List[Dict[str, Any]]
    importance_score: float


# Dependency to get episodic memory
async def get_episodic_memory() -> EpisodicMemory:
    """Get episodic memory instance."""
    return EpisodicMemory()


@router.get("/", response_model=List[EpisodeResponse])
async def list_episodes(
    workspace_id: str = Query(..., description="Workspace ID"),
    session_id: Optional[str] = Query(None, description="Filter by session ID"),
    episode_type: Optional[str] = Query(None, description="Filter by episode type"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    List episodes for a workspace.

    Args:
        workspace_id: Workspace ID
        session_id: Optional session ID filter
        episode_type: Optional episode type filter
        limit: Maximum number of results
        offset: Offset for pagination
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        List of episodes
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # List episodes
        episodes = await episodic_memory.list_episodes(
            workspace_id=workspace_id,
            session_id=session_id,
            episode_type=episode_type,
            limit=limit,
            offset=offset,
        )

        # Convert to response format
        return [
            EpisodeResponse(
                id=episode.id,
                workspace_id=episode.workspace_id,
                user_id=episode.user_id,
                session_id=episode.session_id,
                episode_type=episode.episode_type,
                title=episode.title,
                content=episode.content,
                summary=episode.summary,
                key_decisions=episode.key_decisions,
                entities_mentioned=episode.entities_mentioned,
                action_items=episode.action_items,
                metadata=episode.metadata,
                importance=episode.importance,
                tags=episode.tags,
                started_at=episode.started_at.isoformat(),
                ended_at=episode.ended_at.isoformat() if episode.ended_at else None,
                token_count=episode.token_count,
                message_count=episode.message_count,
                duration_seconds=episode.get_duration_seconds(),
            )
            for episode in episodes
        ]

    except Exception as e:
        logger.error(f"Error listing episodes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/", response_model=EpisodeResponse)
async def create_episode(
    request: EpisodeCreateRequest,
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    Create a new episode.

    Args:
        request: Episode creation request
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        Created episode
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Create episode
        episode_id = await episodic_memory.create_episode(
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            session_id=request.session_id,
            episode_type=request.episode_type,
            title=request.title,
            content=request.content,
            metadata=request.metadata,
        )

        # Get created episode
        episode = await episodic_memory.get_episode(episode_id)

        return EpisodeResponse(
            id=episode.id,
            workspace_id=episode.workspace_id,
            user_id=episode.user_id,
            session_id=episode.session_id,
            episode_type=episode.episode_type,
            title=episode.title,
            content=episode.content,
            summary=episode.summary,
            key_decisions=episode.key_decisions,
            entities_mentioned=episode.entities_mentioned,
            action_items=episode.action_items,
            metadata=episode.metadata,
            importance=episode.importance,
            tags=episode.tags,
            started_at=episode.started_at.isoformat(),
            ended_at=episode.ended_at.isoformat() if episode.ended_at else None,
            token_count=episode.token_count,
            message_count=episode.message_count,
            duration_seconds=episode.get_duration_seconds(),
        )

    except Exception as e:
        logger.error(f"Error creating episode: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{episode_id}", response_model=EpisodeResponse)
async def get_episode(
    episode_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    Get a specific episode by ID.

    Args:
        episode_id: Episode ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        Episode
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get episode
        episode = await episodic_memory.get_episode(episode_id)

        if not episode:
            raise HTTPException(status_code=404, detail="Episode not found")

        return EpisodeResponse(
            id=episode.id,
            workspace_id=episode.workspace_id,
            user_id=episode.user_id,
            session_id=episode.session_id,
            episode_type=episode.episode_type,
            title=episode.title,
            content=episode.content,
            summary=episode.summary,
            key_decisions=episode.key_decisions,
            entities_mentioned=episode.entities_mentioned,
            action_items=episode.action_items,
            metadata=episode.metadata,
            importance=episode.importance,
            tags=episode.tags,
            started_at=episode.started_at.isoformat(),
            ended_at=episode.ended_at.isoformat() if episode.ended_at else None,
            token_count=episode.token_count,
            message_count=episode.message_count,
            duration_seconds=episode.get_duration_seconds(),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting episode: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{episode_id}/end")
async def end_episode(
    episode_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    End an episode.

    Args:
        episode_id: Episode ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        Success message
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # End episode
        success = await episodic_memory.end_episode(episode_id)

        if not success:
            raise HTTPException(status_code=404, detail="Episode not found")

        return {"message": "Episode ended successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending episode: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{episode_id}/turns", response_model=List[TurnResponse])
async def get_episode_turns(
    episode_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    limit: int = Query(100, description="Maximum number of turns"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    Get turns for an episode.

    Args:
        episode_id: Episode ID
        workspace_id: Workspace ID
        limit: Maximum number of turns
        offset: Offset for pagination
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        List of turns
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get turns
        turns = await episodic_memory.get_episode_turns(
            episode_id=episode_id, limit=limit, offset=offset
        )

        # Convert to response format
        return [
            TurnResponse(
                id=turn.id,
                episode_id=turn.episode_id,
                role=turn.role,
                content=turn.content,
                tool_calls=turn.tool_calls,
                tool_results=turn.tool_results,
                turn_index=turn.turn_index,
                timestamp=turn.timestamp.isoformat(),
                metadata=turn.metadata,
                token_count=turn.token_count,
                processing_time_ms=turn.processing_time_ms,
                model_used=turn.model_used,
            )
            for turn in turns
        ]

    except Exception as e:
        logger.error(f"Error getting episode turns: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{episode_id}/turns", response_model=TurnResponse)
async def add_turn(
    episode_id: str,
    request: TurnCreateRequest,
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    Add a turn to an episode.

    Args:
        episode_id: Episode ID
        request: Turn creation request
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        Created turn
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Add turn
        turn_id = await episodic_memory.add_turn(
            episode_id=episode_id,
            role=request.role,
            content=request.content,
            tool_calls=request.tool_calls,
            tool_results=request.tool_results,
            metadata=request.metadata,
        )

        # Get created turn
        turn = await episodic_memory.get_turn(turn_id)

        return TurnResponse(
            id=turn.id,
            episode_id=turn.episode_id,
            role=turn.role,
            content=turn.content,
            tool_calls=turn.tool_calls,
            tool_results=turn.tool_results,
            turn_index=turn.turn_index,
            timestamp=turn.timestamp.isoformat(),
            metadata=turn.metadata,
            token_count=turn.token_count,
            processing_time_ms=turn.processing_time_ms,
            model_used=turn.model_used,
        )

    except Exception as e:
        logger.error(f"Error adding turn: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{episode_id}/summary", response_model=EpisodeSummaryResponse)
async def get_episode_summary(
    episode_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    Get episode summary.

    Args:
        episode_id: Episode ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        Episode summary
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get episode
        episode = await episodic_memory.get_episode(episode_id)
        if not episode:
            raise HTTPException(status_code=404, detail="Episode not found")

        # Generate summary if needed
        if not episode.summary:
            episode = await episodic_memory.generate_summary(episode_id)

        return EpisodeSummaryResponse(
            episode_id=episode.id,
            summary=episode.summary,
            key_decisions=episode.key_decisions,
            action_items=episode.action_items,
            entities_mentioned=episode.entities_mentioned,
            importance_score=episode.importance,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting episode summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{episode_id}/replay")
async def replay_episode(
    episode_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    Replay an episode (reconstruct conversation state).

    Args:
        episode_id: Episode ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        Episode replay data
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Replay episode
        replay_data = await episodic_memory.replay_episode(episode_id)

        return {
            "episode_id": episode_id,
            "replay_data": replay_data,
            "turn_count": len(replay_data.get("turns", [])),
            "total_tokens": replay_data.get("total_tokens", 0),
        }

    except Exception as e:
        logger.error(f"Error replaying episode: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search", response_model=List[EpisodeResponse])
async def search_episodes(
    workspace_id: str = Query(..., description="Workspace ID"),
    query: str = Query(..., description="Search query"),
    episode_type: Optional[str] = Query(None, description="Filter by episode type"),
    limit: int = Query(20, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    Search episodes by content.

    Args:
        workspace_id: Workspace ID
        query: Search query
        episode_type: Optional episode type filter
        limit: Maximum number of results
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        List of matching episodes
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Search episodes
        episodes = await episodic_memory.search_episodes(
            workspace_id=workspace_id,
            query=query,
            episode_type=episode_type,
            limit=limit,
        )

        # Convert to response format
        return [
            EpisodeResponse(
                id=episode.id,
                workspace_id=episode.workspace_id,
                user_id=episode.user_id,
                session_id=episode.session_id,
                episode_type=episode.episode_type,
                title=episode.title,
                content=episode.content,
                summary=episode.summary,
                key_decisions=episode.key_decisions,
                entities_mentioned=episode.entities_mentioned,
                action_items=episode.action_items,
                metadata=episode.metadata,
                importance=episode.importance,
                tags=episode.tags,
                started_at=episode.started_at.isoformat(),
                ended_at=episode.ended_at.isoformat() if episode.ended_at else None,
                token_count=episode.token_count,
                message_count=episode.message_count,
                duration_seconds=episode.get_duration_seconds(),
            )
            for episode in episodes
        ]

    except Exception as e:
        logger.error(f"Error searching episodes: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{episode_id}")
async def delete_episode(
    episode_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    episodic_memory: EpisodicMemory = Depends(get_episodic_memory),
):
    """
    Delete an episode.

    Args:
        episode_id: Episode ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        episodic_memory: Episodic memory instance

    Returns:
        Success message
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Delete episode
        success = await episodic_memory.delete_episode(episode_id)

        if not success:
            raise HTTPException(status_code=404, detail="Episode not found")

        return {"message": "Episode deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting episode: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
