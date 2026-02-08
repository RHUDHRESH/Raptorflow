"""
Muse API (No-Auth Reconstruction Mode)

Goal: keep a single, minimal, working Muse endpoint that the Next.js UI can call.
No user auth. Tenant boundary is `x-workspace-id`.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from backend.services.vertex_ai_service import vertex_ai_service

router = APIRouter(prefix="/muse", tags=["muse"])


def _require_tenant_id(x_workspace_id: Optional[str]) -> str:
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


class MuseGenerateRequest(BaseModel):
    task: str = Field(..., min_length=1)
    context: Dict[str, Any] = Field(default_factory=dict)
    content_type: str = "general"
    tone: str = "professional"
    target_audience: str = "general"
    max_tokens: int = 800
    temperature: float = 0.7


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
    _require_tenant_id(x_workspace_id)
    return {
        "status": "ok",
        "engine": "vertex_ai" if vertex_ai_service else "unconfigured",
        "vertex_ai_configured": bool(vertex_ai_service),
    }


@router.post("/generate", response_model=MuseGenerateResponse)
async def generate(
    payload: MuseGenerateRequest,
    x_workspace_id: Optional[str] = Header(None, alias="x-workspace-id"),
) -> MuseGenerateResponse:
    workspace_id = _require_tenant_id(x_workspace_id)

    if not vertex_ai_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Vertex AI unavailable. Configure VERTEX_AI_PROJECT_ID/credentials.",
        )

    prompt = "\n".join(
        [
            f"Task: {payload.task}",
            f"Type: {payload.content_type}",
            f"Tone: {payload.tone}",
            f"Target audience: {payload.target_audience}",
            f"Context: {json.dumps(payload.context)}",
        ]
    )

    result = await vertex_ai_service.generate_text(
        prompt=prompt,
        workspace_id=workspace_id,
        user_id="reconstruction",
        max_tokens=payload.max_tokens,
        temperature=payload.temperature,
    )

    if result.get("status") != "success":
        error = result.get("error") or "Muse generation failed"
        raise HTTPException(status_code=502, detail=error)

    return MuseGenerateResponse(
        success=True,
        content=result.get("text") or "",
        tokens_used=int(result.get("total_tokens") or 0),
        cost_usd=float(result.get("cost_usd") or 0.0),
        metadata={
            "model": result.get("model"),
            "model_type": result.get("model_type"),
            "generation_time_seconds": result.get("generation_time_seconds"),
        },
    )
