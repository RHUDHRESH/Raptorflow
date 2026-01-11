"""
Budget Tracker for Cognitive Engine

Tracks and manages user budgets for cognitive operations.
Implements PROMPT 24 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from ..models import CostEstimate, ExecutionPlan


class BudgetPeriod(Enum):
    """Budget tracking periods."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"


class BudgetStatus(Enum):
    """Budget status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    EXCEEDED = "exceeded"
    SUSPENDED = "suspended"


@dataclass
class BudgetCheck:
    """Result of budget check."""

    allowed: bool
    remaining: float
    warning: bool
    status: BudgetStatus
    message: str
    period_remaining: Dict[str, float]  # Remaining budget by period
    usage_percentage: float
    estimated_completion_cost: float


@dataclass
class BudgetTransaction:
    """A budget transaction record."""

    transaction_id: str
    user_id: str
    workspace_id: str
    amount: float
    currency: str
    transaction_type: str  # "charge", "refund", "adjustment"
    description: str
    execution_id: Optional[str]
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class UserBudget:
    """User budget configuration."""

    user_id: str
    workspace_id: str
    daily_limit: float
    weekly_limit: float
    monthly_limit: float
    yearly_limit: float
    lifetime_limit: float
    currency: str = "USD"
    status: BudgetStatus = BudgetStatus.HEALTHY
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 0.95  # 95%
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class BudgetTracker:
    """
    Tracks and manages user budgets for cognitive operations.

    Prevents overspending and provides budget insights.
    """

    def __init__(self, storage_client=None, notification_client=None):
        """
        Initialize the budget tracker.

        Args:
            storage_client: Storage client for budget data
            notification_client: Client for budget notifications
        """
        self.storage_client = storage_client
        self.notification_client = notification_client

        # Default budget limits (in USD)
        self.default_limits = {
            BudgetPeriod.DAILY: 10.0,
            BudgetPeriod.WEEKLY: 50.0,
            BudgetPeriod.MONTHLY: 200.0,
            BudgetPeriod.YEARLY: 2000.0,
            BudgetPeriod.LIFETIME: 10000.0,
        }

        # Budget status thresholds
        self.status_thresholds = {
            BudgetStatus.WARNING: 0.8,  # 80%
            BudgetStatus.CRITICAL: 0.95,  # 95%
            BudgetStatus.EXCEEDED: 1.0,  # 100%
        }

    async def check_budget(
        self,
        user_id: str,
        estimated_cost: float,
        workspace_id: str = None,
        execution_id: str = None,
    ) -> BudgetCheck:
        """
        Check if user has sufficient budget for an operation.

        Args:
            user_id: User ID
            estimated_cost: Estimated cost in USD
            workspace_id: Workspace ID
            execution_id: Execution ID for tracking

        Returns:
            BudgetCheck with detailed information
        """
        # Get user budget
        budget = await self._get_user_budget(user_id, workspace_id)

        # Get current usage
        current_usage = await self._get_current_usage(user_id, workspace_id)

        # Calculate remaining budget by period
        period_remaining = {}
        for period in BudgetPeriod:
            limit = getattr(budget, f"{period.value}_limit")
            used = current_usage.get(period.value, 0.0)
            remaining = max(0.0, limit - used)
            period_remaining[period.value] = remaining

        # Check if operation is allowed
        allowed = all(
            remaining >= estimated_cost for remaining in period_remaining.values()
        )

        # Determine status
        status = self._determine_budget_status(budget, current_usage, estimated_cost)

        # Calculate usage percentage (using monthly as primary)
        monthly_usage = current_usage.get("monthly", 0.0)
        monthly_limit = budget.monthly_limit
        usage_percentage = (
            (monthly_usage / monthly_limit * 100) if monthly_limit > 0 else 0.0
        )

        # Generate message
        message = self._generate_budget_message(
            status, usage_percentage, estimated_cost
        )

        # Estimate completion cost
        estimated_completion_cost = monthly_usage + estimated_cost

        return BudgetCheck(
            allowed=allowed,
            remaining=period_remaining.get("monthly", 0.0),
            warning=status in [BudgetStatus.WARNING, BudgetStatus.CRITICAL],
            status=status,
            message=message,
            period_remaining=period_remaining,
            usage_percentage=usage_percentage,
            estimated_completion_cost=estimated_completion_cost,
        )

    async def deduct(
        self,
        user_id: str,
        actual_cost: float,
        workspace_id: str = None,
        execution_id: str = None,
        description: str = None,
    ) -> bool:
        """
        Deduct actual cost from user budget.

        Args:
            user_id: User ID
            actual_cost: Actual cost in USD
            workspace_id: Workspace ID
            execution_id: Execution ID for tracking
            description: Transaction description

        Returns:
            True if deduction successful
        """
        # Create transaction record
        transaction = BudgetTransaction(
            transaction_id=self._generate_transaction_id(),
            user_id=user_id,
            workspace_id=workspace_id or "default",
            amount=actual_cost,
            currency="USD",
            transaction_type="charge",
            description=description or f"Cognitive operation cost",
            execution_id=execution_id,
            timestamp=datetime.now(),
            metadata={},
        )

        # Record transaction
        success = await self._record_transaction(transaction)

        if success:
            # Update user budget status
            await self._update_budget_status(user_id, workspace_id)

            # Check if notifications are needed
            await self._check_budget_notifications(user_id, workspace_id)

        return success

    async def refund(
        self,
        user_id: str,
        amount: float,
        workspace_id: str = None,
        execution_id: str = None,
        reason: str = None,
    ) -> bool:
        """
        Refund amount to user budget.

        Args:
            user_id: User ID
            amount: Amount to refund
            workspace_id: Workspace ID
            execution_id: Execution ID for tracking
            reason: Refund reason

        Returns:
            True if refund successful
        """
        # Create refund transaction
        transaction = BudgetTransaction(
            transaction_id=self._generate_transaction_id(),
            user_id=user_id,
            workspace_id=workspace_id or "default",
            amount=-amount,  # Negative for refund
            currency="USD",
            transaction_type="refund",
            description=reason or "Refund for failed operation",
            execution_id=execution_id,
            timestamp=datetime.now(),
            metadata={},
        )

        # Record transaction
        success = await self._record_transaction(transaction)

        if success:
            # Update user budget status
            await self._update_budget_status(user_id, workspace_id)

        return success

    async def set_budget_limits(
        self,
        user_id: str,
        workspace_id: str = None,
        daily: float = None,
        weekly: float = None,
        monthly: float = None,
        yearly: float = None,
        lifetime: float = None,
    ) -> bool:
        """
        Set budget limits for a user.

        Args:
            user_id: User ID
            workspace_id: Workspace ID
            daily: Daily limit
            weekly: Weekly limit
            monthly: Monthly limit
            yearly: Yearly limit
            lifetime: Lifetime limit

        Returns:
            True if limits set successfully
        """
        budget = await self._get_user_budget(user_id, workspace_id)

        # Update limits
        if daily is not None:
            budget.daily_limit = daily
        if weekly is not None:
            budget.weekly_limit = weekly
        if monthly is not None:
            budget.monthly_limit = monthly
        if yearly is not None:
            budget.yearly_limit = yearly
        if lifetime is not None:
            budget.lifetime_limit = lifetime

        budget.updated_at = datetime.now()

        # Save updated budget
        return await self._save_user_budget(budget)

    async def get_budget_summary(
        self, user_id: str, workspace_id: str = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive budget summary for a user.

        Args:
            user_id: User ID
            workspace_id: Workspace ID

        Returns:
            Budget summary dictionary
        """
        budget = await self._get_user_budget(user_id, workspace_id)
        current_usage = await self._get_current_usage(user_id, workspace_id)

        # Calculate usage by period
        usage_summary = {}
        for period in BudgetPeriod:
            limit = getattr(budget, f"{period.value}_limit")
            used = current_usage.get(period.value, 0.0)
            remaining = max(0.0, limit - used)
            percentage = (used / limit * 100) if limit > 0 else 0.0

            usage_summary[period.value] = {
                "limit": limit,
                "used": used,
                "remaining": remaining,
                "percentage": percentage,
            }

        # Get recent transactions
        recent_transactions = await self._get_recent_transactions(
            user_id, workspace_id, limit=10
        )

        return {
            "user_id": user_id,
            "workspace_id": workspace_id,
            "status": budget.status.value,
            "currency": budget.currency,
            "usage_by_period": usage_summary,
            "recent_transactions": [
                {
                    "transaction_id": t.transaction_id,
                    "amount": t.amount,
                    "type": t.transaction_type,
                    "description": t.description,
                    "timestamp": t.timestamp.isoformat(),
                }
                for t in recent_transactions
            ],
            "last_updated": budget.updated_at.isoformat(),
        }

    async def get_workspace_budget_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get budget statistics for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Workspace budget statistics
        """
        # Get all users in workspace
        users = await self._get_workspace_users(workspace_id)

        total_spent = 0.0
        total_limits = {period.value: 0.0 for period in BudgetPeriod}
        status_counts = {status.value: 0 for status in BudgetStatus}

        for user_id in users:
            budget = await self._get_user_budget(user_id, workspace_id)
            usage = await self._get_current_usage(user_id, workspace_id)

            # Accumulate totals
            total_spent += usage.get("monthly", 0.0)

            for period in BudgetPeriod:
                total_limits[period.value] += getattr(budget, f"{period.value}_limit")

            status_counts[budget.status.value] += 1

        return {
            "workspace_id": workspace_id,
            "total_users": len(users),
            "total_monthly_spent": total_spent,
            "total_limits": total_limits,
            "status_distribution": status_counts,
            "average_monthly_spend": total_spent / len(users) if users > 0 else 0.0,
        }

    async def _get_user_budget(self, user_id: str, workspace_id: str) -> UserBudget:
        """Get or create user budget."""
        if self.storage_client:
            budget = await self.storage_client.get(
                "user_budgets", f"{user_id}_{workspace_id}"
            )
            if budget:
                return UserBudget(**budget)

        # Create default budget
        return UserBudget(
            user_id=user_id,
            workspace_id=workspace_id or "default",
            daily_limit=self.default_limits[BudgetPeriod.DAILY],
            weekly_limit=self.default_limits[BudgetPeriod.WEEKLY],
            monthly_limit=self.default_limits[BudgetPeriod.MONTHLY],
            yearly_limit=self.default_limits[BudgetPeriod.YEARLY],
            lifetime_limit=self.default_limits[BudgetPeriod.LIFETIME],
        )

    async def _save_user_budget(self, budget: UserBudget) -> bool:
        """Save user budget."""
        if self.storage_client:
            key = f"{budget.user_id}_{budget.workspace_id}"
            return await self.storage_client.set("user_budgets", key, asdict(budget))

        # For in-memory storage, would implement here
        return True

    async def _get_current_usage(
        self, user_id: str, workspace_id: str
    ) -> Dict[str, float]:
        """Get current usage by period."""
        if not self.storage_client:
            return {}

        # Get transactions for different periods
        now = datetime.now()
        usage = {}

        for period in BudgetPeriod:
            start_date = self._get_period_start(now, period)

            # Query transactions in this period
            transactions = await self._get_transactions_in_period(
                user_id, workspace_id, start_date, now
            )

            # Sum charges (exclude refunds)
            period_usage = sum(
                t.amount for t in transactions if t.transaction_type == "charge"
            )

            usage[period.value] = period_usage

        return usage

    async def _record_transaction(self, transaction: BudgetTransaction) -> bool:
        """Record a budget transaction."""
        if self.storage_client:
            return await self.storage_client.set(
                "budget_transactions", transaction.transaction_id, asdict(transaction)
            )

        return True

    async def _get_transactions_in_period(
        self, user_id: str, workspace_id: str, start_date: datetime, end_date: datetime
    ) -> List[BudgetTransaction]:
        """Get transactions within a date range."""
        if not self.storage_client:
            return []

        # Get all transactions for user
        all_transactions = await self.storage_client.list(
            "budget_transactions", {"user_id": user_id, "workspace_id": workspace_id}
        )

        # Filter by date range
        transactions = []
        for tx_data in all_transactions:
            tx = BudgetTransaction(**tx_data)
            if start_date <= tx.timestamp <= end_date:
                transactions.append(tx)

        return transactions

    async def _get_recent_transactions(
        self, user_id: str, workspace_id: str, limit: int = 10
    ) -> List[BudgetTransaction]:
        """Get recent transactions for a user."""
        if not self.storage_client:
            return []

        transactions = await self.storage_client.list(
            "budget_transactions",
            {"user_id": user_id, "workspace_id": workspace_id},
            limit=limit,
        )

        return [BudgetTransaction(**tx) for tx in transactions]

    async def _update_budget_status(self, user_id: str, workspace_id: str) -> None:
        """Update budget status based on current usage."""
        budget = await self._get_user_budget(user_id, workspace_id)
        current_usage = await self._get_current_usage(user_id, workspace_id)

        # Determine new status
        new_status = self._determine_budget_status(budget, current_usage, 0.0)

        if new_status != budget.status:
            budget.status = new_status
            budget.updated_at = datetime.now()
            await self._save_user_budget(budget)

    async def _check_budget_notifications(
        self, user_id: str, workspace_id: str
    ) -> None:
        """Check and send budget notifications if needed."""
        budget = await self._get_user_budget(user_id, workspace_id)
        current_usage = await self._get_current_usage(user_id, workspace_id)

        # Check for warning threshold
        monthly_usage = current_usage.get("monthly", 0.0)
        monthly_limit = budget.monthly_limit
        usage_percentage = (
            (monthly_usage / monthly_limit * 100) if monthly_limit > 0 else 0.0
        )

        if usage_percentage >= budget.warning_threshold * 100:
            if self.notification_client:
                await self.notification_client.send_budget_warning(
                    user_id=user_id,
                    workspace_id=workspace_id,
                    usage_percentage=usage_percentage,
                    remaining=monthly_limit - monthly_usage,
                )

    def _determine_budget_status(
        self,
        budget: UserBudget,
        current_usage: Dict[str, float],
        additional_cost: float,
    ) -> BudgetStatus:
        """Determine budget status based on usage."""
        # Use monthly as primary indicator
        monthly_usage = current_usage.get("monthly", 0.0) + additional_cost
        monthly_limit = budget.monthly_limit

        if monthly_limit <= 0:
            return BudgetStatus.SUSPENDED

        usage_percentage = (
            (monthly_usage / monthly_limit * 100) if monthly_limit > 0 else 0.0
        )

        if usage_percentage >= 100:
            return BudgetStatus.EXCEEDED
        elif usage_percentage >= budget.critical_threshold * 100:
            return BudgetStatus.CRITICAL
        elif usage_percentage >= budget.warning_threshold * 100:
            return BudgetStatus.WARNING
        else:
            return BudgetStatus.HEALTHY

    def _generate_budget_message(
        self, status: BudgetStatus, usage_percentage: float, estimated_cost: float
    ) -> str:
        """Generate appropriate budget message."""
        if status == BudgetStatus.HEALTHY:
            return f"Budget is healthy. Current usage: {usage_percentage:.1f}%"
        elif status == BudgetStatus.WARNING:
            return f"Budget warning at {usage_percentage:.1f}% usage. Consider monitoring closely."
        elif status == BudgetStatus.CRITICAL:
            return f"Budget critical at {usage_percentage:.1f}% usage. Immediate attention required."
        elif status == BudgetStatus.EXCEEDED:
            return f"Budget exceeded at {usage_percentage:.1f}% usage. Operations suspended."
        elif status == BudgetStatus.SUSPENDED:
            return "Budget suspended. Please contact administrator."
        else:
            return f"Budget status: {status.value}"

    def _get_period_start(self, date: datetime, period: BudgetPeriod) -> datetime:
        """Get start date for a period."""
        if period == BudgetPeriod.DAILY:
            return date.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == BudgetPeriod.WEEKLY:
            days_since_monday = date.weekday()
            return (date - timedelta(days=days_since_monday)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        elif period == BudgetPeriod.MONTHLY:
            return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == BudgetPeriod.YEARLY:
            return date.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
        else:  # LIFETIME
            return datetime.min

    def _generate_transaction_id(self) -> str:
        """Generate unique transaction ID."""
        import uuid

        return str(uuid.uuid4())

    async def _get_workspace_users(self, workspace_id: str) -> List[str]:
        """Get all users in a workspace."""
        if self.storage_client:
            # This would typically query a workspace_users table
            return await self.storage_client.list(
                "workspace_users", {"workspace_id": workspace_id}
            )

        return []
