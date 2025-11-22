"""
Shared Pydantic base classes for backend models.
Provides common metadata fields and lightweight validation helpers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class BaseSchema(BaseModel):
    """Base schema with common identifiers and timestamps."""

    id: Optional[UUID] = Field(default_factory=uuid4)
    workspace_id: Optional[UUID] = Field(default=None, description="Workspace scoping identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        from_attributes = True

    @field_validator("id", "workspace_id", mode="before")
    @classmethod
    def _validate_uuid(cls, value: object) -> object:
        """Coerce incoming ids into UUID instances when possible."""
        if value is None or isinstance(value, UUID):
            return value
        try:
            return UUID(str(value))
        except (ValueError, TypeError):
            return value

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _ensure_datetime(cls, value: object) -> datetime:
        """Guarantee timezone-aware datetimes for persistence."""
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value)
                return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        return datetime.now(timezone.utc)

    def touch(self) -> None:
        """Update the `updated_at` timestamp."""
        self.updated_at = datetime.now(timezone.utc)
