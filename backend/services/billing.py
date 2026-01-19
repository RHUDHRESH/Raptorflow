"""
Billing service for business logic operations
Handles billing-related business logic and validation
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

try:
    from backend.core.models import ValidationError
    from backend.core.supabase_mgr import get_supabase_client
    from backend.db.billing import BillingRepository
    from backend.db.usage_records import UsageRecordRepository
except ImportError:
    # Fallback for testing without full dependencies
    ValidationError = Exception
    def get_supabase_client():
        return None
    class BillingRepository:
        pass
    class UsageRecordRepository:
        pass


class BillingService:
    """Service for billing business logic"""

    def __init__(self):
        self.repository = BillingRepository()
        self.usage_repository = UsageRecordRepository()
        self.supabase = get_supabase_client()

        # Pricing plans
        self.plans = {
            "free": {
                "price": 0,
                "tokens_per_month": 10000,
                "features": ["basic_features"],
                "rate_limit_multiplier": 1.0,
            },
            "starter": {
                "price": 29,
                "tokens_per_month": 50000,
                "features": ["basic_features", "advanced_features"],
                "rate_limit_multiplier": 2.0,
            },
            "pro": {
                "price": 99,
                "tokens_per_month": 200000,
                "features": ["basic_features", "advanced_features", "premium_features"],
                "rate_limit_multiplier": 5.0,
            },
            "enterprise": {
                "price": 299,
                "tokens_per_month": 1000000,
                "features": ["all_features"],
                "rate_limit_multiplier": 10.0,
            },
        }

    async def get_subscription(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get subscription for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Subscription data or None if not found
        """
        return await self.repository.get_subscription(workspace_id)

    async def update_subscription(self, workspace_id: str, plan: str) -> Dict[str, Any]:
        """
        Update subscription plan

        Args:
            workspace_id: Workspace ID
            plan: New plan

        Returns:
            Updated subscription data
        """
        # Validate plan
        if plan not in self.plans:
            raise ValidationError(f"Invalid plan: {plan}")

        # Get current subscription
        current_sub = await self.get_subscription(workspace_id)

        # Calculate billing period
        now = datetime.utcnow()
        period_start = now
        period_end = now + timedelta(days=30)  # Monthly billing

        subscription_data = {
            "plan": plan,
            "status": "active",
            "current_period_start": period_start.isoformat(),
            "current_period_end": period_end.isoformat(),
        }

        if current_sub:
            # Update existing subscription
            updated_sub = await self.repository.update_subscription(
                workspace_id, subscription_data
            )
            return updated_sub
        else:
            # Create new subscription
            subscription_data["workspace_id"] = workspace_id
            created_sub = await self.repository.create_subscription(
                workspace_id, subscription_data
            )
            return created_sub

    async def record_usage(
        self, workspace_id: str, tokens: int, cost: float, agent: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Record usage for workspace

        Args:
            workspace_id: Workspace ID
            tokens: Number of tokens used
            cost: Cost in USD
            agent: Agent name

        Returns:
            Usage record data
        """
        # Get subscription to check limits
        subscription = await self.get_subscription(workspace_id)
        if not subscription:
            raise ValidationError("No subscription found for workspace")

        plan = subscription.get("plan", "free")
        plan_config = self.plans.get(plan, self.plans["free"])

        # Check if over limit
        current_usage = await self.get_usage_summary(workspace_id, "current_month")
        total_tokens = current_usage.get("total_tokens", 0) + tokens

        if total_tokens > plan_config["tokens_per_month"]:
            # Over limit, record with higher cost
            overage_tokens = total_tokens - plan_config["tokens_per_month"]
            overage_cost = overage_tokens * 0.0001  # $0.0001 per token overage
            cost += overage_cost

        # Record usage
        usage_data = {
            "workspace_id": workspace_id,
            "period_start": datetime.utcnow().replace(day=1).isoformat(),
            "period_end": (
                datetime.utcnow().replace(day=1) + timedelta(days=32)
            ).replace(day=1)
            - timedelta(days=1),
            "tokens_used": tokens,
            "cost_usd": round(cost, 6),
            "agent_breakdown": {agent: tokens},
        }

        return await self.usage_repository.record_usage(workspace_id, usage_data)

    async def get_usage_summary(
        self, workspace_id: str, period: str = "current_month"
    ) -> Dict[str, Any]:
        """
        Get usage summary for workspace

        Args:
            workspace_id: Workspace ID
            period: Period ('current_month', 'last_month', 'current_year')

        Returns:
            Usage summary data
        """
        return await self.usage_repository.get_usage_summary(workspace_id, period)

    async def check_usage_limit(self, workspace_id: str) -> Dict[str, Any]:
        """
        Check if workspace is within usage limits

        Args:
            workspace_id: Workspace ID

        Returns:
            Usage limit check result
        """
        subscription = await self.get_subscription(workspace_id)
        if not subscription:
            raise ValidationError("No subscription found for workspace")

        plan = subscription.get("plan", "free")
        plan_config = self.plans.get(plan, self.plans["free"])

        current_usage = await self.get_usage_summary(workspace_id, "current_month")
        total_tokens = current_usage.get("total_tokens", 0)
        tokens_limit = plan_config["tokens_per_month"]

        remaining_tokens = max(0, tokens_limit - total_tokens)
        percentage_used = (total_tokens / tokens_limit) * 100 if tokens_limit > 0 else 0

        return {
            "plan": plan,
            "tokens_limit": tokens_limit,
            "tokens_used": total_tokens,
            "tokens_remaining": remaining_tokens,
            "percentage_used": round(percentage_used, 2),
            "over_limit": total_tokens > tokens_limit,
            "cost_so_far": current_usage.get("total_cost", 0),
            "estimated_monthly_cost": current_usage.get("total_cost", 0),
        }

    async def get_invoice(
        self, workspace_id: str, period: str = "current_month"
    ) -> Optional[Dict[str, Any]]:
        """
        Get invoice for workspace

        Args:
            workspace_id: Workspace ID
            period: Billing period

        Returns:
            Invoice data or None if not found
        """
        return await self.repository.get_invoice(workspace_id, period)

    async def upgrade_plan(self, workspace_id: str, new_plan: str) -> Dict[str, Any]:
        """
        Upgrade subscription plan

        Args:
            workspace_id: Workspace ID
            new_plan: New plan to upgrade to

        Returns:
            Updated subscription data
        """
        current_sub = await self.get_subscription(workspace_id)
        if not current_sub:
            raise ValidationError("No current subscription found")

        current_plan = current_sub.get("plan", "free")

        # Validate upgrade
        plan_hierarchy = ["free", "starter", "pro", "enterprise"]
        current_index = plan_hierarchy.index(current_plan)
        new_index = plan_hierarchy.index(new_plan)

        if new_index <= current_index:
            raise ValidationError(f"Cannot upgrade from {current_plan} to {new_plan}")

        # Update subscription
        updated_sub = await self.update_subscription(workspace_id, new_plan)

        # Create invoice for upgrade
        plan_config = self.plans[new_plan]
        invoice_data = {
            "workspace_id": workspace_id,
            "amount": plan_config["price"],
            "status": "pending",
            "description": f"Plan upgrade from {current_plan} to {new_plan}",
        }

        await self.repository.create_invoice(workspace_id, invoice_data)

        return updated_sub

    async def get_billing_dashboard(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get billing dashboard data

        Args:
            workspace_id: Workspace ID

        Returns:
            Dashboard data
        """
        subscription = await self.get_subscription(workspace_id)
        usage_summary = await self.get_usage_summary(workspace_id, "current_month")
        usage_limit_check = await self.check_usage_limit(workspace_id)

        # Get recent invoices
        recent_invoices = await self.repository.list_invoices(workspace_id, limit=5)

        # Calculate projected costs
        current_cost = usage_summary.get("total_cost", 0)
        days_in_month = datetime.utcnow().day
        days_in_month_total = 31  # Approximate
        projected_monthly_cost = (current_cost / days_in_month) * days_in_month_total

        return {
            "subscription": subscription,
            "usage_summary": usage_summary,
            "usage_limit_check": usage_limit_check,
            "recent_invoices": recent_invoices,
            "projected_monthly_cost": round(projected_monthly_cost, 2),
            "billing_health": {
                "on_track": usage_limit_check["percentage_used"] < 80,
                "warning_needed": usage_limit_check["percentage_used"] >= 80
                and usage_limit_check["percentage_used"] < 95,
                "over_limit": usage_limit_check["percentage_used"] >= 95,
            },
        }

    async def create_invoice(
        self, workspace_id: str, amount: float, description: str
    ) -> Dict[str, Any]:
        """
        Create invoice for workspace

        Args:
            workspace_id: Workspace ID
            amount: Invoice amount
            description: Invoice description

        Returns:
            Created invoice data
        """
        invoice_data = {
            "workspace_id": workspace_id,
            "amount": round(amount, 2),
            "status": "draft",
            "description": description,
        }

        return await self.repository.create_invoice(workspace_id, invoice_data)

    async def get_available_plans(self) -> Dict[str, Any]:
        """
        Get available pricing plans

        Returns:
            Available plans data
        """
        return {
            "plans": self.plans,
            "recommended_plan": "starter",  # Default recommendation
            "upgrade_paths": {
                "free": ["starter", "pro", "enterprise"],
                "starter": ["pro", "enterprise"],
                "pro": ["enterprise"],
                "enterprise": [],
            },
        }

    async def validate_billing_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate billing data before saving

        Args:
            data: Billing data to validate

        Returns:
            True if valid, raises ValidationError if invalid
        """
        # Validate plan
        if "plan" in data:
            plan = data["plan"]
            if plan not in self.plans:
                raise ValidationError(f"Invalid plan: {plan}")

        # Validate amount
        if "amount" in data:
            amount = data["amount"]
            if not isinstance(amount, (int, float, Decimal)) or amount < 0:
                raise ValidationError("Amount must be a positive number")

        # Validate status
        if "status" in data:
            status = data["status"]
            valid_statuses = ["active", "cancelled", "past_due", "unpaid"]
            if status not in valid_statuses:
                raise ValidationError(f"Invalid status: {status}")

        # Validate tokens used
        if "tokens_used" in data:
            tokens = data["tokens_used"]
            if not isinstance(tokens, int) or tokens < 0:
                raise ValidationError("Tokens used must be a non-negative integer")

        # Validate cost
        if "cost_usd" in data:
            cost = data["cost_usd"]
            if not isinstance(cost, (int, float, Decimal)) or cost < 0:
                raise ValidationError("Cost must be a non-negative number")

        return True
