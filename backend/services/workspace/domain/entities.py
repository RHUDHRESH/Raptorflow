"""
Workspace domain entities.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Workspace:
    """Workspace domain entity."""

    id: str
    name: str
    slug: str
    owner_id: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "owner_id": self.owner_id,
            "settings": self.settings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Workspace":
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))

        return cls(
            id=data["id"],
            name=data.get("name", ""),
            slug=data.get("slug", ""),
            owner_id=data.get("owner_id"),
            settings=data.get("settings"),
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class OnboardingStatus:
    """Onboarding status for a workspace."""

    workspace_id: str
    completed_steps: list[str]
    current_step: Optional[str] = None
    schema_version: str = "2026.02"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workspace_id": self.workspace_id,
            "completed_steps": self.completed_steps,
            "current_step": self.current_step,
            "schema_version": self.schema_version,
        }
