"""
Authentication API endpoints
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from ..core.auth import get_auth_context, get_current_user, get_workspace_id
from ..core.models import AuthContext, User
from ..core.supabase_mgr import get_supabase_client
from ..services.profile_service import ProfileError, ProfileService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])
profile_service = ProfileService()


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileResponse(BaseModel):
    user_id: str
    workspace_id: Optional[str]
    subscription_plan: Optional[str]
    subscription_status: Optional[str]


def _extract_auth_user(auth_result: Any) -> Optional[Any]:
    if isinstance(auth_result, dict):
        return auth_result.get("user")
    return getattr(auth_result, "user", None)


def _extract_auth_session(auth_result: Any) -> Optional[Any]:
    if isinstance(auth_result, dict):
        return auth_result.get("session")
    return getattr(auth_result, "session", None)


def _get_user_metadata(user: Any) -> Dict[str, Any]:
    if isinstance(user, dict):
        return user.get("user_metadata") or {}
    return getattr(user, "user_metadata", {}) or {}


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current user information
    """
    return current_user


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest) -> Dict[str, Any]:
    """
    Register a new user with Supabase Auth and create profile/workspace records.
    """
    supabase = get_supabase_client()
    try:
        sign_up_result = supabase.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {"data": {"full_name": payload.full_name}},
            }
        )
    except Exception as exc:
        logger.error("Signup failed for %s: %s", payload.email, exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to complete signup",
        ) from exc

    user = _extract_auth_user(sign_up_result)
    session = _extract_auth_session(sign_up_result)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup did not return a user record",
        )

    metadata = _get_user_metadata(user)
    auth_user = User(
        id=user["id"] if isinstance(user, dict) else user.id,
        email=user["email"] if isinstance(user, dict) else user.email,
        full_name=payload.full_name or metadata.get("full_name"),
        avatar_url=metadata.get("avatar_url"),
        subscription_tier="free",
    )

    try:
        profile_result = profile_service.ensure_profile(auth_user)
    except ProfileError as exc:
        logger.error("Profile creation error for user %s: %s", auth_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": exc.error_type, "message": str(exc), "context": exc.context},
        ) from exc
    except Exception as exc:
        logger.error(
            "Unexpected error creating profile for user %s: %s", auth_user.id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating profile",
        ) from exc

    response = {
        "user_id": profile_result["user_id"],
        "workspace_id": profile_result["workspace_id"],
        "subscription_plan": profile_result["subscription_plan"],
        "subscription_status": profile_result["subscription_status"],
    }

    if session:
        response.update(
            {
                "access_token": session["access_token"]
                if isinstance(session, dict)
                else session.access_token,
                "refresh_token": session["refresh_token"]
                if isinstance(session, dict)
                else session.refresh_token,
                "token_type": session["token_type"]
                if isinstance(session, dict)
                else session.token_type,
                "expires_in": session["expires_in"]
                if isinstance(session, dict)
                else session.expires_in,
            }
        )

    return response


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: SignupRequest) -> Dict[str, Any]:
    """Alias for signup endpoint."""
    return await signup(payload)


@router.post("/login")
async def login(payload: LoginRequest) -> Dict[str, Any]:
    """
    Authenticate user with Supabase Auth and ensure profile/workspace records exist.
    """
    supabase = get_supabase_client()
    try:
        sign_in_result = supabase.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except Exception as exc:
        logger.warning("Login failed for %s: %s", payload.email, exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from exc

    user = _extract_auth_user(sign_in_result)
    session = _extract_auth_session(sign_in_result)
    if not user or not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login response",
        )

    metadata = _get_user_metadata(user)
    auth_user = User(
        id=user["id"] if isinstance(user, dict) else user.id,
        email=user["email"] if isinstance(user, dict) else user.email,
        full_name=metadata.get("full_name"),
        avatar_url=metadata.get("avatar_url"),
        subscription_tier="free",
    )
    try:
        profile_result = profile_service.ensure_profile(auth_user)
    except ProfileError as exc:
        logger.error("Profile creation error for user %s: %s", auth_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": exc.error_type, "message": str(exc), "context": exc.context},
        ) from exc
    except Exception as exc:
        logger.error(
            "Unexpected error creating profile for user %s: %s", auth_user.id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating profile",
        ) from exc

    return {
        "access_token": session["access_token"]
        if isinstance(session, dict)
        else session.access_token,
        "refresh_token": session["refresh_token"]
        if isinstance(session, dict)
        else session.refresh_token,
        "token_type": session["token_type"] if isinstance(session, dict) else session.token_type,
        "expires_in": session["expires_in"] if isinstance(session, dict) else session.expires_in,
        "user_id": profile_result["user_id"],
        "workspace_id": profile_result["workspace_id"],
        "subscription_plan": profile_result["subscription_plan"],
        "subscription_status": profile_result["subscription_status"],
    }


