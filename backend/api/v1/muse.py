from typing import Any, Dict, List, Optional
from uuid import UUID

import psycopg
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel, Field

from core.auth import get_internal_or_user, get_tenant_id
from core.config import get_settings
from db import get_db_connection, save_asset_db, vector_search
from graphs.muse_create import build_muse_spine
from graphs.rag_ingest import rag_ingest_graph
from inference import InferenceProvider
from models.cognitive import CognitiveStatus, LifecycleState
from services.storage_service import MuseAssetManager

router = APIRouter(prefix="/v1/muse", tags=["muse"])


class MuseCreateRequest(BaseModel):
    prompt: str
    workspace_id: Optional[str] = None
    thread_id: Optional[str] = None


class MuseResponse(BaseModel):
    status: str
    asset_content: Optional[str] = None
    thread_id: str
    quality_score: float = 0.0


ALLOWED_MUSE_ASSET_TYPES = {
    "email",
    "social_post",
    "meme",
    "text",
    "image",
    "video",
    "document",
}

ALLOWED_MUSE_STATUSES = {"generating", "ready", "blocked", "archived"}


def _normalize_asset_type(asset_type: Optional[str]) -> str:
    if not asset_type:
        return "text"
    candidate = asset_type.replace("-", "_").lower()
    if candidate in ALLOWED_MUSE_ASSET_TYPES:
        return candidate
    return "text"


def _normalize_status(status_value: Optional[str]) -> str:
    if not status_value:
        return "ready"
    candidate = status_value.lower()
    if candidate in ALLOWED_MUSE_STATUSES:
        return candidate
    return "ready"


class MuseAssetCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    asset_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: Optional[str] = None
    quality_score: Optional[float] = None
    generation_prompt: Optional[str] = None
    generation_model: Optional[str] = None
    generation_tokens: Optional[int] = None
    tags: Optional[List[str]] = None


class MuseAssetUpdateRequest(BaseModel):
    content: Optional[str] = None
    asset_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    quality_score: Optional[float] = None
    tags: Optional[List[str]] = None


class MuseAssetRecord(BaseModel):
    id: str
    content: str
    asset_type: str
    metadata: Dict[str, Any]
    status: str
    quality_score: Optional[float] = None
    generation_prompt: Optional[str] = None
    generation_model: Optional[str] = None
    generation_tokens: Optional[int] = None
    tags: Optional[List[str]] = None
    created_at: str
    updated_at: str


class MuseSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    limit: int = Field(5, ge=1, le=25)
    filters: Optional[Dict[str, Any]] = None


class MuseIngestRequest(BaseModel):
    content: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


ASSET_SELECT_COLUMNS = """
    id,
    content,
    asset_type,
    metadata,
    status,
    quality_score,
    generation_prompt,
    generation_model,
    generation_tokens,
    tags,
    created_at,
    updated_at
"""


def _map_asset_row(row) -> MuseAssetRecord:
    created_at = row[10].isoformat() if hasattr(row[10], "isoformat") else str(row[10])
    updated_at = row[11].isoformat() if hasattr(row[11], "isoformat") else str(row[11])
    return MuseAssetRecord(
        id=str(row[0]),
        content=row[1],
        asset_type=row[2] or "text",
        metadata=row[3] or {},
        status=row[4] or "ready",
        quality_score=row[5],
        generation_prompt=row[6],
        generation_model=row[7],
        generation_tokens=row[8],
        tags=row[9] or [],
        created_at=created_at,
        updated_at=updated_at,
    )


@router.post("/create", response_model=MuseResponse)
async def create_muse_asset(
    request: MuseCreateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_internal_or_user),
):
    """
    SOTA Endpoint: Triggers the full Muse Cognitive Spine.
    """
    try:
        spine = build_muse_spine()

        workspace_id = request.workspace_id or str(tenant_id)

        # Initialize state
        initial_state = {
            "raw_prompt": request.prompt,
            "workspace_id": workspace_id,
            "tenant_id": str(tenant_id),
            "messages": [],
            "generated_assets": [],
            "reflection_log": [],
            "status": CognitiveStatus.IDLE,
            "lifecycle_state": LifecycleState.IDLE,
            "lifecycle_transitions": [],
            "cost_accumulator": 0.0,
            "token_usage": {},
            "brief": {},
            "research_bundle": {},
            "quality_score": 0.0,
            "error": None,
        }

        # Configuration for LangGraph (thread_id for persistence)
        config = {"configurable": {"thread_id": request.thread_id or "default"}}

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
            thread_id=request.thread_id or "default",
            quality_score=result.get("quality_score", 0.0),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assets", response_model=List[MuseAssetRecord])
async def list_muse_assets(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_internal_or_user),
):
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT {ASSET_SELECT_COLUMNS}
                FROM muse_assets
                WHERE workspace_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (str(tenant_id), limit, offset),
            )
            rows = await cur.fetchall()
    return [_map_asset_row(row) for row in rows]


