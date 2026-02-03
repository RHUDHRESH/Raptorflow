"""
BCM Evolution API
=================

Exposes the Evolutionary Intelligence Engine for RaptorFlow.
Handles strategic refinement, ledger projection, and semantic compression.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from ..services.bcm_projector import BCMProjector
from ..services.bcm_service import BCMService
from ..services.bcm_sweeper import BCMSweeper

router = APIRouter(prefix="/evolution", tags=["evolution"])


class RefineRequest(BaseModel):
    ucid: str


class EvolutionStateResponse(BaseModel):
    ucid: str
    state: Dict[str, Any]


@router.post("/refine", status_code=status.HTTP_200_OK)
async def refine_strategic_context(
    request: RefineRequest, workspace_id: str = Query(..., description="Workspace ID")
):
    """
    Analyzes recent history and refines the current business context.
    """
    try:
        service = BCMService()
        result = await service.refine_context(
            workspace_id=auth.workspace_id, ucid=request.ucid
        )
        return {"success": True, "refinement": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Strategic refinement failed: {str(e)}",
        )


@router.get("/state/{ucid}", response_model=EvolutionStateResponse)
async def get_projected_state(
    ucid: str, workspace_id: str = Query(..., description="Workspace ID")
):
    """
    Returns the 'Everything' projected state for a given UCID.
    """
    try:
        projector = BCMProjector()
        state = await projector.get_latest_state(
            workspace_id=auth.workspace_id, ucid=ucid
        )
        return EvolutionStateResponse(ucid=ucid, state=state.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to project BCM state: {str(e)}",
        )


@router.post("/sweep", status_code=status.HTTP_200_OK)
async def trigger_semantic_sweep(
    request: RefineRequest, workspace_id: str = Query(..., description="Workspace ID")
):
    """
    Triggers semantic compression of old events into summaries.
    """
    try:
        sweeper = BCMSweeper()
        result = await sweeper.compress_events(
            workspace_id=auth.workspace_id, ucid=request.ucid
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic sweep failed: {str(e)}",
        )


@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze_and_sync_evolution(
    request: RefineRequest, workspace_id: str = Query(..., description="Workspace ID")
):
    """
    Recalculates the Evolution Index and syncs it to the workspace profile.
    """
    try:
        service = BCMService()
        result = await service.analyze_evolution(
            workspace_id=auth.workspace_id, ucid=request.ucid
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evolution analysis failed: {str(e)}",
        )
