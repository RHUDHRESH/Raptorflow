"""
Memory Router - API endpoints for semantic memory and context management.
"""

import structlog
from typing import Annotated, Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from backend.utils.auth import get_current_user_and_workspace
from backend.services.semantic_memory import semantic_memory
from backend.utils.correlation import generate_correlation_id

router = APIRouter(prefix="/memory", tags=["Memory"])
logger = structlog.get_logger(__name__)


# --- Request/Response Models ---

class StoreContextRequest(BaseModel):
    """Request to store context in semantic memory."""
    context_type: str = Field(..., description="Type of context (icp, strategy, content, campaign, etc.)")
    content: str = Field(..., description="Content to store")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "context_type": "icp",
                "content": "Target audience: B2B SaaS founders aged 30-45, focused on growth and scaling...",
                "metadata": {
                    "icp_id": "123e4567-e89b-12d3-a456-426614174000",
                    "industry": "SaaS",
                    "created_by": "research_agent"
                }
            }
        }


class StoreContextResponse(BaseModel):
    """Response after storing context."""
    context_id: str
    workspace_id: str
    context_type: str
    stored_at: str
    message: str


class RetrieveContextRequest(BaseModel):
    """Request to retrieve context using semantic search."""
    query: str = Field(..., description="Search query")
    context_type: Optional[str] = Field(None, description="Filter by context type")
    limit: int = Field(5, description="Maximum number of results", ge=1, le=50)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What do we know about our target audience's pain points?",
                "context_type": "icp",
                "limit": 5
            }
        }


class ContextItem(BaseModel):
    """Context item with metadata."""
    id: str
    content: str
    context_type: str
    metadata: Dict[str, Any]
    timestamp: Optional[str] = None
    similarity: Optional[float] = None


class RetrieveContextResponse(BaseModel):
    """Response with retrieved context items."""
    query: str
    context_type: Optional[str]
    results: List[ContextItem]
    result_count: int


class WorkspaceContextResponse(BaseModel):
    """Response with all workspace context."""
    workspace_id: str
    context_type: Optional[str]
    contexts: List[ContextItem]
    total_count: int


# --- Endpoints ---

