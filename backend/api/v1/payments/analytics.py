"""
Payment Analytics API Endpoints
Provides REST API endpoints for payment analytics and monitoring
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..core.auth import get_current_user, get_workspace_id
from ..core.models import User, AuthContext
from ..services.payment_analytics import (
    payment_analytics_service,
    PaymentAnalyticsService,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["payment-analytics"])
security = HTTPBearer()


@router.get("/overview")
async def get_payment_analytics_overview(
    days: int = Query(default=30, ge=1, le=365),
    plan_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
) -> Dict[str, Any]:
    """
    Get comprehensive payment analytics overview.

    Args:
        days: Number of days to analyze (default: 30)
        plan_filter: Optional plan name filter
        current_user: Authenticated user
        workspace_id: User's workspace ID

    Returns:
        Comprehensive payment analytics data
    """
    try:
        # Validate user has permission to view analytics
        if not _has_analytics_permission(current_user, workspace_id):
            raise HTTPException(
                status_code=403, detail="Insufficient permissions to view analytics"
            )

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get analytics data
        analytics = payment_analytics_service.get_payment_analytics(
            start_date=start_date, end_date=end_date, plan_filter=plan_filter
        )

        return {
            "success": True,
            "data": {
                "metrics": {
                    "total_payments": analytics.metrics.total_payments,
                    "successful_payments": analytics.metrics.successful_payments,
                    "failed_payments": analytics.metrics.failed_payments,
                    "total_revenue": analytics.metrics.total_revenue,
                    "average_payment_amount": analytics.metrics.average_payment_amount,
                    "conversion_rate": analytics.metrics.conversion_rate,
                    "failure_rate": analytics.metrics.failure_rate,
                    "payment_by_plan": analytics.metrics.payment_by_plan,
                },
                "recent_transactions": analytics.recent_transactions,
                "error_breakdown": analytics.error_breakdown,
                "plan_performance": analytics.plan_performance,
                "time_trends": analytics.time_based_analytics,
                "date_range": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days,
                },
            },
        }

    except Exception as exc:
        logger.error(f"Failed to get payment analytics overview: {exc}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve payment analytics"
        ) from exc


@router.get("/conversion-rates")
async def get_conversion_rates(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
) -> Dict[str, Any]:
    """
    Get payment conversion rates by plan.

    Args:
        days: Number of days to analyze (default: 30)
        current_user: Authenticated user
        workspace_id: User's workspace ID

    Returns:
        Conversion rates data by plan
    """
    try:
        if not _has_analytics_permission(current_user, workspace_id):
            raise HTTPException(
                status_code=403, detail="Insufficient permissions to view analytics"
            )

        conversion_rates = payment_analytics_service.get_conversion_rates(days)

        return {
            "success": True,
            "data": {
                "conversion_rates": conversion_rates,
                "period_days": days,
                "calculated_at": datetime.now().isoformat(),
            },
        }

    except Exception as exc:
        logger.error(f"Failed to get conversion rates: {exc}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve conversion rates"
        ) from exc


@router.get("/failure-reasons")
async def get_failure_reasons(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
) -> Dict[str, Any]:
    """
    Get payment failure reasons breakdown.

    Args:
        days: Number of days to analyze (default: 30)
        current_user: Authenticated user
        workspace_id: User's workspace ID

    Returns:
        Failure reasons breakdown
    """
    try:
        if not _has_analytics_permission(current_user, workspace_id):
            raise HTTPException(
                status_code=403, detail="Insufficient permissions to view analytics"
            )

        failure_reasons = payment_analytics_service.get_failure_reasons(days)

        # Sort by frequency
        sorted_failures = sorted(
            failure_reasons.items(), key=lambda x: x[1], reverse=True
        )

        return {
            "success": True,
            "data": {
                "failure_reasons": dict(sorted_failures),
                "total_failures": sum(failure_reasons.values()),
                "period_days": days,
                "calculated_at": datetime.now().isoformat(),
            },
        }

    except Exception as exc:
        logger.error(f"Failed to get failure reasons: {exc}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve failure reasons"
        ) from exc


@router.get("/revenue")
async def get_revenue_metrics(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
) -> Dict[str, Any]:
    """
    Get revenue metrics.

    Args:
        days: Number of days to analyze (default: 30)
        current_user: Authenticated user
        workspace_id: User's workspace ID

    Returns:
        Revenue metrics data
    """
    try:
        if not _has_analytics_permission(current_user, workspace_id):
            raise HTTPException(
                status_code=403, detail="Insufficient permissions to view analytics"
            )

        revenue_metrics = payment_analytics_service.get_revenue_metrics(days)

        return {
            "success": True,
            "data": {
                **revenue_metrics,
                "period_days": days,
                "calculated_at": datetime.now().isoformat(),
            },
        }

    except Exception as exc:
        logger.error(f"Failed to get revenue metrics: {exc}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve revenue metrics"
        ) from exc


@router.get("/dashboard")
async def get_payment_dashboard(
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
) -> Dict[str, Any]:
    """
    Get payment dashboard data (combined analytics for admin dashboard).

    Args:
        days: Number of days to analyze (default: 30)
        current_user: Authenticated user
        workspace_id: User's workspace ID

    Returns:
        Combined dashboard data
    """
    try:
        if not _has_analytics_permission(current_user, workspace_id):
            raise HTTPException(
                status_code=403, detail="Insufficient permissions to view analytics"
            )

        # Get all analytics data
        analytics = payment_analytics_service.get_payment_analytics(
            start_date=datetime.now() - timedelta(days=days), end_date=datetime.now()
        )

        conversion_rates = payment_analytics_service.get_conversion_rates(days)
        failure_reasons = payment_analytics_service.get_failure_reasons(days)
        revenue_metrics = payment_analytics_service.get_revenue_metrics(days)

        return {
            "success": True,
            "data": {
                "summary": {
                    "total_payments": analytics.metrics.total_payments,
                    "successful_payments": analytics.metrics.successful_payments,
                    "total_revenue": analytics.metrics.total_revenue,
                    "conversion_rate": analytics.metrics.conversion_rate,
                    "failure_rate": analytics.metrics.failure_rate,
                },
                "conversion_rates": conversion_rates,
                "failure_reasons": failure_reasons,
                "revenue_metrics": revenue_metrics,
                "plan_performance": analytics.plan_performance,
                "recent_transactions": analytics.recent_transactions[
                    :5
                ],  # Last 5 transactions
                "time_trends": analytics.time_based_analytics,
                "period_days": days,
                "calculated_at": datetime.now().isoformat(),
            },
        }

    except Exception as exc:
        logger.error(f"Failed to get payment dashboard: {exc}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve payment dashboard"
        ) from exc


@router.post("/track-event")
async def track_payment_event(
    event_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
) -> Dict[str, Any]:
    """
    Track a payment event for analytics.

    Args:
        event_data: Event data to track
        current_user: Authenticated user
        workspace_id: User's workspace ID

    Returns:
        Tracking result
    """
    try:
        # Validate required fields
        required_fields = [
            "event_type",
            "transaction_id",
            "plan_name",
            "amount",
            "status",
        ]
        for field in required_fields:
            if field not in event_data:
                raise HTTPException(
                    status_code=400, detail=f"Missing required field: {field}"
                )

        # Track the event
        success = payment_analytics_service.track_payment_event(
            event_type=event_data["event_type"],
            transaction_id=event_data["transaction_id"],
            plan_name=event_data["plan_name"],
            amount=event_data["amount"],
            status=event_data["status"],
            error_type=event_data.get("error_type"),
            user_id=current_user.id,
            metadata=event_data.get("metadata", {}),
        )

        if success:
            return {
                "success": True,
                "message": "Payment event tracked successfully",
                "tracked_at": datetime.now().isoformat(),
            }
        else:
            return {"success": False, "message": "Failed to track payment event"}

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Failed to track payment event: {exc}")
        raise HTTPException(
            status_code=500, detail="Failed to track payment event"
        ) from exc


def _has_analytics_permission(user: User, workspace_id: str) -> bool:
    """
    Check if user has permission to view analytics.

    Args:
        user: User object
        workspace_id: Workspace ID

    Returns:
        True if user has permission, False otherwise
    """
    # For now, allow all authenticated users to view analytics
    # In a real implementation, you might check for admin/owner roles
    return True


# Export router for inclusion in main API
__all__ = ["router"]
