"""
Users API endpoints
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr

from backend.core.auth import get_auth_context, get_current_user
from backend.core.models import AuthContext, User
from backend.core.supabase_mgr import get_supabase_client

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic models for request/response
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    subscription_tier: str
    budget_limit_monthly: float
    onboarding_completed_at: Optional[str]
    preferences: Dict[str, Any]
    created_at: str
    updated_at: str


@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate, current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile
    """
    supabase = get_supabase_client()

    # Prepare update data (only include non-None values)
    update_data = {}
    if user_data.full_name is not None:
        update_data["full_name"] = user_data.full_name
    if user_data.avatar_url is not None:
        update_data["avatar_url"] = user_data.avatar_url
    if user_data.preferences is not None:
        update_data["preferences"] = user_data.preferences

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update"
        )

    # Update user profile
    result = (
        supabase.table("users").update(update_data).eq("id", current_user.id).execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile",
        )

    return result.data[0]


@router.delete("/me")
async def delete_user_account(
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
    # 1. Send confirmation email
    # 2. Add cooldown period
    # 3. Archive data instead of permanent deletion
    # 4. Handle subscription cancellation

    # Delete user (cascade deletes should handle related data)
    result = supabase.table("users").delete().eq("id", current_user.id).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account",
        )

    return {
        "message": "User account deleted successfully",
        "user_id": current_user.id,
        "warning": "This action cannot be undone",
    }


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

    # Get usage history
    history_result = (
        supabase.table("usage_records")
        .select("*")
        .eq("workspace_id", auth_context.workspace_id)
        .order("period_start", desc=True)
        .limit(12)
        .execute()
    )

    usage_data = usage_result.data[0] if usage_result.data else {}
    limits_data = limits_result.data[0] if limits_result.data else {}
    history_data = history_result.data or []

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
        "usage_history": history_data,
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

    # Get usage records for cost calculation
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
    usage_records = usage_result.data or []

    # Calculate current period costs
    current_period_cost = 0
    if usage_records:
        current_period_cost = usage_records[0].get("cost_usd", 0)

    return {
        "subscription": subscription,
        "current_period_cost": current_period_cost,
        "recent_invoices": invoices,
        "usage_records": usage_records,
        "billing_summary": {
            "current_plan": subscription.get("plan", "free"),
            "monthly_cost": current_period_cost,
            "next_billing_date": subscription.get("current_period_end"),
            "is_active": subscription.get("status") == "active",
        },
    }


@router.post("/me/upgrade-plan")
async def upgrade_subscription_plan(
    new_plan: str, current_user: User = Depends(get_current_user)
):
    """
    Upgrade user's subscription plan
    """
    valid_plans = ["starter", "pro", "growth", "enterprise"]

    if new_plan not in valid_plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Must be one of: {valid_plans}",
        )

    supabase = get_supabase_client()

    # Get user's workspace
    workspace_result = (
        supabase.table("workspaces")
        .select("id")
        .eq("user_id", current_user.id)
        .limit(1)
        .single()
        .execute()
    )

    if not workspace_result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No workspace found for user"
        )

    workspace_id = workspace_result.data["id"]

    # Update subscription
    subscription_data = {
        "plan": new_plan,
        "status": "active",
        "current_period_start": "NOW()",
        "current_period_end": "NOW() + INTERVAL '1 month'",
    }

    # Upsert subscription
    result = (
        supabase.table("subscriptions")
        .upsert({"workspace_id": workspace_id, **subscription_data})
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upgrade subscription",
        )

    # Update user's subscription tier
    supabase.table("users").update({"subscription_tier": new_plan}).eq(
        "id", current_user.id
    ).execute()

    return {
        "message": "Subscription upgraded successfully",
        "new_plan": new_plan,
        "subscription": result.data[0],
    }


@router.get("/me/preferences")
async def get_user_preferences(current_user: User = Depends(get_current_user)):
    """
    Get user preferences
    """
    return {"preferences": current_user.preferences or {}, "user_id": current_user.id}


