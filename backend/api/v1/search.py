"""
Search API endpoints
Handles real-time and asynchronous native search aggregation.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..services.search.orchestrator import SOTASearchOrchestrator

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    site: Optional[str] = None


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    source: str
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    count: int
    query: str


_orchestrator: Optional[SOTASearchOrchestrator] = None


def get_search_orchestrator() -> SOTASearchOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SOTASearchOrchestrator()
    return _orchestrator


@router.get("/sync", response_model=SearchResponse)
async def sync_search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Result limit"),
    site: Optional[str] = Query(None, description="Site filter"),
    user_id: str = Query(..., description="User ID"),
    orchestrator: SOTASearchOrchestrator = Depends(get_search_orchestrator),
):
    """
    Real-time aggregated search from native cluster.
    """
    try:
        results = await orchestrator.query(q, limit=limit, site=site)
        return SearchResponse(
            results=[SearchResult(**r) for r in results], count=len(results), query=q
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/async")
async def async_search_trigger(
    request: SearchRequest,
    user_id: str = Query(..., description="User ID"),
    workspace_id: str = Query(..., description="Workspace ID"),
):
    """
    Triggers an asynchronous search task (Deep Research).
    Currently implemented as a placeholder for Pub/Sub integration.
    """
    # TODO: Implement Pub/Sub message publishing
    return {
        "status": "queued",
        "message": "Deep research search task triggered",
        "query": request.query,
        "workspace_id": workspace_id,
    }
