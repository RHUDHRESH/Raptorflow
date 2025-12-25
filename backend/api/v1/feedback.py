from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.core.auth import get_current_user, get_tenant_id
from backend.memory.swarm_learning import SwarmLearningMemory

router = APIRouter(prefix="/v1/feedback", tags=["feedback"])


class FeedbackPayload(BaseModel):
    feedback: str = Field(..., min_length=1, description="User feedback text.")
    context: str = Field(
        ..., min_length=1, description="Context of the request or outcome."
    )
    signal: Optional[str] = Field(
        default="neutral",
        description="Optional sentiment signal (positive, negative, neutral).",
    )
    tool_hint: Optional[str] = Field(
        default=None,
        description="Optional tool name hint to influence tool selection.",
    )
    agent_hint: Optional[str] = Field(
        default=None,
        description="Optional agent name hint to influence routing.",
    )
    timestamp: Optional[datetime] = Field(
        default=None, description="Optional client-provided timestamp."
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def ingest_feedback(
    payload: FeedbackPayload,
    tenant_id=Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Ingests user feedback and persists it to swarm learning memory."""
    metadata = {
        "user_id": current_user.get("id"),
        "user_email": current_user.get("email"),
        "context": payload.context,
        "signal": payload.signal,
        "tool_hint": payload.tool_hint,
        "agent_hint": payload.agent_hint,
        "timestamp": _normalize_timestamp(payload.timestamp),
    }

    memory = SwarmLearningMemory()
    try:
        feedback_id = await memory.store_feedback(
            workspace_id=str(tenant_id),
            feedback=payload.feedback,
            context=payload.context,
            metadata=metadata,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store feedback: {exc}",
        ) from exc

    return {"status": "stored", "feedback_id": feedback_id}


def _normalize_timestamp(value: Optional[datetime]) -> str:
    if not value:
        return datetime.now(timezone.utc).isoformat()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()
