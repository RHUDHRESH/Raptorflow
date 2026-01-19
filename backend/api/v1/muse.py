"""
Muse API - Legacy fallback endpoint.

Kept minimal to avoid import-time failures while the primary Muse Vertex AI
router handles production traffic at /api/v1/muse/*.
"""

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

try:
    from synapse import brain
    from schemas import NodeInput
except Exception:
    brain = None
    NodeInput = None


router = APIRouter(prefix="/muse", tags=["muse"])


class ContentRequest(BaseModel):
    task: str
    context: Dict[str, Any] = {}
    user_id: str
    workspace_id: str
    session_id: str = "default"


class ContentResponse(BaseModel):
    success: bool
    content: str = ""
    seo_score: float = 0.0
    suggestions: List[str] = []
    error: str = ""


@router.post("/generate", response_model=ContentResponse)
async def generate_content(request: ContentRequest) -> ContentResponse:
    if not brain or not NodeInput:
        return ContentResponse(success=False, error="Muse legacy service unavailable")

    try:
        node_input = NodeInput(
            task=request.task,
            context=request.context,
            user_id=request.user_id,
            workspace_id=request.workspace_id,
            session_id=request.session_id,
        )

        result = await brain.run_node("content_creator", node_input.dict())

        if result.get("status") != "success":
            return ContentResponse(success=False, error=result.get("error", "Unknown error"))

        seo_score = 0.0
        suggestions: List[str] = []
        try:
            seo_result = await brain.run_node("seo_skill", {"content": result["data"]["content"]})
            seo_score = seo_result.get("data", {}).get("seo_score", 0.0)
            suggestions = seo_result.get("data", {}).get("suggestions", [])
        except Exception:
            pass

        return ContentResponse(
            success=True,
            content=result.get("data", {}).get("content", ""),
            seo_score=seo_score,
            suggestions=suggestions,
        )
    except Exception as exc:
        return ContentResponse(success=False, error=str(exc))
