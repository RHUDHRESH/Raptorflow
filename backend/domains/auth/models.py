"""
Auth Domain - Models
Updated to match database schema (profiles, workspaces, workspace_members)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field


class Profile(BaseModel):
    """User profile (matches profiles table)"""
    id: str  # UUID from auth.users
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    ucid: Optional[str] = None
    role: str = "user"
    onboarding_status: str = "pending"
    subscription_plan: str = "free"
    subscription_status: str = "none"
    workspace_preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Workspace(BaseModel):
    """Workspace (matches workspaces table)"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    owner_id: str
    name: str
    slug: Optional[str] = None
    description: Optional[str] = None
    settings: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkspaceMember(BaseModel):
    """Workspace membership (matches workspace_members table)"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str
    user_id: str
    role: str = "member"  # owner, admin, member
    is_active: bool = True
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserSession(BaseModel):
    """User session (matches user_sessions table)"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    token: str
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuthUser(BaseModel):
    """Supabase Auth user (from auth.users)"""
    id: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    last_sign_in_at: Optional[datetime] = None
    app_metadata: Dict[str, Any] = Field(default_factory=dict)
    user_metadata: Dict[str, Any] = Field(default_factory=dict)
    aud: str
    confirmation_sent_at: Optional[datetime] = None
    recovery_sent_at: Optional[datetime] = None
    email_confirmed_at: Optional[datetime] = None
