"""
Billing jobs for Raptorflow.

Provides background jobs for usage calculation,
invoice generation, and usage limit monitoring.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from infrastructure.cloud_monitoring import get_cloud_monitoring
from infrastructure.logging import get_cloud_logging
from decorators import background_job, daily_job, hourly_job, job, weekly_job
from .models import JobResult, JobStatus

logger = logging.getLogger(__name__)


@dataclass
class UsageCalculationResult:
    """Result of usage calculation operation."""

    workspace_id: str
    period_start: str
    period_end: str
    total_api_requests: int
    total_agent_executions: int
    total_tokens_used: int
    total_storage_gb: float
    total_users: int
    total_sessions: int
    usage_breakdown: Dict[str, Any]
    cost_breakdown: Dict[str, Any]
    total_cost: float
    processing_time_seconds: float
    errors: List[str]


@dataclass
class InvoiceGenerationResult:
    """Result of invoice generation operation."""

    workspace_id: str
    invoice_id: str
    period_start: str
    period_end: str
    billing_period: str
    subtotal: float
    tax_amount: float
    total_amount: float
    currency: str
    line_items: List[Dict[str, Any]]
    status: str
    due_date: str
    processing_time_seconds: float
    errors: List[str]


@dataclass
class UsageLimitCheckResult:
    """Result of usage limit check operation."""

    workspace_id: str
    current_usage: Dict[str, Any]
    limits: Dict[str, Any]
    exceeded_limits: List[Dict[str, Any]]
    warnings: List[Dict[str, Any]]
    recommendations: List[str]
    processing_time_seconds: float
    errors: List[str]


@dataclass
class BillingReportResult:
    """Result of billing report generation."""

    period_start: str
    period_end: str
    total_workspaces: int
    active_workspaces: int
    total_revenue: float
    total_costs: float
    gross_margin: float
    top_workspaces: List[Dict[str, Any]]
    usage_trends: Dict[str, Any]
    revenue_trends: Dict[str, Any]
    processing_time_seconds: float
    errors: List[str]


class BillingJobs:
    """Billing job implementations."""

    def __init__(self):
        self.logger = logging.getLogger("billing_jobs")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

    async def calculate_usage_job(
        self,
        workspace_id: str,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
    ) -> UsageCalculationResult:
        """Calculate usage for a workspace."""
        if period_start is None:
            period_start = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

        if period_end is None:
            period_end = datetime.utcnow().strftime("%Y-%m-%d")

        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting usage calculation for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "job_type": "calculate_usage",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get billing service
            from billing.billing_service import get_billing_service

            billing_service = get_billing_service()

            # Get usage metrics
            usage_metrics = await billing_service.get_usage_metrics(
                workspace_id, period_start, period_end
            )

            # Get cost breakdown
            cost_breakdown = await billing_service.calculate_costs(
                workspace_id, usage_metrics
            )

            # Get detailed usage breakdown
            usage_breakdown = await billing_service.get_usage_breakdown(
                workspace_id, period_start, period_end
            )

            # Calculate total cost
            total_cost = sum(item.get("cost", 0.0) for item in cost_breakdown.values())

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = UsageCalculationResult(
                workspace_id=workspace_id,
                period_start=period_start,
                period_end=period_end,
                total_api_requests=usage_metrics.get("total_api_requests", 0),
                total_agent_executions=usage_metrics.get("total_agent_executions", 0),
                total_tokens_used=usage_metrics.get("total_tokens_used", 0),
                total_storage_gb=usage_metrics.get("total_storage_gb", 0.0),
                total_users=usage_metrics.get("total_users", 0),
                total_sessions=usage_metrics.get("total_sessions", 0),
                usage_breakdown=usage_breakdown,
                cost_breakdown=cost_breakdown,
                total_cost=total_cost,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "usage_calculation_total_cost",
                total_cost,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "usage_calculation_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Usage calculation completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "total_cost": total_cost,
                    "total_api_requests": result.total_api_requests,
                    "total_agent_executions": result.total_agent_executions,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Usage calculation failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Usage calculation failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def generate_invoice_job(
        self,
        workspace_id: str,
        period_start: Optional[str] = None,
        period_end: Optional[str] = None,
    ) -> InvoiceGenerationResult:
        """Generate invoice for a workspace."""
        if period_start is None:
            period_start = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

        if period_end is None:
            period_end = datetime.utcnow().strftime("%Y-%m-%d")

        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting invoice generation for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "job_type": "generate_invoice",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get billing service
            from billing.billing_service import get_billing_service

            billing_service = get_billing_service()

            # Calculate usage first
            usage_result = await self.calculate_usage_job(
                workspace_id, period_start, period_end
            )

            # Generate invoice
            invoice_result = await billing_service.generate_invoice(
                workspace_id, usage_result, period_start, period_end
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = InvoiceGenerationResult(
                workspace_id=workspace_id,
                invoice_id=invoice_result.get("invoice_id"),
                period_start=period_start,
                period_end=period_end,
                billing_period=invoice_result.get("billing_period"),
                subtotal=invoice_result.get("subtotal", 0.0),
                tax_amount=invoice_result.get("tax_amount", 0.0),
                total_amount=invoice_result.get("total_amount", 0.0),
                currency=invoice_result.get("currency", "USD"),
                line_items=invoice_result.get("line_items", []),
                status=invoice_result.get("status", "draft"),
                due_date=invoice_result.get("due_date"),
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "invoice_generation_total_amount",
                result.total_amount,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "invoice_generation_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Invoice generation completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "invoice_id": result.invoice_id,
                    "total_amount": result.total_amount,
                    "status": result.status,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Invoice generation failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Invoice generation failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def check_usage_limits_job(
        self, workspace_id: Optional[str] = None
    ) -> UsageLimitCheckResult:
        """Check usage limits for workspaces."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting usage limits check for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "check_usage_limits",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get billing service
            from billing.billing_service import get_billing_service

            billing_service = get_billing_service()

            if workspace_id:
                # Check specific workspace
                current_usage = await billing_service.get_current_usage(workspace_id)
                limits = await billing_service.get_usage_limits(workspace_id)

                # Check for exceeded limits
                exceeded_limits = []
                warnings = []

                for metric, limit in limits.items():
                    current = current_usage.get(metric, 0)
                    if current > limit:
                        exceeded_limits.append(
                            {
                                "metric": metric,
                                "current": current,
                                "limit": limit,
                                "percentage": (current / limit) * 100,
                            }
                        )
                    elif current > limit * 0.8:  # 80% warning threshold
                        warnings.append(
                            {
                                "metric": metric,
                                "current": current,
                                "limit": limit,
                                "percentage": (current / limit) * 100,
                            }
                        )

                # Generate recommendations
                recommendations = await billing_service.generate_usage_recommendations(
                    workspace_id, current_usage, limits, exceeded_limits, warnings
                )

            else:
                # Check all workspaces
                current_usage = {"all_workspaces": True}
                limits = {"all_workspaces": True}
                exceeded_limits = []
                warnings = []
                recommendations = []

                # Get all workspaces
                from core.workspace import get_workspace_service

                workspace_service = get_workspace_service()
                workspaces = await workspace_service.get_all_workspaces()

                for ws in workspaces:
                    try:
                        ws_usage = await billing_service.get_current_usage(ws.id)
                        ws_limits = await billing_service.get_usage_limits(ws.id)

                        for metric, limit in ws_limits.items():
                            current = ws_usage.get(metric, 0)
                            if current > limit:
                                exceeded_limits.append(
                                    {
                                        "workspace_id": ws.id,
                                        "workspace_name": ws.name,
                                        "metric": metric,
                                        "current": current,
                                        "limit": limit,
                                        "percentage": (current / limit) * 100,
                                    }
                                )
                            elif current > limit * 0.8:
                                warnings.append(
                                    {
                                        "workspace_id": ws.id,
                                        "workspace_name": ws.name,
                                        "metric": metric,
                                        "current": current,
                                        "limit": limit,
                                        "percentage": (current / limit) * 100,
                                    }
                                )

                    except Exception as e:
                        errors.append(f"Failed to check workspace {ws.id}: {str(e)}")

                recommendations = (
                    await billing_service.generate_global_usage_recommendations(
                        exceeded_limits, warnings
                    )
                )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = UsageLimitCheckResult(
                workspace_id=workspace_id or "all",
                current_usage=current_usage,
                limits=limits,
                exceeded_limits=exceeded_limits,
                warnings=warnings,
                recommendations=recommendations,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "usage_limits_exceeded_count",
                len(exceeded_limits),
                {"workspace_id": workspace_id or "all"},
            )

            await self.monitoring.record_metric(
                "usage_limits_warnings_count",
                len(warnings),
                {"workspace_id": workspace_id or "all"},
            )

            await self.monitoring.record_metric(
                "usage_limits_check_processing_time",
                processing_time,
                {"workspace_id": workspace_id or "all"},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Usage limits check completed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "exceeded_limits_count": len(exceeded_limits),
                    "warnings_count": len(warnings),
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Usage limits check failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Usage limits check failed for workspace: {workspace_id or 'all'}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def billing_report_job(
        self, period_start: Optional[str] = None, period_end: Optional[str] = None
    ) -> BillingReportResult:
        """Generate billing report."""
        if period_start is None:
            period_start = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

        if period_end is None:
            period_end = datetime.utcnow().strftime("%Y-%m-%d")

        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting billing report for period: {period_start} to {period_end}",
                {
                    "period_start": period_start,
                    "period_end": period_end,
                    "job_type": "billing_report",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get billing service
            from billing.billing_service import get_billing_service

            billing_service = get_billing_service()

            # Get workspace statistics
            workspace_stats = await billing_service.get_workspace_statistics(
                period_start, period_end
            )

            # Get revenue data
            revenue_data = await billing_service.get_revenue_data(
                period_start, period_end
            )

            # Get cost data
            cost_data = await billing_service.get_cost_data(period_start, period_end)

            # Get top workspaces
            top_workspaces = await billing_service.get_top_workspaces(
                period_start, period_end, limit=10
            )

            # Get usage trends
            usage_trends = await billing_service.get_usage_trends(
                period_start, period_end
            )

            # Get revenue trends
            revenue_trends = await billing_service.get_revenue_trends(
                period_start, period_end
            )

            # Calculate metrics
            total_workspaces = workspace_stats.get("total_workspaces", 0)
            active_workspaces = workspace_stats.get("active_workspaces", 0)
            total_revenue = revenue_data.get("total_revenue", 0.0)
            total_costs = cost_data.get("total_costs", 0.0)
            gross_margin = total_revenue - total_costs
            gross_margin_percentage = (
                (gross_margin / total_revenue * 100) if total_revenue > 0 else 0.0
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = BillingReportResult(
                period_start=period_start,
                period_end=period_end,
                total_workspaces=total_workspaces,
                active_workspaces=active_workspaces,
                total_revenue=total_revenue,
                total_costs=total_costs,
                gross_margin=gross_margin_percentage,
                top_workspaces=top_workspaces,
                usage_trends=usage_trends,
                revenue_trends=revenue_trends,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "billing_report_total_revenue",
                total_revenue,
                {"period_start": period_start, "period_end": period_end},
            )

            await self.monitoring.record_metric(
                "billing_report_gross_margin",
                gross_margin_percentage,
                {"period_start": period_start, "period_end": period_end},
            )

            await self.monitoring.record_metric(
                "billing_report_processing_time",
                processing_time,
                {"period_start": period_start, "period_end": period_end},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Billing report completed for period: {period_start} to {period_end}",
                {
                    "period_start": period_start,
                    "period_end": period_end,
                    "total_workspaces": total_workspaces,
                    "active_workspaces": active_workspaces,
                    "total_revenue": total_revenue,
                    "gross_margin_percentage": gross_margin_percentage,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Billing report failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Billing report failed for period: {period_start} to {period_end}",
                {
                    "period_start": period_start,
                    "period_end": period_end,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def subscription_renewal_job(self) -> Dict[str, Any]:
        """Process subscription renewals."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                "Starting subscription renewal processing",
                {
                    "job_type": "subscription_renewal",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get billing service
            from billing.billing_service import get_billing_service

            billing_service = get_billing_service()

            # Get subscriptions due for renewal
            subscriptions = await billing_service.get_subscriptions_due_for_renewal()

            renewal_results = []

            for subscription in subscriptions:
                try:
                    # Process renewal
                    renewal_result = await billing_service.process_subscription_renewal(
                        subscription
                    )
                    renewal_results.append(renewal_result)

                except Exception as e:
                    errors.append(
                        f"Failed to renew subscription {subscription.id}: {str(e)}"
                    )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "subscriptions_processed": len(subscriptions),
                "successful_renewals": len(
                    [r for r in renewal_results if r.get("success", False)]
                ),
                "failed_renewals": len(
                    [r for r in renewal_results if not r.get("success", False)]
                ),
                "renewal_results": renewal_results,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Record metrics
            await self.monitoring.record_metric(
                "subscription_renewal_successful_count",
                result["successful_renewals"],
                {"operation": "renewal"},
            )

            await self.monitoring.record_metric(
                "subscription_renewal_failed_count",
                result["failed_renewals"],
                {"operation": "renewal"},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                "Subscription renewal processing completed",
                {
                    "subscriptions_processed": result["subscriptions_processed"],
                    "successful_renewals": result["successful_renewals"],
                    "failed_renewals": result["failed_renewals"],
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Subscription renewal processing failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                "Subscription renewal processing failed",
                {"error": str(e), "processing_time_seconds": processing_time},
            )

            raise


# Create global instance
_billing_jobs = BillingJobs()


# Job implementations with decorators
@daily_job(
    hour=1,
    minute=30,
    queue="billing",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Calculate usage for all workspaces",
)
async def calculate_usage_job() -> Dict[str, Any]:
    """Calculate usage job for all workspaces."""
    # Get all workspaces and calculate usage for each
    from core.workspace import get_workspace_service

    workspace_service = get_workspace_service()
    workspaces = await workspace_service.get_all_workspaces()

    results = []
    for workspace in workspaces:
        try:
            result = await _billing_jobs.calculate_usage_job(workspace.id)
            results.append(result.__dict__)
        except Exception as e:
            logger.error(f"Failed to calculate usage for workspace {workspace.id}: {e}")

    return {"results": results, "processed_workspaces": len(results)}


@daily_job(
    hour=2,
    minute=0,
    queue="billing",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Generate invoices for all workspaces",
)
async def generate_invoice_job() -> Dict[str, Any]:
    """Generate invoice job for all workspaces."""
    # Get all workspaces and generate invoices for each
    from core.workspace import get_workspace_service

    workspace_service = get_workspace_service()
    workspaces = await workspace_service.get_all_workspaces()

    results = []
    for workspace in workspaces:
        try:
            result = await _billing_jobs.generate_invoice_job(workspace.id)
            results.append(result.__dict__)
        except Exception as e:
            logger.error(
                f"Failed to generate invoice for workspace {workspace.id}: {e}"
            )

    return {"results": results, "processed_workspaces": len(results)}


@hourly_job(
    minute=0,
    queue="billing",
    retries=1,
    timeout=600,  # 10 minutes
    description="Check usage limits",
)
async def check_usage_limits_job() -> Dict[str, Any]:
    """Check usage limits job."""
    result = await _billing_jobs.check_usage_limits_job()
    return result.__dict__


@weekly_job(
    day_of_week=0,  # Sunday
    hour=3,
    minute=0,
    queue="billing",
    retries=2,
    timeout=3600,  # 1 hour
    description="Generate billing report",
)
async def billing_report_job() -> Dict[str, Any]:
    """Billing report job."""
    result = await _billing_jobs.billing_report_job()
    return result.__dict__


@daily_job(
    hour=0,
    minute=0,
    queue="billing",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Process subscription renewals",
)
async def subscription_renewal_job() -> Dict[str, Any]:
    """Subscription renewal job."""
    result = await _billing_jobs.subscription_renewal_job()
    return result


@background_job(
    queue="billing",
    retries=1,
    timeout=300,  # 5 minutes
    description="Calculate usage for specific workspace",
)
async def workspace_usage_calculation_job(
    workspace_id: str,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
) -> Dict[str, Any]:
    """Workspace-specific usage calculation job."""
    result = await _billing_jobs.calculate_usage_job(
        workspace_id, period_start, period_end
    )
    return result.__dict__


@background_job(
    queue="billing",
    retries=1,
    timeout=300,  # 5 minutes
    description="Generate invoice for specific workspace",
)
async def workspace_invoice_generation_job(
    workspace_id: str,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
) -> Dict[str, Any]:
    """Workspace-specific invoice generation job."""
    result = await _billing_jobs.generate_invoice_job(
        workspace_id, period_start, period_end
    )
    return result.__dict__


# Convenience functions
async def calculate_workspace_usage(
    workspace_id: str,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
) -> UsageCalculationResult:
    """Calculate usage for a specific workspace."""
    return await _billing_jobs.calculate_usage_job(
        workspace_id, period_start, period_end
    )


async def generate_workspace_invoice(
    workspace_id: str,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None,
) -> InvoiceGenerationResult:
    """Generate invoice for a specific workspace."""
    return await _billing_jobs.generate_invoice_job(
        workspace_id, period_start, period_end
    )


async def check_workspace_usage_limits(workspace_id: str) -> UsageLimitCheckResult:
    """Check usage limits for a specific workspace."""
    return await _billing_jobs.check_usage_limits_job(workspace_id)


async def generate_billing_report(
    period_start: Optional[str] = None, period_end: Optional[str] = None
) -> BillingReportResult:
    """Generate billing report."""
    return await _billing_jobs.billing_report_job(period_start, period_end)


async def process_subscription_renewals() -> Dict[str, Any]:
    """Process subscription renewals."""
    return await _billing_jobs.subscription_renewal_job()


# Export all jobs
__all__ = [
    "BillingJobs",
    "calculate_usage_job",
    "generate_invoice_job",
    "check_usage_limits_job",
    "billing_report_job",
    "subscription_renewal_job",
    "workspace_usage_calculation_job",
    "workspace_invoice_generation_job",
    "calculate_workspace_usage",
    "generate_workspace_invoice",
    "check_workspace_usage_limits",
    "generate_billing_report",
    "process_subscription_renewals",
]
