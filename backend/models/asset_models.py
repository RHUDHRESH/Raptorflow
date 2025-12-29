from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class AssetBase(BaseModel):
    """Base model for Muse assets."""

    title: str = Field(..., min_length=1, max_length=255, description="Asset title")
    content: str = Field(..., min_length=1, description="Asset content")
    asset_type: str = Field(..., description="Type of asset")
    folder: str = Field(
        default="default", max_length=100, description="Folder organization"
    )
    prompt: Optional[str] = Field(
        None, max_length=2000, description="Generation prompt"
    )
    status: str = Field(default="draft", description="Asset status")
    tags: List[str] = Field(default_factory=list, description="Asset tags")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )

    @validator("asset_type")
    def validate_asset_type(cls, v):
        allowed_types = [
            "email",
            "tagline",
            "social-post",
            "ad-copy",
            "landing-page",
            "blog-post",
            "press-release",
            "video-script",
            "image-prompt",
            "other",
        ]
        if v not in allowed_types:
            raise ValueError(f'Asset type must be one of: {", ".join(allowed_types)}')
        return v

    @validator("status")
    def validate_status(cls, v):
        allowed_statuses = ["draft", "ready", "archived", "deleted"]
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class AssetCreate(AssetBase):
    """Model for creating a new asset."""

    use_speed_daemon: Optional[bool] = Field(
        default=False, description="Use Windsurf service for auto-generation"
    )


class AssetUpdate(BaseModel):
    """Model for updating an existing asset."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    folder: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    version: Optional[int] = Field(None, description="Version for optimistic locking")

    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ["draft", "ready", "archived", "deleted"]
            if v not in allowed_statuses:
                raise ValueError(
                    f'Status must be one of: {", ".join(allowed_statuses)}'
                )
        return v


class AssetResponse(AssetBase):
    """Model for asset response."""

    id: UUID
    workspace_id: UUID
    version: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    quality_score: Optional[float] = None
    generation_prompt: Optional[str] = None
    generation_model: Optional[str] = None
    generation_tokens: Optional[int] = None

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    """Model for paginated asset list response."""

    assets: List[AssetResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AssetSearchParams(BaseModel):
    """Model for asset search parameters."""

    type: Optional[str] = None
    folder: Optional[str] = None
    status: Optional[str] = None
    search_text: Optional[str] = None
    tags: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @validator("type")
    def validate_type(cls, v):
        if v is not None:
            allowed_types = [
                "email",
                "tagline",
                "social-post",
                "ad-copy",
                "landing-page",
                "blog-post",
                "press-release",
                "video-script",
                "image-prompt",
                "other",
            ]
            if v not in allowed_types:
                raise ValueError(
                    f'Asset type must be one of: {", ".join(allowed_types)}'
                )
        return v

    @validator("status")
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ["draft", "ready", "archived"]
            if v not in allowed_statuses:
                raise ValueError(
                    f'Status must be one of: {", ".join(allowed_statuses)}'
                )
        return v
