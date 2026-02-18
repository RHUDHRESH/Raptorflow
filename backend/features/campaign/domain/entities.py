"""
Campaign domain entities.

Pure Python business objects with no infrastructure dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from backend.core.exceptions import ValidationError, NotFoundError


# Allowed values (from original API)
ALLOWED_OBJECTIVES = {"acquire", "convert", "launch", "proof", "retain", "reposition"}
ALLOWED_STATUSES = {"planned", "active", "paused", "wrapup", "archived"}
DEFAULT_OBJECTIVE = "acquire"
DEFAULT_STATUS = "active"


@dataclass
class Campaign:
    """
    Campaign domain entity.

    This is a pure domain object with business logic.
    """

    id: str
    workspace_id: str
    title: str
    description: Optional[str] = None
    objective: str = DEFAULT_OBJECTIVE
    status: str = DEFAULT_STATUS
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate the campaign after construction."""
        self._validate()

    def _validate(self) -> None:
        """Validate business rules."""
        if not self.title or not self.title.strip():
            raise ValidationError("Campaign title cannot be empty")

        if self.objective not in ALLOWED_OBJECTIVES:
            raise ValidationError(
                f"Invalid objective '{self.objective}'. Allowed: {ALLOWED_OBJECTIVES}"
            )

        if self.status not in ALLOWED_STATUSES:
            raise ValidationError(
                f"Invalid status '{self.status}'. Allowed: {ALLOWED_STATUSES}"
            )

    def activate(self) -> None:
        """Activate the campaign."""
        if self.status == "archived":
            raise ValidationError("Cannot activate an archived campaign")
        self.status = "active"
        self.updated_at = datetime.utcnow()

    def pause(self) -> None:
        """Pause the campaign."""
        if self.status == "archived":
            raise ValidationError("Cannot pause an archived campaign")
        self.status = "paused"
        self.updated_at = datetime.utcnow()

    def archive(self) -> None:
        """Archive the campaign."""
        self.status = "archived"
        self.updated_at = datetime.utcnow()

    def update_title(self, new_title: str) -> None:
        """Update the campaign title."""
        if not new_title or not new_title.strip():
            raise ValidationError("Campaign title cannot be empty")
        self.title = new_title.strip()
        self.updated_at = datetime.utcnow()

    def update_objective(self, new_objective: str) -> None:
        """Update the campaign objective."""
        normalized = new_objective.strip().lower()
        if normalized not in ALLOWED_OBJECTIVES:
            raise ValidationError(
                f"Invalid objective '{new_objective}'. Allowed: {ALLOWED_OBJECTIVES}"
            )
        self.objective = normalized
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert to dictionary for persistence."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "title": self.title,
            "description": self.description,
            "objective": self.objective,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Campaign":
        """Create from dictionary (e.g., from database)."""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

        return cls(
            id=data["id"],
            workspace_id=data["workspace_id"],
            title=data["title"],
            description=data.get("description"),
            objective=data.get("objective", DEFAULT_OBJECTIVE),
            status=data.get("status", DEFAULT_STATUS),
            created_at=created_at,
            updated_at=updated_at,
        )