@router.post("/profile", response_model=ProfileResponse)
async def create_profile(current_user: User = Depends(get_current_user)):
    """Create profile/workspace records for an authenticated user."""
    try:
        result = profile_service.ensure_profile(current_user)
        return {
            "user_id": result["user_id"],
            "workspace_id": result["workspace_id"],
            "subscription_plan": result["subscription_plan"],
            "subscription_status": result["subscription_status"],
        }
    except ProfileError as exc:
        logger.error("Profile creation error for user %s: %s", current_user.id, exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": exc.error_type, "message": str(exc), "context": exc.context},
        ) from exc
    except Exception as exc:
        logger.error(
            "Unexpected error creating profile for user %s: %s", current_user.id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating profile",
        ) from exc


@router.get("/me/workspace")
async def get_user_workspace(auth_context: AuthContext = Depends(get_auth_context)):
    """
    Get user's current workspace information
    """
    if not auth_context.workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No workspace found for user"
        )

    return {
        "workspace": auth_context.workspace,
        "permissions": auth_context.permissions,
        "workspace_id": auth_context.workspace_id,
    }


@router.post("/ensure-profile")
async def ensure_profile(current_user: User = Depends(get_current_user)):
    """Create missing Supabase profile/workspace/membership records for the user."""
    try:
        logger.info("Ensuring profile for user %s", current_user.id)
        result = profile_service.ensure_profile(current_user)
        logger.info(
            "Profile ensured successfully for user %s, workspace %s",
            current_user.id,
            result.get("workspace_id"),
        )
        return {
            "user_id": result["user_id"],
            "workspace_id": result["workspace_id"],
            "subscription_plan": result["subscription_plan"],
            "subscription_status": result["subscription_status"],
        }
    except ProfileError as e:
        logger.error("Profile service error for user %s: %s", current_user.id, e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": e.error_type, "message": str(e), "context": e.context},
        ) from e
    except Exception as e:
        logger.error(
            "Unexpected error ensuring profile for user %s: %s", current_user.id, e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while ensuring profile",
        ) from e


@router.get("/verify-profile")
async def verify_profile(current_user: User = Depends(get_current_user)):
    """Return profile/workspace/payment readiness so the frontend can gate access."""
    try:
        logger.debug("Verifying profile for user %s", current_user.id)
        result = profile_service.verify_profile(current_user)

        # Log verification outcome for monitoring
        if not result.get("profile_exists"):
            logger.warning(
                "Profile verification failed: profile not found for user %s",
                current_user.id,
            )
        elif not result.get("workspace_exists"):
            logger.warning(
                "Profile verification failed: workspace not found for user %s",
                current_user.id,
            )
        elif result.get("needs_payment"):
            logger.info(
                "Profile verification: payment required for user %s, status %s",
                current_user.id,
                result.get("subscription_status"),
            )
        else:
            logger.info("Profile verification successful for user %s", current_user.id)

        return result
    except ProfileError as e:
        logger.error("Profile verification error for user %s: %s", current_user.id, e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": e.error_type, "message": str(e), "context": e.context},
        ) from e
    except Exception as e:
        logger.error(
            "Unexpected error verifying profile for user %s: %s", current_user.id, e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while verifying profile",
        ) from e


@router.get("/me/usage")
async def get_user_usage(
    auth_context: AuthContext = Depends(get_auth_context),
) -> Dict[str, Any]:
    """
    Get current user's usage statistics
    """
    supabase = get_supabase_client()

    # Get current usage
    usage_result = supabase.rpc(
        "get_current_usage", {"workspace_id": auth_context.workspace_id}
    ).execute()

    # Get subscription limits
    limits_result = supabase.rpc(
        "check_subscription_limits",
        {
            "workspace_id": auth_context.workspace_id,
            "required_tokens": 0,
            "required_cost": 0,
        },
    ).execute()

    usage_data = usage_result.data or [{}][0] if usage_result.data else {}
    limits_data = limits_result.data or [{}][0] if limits_result.data else {}

    return {
        "current_usage": {
            "tokens_used": usage_data.get("tokens_used", 0),
            "cost_usd": usage_data.get("cost_usd", 0),
            "period_start": usage_data.get("period_start"),
            "period_end": usage_data.get("period_end"),
            "agent_breakdown": usage_data.get("agent_breakdown", {}),
        },
        "limits": {
            "allowed": limits_data.get("allowed", True),
            "limit_tokens": limits_data.get("limit_tokens", 0),
            "limit_cost": limits_data.get("limit_cost", 0),
            "subscription_tier": limits_data.get("subscription_tier", "free"),
        },
        "usage_percentage": {
            "tokens": (
                (
                    usage_data.get("tokens_used", 0)
                    / limits_data.get("limit_tokens", 1)
                    * 100
                )
                if limits_data.get("limit_tokens", 0) > 0
                else 0
            ),
            "cost": (
                (usage_data.get("cost_usd", 0) / limits_data.get("limit_cost", 1) * 100)
                if limits_data.get("limit_cost", 0) > 0
                else 0
            ),
        },
    }


