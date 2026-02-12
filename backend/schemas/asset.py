"""Asset schemas for upload/list lifecycle."""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

AssetType = Literal["image", "document", "video", "audio"]


class AssetRecordOut(BaseModel):
    id: str
    workspace_id: str
    filename: str
    original_name: str
    mime_type: str
    size_bytes: int
    storage_path: str
    public_url: Optional[str] = None
    asset_type: AssetType
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AssetUploadTargetOut(BaseModel):
    signed_url: str
    token: str
    path: str
    bucket: str


class AssetCreateSessionIn(BaseModel):
    original_name: str = Field(..., min_length=1)
    mime_type: str = Field(..., min_length=1)
    size_bytes: int = Field(..., gt=0, le=50_000_000)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssetCreateSessionOut(BaseModel):
    asset: AssetRecordOut
    upload: AssetUploadTargetOut


class AssetConfirmUploadIn(BaseModel):
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AssetListOut(BaseModel):
    assets: list[AssetRecordOut]
    total: int
    offset: int
    limit: int
