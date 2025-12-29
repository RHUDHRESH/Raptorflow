from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Header,
    HTTPException,
    Query,
    UploadFile,
    status,
)

from core.auth import get_current_user, get_tenant_id
from core.config import get_settings
from models.asset_models import (
    AssetCreate,
    AssetListResponse,
    AssetResponse,
    AssetSearchParams,
    AssetUpdate,
)
from services.asset_service import AssetService
from services.storage_service import BrandAssetManager

router = APIRouter(prefix="/v1/assets", tags=["assets"])


async def get_brand_asset_manager():
    settings = get_settings()
    return BrandAssetManager(bucket_name=settings.GCS_INGEST_BUCKET)


@router.post("/upload-logo")
async def upload_logo(
    file: UploadFile = File(...),
    public: bool = False,
    authorization: Optional[str] = Header(None),
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
    manager: BrandAssetManager = Depends(get_brand_asset_manager),
):
    """
    Industrial endpoint for brand logo uploads.
    Supports PNG, JPG, SVG.
    """
    # 1. Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/svg+xml"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, detail="Unsupported file type. Use PNG, JPG, or SVG."
        )

    # 2. Read content
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB limit
        raise HTTPException(status_code=400, detail="File too large. Maximum 5MB.")

    # 3. Authorize public assets if requested
    if public:
        current_user = await get_current_user(authorization)
        if current_user.get("role") not in {"founder", "admin"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to publish public assets.",
            )

    # 4. Upload to GCS
    try:
        blob_name = manager.upload_logo(
            file_content=content,
            filename=file.filename,
            content_type=file.content_type,
            tenant_id=str(tenant_id),
        )
        if public:
            asset_url = manager.make_blob_public(blob_name)
        else:
            asset_url = manager.generate_signed_url(blob_name)
        return {"url": asset_url, "status": "success", "public": public}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("", response_model=AssetListResponse)
async def list_assets(
    type: Optional[str] = Query(None, description="Filter by asset type"),
    folder: Optional[str] = Query(None, description="Filter by folder"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search_text: Optional[str] = Query(
        None, description="Search in title, content, and prompt"
    ),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """
    List assets for a workspace with filtering and pagination.
    """
    search_params = AssetSearchParams(
        type=type,
        folder=folder,
        status=status,
        search_text=search_text,
        tags=tags,
        page=page,
        page_size=page_size,
    )

    assets, total = await AssetService.get_assets(tenant_id, search_params)

    total_pages = (total + page_size - 1) // page_size

    return AssetListResponse(
        assets=assets,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("", response_model=AssetResponse, status_code=201)
async def create_asset(
    asset_data: AssetCreate,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """
    Create a new asset.
    """
    return await AssetService.create_asset(tenant_id, asset_data)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """
    Get a single asset by ID.
    """
    asset = await AssetService.get_asset_by_id(tenant_id, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: UUID,
    update_data: AssetUpdate,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """
    Update an asset with optimistic locking.
    """
    try:
        return await AssetService.update_asset(tenant_id, asset_id, update_data)
    except Exception as e:
        if "has been modified by another user" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        elif "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Asset not found")
        elif "has been deleted" in str(e).lower():
            raise HTTPException(status_code=410, detail="Asset has been deleted")
        else:
            raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{asset_id}", status_code=204)
async def delete_asset(
    asset_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """
    Soft delete an asset.
    """
    success = await AssetService.delete_asset(tenant_id, asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    return None


@router.post("/{asset_id}/duplicate", response_model=AssetResponse, status_code=201)
async def duplicate_asset(
    asset_id: UUID,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """
    Duplicate an asset with '(Copy)' appended to the title.
    """
    try:
        return await AssetService.duplicate_asset(tenant_id, asset_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Asset not found")
        else:
            raise HTTPException(status_code=500, detail=str(e))
