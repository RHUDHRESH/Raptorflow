"""
Titan SOTA Intelligence API Endpoints
Handles multi-modal research requests (LITE, RESEARCH, DEEP).
"""

from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.core.auth import get_current_user, get_workspace_id
from backend.core.models import User
from backend.services.titan.orchestrator import TitanOrchestrator, TitanMode

router = APIRouter(prefix="/titan", tags=["titan"])

class TitanResearchRequest(BaseModel):
    query: str = Field(..., description="The primary research objective or company name.")
    mode: str = Field(default="LITE", description="Research mode: LITE, RESEARCH, or DEEP.")
    focus_areas: Optional[List[str]] = Field(default_factory=list, description="Optional focus areas (e.g. pricing, ICP).")
    max_results: Optional[int] = Field(None, description="Limit on the number of results.")
    use_stealth: bool = Field(default=True, description="Whether to use stealth escalation ladder.")

class TitanResearchResponse(BaseModel):
    query: str
    mode: str
    results: List[Dict[str, Any]]
    count: int
    engine: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

_orchestrator: Optional[TitanOrchestrator] = None

def get_titan_orchestrator() -> TitanOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TitanOrchestrator()
    return _orchestrator

@router.post("/research", response_model=TitanResearchResponse)
async def execute_research(
    request: TitanResearchRequest,
    user: User = Depends(get_current_user),
    orchestrator: TitanOrchestrator = Depends(get_titan_orchestrator),
):
    """
    Execute tiered research (Lite, Research, or Deep).
    """
    try:
        result = await orchestrator.execute(
            query=request.query,
            mode=request.mode,
            focus_areas=request.focus_areas,
            max_results=request.max_results or (10 if request.mode == "RESEARCH" else 50 if request.mode == "DEEP" else 10),
            use_stealth=request.use_stealth
        )
        
        return TitanResearchResponse(
            query=result["query"],
            mode=result["mode"],
            results=result.get("results", []),
            count=result.get("count", 0),
            engine="Titan SOTA Intelligence",
            timestamp=result.get("timestamp", ""),
            metadata=result.get("metadata")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Titan research failed: {str(e)}")

@router.get("/status/{request_id}")
async def get_research_status(
    request_id: str,
    user: User = Depends(get_current_user)
):
    """
    Get status of a long-running DEEP research task.
    (Placeholder for async implementation)
    """
    return {"request_id": request_id, "status": "completed", "message": "Result available in Evidence Vault"}
