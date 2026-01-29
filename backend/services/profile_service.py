"""Profile and workspace orchestration service."""

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from core.models import User
from core.supabase_mgr import get_supabase_admin

logger = logging.getLogger(__name__)


class ProfileError(Exception):
    """Structured profile service errors."""

    def __init__(self, message: str, error_type: str, context: Dict[str, Any] = None):
        super().__init__(message)
        self.error_type = error_type
        self.context = context or {}


class ProfileService:
    """Ensures users have profiles, workspaces, and subscription metadata."""

    def __init__(self):
        self.supabase = get_supabase_admin()

    def ensure_profile(self, auth_user: User) -> Dict[str, Any]:
        """Ensure Supabase profile/workspace records exist for the authenticated user."""
        try:
            user_record = self._get_or_create_user(auth_user)
            workspace_record = self._get_or_create_workspace(user_record, auth_user)
            return {
                "user_id": user_record["id"],
                "workspace_id": workspace_record["id"],
                "subscription_plan": user_record.get("subscription_plan")
                or user_record.get("subscription_tier")
                or "free",
                "subscription_status": user_record.get("subscription_status", "trial"),
            }
        except Exception as exc:
            logger.error("Failed to ensure profile for user %s: %s", auth_user.id, exc)
            raise ProfileError(
                f"Profile creation failed: {exc}",
                "PROFILE_CREATION_ERROR",
                {"user_id": auth_user.id, "email": auth_user.email},
            ) from exc

    def verify_profile(self, auth_user: User) -> Dict[str, Any]:
        """Check whether the user has the required profile/workspace/payment state."""
        try:
            # Optimized: Single query to get user and workspace data
            user_workspace_data = self._get_user_workspace_data(auth_user.id)
            profile_exists = user_workspace_data is not None

            if not profile_exists:
                return {
                    "profile_exists": False,
                    "workspace_exists": False,
                    "workspace_id": None,
                    "subscription_plan": None,
                    "subscription_status": None,
                    "needs_payment": True,
                    "error": "Profile not found",
                }

            # Extract data from optimized query result
            user_record = user_workspace_data.get("user", {})
            workspace_record = user_workspace_data.get("workspace")
            workspace_exists = workspace_record is not None

            # Get subscription data if workspace exists
            subscription = None
            if workspace_exists:
                subscription = self._get_active_subscription(workspace_record["id"])

            # Determine subscription status with explicit state handling
            subscription_plan = (
                user_record.get("subscription_plan")
                or user_record.get("subscription_tier")
                or "free"
            )
            subscription_status = user_record.get("subscription_status", "trial")

            if subscription:
                subscription_plan = subscription.get("plan") or subscription_plan
                subscription_status = subscription.get("status") or subscription_status

            # Enhanced payment logic with timestamp validation
            needs_payment = self._determine_payment_needs(
                subscription_status, subscription, user_record
            )

            return {
                "profile_exists": profile_exists,
                "workspace_exists": workspace_exists,
                "workspace_id": (
                    workspace_record.get("id") if workspace_record else None
                ),
                "subscription_plan": subscription_plan,
                "subscription_status": subscription_status,
                "needs_payment": needs_payment,
            }
        except Exception as exc:
            logger.error("Failed to verify profile for user %s: %s", auth_user.id, exc)
            raise ProfileError(
                f"Profile verification failed: {exc}",
                "PROFILE_VERIFICATION_ERROR",
                {"user_id": auth_user.id, "email": auth_user.email},
            ) from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_user_by_auth_id(self, auth_user_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = (
                self.supabase.table("users")
                .select("*")
                .eq("auth_user_id", auth_user_id)
                .single()
                .execute()
            )
            return result.data
        except Exception:
            return None

    def _get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = (
                self.supabase.table("users")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )
            return result.data
        except Exception:
            return None

    def _get_or_create_user(self, auth_user: User) -> Dict[str, Any]:
        existing_user = self._get_user_by_auth_id(auth_user.id) or self._get_user_by_id(
            auth_user.id
        )
        if existing_user:
            return existing_user

        payload = {
            "auth_user_id": auth_user.id,
            "email": auth_user.email,
            "full_name": auth_user.full_name,
            "avatar_url": auth_user.avatar_url,
            "subscription_plan": getattr(auth_user, "subscription_tier", None)
            or "free",
            "subscription_status": "trial",
        }
        try:
            result = (
                self.supabase.table("users")
                .insert(payload)
                .select("*")
                .single()
                .execute()
            )
            return result.data
        except Exception as exc:
            logger.error("Failed to create user profile: %s", exc)
            raise

    def _get_workspace_for_owner(self, owner_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = (
                self.supabase.table("workspaces")
                .select("*")
                .eq("owner_id", owner_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                return result.data[0]
            return None
        except Exception:
            return None

    def _get_or_create_workspace(
        self, user_record: Dict[str, Any], auth_user: User
    ) -> Dict[str, Any]:
        workspace = self._get_workspace_for_owner(user_record["id"])
        if workspace:
            self._ensure_membership(workspace["id"], user_record["id"])
            return workspace

        slug = self._generate_slug(auth_user.email or user_record["id"])
        workspace_payload = {
            "owner_id": user_record["id"],
            "name": self._derive_workspace_name(auth_user),
            "slug": slug,
            "is_trial": True,
        }
        try:
            result = (
                self.supabase.table("workspaces")
                .insert(workspace_payload)
                .select("*")
                .single()
                .execute()
            )
            workspace = result.data
            self._ensure_membership(workspace["id"], user_record["id"])
            return workspace
        except Exception as exc:
            logger.error("Failed to create workspace: %s", exc)
            raise

    def _ensure_membership(self, workspace_id: str, user_id: str) -> None:
        payload = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "role": "owner",
            "is_active": True,
        }
        try:
            self.supabase.table("workspace_members").upsert(
                payload, on_conflict="workspace_id,user_id"
            ).execute()
        except Exception as exc:
            logger.warning("Failed to upsert workspace membership: %s", exc)

    def _generate_slug(self, base: str) -> str:
        cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", base.split("@")[0]).strip("-").lower()
        if not cleaned:
            cleaned = "workspace"
        unique_suffix = uuid.uuid4().hex[:8]
        return f"{cleaned}-{unique_suffix}"

    def _derive_workspace_name(self, auth_user: User) -> str:
        if auth_user.full_name:
            return f"{auth_user.full_name}'s Workspace"
        if auth_user.email:
            return f"{auth_user.email.split('@')[0]}'s Workspace"
        return "Raptorflow Workspace"

    def _determine_payment_needs(
        self,
        status: str,
        subscription: Dict[str, Any] = None,
        user_record: Dict[str, Any] = None,
    ) -> bool:
        """Determine if payment is needed based on subscription status and timestamps."""
        now = datetime.now(timezone.utc)

        # Explicit subscription state handling
        if status == "active":
            return False
        elif status == "trialing":
            # Check if trial has expired
            trial_end = self._parse_timestamp(
                subscription.get("trial_end")
                if subscription
                else user_record.get("trial_end")
            )
            if trial_end and now > trial_end:
                return True  # Trial expired
            return False  # Trial still active
        elif status == "past_due":
            # Check grace period
            grace_end = self._parse_timestamp(
                subscription.get("grace_period_end")
                if subscription
                else user_record.get("grace_period_end")
            )
            if grace_end and now <= grace_end:
                return False  # Still in grace period
            return True  # Grace period expired
        elif status == "canceled":
            # Check if access continues until period end
            period_end = self._parse_timestamp(
                subscription.get("current_period_end")
                if subscription
                else user_record.get("current_period_end")
            )
            if period_end and now <= period_end:
                return False  # Still paid until period end
            return True  # Cancellation effective
        elif status == "unpaid":
            return True  # Immediate payment required
        elif status == "incomplete":
            return True  # Payment processing incomplete
        elif status == "incomplete_expired":
            return True  # Payment expired
        elif status == "paused":
            return True  # Subscription paused
        else:
            # Default to requiring payment for unknown states
            return True

    def _parse_timestamp(self, timestamp: Union[str, int, None]) -> Optional[datetime]:
        """Parse various timestamp formats to datetime."""
        if not timestamp:
            return None

        try:
            if isinstance(timestamp, int):
                # Unix timestamp
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
            elif isinstance(timestamp, str):
                # ISO string or other format
                if timestamp.isdigit():
                    return datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
                return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except Exception as exc:
            logger.warning("Failed to parse timestamp %s: %s", timestamp, exc)

        return None

    def _get_active_subscription(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        try:
            result = (
                self.supabase.table("subscriptions")
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("status", "active")
                .limit(1)
                .execute()
            )
            if result.data:
                return result.data[0]
            return None
        except Exception:
            return None

    def _get_user_workspace_data(self, auth_id: str) -> Optional[Dict[str, Any]]:
        """Optimized single query to get user and workspace data together."""
        try:
            # Use RPC to get user and workspace data in a single query
            result = self.supabase.rpc(
                "get_user_workspace_data", {"auth_id": auth_id}
            ).execute()

            if result.data:
                return result.data[0] if isinstance(result.data, list) else result.data
            return None
        except Exception as exc:
            logger.debug("RPC call failed, falling back to individual queries: %s", exc)
            # Fallback to individual queries if RPC not available
            return self._get_user_workspace_data_fallback(auth_id)

    def _get_user_workspace_data_fallback(
        self, auth_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fallback method using individual queries."""
        try:
            user_record = self._get_user_by_auth_id(auth_id) or self._get_user_by_id(
                auth_id
            )
            if not user_record:
                return None

            workspace_record = self._get_workspace_for_owner(user_record["id"])

            return {"user": user_record, "workspace": workspace_record}
        except Exception:
            return None
