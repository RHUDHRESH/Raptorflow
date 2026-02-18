"""
Muse API

Goal: keep a single, minimal, working Muse endpoint that the Next.js UI can call.
Authentication is handled by the auth service.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, Header, HTTPException, Depends, status
from pydantic import BaseModel, Field

from backend.api.v1.workspace_guard import (
    enforce_bcm_ready,
    require_workspace_id,
)
from backend.services.muse_service import muse_service
from backend.services.exceptions import ServiceError, ServiceUnavailableError
from backend.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/muse", tags=["muse"])


class MuseGenerateRequest(BaseModel):
    task: str = Field(..., min_length=1)
    context: Dict[str, Any] = Field(default_factory=dict)
    content_type: str = "general"
    tone: str = "professional"
    target_audience: str = "general"
    max_tokens: int = Field(default=800, ge=64, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    reasoning_depth: Literal["low", "medium", "high"] = "medium"
    intensity: Optional[Literal["low", "medium", "high"]] = None
    execution_mode: Optional[Literal["single", "council", "swarm"]] = None


class MuseGenerateResponse(BaseModel):
    success: bool
    content: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    suggestions: List[str] = Field(default_factory=list)
    error: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


@router.get("/health")
async def muse_health(
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> Dict[str, Any]:
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)
    health = await muse_service.check_health()
    return {
        "status": "ok" if health.get("status") == "healthy" else health.get("status"),
        "engine": health.get("engine", "unconfigured"),
        "vertex_ai_configured": health.get("status") == "healthy",
    }


@router.post("/generate", response_model=MuseGenerateResponse)
async def generate(
    payload: MuseGenerateRequest,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MuseGenerateResponse:
    workspace_id = require_workspace_id(x_workspace_id)
    enforce_bcm_ready(workspace_id)

    try:
        result = await muse_service.generate(
            workspace_id=workspace_id,
            task=payload.task,
            content_type=payload.content_type,
            tone=payload.tone,
            target_audience=payload.target_audience,
            context=payload.context,
            max_tokens=payload.max_tokens,
            temperature=payload.temperature,
            reasoning_depth=payload.reasoning_depth,
            intensity=payload.intensity,
            execution_mode=payload.execution_mode,
        )

        return MuseGenerateResponse(
            success=result.get("success", False),
            content=result.get("content", ""),
            tokens_used=result.get("tokens_used", 0),
            cost_usd=result.get("cost_usd", 0.0),
            metadata=result.get("metadata", {}),
        )
    except ServiceUnavailableError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )
    except ServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
