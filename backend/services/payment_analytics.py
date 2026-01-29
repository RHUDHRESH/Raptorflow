"""
Payment Analytics Service
Provides comprehensive analytics and monitoring for payment operations
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from core.supabase_mgr import get_supabase_admin

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentErrorType(Enum):
    """Payment error type enumeration."""

    INSUFFICIENT_FUNDS = "insufficient_funds"
    CARD_DECLINED = "card_declined"
    EXPIRED_CARD = "expired_card"
    INVALID_CVC = "invalid_cvc"
    PROCESSING_ERROR = "processing_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


@dataclass
class PaymentMetrics:
    """Payment metrics data structure."""

    total_payments: int
    successful_payments: int
    failed_payments: int
    total_revenue: int
    average_payment_amount: float
    conversion_rate: float
    failure_rate: float
    most_common_error: Optional[str]
    payment_by_plan: Dict[str, Dict[str, Any]]
    daily_trends: List[Dict[str, Any]]
    hourly_trends: List[Dict[str, Any]]


@dataclass
class PaymentAnalytics:
    """Comprehensive payment analytics."""

    metrics: PaymentMetrics
    recent_transactions: List[Dict[str, Any]]
    error_breakdown: Dict[str, int]
    plan_performance: Dict[str, Dict[str, Any]]
    time_based_analytics: Dict[str, List[Dict[str, Any]]]


class PaymentAnalyticsService:
    """Service for payment analytics and monitoring."""

    def __init__(self):
        """Initialize payment analytics service."""
        self.supabase = get_supabase_admin()

    def get_payment_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        plan_filter: Optional[str] = None,
    ) -> PaymentAnalytics:
        """Get comprehensive payment analytics."""
        try:
            # Default to last 30 days if no date range provided
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()

            # Fetch payment data
            payments_data = self._fetch_payments_data(start_date, end_date, plan_filter)

            # Calculate metrics
            metrics = self._calculate_metrics(payments_data)

            # Get recent transactions
            recent_transactions = self._get_recent_transactions(payments_data, limit=10)

            # Analyze errors
            error_breakdown = self._analyze_errors(payments_data)

            # Plan performance analysis
            plan_performance = self._analyze_plan_performance(payments_data)

            # Time-based analytics
            time_based_analytics = self._analyze_time_trends(
                payments_data, start_date, end_date
            )

            return PaymentAnalytics(
                metrics=metrics,
                recent_transactions=recent_transactions,
                error_breakdown=error_breakdown,
                plan_performance=plan_performance,
                time_based_analytics=time_based_analytics,
            )

        except Exception as exc:
            logger.error(f"Failed to get payment analytics: {exc}")
            raise

    def track_payment_event(
        self,
        event_type: str,
        transaction_id: str,
        plan_name: str,
        amount: int,
        status: str,
        error_type: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Track a payment event for analytics."""
        try:
            event_data = {
                "event_type": event_type,
                "transaction_id": transaction_id,
                "plan_name": plan_name,
                "amount": amount,
                "status": status,
                "error_type": error_type,
                "user_id": user_id,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
            }

            result = (
                self.supabase.table("payment_analytics_events")
                .insert(event_data)
                .execute()
            )

            if result.data:
                logger.info(f"Payment event tracked: {event_type} for {transaction_id}")
                return True
            else:
                logger.error(f"Failed to track payment event: {result}")
                return False

        except Exception as exc:
            logger.error(f"Error tracking payment event: {exc}")
            return False

    def get_conversion_rates(self, days: int = 30) -> Dict[str, float]:
        """Get payment conversion rates by plan."""
        try:
            start_date = datetime.now() - timedelta(days=days)

            # Get initiated payments
            initiated_result = (
                self.supabase.table("payment_analytics_events")
                .select("plan_name, transaction_id")
                .eq("event_type", "payment_initiated")
                .gte("timestamp", start_date.isoformat())
                .execute()
            )

            # Get completed payments
            completed_result = (
                self.supabase.table("payment_analytics_events")
                .select("plan_name, transaction_id")
                .eq("event_type", "payment_completed")
                .gte("timestamp", start_date.isoformat())
                .execute()
            )

            initiated_by_plan = {}
            completed_by_plan = {}

            for event in initiated_result.data or []:
                plan = event["plan_name"]
                initiated_by_plan[plan] = initiated_by_plan.get(plan, 0) + 1

            for event in completed_result.data or []:
                plan = event["plan_name"]
                completed_by_plan[plan] = completed_by_plan.get(plan, 0) + 1

            conversion_rates = {}
            for plan in initiated_by_plan:
                initiated = initiated_by_plan[plan]
                completed = completed_by_plan.get(plan, 0)
                conversion_rates[plan] = (
                    (completed / initiated * 100) if initiated > 0 else 0
                )

            return conversion_rates

        except Exception as exc:
            logger.error(f"Failed to get conversion rates: {exc}")
            return {}

    def get_failure_reasons(self, days: int = 30) -> Dict[str, int]:
        """Get payment failure reasons breakdown."""
        try:
            start_date = datetime.now() - timedelta(days=days)

            result = (
                self.supabase.table("payment_analytics_events")
                .select("error_type")
                .eq("event_type", "payment_failed")
                .gte("timestamp", start_date.isoformat())
                .execute()
            )

            failure_reasons = {}
            for event in result.data or []:
                error_type = event["error_type"] or "unknown"
                failure_reasons[error_type] = failure_reasons.get(error_type, 0) + 1

            return failure_reasons

        except Exception as exc:
            logger.error(f"Failed to get failure reasons: {exc}")
            return {}

    def get_revenue_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get revenue metrics."""
        try:
            start_date = datetime.now() - timedelta(days=days)

            result = (
                self.supabase.table("payment_analytics_events")
                .select("amount, plan_name, timestamp")
                .eq("event_type", "payment_completed")
                .gte("timestamp", start_date.isoformat())
                .execute()
            )

            total_revenue = 0
            revenue_by_plan = {}
            daily_revenue = {}

            for event in result.data or []:
                amount = event["amount"]
                plan = event["plan_name"]
                timestamp = event["timestamp"]

                total_revenue += amount

                # Revenue by plan
                revenue_by_plan[plan] = revenue_by_plan.get(plan, 0) + amount

                # Daily revenue
                date = timestamp.split("T")[0]
                daily_revenue[date] = daily_revenue.get(date, 0) + amount

            return {
                "total_revenue": total_revenue,
                "revenue_by_plan": revenue_by_plan,
                "daily_revenue": daily_revenue,
                "average_daily_revenue": total_revenue / days if days > 0 else 0,
            }

        except Exception as exc:
            logger.error(f"Failed to get revenue metrics: {exc}")
            return {}

    def _fetch_payments_data(
        self, start_date: datetime, end_date: datetime, plan_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Fetch payments data from database."""
        try:
            query = (
                self.supabase.table("subscriptions")
                .select("*")
                .gte("created_at", start_date.isoformat())
                .lte("created_at", end_date.isoformat())
            )

            if plan_filter:
                query = query.eq("plan", plan_filter)

            result = query.execute()
            return result.data or []

        except Exception as exc:
            logger.error(f"Failed to fetch payments data: {exc}")
            return []

    def _calculate_metrics(self, payments_data: List[Dict[str, Any]]) -> PaymentMetrics:
        """Calculate payment metrics."""
        total_payments = len(payments_data)
        successful_payments = len(
            [p for p in payments_data if p.get("status") == "active"]
        )
        failed_payments = len([p for p in payments_data if p.get("status") == "failed"])

        total_revenue = sum(
            p.get("amount", 0) for p in payments_data if p.get("status") == "active"
        )
        average_payment_amount = (
            total_revenue / successful_payments if successful_payments > 0 else 0
        )

        conversion_rate = (
            (successful_payments / total_payments * 100) if total_payments > 0 else 0
        )
        failure_rate = (
            (failed_payments / total_payments * 100) if total_payments > 0 else 0
        )

        # Payment by plan
        payment_by_plan = {}
        for payment in payments_data:
            plan = payment.get("plan", "unknown")
            if plan not in payment_by_plan:
                payment_by_plan[plan] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "revenue": 0,
                }

            payment_by_plan[plan]["total"] += 1
            if payment.get("status") == "active":
                payment_by_plan[plan]["successful"] += 1
                payment_by_plan[plan]["revenue"] += payment.get("amount", 0)
            elif payment.get("status") == "failed":
                payment_by_plan[plan]["failed"] += 1

        return PaymentMetrics(
            total_payments=total_payments,
            successful_payments=successful_payments,
            failed_payments=failed_payments,
            total_revenue=total_revenue,
            average_payment_amount=average_payment_amount,
            conversion_rate=conversion_rate,
            failure_rate=failure_rate,
            most_common_error=None,  # Would need error data to calculate
            payment_by_plan=payment_by_plan,
            daily_trends=[],
            hourly_trends=[],
        )

    def _get_recent_transactions(
        self, payments_data: List[Dict[str, Any]], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent transactions."""
        # Sort by created_at and return recent ones
        sorted_payments = sorted(
            payments_data, key=lambda x: x.get("created_at", ""), reverse=True
        )

        return sorted_payments[:limit]

    def _analyze_errors(self, payments_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze payment errors."""
        error_breakdown = {}

        for payment in payments_data:
            if payment.get("status") == "failed":
                error_type = payment.get("error_type", "unknown")
                error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1

        return error_breakdown

    def _analyze_plan_performance(
        self, payments_data: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze plan performance."""
        plan_performance = {}

        for payment in payments_data:
            plan = payment.get("plan", "unknown")
            if plan not in plan_performance:
                plan_performance[plan] = {
                    "total_payments": 0,
                    "successful_payments": 0,
                    "total_revenue": 0,
                    "average_payment": 0,
                    "conversion_rate": 0,
                }

            plan_performance[plan]["total_payments"] += 1
            if payment.get("status") == "active":
                plan_performance[plan]["successful_payments"] += 1
                plan_performance[plan]["total_revenue"] += payment.get("amount", 0)

        # Calculate derived metrics
        for plan, data in plan_performance.items():
            if data["successful_payments"] > 0:
                data["average_payment"] = (
                    data["total_revenue"] / data["successful_payments"]
                )
            if data["total_payments"] > 0:
                data["conversion_rate"] = (
                    data["successful_payments"] / data["total_payments"]
                ) * 100

        return plan_performance

    def _analyze_time_trends(
        self,
        payments_data: List[Dict[str, Any]],
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze time-based trends."""
        daily_trends = {}
        hourly_trends = {}

        for payment in payments_data:
            created_at = payment.get("created_at", "")
            if not created_at:
                continue

            try:
                payment_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                date_key = payment_date.strftime("%Y-%m-%d")
                hour_key = payment_date.strftime("%H")

                # Daily trends
                if date_key not in daily_trends:
                    daily_trends[date_key] = {
                        "date": date_key,
                        "payments": 0,
                        "revenue": 0,
                    }

                daily_trends[date_key]["payments"] += 1
                if payment.get("status") == "active":
                    daily_trends[date_key]["revenue"] += payment.get("amount", 0)

                # Hourly trends
                if hour_key not in hourly_trends:
                    hourly_trends[hour_key] = {
                        "hour": int(hour_key),
                        "payments": 0,
                        "revenue": 0,
                    }

                hourly_trends[hour_key]["payments"] += 1
                if payment.get("status") == "active":
                    hourly_trends[hour_key]["revenue"] += payment.get("amount", 0)

            except ValueError:
                continue

        return {
            "daily": sorted(daily_trends.values(), key=lambda x: x["date"]),
            "hourly": sorted(hourly_trends.values(), key=lambda x: x["hour"]),
        }


# Singleton instance
payment_analytics_service = PaymentAnalyticsService()
