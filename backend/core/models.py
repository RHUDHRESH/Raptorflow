"""
Core data models for authentication and authorization
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# Validation constants
VALID_SUBSCRIPTION_TIERS = {"free", "starter", "growth", "enterprise", "pro"}
VALID_CURRENCIES = {"USD", "EUR", "GBP", "INR", "JPY", "CNY"}
VALID_TIMEZONES = {
    "UTC",
    "America/New_York",
    "America/Los_Angeles",
    "Europe/London",
    "Europe/Paris",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Kolkata",
}


class ValidationError(Exception):
    """Validation error for model fields"""

    pass


@dataclass
class User:
    """User model from Supabase auth.users"""

    id: str
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    subscription_tier: str = "free"
    budget_limit_monthly: float = 1.0
    onboarding_completed_at: Optional[datetime] = None
    preferences: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Validate email format
        if not self.email or not re.match(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.email
        ):
            raise ValidationError(f"Invalid email format: {self.email}")

        # Validate subscription tier
        if self.subscription_tier not in VALID_SUBSCRIPTION_TIERS:
            raise ValidationError(
                f"Invalid subscription tier: {self.subscription_tier}. Must be one of: {VALID_SUBSCRIPTION_TIERS}"
            )

        # Validate budget
        if self.budget_limit_monthly < 0:
            raise ValidationError(
                f"Budget limit cannot be negative: {self.budget_limit_monthly}"
            )

        if self.budget_limit_monthly > 1000000:  # Reasonable upper limit
            raise ValidationError(f"Budget limit too high: {self.budget_limit_monthly}")

        # Initialize preferences with validation
        if self.preferences is None:
            self.preferences = {}
        else:
            self._validate_preferences()

    def _validate_preferences(self):
        """Validate user preferences"""
        if not isinstance(self.preferences, dict):
            raise ValidationError("Preferences must be a dictionary")

        # Validate theme if present
        if "theme" in self.preferences:
            valid_themes = {"light", "dark", "auto"}
            if self.preferences["theme"] not in valid_themes:
                raise ValidationError(f"Invalid theme: {self.preferences['theme']}")

        # Validate language if present
        if "language" in self.preferences:
            if (
                not isinstance(self.preferences["language"], str)
                or len(self.preferences["language"]) != 2
            ):
                raise ValidationError(
                    f"Invalid language code: {self.preferences['language']}"
                )


@dataclass
class Workspace:
    """Workspace model for multi-tenant isolation"""

    id: str
    user_id: str
    name: str
    slug: Optional[str] = None
    settings: Dict[str, Any] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        # Validate workspace name
        if not self.name or len(self.name.strip()) < 1:
            raise ValidationError("Workspace name cannot be empty")

        if len(self.name) > 100:
            raise ValidationError("Workspace name too long (max 100 characters)")

        # Validate slug format if provided
        if self.slug:
            if not re.match(r"^[a-z0-9-]+$", self.slug):
                raise ValidationError(
                    f"Invalid slug format: {self.slug}. Only lowercase letters, numbers, and hyphens allowed"
                )

        # Initialize and validate settings
        if self.settings is None:
            self.settings = {}
        else:
            self._validate_settings()

    def _validate_settings(self):
        """Validate workspace settings"""
        if not isinstance(self.settings, dict):
            raise ValidationError("Settings must be a dictionary")

        # Validate timezone if present
        if "timezone" in self.settings:
            if self.settings["timezone"] not in VALID_TIMEZONES:
                raise ValidationError(f"Invalid timezone: {self.settings['timezone']}")

        # Validate currency if present
        if "currency" in self.settings:
            if self.settings["currency"] not in VALID_CURRENCIES:
                raise ValidationError(f"Invalid currency: {self.settings['currency']}")

        # Validate language if present
        if "language" in self.settings:
            if (
                not isinstance(self.settings["language"], str)
                or len(self.settings["language"]) != 2
            ):
                raise ValidationError(
                    f"Invalid language code: {self.settings['language']}"
                )


@dataclass
class AuthContext:
    """Authentication context for requests"""

    user: User
    workspace_id: str
    workspace: Optional[Workspace] = None
    permissions: Dict[str, bool] = None

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = {
                "read": True,
                "write": True,
                "delete": True,
                "admin": False,
            }

        # CRITICAL SECURITY CHECK: Validate workspace ownership
        self._validate_workspace_ownership()

    def _validate_workspace_ownership(self):
        """Validate that the user owns the workspace - CRITICAL SECURITY"""
        if self.workspace and self.workspace.user_id != self.user.id:
            raise ValidationError(
                f"SECURITY VIOLATION: User {self.user.id} attempting to access "
                f"workspace {self.workspace.id} owned by user {self.workspace.user_id}"
            )

        # If workspace_id is provided, validate it matches the workspace
        if self.workspace and self.workspace.id != self.workspace_id:
            raise ValidationError(
                f"Workspace ID mismatch: context.workspace_id={self.workspace_id} "
                f"but workspace.id={self.workspace.id}"
            )

    def can_access_workspace(self, workspace_id: str) -> bool:
        """Check if user can access specific workspace"""
        return workspace_id == self.workspace_id and workspace_id == (
            self.workspace.id if self.workspace else None
        )

    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return self.permissions.get(permission, False)


@dataclass
class JWTPayload:
    """JWT payload from Supabase"""

    sub: str  # User ID
    email: str
    role: str = "authenticated"
    aud: str = "authenticated"
    exp: Optional[int] = None
    iat: Optional[int] = None
    iss: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JWTPayload":
        """Create JWTPayload from dictionary"""
        return cls(
            sub=data.get("sub"),
            email=data.get("email"),
            role=data.get("role", "authenticated"),
            aud=data.get("aud", "authenticated"),
            exp=data.get("exp"),
            iat=data.get("iat"),
            iss=data.get("iss"),
        )


@dataclass
class SessionInfo:
    """Session information for tracking"""

    session_id: str
    user_id: str
    workspace_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