@router.get("/assets/{asset_id}", response_model=MuseAssetRecord)
async def get_muse_asset(
    asset_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_internal_or_user),
):
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT {ASSET_SELECT_COLUMNS}
                FROM muse_assets
                WHERE id = %s AND workspace_id = %s
                """,
                (asset_id, str(tenant_id)),
            )
            row = await cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Muse asset not found")
    return _map_asset_row(row)


@router.post("/assets", response_model=MuseAssetRecord)
async def create_muse_asset_record(
    request: MuseAssetCreateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_internal_or_user),
):
    asset_data = {
        "content": request.content,
        "asset_type": _normalize_asset_type(request.asset_type),
        "metadata": request.metadata or {},
        "status": _normalize_status(request.status),
        "quality_score": request.quality_score,
        "generation_prompt": request.generation_prompt,
        "generation_model": request.generation_model,
        "generation_tokens": request.generation_tokens,
        "tags": request.tags,
    }
    asset_id = await save_asset_db(str(tenant_id), asset_data)
    return await get_muse_asset(asset_id, tenant_id=tenant_id, _current_user=_current_user)


@router.put("/assets/{asset_id}", response_model=MuseAssetRecord)
async def update_muse_asset(
    asset_id: str,
    request: MuseAssetUpdateRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_internal_or_user),
):
    updates = []
    params: List[Any] = []

    if request.content is not None:
        updates.append("content = %s")
        params.append(request.content)
    if request.asset_type is not None:
        updates.append("asset_type = %s")
        params.append(_normalize_asset_type(request.asset_type))
    if request.metadata is not None:
        updates.append("metadata = %s")
        params.append(psycopg.types.json.Jsonb(request.metadata))
    if request.status is not None:
        updates.append("status = %s")
        params.append(_normalize_status(request.status))
    if request.quality_score is not None:
        updates.append("quality_score = %s")
        params.append(request.quality_score)
    if request.tags is not None:
        updates.append("tags = %s")
        params.append(request.tags)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided.",
        )

    updates.append("updated_at = now()")
    params.extend([asset_id, str(tenant_id)])

    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                UPDATE muse_assets
                SET {", ".join(updates)}
                WHERE id = %s AND workspace_id = %s
                RETURNING {ASSET_SELECT_COLUMNS}
                """,
                tuple(params),
            )
            row = await cur.fetchone()
            await conn.commit()
    if not row:
        raise HTTPException(status_code=404, detail="Muse asset not found")
    return _map_asset_row(row)


@router.delete("/assets/{asset_id}")
async def delete_muse_asset(
    asset_id: str,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_internal_or_user),
):
    async with get_db_connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                DELETE FROM muse_assets
                WHERE id = %s AND workspace_id = %s
                RETURNING id;
                """,
                (asset_id, str(tenant_id)),
            )
            row = await cur.fetchone()
            await conn.commit()
    if not row:
        raise HTTPException(status_code=404, detail="Muse asset not found")
    return {"status": "deleted", "id": str(row[0])}


@router.post("/assets/upload")
async def upload_muse_asset(
    file: UploadFile = File(...),
    public: bool = False,
    folder: str = "generated",
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_internal_or_user),
):
    settings = get_settings()
    manager = MuseAssetManager(bucket_name=settings.GCS_MUSE_CREATIVES_BUCKET)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    blob_name = manager.upload_asset(
        file_content=content,
        filename=file.filename or "muse_asset",
        content_type=file.content_type or "application/octet-stream",
        tenant_id=str(tenant_id),
        folder=folder,
    )

    asset_url = (
        manager.make_blob_public(blob_name)
        if public
        else manager.generate_signed_url(blob_name)
    )

    asset_type = "image" if (file.content_type or "").startswith("image/") else "document"
    metadata = {
        "gcs_bucket": settings.GCS_MUSE_CREATIVES_BUCKET,
        "gcs_path": blob_name,
        "content_type": file.content_type,
        "original_filename": file.filename,
        "public": public,
    }
    asset_id = await save_asset_db(
        str(tenant_id),
        {
            "content": asset_url,
            "asset_type": asset_type,
            "metadata": metadata,
            "status": "ready",
        },
    )

    return {"id": asset_id, "url": asset_url, "status": "uploaded"}


@router.post("/search")
async def search_muse_assets(
    request: MuseSearchRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_internal_or_user),
):
    embedder = InferenceProvider.get_embeddings()
    query_embedding = await embedder.aembed_query(request.query)
    results = await vector_search(
        workspace_id=str(tenant_id),
        embedding=query_embedding,
        table="muse_assets",
        limit=request.limit,
        filters=request.filters,
    )
    formatted = [
        {"id": r[0], "content": r[1], "metadata": r[2], "similarity": r[3]}
        for r in results
    ]
    return {"results": formatted, "total_found": len(formatted)}


@router.post("/ingest")
async def ingest_muse_content(
    request: MuseIngestRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_internal_or_user),
):
    state = {
        "workspace_id": str(tenant_id),
        "content": request.content,
        "filename": request.filename,
        "metadata": request.metadata,
    }
    result = await rag_ingest_graph.ainvoke(state)
    chunks = result.get("chunks", [])
    return {"status": result.get("status", "complete"), "chunks_ingested": len(chunks)}


@router.get("/health")
async def muse_health():
    return {"status": "healthy", "engine": "Muse Creative Engine"}
