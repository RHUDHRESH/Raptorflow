"""
Auth domain entities.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class User:
    """User domain entity."""

    id: str
    email: str
    workspace_id: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "email": self.email,
            "workspace_id": self.workspace_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return cls(
            id=data["id"],
            email=data.get("email", ""),
            workspace_id=data.get("workspace_id"),
            created_at=created_at,
        )


@dataclass
class Session:
    """Session domain entity."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = 3600
    expires_at: Optional[int] = None
    user: Optional[User] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "expires_at": self.expires_at,
        }
        if self.user:
            result["user"] = self.user.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        user = data.get("user")
        if user:
            user = User.from_dict(user)

        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            token_type=data.get("token_type", "bearer"),
            expires_in=data.get("expires_in", 3600),
            expires_at=data.get("expires_at"),
            user=user,
        )
