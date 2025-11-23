"""
Shared Pydantic base classes for backend models.

This module provides the foundational BaseSchema class that all RaptorFlow models
extend. It includes common metadata fields (id, workspace_id, timestamps) and
validation helpers to ensure data consistency across the system.

The BaseSchema uses Pydantic v2 features for robust validation and serialization,
with ORM mode enabled for seamless database integration.
"""

from __future__ import annotations

from abc import ABC
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, UUID4, ConfigDict


class BaseSchema(BaseModel, ABC):
    """
    Abstract base schema with common identifiers and timestamps.

    All RaptorFlow entity models should extend this class to ensure
    consistent metadata tracking and serialization behavior.

    Attributes:
        id: Unique identifier for the entity (auto-generated UUID4)
        workspace_id: Workspace scoping identifier for multi-tenancy
        created_at: Timezone-aware timestamp of entity creation
        updated_at: Timezone-aware timestamp of last modification

    Configuration:
        - ORM mode enabled (from_attributes=True) for database ORM integration
        - Alias support enabled (populate_by_name=True) for flexible field naming
        - Automatic UUID and datetime validation

    Example:
        ```python
        class MyModel(BaseSchema):
            name: str
            value: int

        instance = MyModel(name="test", value=42)
        # id and timestamps are automatically populated
        ```
    """

    id: UUID4 = Field(
        default_factory=uuid4,
        description="Unique identifier (UUID4)",
    )
    workspace_id: Optional[UUID4] = Field(
        default=None,
        description="Workspace scoping identifier for multi-tenant isolation",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when this entity was created (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when this entity was last updated (UTC)",
    )

    model_config = ConfigDict(
        populate_by_name=True,  # Allow both field names and aliases
        from_attributes=True,  # Enable ORM mode for SQLAlchemy/database models
    )

    @field_validator("id", "workspace_id", mode="before")
    @classmethod
    def _validate_uuid(cls, value: object) -> object:
        """
        Coerce incoming IDs into UUID instances when possible.

        Accepts UUID objects, strings, or None. Invalid values are passed
        through to let Pydantic's native validation handle the error.

        Args:
            value: Input value that should be a UUID

        Returns:
            UUID instance or original value if conversion fails
        """
        if value is None or isinstance(value, UUID):
            return value
        try:
            return UUID(str(value))
        except (ValueError, TypeError):
            return value

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def _ensure_datetime(cls, value: object) -> datetime:
        """
        Guarantee timezone-aware datetimes for persistence.

        Converts naive datetimes to UTC-aware, parses ISO format strings,
        and ensures all timestamp fields are timezone-aware to prevent
        database serialization issues.

        Args:
            value: Input value that should be a datetime

        Returns:
            Timezone-aware datetime (UTC)
        """
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
        """
        Update the `updated_at` timestamp to the current UTC time.

        Call this method when making modifications to the model to
        track when changes occurred.

        Example:
            ```python
            model.some_field = new_value
            model.touch()  # Mark as modified
            ```
        """
        self.updated_at = datetime.now(timezone.utc)

    @staticmethod
    def validate_uuid(value: Any) -> UUID:
        """
        Static helper to validate and convert UUID values.

        Use this in custom validators or business logic that needs
        to ensure a value is a valid UUID.

        Args:
            value: Input value to validate as UUID

        Returns:
            Valid UUID instance

        Raises:
            ValueError: If the value cannot be converted to a UUID

        Example:
            ```python
            try:
                valid_id = BaseSchema.validate_uuid(user_input)
            except ValueError:
                # Handle invalid UUID
                pass
            ```
        """
        if isinstance(value, UUID):
            return value
        if isinstance(value, str):
            try:
                return UUID(value)
            except ValueError as e:
                raise ValueError(f"Invalid UUID format: {value}") from e
        raise ValueError(f"Cannot convert {type(value).__name__} to UUID: {value}")

    @staticmethod
    def validate_positive_number(value: float, field_name: str = "value") -> float:
        """
        Static helper to validate positive numbers.

        Args:
            value: Number to validate
            field_name: Name of the field (for error messages)

        Returns:
            The validated number

        Raises:
            ValueError: If the number is not positive
        """
        if value <= 0:
            raise ValueError(f"{field_name} must be positive, got {value}")
        return value

    @staticmethod
    def validate_non_empty_string(value: str, field_name: str = "value") -> str:
        """
        Static helper to validate non-empty strings.

        Args:
            value: String to validate
            field_name: Name of the field (for error messages)

        Returns:
            The validated string (stripped of whitespace)

        Raises:
            ValueError: If the string is empty or whitespace-only
        """
        if not value or not value.strip():
            raise ValueError(f"{field_name} cannot be empty")
        return value.strip()

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        """
        Convert model to dictionary with optional exclusion of None values.

        Args:
            exclude_none: If True, exclude fields with None values

        Returns:
            Dictionary representation of the model
        """
        return self.model_dump(exclude_none=exclude_none, mode='python')