@router.post(
    "/context",
    response_model=StoreContextResponse,
    summary="Store Context",
    description="Store context in semantic memory for later retrieval"
)
async def store_context(
    request: StoreContextRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Store context with semantic embeddings for intelligent retrieval.

    **Use Cases:**
    - Store ICP research findings
    - Save strategy decisions
    - Archive campaign learnings
    - Preserve content insights

    **Features:**
    - Semantic search capability
    - Workspace isolation
    - Metadata tagging
    - Timestamp tracking
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    logger.info(
        "Storing context",
        workspace_id=workspace_id,
        context_type=request.context_type,
        correlation_id=correlation_id
    )

    try:
        context_id = await semantic_memory.store_context(
            workspace_id=str(workspace_id),
            context_type=request.context_type,
            content=request.content,
            metadata=request.metadata,
            correlation_id=correlation_id
        )

        logger.info(
            "Context stored successfully",
            context_id=context_id,
            workspace_id=workspace_id,
            correlation_id=correlation_id
        )

        return StoreContextResponse(
            context_id=context_id,
            workspace_id=str(workspace_id),
            context_type=request.context_type,
            stored_at=datetime.now(timezone.utc).isoformat(),
            message="Context stored successfully"
        )

    except Exception as e:
        logger.error(f"Failed to store context: {e}", correlation_id=correlation_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store context: {str(e)}"
        )


@router.post(
    "/context/search",
    response_model=RetrieveContextResponse,
    summary="Search Context",
    description="Retrieve relevant context using semantic search"
)
async def search_context(
    request: RetrieveContextRequest,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Retrieve context using semantic search.

    **Features:**
    - Semantic similarity matching
    - Context type filtering
    - Configurable result limit
    - Relevance scoring

    **Example Queries:**
    - "What are our target audience's main challenges?"
    - "Show me past successful campaign strategies"
    - "What content performed best on LinkedIn?"
    """
    workspace_id = auth["workspace_id"]
    correlation_id = generate_correlation_id()

    logger.info(
        "Searching context",
        workspace_id=workspace_id,
        query=request.query,
        context_type=request.context_type,
        correlation_id=correlation_id
    )

    try:
        results = await semantic_memory.retrieve_context(
            workspace_id=str(workspace_id),
            query=request.query,
            context_type=request.context_type,
            limit=request.limit,
            correlation_id=correlation_id
        )

        context_items = [
            ContextItem(
                id=item["id"],
                content=item["content"],
                context_type=item.get("context_type", "unknown"),
                metadata=item.get("metadata", {}),
                timestamp=item.get("timestamp"),
                similarity=item.get("similarity")
            )
            for item in results
        ]

        logger.info(
            "Context search completed",
            results_found=len(context_items),
            workspace_id=workspace_id,
            correlation_id=correlation_id
        )

        return RetrieveContextResponse(
            query=request.query,
            context_type=request.context_type,
            results=context_items,
            result_count=len(context_items)
        )

    except Exception as e:
        logger.error(f"Context search failed: {e}", correlation_id=correlation_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context search failed: {str(e)}"
        )


@router.get(
    "/context/{workspace_id}",
    response_model=WorkspaceContextResponse,
    summary="Get Workspace Context",
    description="Get all context for a workspace (admin/debugging)"
)
async def get_workspace_context(
    workspace_id: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)],
    context_type: Optional[str] = Query(None, description="Filter by context type"),
    limit: int = Query(50, description="Maximum number of results", ge=1, le=500)
):
    """
    Get all stored context for a workspace.

    **Note:** This is primarily for admin/debugging purposes.
    For intelligent retrieval, use the search endpoint instead.
    """
    # Verify workspace access
    if str(auth["workspace_id"]) != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this workspace"
        )

    correlation_id = generate_correlation_id()

    logger.info(
        "Getting workspace context",
        workspace_id=workspace_id,
        context_type=context_type,
        correlation_id=correlation_id
    )

    try:
        contexts = await semantic_memory.get_workspace_context(
            workspace_id=workspace_id,
            context_type=context_type,
            limit=limit,
            correlation_id=correlation_id
        )

        context_items = [
            ContextItem(
                id=item["id"],
                content=item["content"],
                context_type=item.get("context_type", "unknown"),
                metadata=item.get("metadata", {}),
                timestamp=item.get("timestamp")
            )
            for item in contexts
        ]

        logger.info(
            "Workspace context retrieved",
            count=len(context_items),
            workspace_id=workspace_id,
            correlation_id=correlation_id
        )

        return WorkspaceContextResponse(
            workspace_id=workspace_id,
            context_type=context_type,
            contexts=context_items,
            total_count=len(context_items)
        )

    except Exception as e:
        logger.error(f"Failed to get workspace context: {e}", correlation_id=correlation_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workspace context: {str(e)}"
        )


@router.delete(
    "/context/{workspace_id}",
    summary="Delete Workspace Context",
    description="Delete all context for a workspace"
)
async def delete_workspace_context(
    workspace_id: str,
    auth: Annotated[dict, Depends(get_current_user_and_workspace)]
):
    """
    Delete all stored context for a workspace.

    **Warning:** This action cannot be undone.
    """
    # Verify workspace access
    if str(auth["workspace_id"]) != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this workspace"
        )

    correlation_id = generate_correlation_id()

    logger.warning(
        "Deleting workspace context",
        workspace_id=workspace_id,
        correlation_id=correlation_id
    )

    try:
        deleted_count = await semantic_memory.delete_workspace_context(
            workspace_id=workspace_id,
            correlation_id=correlation_id
        )

        logger.info(
            "Workspace context deleted",
            deleted_count=deleted_count,
            workspace_id=workspace_id,
            correlation_id=correlation_id
        )

        return {
            "workspace_id": workspace_id,
            "deleted_count": deleted_count,
            "message": f"Deleted {deleted_count} context items"
        }

    except Exception as e:
        logger.error(f"Failed to delete workspace context: {e}", correlation_id=correlation_id, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workspace context: {str(e)}"
        )
