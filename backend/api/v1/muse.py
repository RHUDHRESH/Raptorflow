from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.auth import get_current_user, get_tenant_id
from backend.graphs.muse_create import build_muse_spine
from backend.models.cognitive import CognitiveStatus

router = APIRouter(prefix="/v1/muse", tags=["muse"])


class MuseCreateRequest(BaseModel):
    prompt: str
    workspace_id: str
    thread_id: Optional[str] = None


class MuseResponse(BaseModel):
    status: str
    asset_content: Optional[str] = None
    thread_id: str
    quality_score: float = 0.0


@router.post("/create", response_model=MuseResponse)
async def create_muse_asset(
    request: MuseCreateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """
    SOTA Endpoint: Triggers the full Muse Cognitive Spine.
    """
    try:
        spine = build_muse_spine()

        # Initialize state
        initial_state = {
            "raw_prompt": request.prompt,
            "workspace_id": request.workspace_id,
            "tenant_id": str(tenant_id),
            "messages": [],
            "generated_assets": [],
            "reflection_log": [],
            "status": CognitiveStatus.IDLE,
            "cost_accumulator": 0.0,
            "token_usage": {},
            "brief": {},
            "research_bundle": {},
            "quality_score": 0.0,
            "error": None,
        }

        base_thread_id = request.thread_id or str(uuid4())
        thread_id = f"{tenant_id}:{current_user['id']}:{base_thread_id}"

        # Configuration for LangGraph (thread_id for persistence)
        config = {"configurable": {"thread_id": thread_id}}

        # Execute the graph
        # For a production build, this might be backgrounded or streamed.
        # Here we invoke it synchronously for simplicity in the current endpoint.
        result = await spine.ainvoke(initial_state, config=config)

        final_asset = (
            result["generated_assets"][-1]["content"]
            if result["generated_assets"]
            else "Generation failed."
        )

        return MuseResponse(
            status=result["status"],
            asset_content=final_asset,
            thread_id=thread_id,
            quality_score=result.get("quality_score", 0.0),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def muse_health():
    return {"status": "healthy", "engine": "Muse Creative Engine"}
