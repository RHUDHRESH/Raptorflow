import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class BaseRequestModel(BaseModel):
    """Base model for all API requests with common validation."""

    class Config:
        extra = "forbid"  # Prevent unknown fields
        validate_assignment = True


class CampaignCreateRequest(BaseRequestModel):
    """Request model for creating campaigns."""

    title: str = Field(..., min_length=1, max_length=200, description="Campaign title")
    objective: str = Field(
        ..., min_length=10, max_length=1000, description="Campaign objective"
    )
    status: Optional[str] = Field("draft", pattern="^(draft|active|paused|completed)$")

    @validator("title")
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        # Remove any potentially harmful characters
        return re.sub(r'[<>"\']', "", v.strip())


class CampaignUpdateRequest(BaseRequestModel):
    """Request model for updating campaigns."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    objective: Optional[str] = Field(None, min_length=10, max_length=1000)
    status: Optional[str] = Field(None, pattern="^(draft|active|paused|completed)$")
    arc_data: Optional[Dict[str, Any]] = None
    kpi_targets: Optional[Dict[str, Any]] = None


class MoveCreateRequest(BaseRequestModel):
    """Request model for creating moves."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    priority: Optional[int] = Field(3, ge=1, le=5)
    move_type: str = Field(..., pattern="^(content|paid|organic|technical|research)$")
    tool_requirements: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class AssetCreateRequest(BaseRequestModel):
    """Request model for creating assets."""

    content: str = Field(..., min_length=1, max_length=50000)
    asset_type: str = Field(..., pattern="^(image|text|video|document|creative)$")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class VectorSearchRequest(BaseRequestModel):
    """Request model for vector search."""

    embedding: List[float] = Field(..., min_items=1, max_items=1536)
    limit: Optional[int] = Field(10, ge=1, le=100)
    memory_type: Optional[str] = Field("semantic", pattern="^(semantic|episodic)$")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("embedding")
    def validate_embedding(cls, v):
        if len(v) == 0:
            raise ValueError("Embedding cannot be empty")
        # Check for valid float values
        for i, val in enumerate(v):
            if not isinstance(val, (int, float)):
                raise ValueError(f"Embedding value at index {i} is not a number: {val}")
            if abs(val) > 10:  # Basic sanity check
                raise ValueError(f"Embedding value at index {i} seems invalid: {val}")
        return v


class MemorySaveRequest(BaseRequestModel):
    """Request model for saving memory."""

    content: str = Field(..., min_length=1, max_length=10000)
    embedding: List[float] = Field(..., min_items=1, max_items=1536)
    memory_type: str = Field("semantic", pattern="^(semantic|episodic)$")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()


class HealthCheckRequest(BaseRequestModel):
    """Request model for health checks (minimal)."""

    detailed: Optional[bool] = Field(False)
