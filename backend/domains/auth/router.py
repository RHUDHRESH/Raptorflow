"""
Auth Domain - Router
Authentication endpoints using Supabase Auth
"""

from typing import Any, Dict, Optional

from app.auth_middleware import get_current_user_id, require_auth
from domains.auth.models import Profile
from domains.auth.service import AuthService, get_auth_service
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth")


# ============ Request/Response Models ============


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class SignInRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class AuthResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    onboarding_status: str
    subscription_plan: str


class WorkspaceCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None


# ============ Auth Endpoints ============


@router.post("/signup", response_model=AuthResponse)
async def signup(data: SignUpRequest, auth: AuthService = Depends(get_auth_service)):
    """
    Sign up a new user.
    Creates auth user + profile + default workspace.
    """
    user_metadata = {"full_name": data.full_name} if data.full_name else {}

    result = await auth.sign_up(
        email=data.email, password=data.password, user_metadata=user_metadata
    )

    if result["success"]:
        return AuthResponse(
            success=True,
            access_token=result.get("session", {}).get("access_token"),
            refresh_token=result.get("session", {}).get("refresh_token"),
            user=result.get("user"),
        )
    else:
        raise HTTPException(
            status_code=400, detail=result.get("error", "Signup failed")
        )


@router.post("/login", response_model=AuthResponse)
async def login(data: SignInRequest, auth: AuthService = Depends(get_auth_service)):
    """
    Sign in an existing user.
    Returns access token and user data.
    """
    result = await auth.sign_in(email=data.email, password=data.password)

    if result["success"]:
        return AuthResponse(
            success=True,
            access_token=result["session"]["access_token"],
            refresh_token=result["session"]["refresh_token"],
            user=result["user"],
        )
    else:
        raise HTTPException(
            status_code=401, detail=result.get("error", "Invalid credentials")
        )


@router.post("/logout")
async def logout(request: Request, auth: AuthService = Depends(get_auth_service)):
    """Sign out the current user"""
    token = getattr(request.state, "access_token", None)
    if token:
        await auth.sign_out(token)
    return {"success": True, "message": "Logged out successfully"}


@router.post("/refresh")
async def refresh_token(
    data: RefreshTokenRequest, auth: AuthService = Depends(get_auth_service)
):
    """Refresh access token using refresh token"""
    result = await auth.refresh_token(data.refresh_token)

    if result["success"]:
        return {
            "success": True,
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "expires_at": result["expires_at"],
        }
    else:
        raise HTTPException(
            status_code=401, detail=result.get("error", "Token refresh failed")
        )


# ============ Profile Endpoints ============


@router.get("/me", response_model=ProfileResponse)
async def get_me(
    user_id: str = Depends(require_auth), auth: AuthService = Depends(get_auth_service)
):
    """Get current authenticated user's profile"""
    profile = await auth.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return ProfileResponse(
        id=profile.id,
        email=profile.email,
        full_name=profile.full_name,
        avatar_url=profile.avatar_url,
        role=profile.role,
        onboarding_status=profile.onboarding_status,
        subscription_plan=profile.subscription_plan,
    )


@router.get("/profile/{user_id}")
async def get_profile(user_id: str, auth: AuthService = Depends(get_auth_service)):
    """Get a user's profile by ID (public info only)"""
    profile = await auth.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Return limited public info
    return {
        "id": profile.id,
        "full_name": profile.full_name,
        "avatar_url": profile.avatar_url,
        "ucid": profile.ucid,
    }


# ============ Workspace Endpoints ============


@router.get("/workspaces")
async def list_workspaces(
    user_id: str = Depends(require_auth), auth: AuthService = Depends(get_auth_service)
):
    """List all workspaces for current user"""
    workspaces = await auth.list_user_workspaces(user_id)
    return {"success": True, "workspaces": [w.model_dump() for w in workspaces]}


@router.post("/workspaces")
async def create_workspace(
    data: WorkspaceCreateRequest,
    user_id: str = Depends(require_auth),
    auth: AuthService = Depends(get_auth_service),
):
    """Create a new workspace"""
    workspace = await auth.create_workspace(
        owner_id=user_id, name=data.name, description=data.description
    )

    if workspace:
        return {"success": True, "workspace": workspace.model_dump()}
    else:
        raise HTTPException(status_code=400, detail="Failed to create workspace")


@router.get("/workspaces/{workspace_id}")
async def get_workspace(
    workspace_id: str,
    user_id: str = Depends(require_auth),
    auth: AuthService = Depends(get_auth_service),
):
    """Get workspace details"""
    # Check access
    has_access = await auth.check_workspace_access(workspace_id, user_id)
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied to workspace")

    workspace = await auth.get_workspace(workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return {"success": True, "workspace": workspace.model_dump()}
