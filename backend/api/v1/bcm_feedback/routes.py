"""
BCM Feedback API — endpoints for user feedback, memories, and generation history.

Allows the frontend to:
- Submit feedback (thumbs up/down + edits) on Muse generations
- View accumulated memories
- View generation history
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from backend.services import bcm_memory, bcm_generation_logger

router = APIRouter(prefix="/context/feedback", tags=["context", "feedback"])


def _require_workspace_id(x_workspace_id: Optional[str]) -> str:
    if not x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Workspace-Id header",
        )
    try:
        UUID(x_workspace_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid X-Workspace-Id header (must be UUID)",
        )
    return x_workspace_id


# ── Request/Response models ──────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    generation_id: str
    score: int = Field(..., ge=1, le=5)
    edits: Optional[str] = None


class FeedbackResponse(BaseModel):
    success: bool
    memory_id: str = ""


class MemoryOut(BaseModel):
    id: str
    memory_type: str
    content: Dict[str, Any]
    source: str
    confidence: float
    created_at: Optional[str] = None


class MemorySummaryOut(BaseModel):
    total_count: int
    type_counts: Dict[str, int]
    top_memories: List[Dict[str, Any]]


class GenerationOut(BaseModel):
    id: str
    content_type: str
    output: str
    bcm_version: int
    feedback_score: Optional[int] = None
    tokens_used: Optional[int] = None
    created_at: Optional[str] = None


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    payload: FeedbackRequest,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> FeedbackResponse:
    """Submit feedback on a Muse generation (thumbs up/down + optional edits)."""
    workspace_id = _require_workspace_id(x_workspace_id)

    try:
        memory = bcm_memory.record_feedback(
            workspace_id=workspace_id,
            generation_id=payload.generation_id,
            score=payload.score,
            edits=payload.edits,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return FeedbackResponse(
        success=True,
        memory_id=memory.get("id", ""),
    )


@router.get("/memories", response_model=List[MemoryOut])
async def list_memories(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
    memory_type: Optional[str] = None,
    limit: int = 20,
) -> List[MemoryOut]:
    """List accumulated BCM memories for the workspace."""
    workspace_id = _require_workspace_id(x_workspace_id)
    rows = bcm_memory.get_relevant_memories(
        workspace_id, memory_type=memory_type, limit=limit,
    )
    return [
        MemoryOut(
            id=r["id"],
            memory_type=r["memory_type"],
            content=r["content"],
            source=r["source"],
            confidence=r.get("confidence", 0.5),
            created_at=r.get("created_at"),
        )
        for r in rows
    ]


@router.get("/memories/summary", response_model=MemorySummaryOut)
async def memory_summary(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MemorySummaryOut:
    """Get a summary of accumulated memories."""
    workspace_id = _require_workspace_id(x_workspace_id)
    summary = bcm_memory.get_memory_summary(workspace_id)
    return MemorySummaryOut(**summary)


@router.delete("/memories/{memory_id}")
async def delete_memory(
    memory_id: str,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> Dict[str, str]:
    """Delete a specific memory."""
    workspace_id = _require_workspace_id(x_workspace_id)
    deleted = bcm_memory.delete_memory(workspace_id, memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted", "memory_id": memory_id}


@router.get("/generations", response_model=List[GenerationOut])
async def list_generations(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
    content_type: Optional[str] = None,
    limit: int = 20,
) -> List[GenerationOut]:
    """List recent Muse generations for the workspace."""
    workspace_id = _require_workspace_id(x_workspace_id)
    rows = bcm_generation_logger.get_recent_generations(
        workspace_id, content_type=content_type, limit=limit,
    )
    return [
        GenerationOut(
            id=r["id"],
            content_type=r["content_type"],
            output=r.get("output", "")[:500],
            bcm_version=r.get("bcm_version", 0),
            feedback_score=r.get("feedback_score"),
            tokens_used=r.get("tokens_used"),
            created_at=r.get("created_at"),
        )
        for r in rows
    ]
