from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status

from core.auth import get_current_user, get_tenant_id
from core.config import get_settings
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
