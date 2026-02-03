"""
Memory API endpoints for vector, graph, episodic, and working memory.

This module provides REST API endpoints for accessing and manipulating
memory systems in the Raptorflow backend.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Workspace
from fastapi.responses import JSONResponse
from memory.controller import MemoryController
from memory.models import MemoryChunk, MemoryType
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/memory", tags=["memory"])


# Pydantic models for API requests/responses
class MemorySearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    memory_types: Optional[List[str]] = Field(
        None, description="Memory types to search"
    )
    limit: int = Field(10, description="Maximum number of results")
    workspace_id: str = Field(..., description="Workspace ID")


class MemoryStoreRequest(BaseModel):
    content: str = Field(..., description="Content to store")
    memory_type: str = Field(..., description="Type of memory")
    metadata: Optional[Dict[str, Any]] = Field(
        default={}, description="Additional metadata"
    )
    reference_id: Optional[str] = Field(None, description="Reference ID")
    reference_table: Optional[str] = Field(None, description="Reference table")
    workspace_id: str = Field(..., description="Workspace ID")


class MemoryUpdateRequest(BaseModel):
    content: Optional[str] = Field(None, description="Updated content")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")
    workspace_id: str = Field(..., description="Workspace ID")


class MemoryChunkResponse(BaseModel):
    id: str
    workspace_id: str
    memory_type: str
    content: str
    metadata: Dict[str, Any]
    score: Optional[float]
    created_at: str
    updated_at: str
    reference_id: Optional[str]
    reference_table: Optional[str]


class MemoryStatsResponse(BaseModel):
    total_chunks: int
    chunks_by_type: Dict[str, int]
    storage_bytes: int
    avg_age_days: float
    most_recent: str
    oldest: str


# Dependency to get memory controller
async def get_memory_controller() -> MemoryController:
    """Get memory controller instance."""
    return MemoryController()


@router.post("/search", response_model=List[MemoryChunkResponse])
async def search_memory(
    request: MemorySearchRequest,
    user_id: str = Query(..., description="User ID"),
    memory_controller: MemoryController = Depends(get_memory_controller),
):
    """
    Search memory across all types.

    Args:
        request: Search request containing query and filters
        current_user: Authenticated user
        memory_controller: Memory controller instance

    Returns:
        List of matching memory chunks
    """
    try:
        # Workspace access validation placeholder (workspace_id provided in request)
        workspace = {"id": request.workspace_id}

        # Convert memory types if provided
        memory_types = None
        if request.memory_types:
            memory_types = [MemoryType.from_string(t) for t in request.memory_types]

        # Perform search
        chunks = await memory_controller.search(
            workspace_id=request.workspace_id,
            query=request.query,
            memory_types=memory_types,
            limit=request.limit,
        )

        # Convert to response format
        return [
            MemoryChunkResponse(
                id=chunk.id or "",
                workspace_id=chunk.workspace_id or "",
                memory_type=chunk.memory_type.value if chunk.memory_type else "",
                content=chunk.content,
                metadata=chunk.metadata or {},
                score=chunk.score,
                created_at=chunk.created_at.isoformat() if chunk.created_at else "",
                updated_at=chunk.updated_at.isoformat() if chunk.updated_at else "",
                reference_id=chunk.reference_id,
                reference_table=chunk.reference_table,
            )
            for chunk in chunks
        ]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/store", response_model=MemoryChunkResponse)
async def store_memory(
    request: MemoryStoreRequest,
    user_id: str = Query(..., description="User ID"),
    memory_controller: MemoryController = Depends(get_memory_controller),
):
    """
    Store content in memory.

    Args:
        request: Store request with content and metadata
        current_user: Authenticated user
        memory_controller: Memory controller instance

    Returns:
        Created memory chunk
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Create memory chunk
        chunk = MemoryChunk(
            workspace_id=request.workspace_id,
            memory_type=MemoryType.from_string(request.memory_type),
            content=request.content,
            metadata=request.metadata,
            reference_id=request.reference_id,
            reference_table=request.reference_table,
        )

        # Store chunk
        stored_chunk = await memory_controller.store(chunk)

        return MemoryChunkResponse(
            id=stored_chunk.id or "",
            workspace_id=stored_chunk.workspace_id or "",
            memory_type=(
                stored_chunk.memory_type.value if stored_chunk.memory_type else ""
            ),
            content=stored_chunk.content,
            metadata=stored_chunk.metadata or {},
            score=stored_chunk.score,
            created_at=(
                stored_chunk.created_at.isoformat() if stored_chunk.created_at else ""
            ),
            updated_at=(
                stored_chunk.updated_at.isoformat() if stored_chunk.updated_at else ""
            ),
            reference_id=stored_chunk.reference_id,
            reference_table=stored_chunk.reference_table,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{chunk_id}", response_model=MemoryChunkResponse)
async def get_memory_chunk(
    chunk_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    user_id: str = Query(..., description="User ID"),
    memory_controller: MemoryController = Depends(get_memory_controller),
):
    """
    Get a specific memory chunk by ID.

    Args:
        chunk_id: Memory chunk ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        memory_controller: Memory controller instance

    Returns:
        Memory chunk
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Retrieve chunk
        chunk = await memory_controller.retrieve(chunk_id, workspace_id)

        if not chunk:
            raise HTTPException(status_code=404, detail="Memory chunk not found")

        return MemoryChunkResponse(
            id=chunk.id or "",
            workspace_id=chunk.workspace_id or "",
            memory_type=chunk.memory_type.value if chunk.memory_type else "",
            content=chunk.content,
            metadata=chunk.metadata or {},
            score=chunk.score,
            created_at=chunk.created_at.isoformat() if chunk.created_at else "",
            updated_at=chunk.updated_at.isoformat() if chunk.updated_at else "",
            reference_id=chunk.reference_id,
            reference_table=chunk.reference_table,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting memory chunk: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{chunk_id}", response_model=MemoryChunkResponse)
async def update_memory_chunk(
    chunk_id: str,
    request: MemoryUpdateRequest,
    user_id: str = Query(..., description="User ID"),
    memory_controller: MemoryController = Depends(get_memory_controller),
):
    """
    Update a memory chunk.

    Args:
        chunk_id: Memory chunk ID
        request: Update request
        current_user: Authenticated user
        memory_controller: Memory controller instance

    Returns:
        Updated memory chunk
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Get existing chunk
        existing_chunk = await memory_controller.retrieve(
            chunk_id, request.workspace_id
        )
        if not existing_chunk:
            raise HTTPException(status_code=404, detail="Memory chunk not found")

        # Update chunk
        if request.content is not None:
            existing_chunk.content = request.content
        if request.metadata is not None:
            existing_chunk.metadata = request.metadata

        updated_chunk = await memory_controller.update(existing_chunk)

        return MemoryChunkResponse(
            id=updated_chunk.id or "",
            workspace_id=updated_chunk.workspace_id or "",
            memory_type=(
                updated_chunk.memory_type.value if updated_chunk.memory_type else ""
            ),
            content=updated_chunk.content,
            metadata=updated_chunk.metadata or {},
            score=updated_chunk.score,
            created_at=(
                updated_chunk.created_at.isoformat() if updated_chunk.created_at else ""
            ),
            updated_at=(
                updated_chunk.updated_at.isoformat() if updated_chunk.updated_at else ""
            ),
            reference_id=updated_chunk.reference_id,
            reference_table=updated_chunk.reference_table,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating memory chunk: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{chunk_id}")
async def delete_memory_chunk(
    chunk_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    user_id: str = Query(..., description="User ID"),
    memory_controller: MemoryController = Depends(get_memory_controller),
):
    """
    Delete a memory chunk.

    Args:
        chunk_id: Memory chunk ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        memory_controller: Memory controller instance

    Returns:
        Success message
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Delete chunk
        success = await memory_controller.delete(chunk_id, workspace_id)

        if not success:
            raise HTTPException(status_code=404, detail="Memory chunk not found")

        return {"message": "Memory chunk deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting memory chunk: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(
    workspace_id: str = Query(..., description="Workspace ID"),
    user_id: str = Query(..., description="User ID"),
    memory_controller: MemoryController = Depends(get_memory_controller),
):
    """
    Get memory statistics for a workspace.

    Args:
        workspace_id: Workspace ID
        current_user: Authenticated user
        memory_controller: Memory controller instance

    Returns:
        Memory statistics
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get stats
        stats = await memory_controller.get_stats(workspace_id)

        return MemoryStatsResponse(
            total_chunks=stats.get("total_chunks", 0),
            chunks_by_type=stats.get("chunks_by_type", {}),
            storage_bytes=stats.get("storage_bytes", 0),
            avg_age_days=stats.get("avg_age_days", 0.0),
            most_recent=stats.get("most_recent", ""),
            oldest=stats.get("oldest", ""),
        )

    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types", response_model=List[str])
async def get_memory_types(user_id: str = Query(..., description="User ID")):
    """
    Get available memory types.

    Args:
        current_user: Authenticated user

    Returns:
        List of memory types
    """
    try:
        return MemoryType.get_all_types()
    except Exception as e:
        logger.error(f"Error getting memory types: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/context")
async def get_memory_context(
    request: MemorySearchRequest,
    user_id: str = Query(..., description="User ID"),
    memory_controller: MemoryController = Depends(get_memory_controller),
):
    """
    Get relevant context for a query.

    Args:
        request: Context request
        current_user: Authenticated user
        memory_controller: Memory controller instance

    Returns:
        Context string and metadata
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Get context
        context_data = await memory_controller.get_context(
            workspace_id=request.workspace_id, query=request.query, max_tokens=2000
        )

        return {
            "context": context_data.get("context", ""),
            "chunks_used": context_data.get("chunks_used", []),
            "tokens_used": context_data.get("tokens_used", 0),
        }

    except Exception as e:
        logger.error(f"Error getting memory context: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/clear")
async def clear_workspace_memory(
    workspace_id: str = Query(..., description="Workspace ID"),
    memory_type: Optional[str] = Query(None, description="Memory type to clear"),
    user_id: str = Query(..., description="User ID"),
    memory_controller: MemoryController = Depends(get_memory_controller),
):
    """
    Clear memory for a workspace.

    Args:
        workspace_id: Workspace ID
        memory_type: Optional memory type to clear
        current_user: Authenticated user
        memory_controller: Memory controller instance

    Returns:
        Success message
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Clear memory
        target_type = MemoryType.from_string(memory_type) if memory_type else None
        deleted_count = await memory_controller.clear_workspace(
            workspace_id=workspace_id, memory_type=target_type
        )

        return {
            "message": f"Cleared {deleted_count} memory chunks",
            "deleted_count": deleted_count,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error clearing workspace memory: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