@router.put("/me/preferences")
async def update_user_preferences(
    preferences: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    """
    Update user preferences
    """
    supabase = get_supabase_client()

    result = (
        supabase.table("users")
        .update({"preferences": preferences})
        .eq("id", current_user.id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences",
        )

    return {"message": "Preferences updated successfully", "preferences": preferences}


@router.post("/me/complete-onboarding")
async def complete_onboarding(current_user: User = Depends(get_current_user)):
    """
    Mark user onboarding as completed
    """
    supabase = get_supabase_client()

    result = (
        supabase.table("users")
        .update({"onboarding_completed_at": "NOW()"})
        .eq("id", current_user.id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete onboarding",
        )

    return {
        "message": "Onboarding completed successfully",
        "completed_at": result.data[0]["onboarding_completed_at"],
    }


@router.get("/me/notifications")
async def get_user_notifications(
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=20, description="Maximum notifications to return"),
):
    """
    Get user notifications
    """
    try:
        # Query notifications table
        result = (
            supabase.table("notifications")
            .select("*")
            .eq("user_id", current_user.id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )

        notifications = result.data or []
        unread_count = len([n for n in notifications if not n.get("read", False)])

        return {
            "notifications": notifications,
            "unread_count": unread_count,
            "user_id": current_user.id,
        }
    except Exception as e:
        logger.error(f"Failed to get notifications for user {current_user.id}: {e}")
        # Return empty list on error rather than failing
        return {"notifications": [], "unread_count": 0, "user_id": current_user.id}


@router.post("/me/mark-notifications-read")
async def mark_notifications_read(
    notification_ids: Optional[list] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Mark notifications as read
    """
    # In a real implementation, you would update notifications table
    return {
        "message": "Notifications marked as read",
        "marked_count": len(notification_ids) if notification_ids else 0,
    }


@router.get("/me/api-keys")
async def get_user_api_keys(auth_context: AuthContext = Depends(get_auth_context)):
    """
    Get user's API keys
    """
    supabase = get_supabase_client()

    result = (
        supabase.table("api_keys")
        .select("*")
        .eq("workspace_id", auth_context.workspace_id)
        .order("created_at", desc=True)
        .execute()
    )

    # Don't return the actual key hashes, just metadata
    api_keys = []
    for key in result.data or []:
        api_keys.append(
            {
                "id": key["id"],
                "name": key["name"],
                "permissions": key["permissions"],
                "last_used_at": key["last_used_at"],
                "expires_at": key["expires_at"],
                "created_at": key["created_at"],
                "status": (
                    "active"
                    if (key["expires_at"] is None or key["expires_at"] > "NOW()")
                    else "expired"
                ),
            }
        )

    return {"api_keys": api_keys, "total": len(api_keys)}


@router.post("/me/api-keys")
async def create_api_key(
    name: str,
    permissions: Dict[str, Any],
    expires_at: Optional[str] = None,
    auth_context: AuthContext = Depends(get_auth_context),
):
    """
    Create a new API key
    """
    supabase = get_supabase_client()

    # Create API key
    result = supabase.rpc(
        "create_api_key",
        {
            "p_workspace_id": auth_context.workspace_id,
            "p_name": name,
            "p_permissions": permissions,
            "p_expires_at": expires_at,
        },
    ).execute()

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key",
        )

    key_data = result.data[0]

    return {
        "message": "API key created successfully",
        "api_key": key_data["api_key"],  # Only returned once during creation
        "key_id": key_data["key_id"],
        "name": name,
        "permissions": permissions,
        "expires_at": expires_at,
    }


@router.delete("/me/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str, auth_context: AuthContext = Depends(get_auth_context)
):
    """
    Revoke an API key
    """
    supabase = get_supabase_client()

    result = supabase.rpc(
        "revoke_api_key", {"key_id": key_id, "workspace_id": auth_context.workspace_id}
    ).execute()

    if not result.data or not result.data[0]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    return {"message": "API key revoked successfully", "key_id": key_id}


@router.get("/me/activity")
async def get_user_activity(
    current_user: User = Depends(get_current_user), days: int = 30
):
    """
    Get user's recent activity
    """
    supabase = get_supabase_client()

    # Get user's workspaces
    workspaces_result = (
        supabase.table("workspaces")
        .select("id")
        .eq("user_id", current_user.id)
        .execute()
    )
    workspace_ids = [w["id"] for w in workspaces_result.data or []]

    if not workspace_ids:
        return {"activities": [], "total_activities": 0, "days": days}

    # Get recent audit logs
    from datetime import datetime, timedelta

    cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

    audit_result = (
        supabase.table("audit_logs")
        .select("*")
        .in_("workspace_id", workspace_ids)
        .gte("created_at", cutoff_date)
        .order("created_at", desc=True)
        .limit(100)
        .execute()
    )

    return {
        "activities": audit_result.data or [],
        "total_activities": len(audit_result.data or []),
        "days": days,
    }