@router.get("/me/billing")
async def get_user_billing(
    auth_context: AuthContext = Depends(get_auth_context),
) -> Dict[str, Any]:
    """
    Get user's billing information
    """
    supabase = get_supabase_client()

    # Get subscription info
    subscription_result = (
        supabase.table("subscriptions")
        .select("*")
        .eq("workspace_id", auth_context.workspace_id)
        .eq("status", "active")
        .single()
        .execute()
    )

    # Get recent invoices
    invoices_result = (
        supabase.table("invoices")
        .select("*")
        .eq("workspace_id", auth_context.workspace_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )

    # Get usage history
    usage_result = (
        supabase.table("usage_records")
        .select("*")
        .eq("workspace_id", auth_context.workspace_id)
        .order("period_start", desc=True)
        .limit(12)
        .execute()
    )

    subscription = subscription_result.data or {}
    invoices = invoices_result.data or []
    usage_history = usage_result.data or []

    return {
        "subscription": subscription,
        "recent_invoices": invoices,
        "usage_history": usage_history,
        "current_period": {
            "start": subscription.get("current_period_start"),
            "end": subscription.get("current_period_end"),
            "days_remaining": None,  # Would calculate based on current date
        },
    }


@router.post("/validate")
async def validate_session(current_user: User = Depends(get_current_user)):
    """
    Validate current session/token
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "subscription_tier": current_user.subscription_tier,
    }


@router.get("/permissions")
async def get_user_permissions(auth_context: AuthContext = Depends(get_auth_context)):
    """
    Get user's permissions for current workspace
    """
    return {
        "workspace_id": auth_context.workspace_id,
        "permissions": auth_context.permissions,
        "user_id": auth_context.user.id,
        "subscription_tier": auth_context.user.subscription_tier,
    }


@router.post("/switch-workspace")
async def switch_workspace(
    workspace_id: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Switch to a different workspace
    """
    supabase = get_supabase_client()

    # Validate user owns the workspace using owner_id only
    workspace_result = (
        supabase.table("workspaces")
        .select("*")
        .eq("id", workspace_id)
        .eq("owner_id", current_user.id)
        .single()
        .execute()
    )

    if not workspace_result.data:
        # Also check membership
        membership_check = (
            supabase.table("workspace_members")
            .select("workspace_id")
            .eq("workspace_id", workspace_id)
            .eq("user_id", current_user.id)
            .eq("is_active", True)
            .single()
            .execute()
        )

        if not membership_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or access denied",
            )

        # Get workspace details for member
        workspace_result = (
            supabase.table("workspaces")
            .select("*")
            .eq("id", workspace_id)
            .single()
            .execute()
        )

    workspace = workspace_result.data

    return {
        "message": "Workspace switched successfully",
        "workspace": workspace,
        "workspace_id": workspace_id,
    }


@router.get("/workspaces")
async def list_user_workspaces(current_user: User = Depends(get_current_user)):
    """
    List all workspaces for the current user
    """
    supabase = get_supabase_client()

    owned = (
        supabase.table("workspaces")
        .select("*")
        .eq("owner_id", current_user.id)
        .execute()
    )
    workspace_map = {ws["id"]: ws for ws in (owned.data or [])}

    memberships = (
        supabase.table("workspace_members")
        .select("workspace_id")
        .eq("user_id", current_user.id)
        .execute()
    )
    member_ids = [entry["workspace_id"] for entry in memberships.data or []]
    if member_ids:
        member_records = (
            supabase.table("workspaces").select("*").in_("id", member_ids).execute()
        )
        for record in member_records.data or []:
            workspace_map.setdefault(record["id"], record)

    workspaces = list(workspace_map.values())
    return {"workspaces": workspaces, "total": len(workspaces)}


@router.delete("/me")
async def delete_account(
    confirmation: str, current_user: User = Depends(get_current_user)
):
    """
    Delete user account and all associated data
    """
    if confirmation.lower() != "delete my account":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation text must be exactly 'delete my account'",
        )

    supabase = get_supabase_client()

    # In a real implementation, you would:
    # 1. Delete all workspace data
    # 2. Delete workspaces
    # 3. Delete user profile
    # 4. Delete user from Supabase Auth

    return {
        "message": "Account deletion initiated",
        "note": "This would delete all data and cannot be undone",
        "user_id": current_user.id,
    }
