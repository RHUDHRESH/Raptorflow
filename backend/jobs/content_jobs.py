"""
Content jobs for Raptorflow.

Provides background jobs for daily content generation,
quality checks, and content scheduling.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from decorators import background_job, daily_job, hourly_job, job, weekly_job
from infrastructure.cloud_monitoring import get_cloud_monitoring
from infrastructure.logging import get_cloud_logging

from .models import JobResult, JobStatus

logger = logging.getLogger(__name__)


@dataclass
class DailyWinsResult:
    """Result of daily wins generation."""

    workspace_id: str
    date: str
    wins_generated: int
    categories_covered: List[str]
    engagement_metrics: Dict[str, Any]
    quality_score: float
    distribution_channels: List[str]
    user_feedback: Dict[str, Any]
    processing_time_seconds: float
    errors: List[str]


@dataclass
class ContentQualityCheckResult:
    """Result of content quality check."""

    workspace_id: str
    content_items_checked: int
    quality_scores: Dict[str, float]
    issues_found: List[Dict[str, Any]]
    recommendations: List[str]
    auto_fixes_applied: int
    manual_review_required: int
    overall_quality_score: float
    processing_time_seconds: float
    errors: List[str]


@dataclass
class ContentScheduleResult:
    """Result of content scheduling."""

    workspace_id: str
    content_scheduled: int
    schedule_optimizations: List[Dict[str, Any]]
    audience_segments: List[str]
    timing_recommendations: List[str]
    performance_predictions: Dict[str, Any]
    a_b_tests_created: int
    processing_time_seconds: float
    errors: List[str]


@dataclass
class ContentAnalysisResult:
    """Result of content analysis."""

    workspace_id: str
    total_content: int
    engagement_rates: Dict[str, float]
    top_performing_content: List[Dict[str, Any]]
    content_gaps: List[str]
    audience_insights: Dict[str, Any]
    trend_analysis: Dict[str, Any]
    optimization_opportunities: List[str]
    processing_time_seconds: float
    errors: List[str]


class ContentJobs:
    """Content job implementations."""

    def __init__(self):
        self.logger = logging.getLogger("content_jobs")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

    async def generate_daily_wins_job(
        self, workspace_id: str, date: Optional[str] = None
    ) -> DailyWinsResult:
        """Generate daily wins content for a workspace."""
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")

        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting daily wins generation for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "date": date,
                    "job_type": "generate_daily_wins",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get content service
            from content.content_service import get_content_service

            content_service = get_content_service()

            # Get workspace content preferences
            content_preferences = (
                await content_service.get_workspace_content_preferences(workspace_id)
            )

            # Generate daily wins
            wins_result = await content_service.generate_daily_wins(
                workspace_id, date, content_preferences
            )

            # Extract results
            wins_generated = wins_result.get("wins_count", 0)
            categories_covered = wins_result.get("categories", [])
            engagement_metrics = wins_result.get("engagement_metrics", {})
            quality_score = wins_result.get("quality_score", 0.0)
            distribution_channels = wins_result.get("distribution_channels", [])
            user_feedback = wins_result.get("user_feedback", {})

            # Schedule content distribution
            if wins_generated > 0:
                await content_service.schedule_content_distribution(
                    workspace_id, wins_result.get("content_items", [])
                )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = DailyWinsResult(
                workspace_id=workspace_id,
                date=date,
                wins_generated=wins_generated,
                categories_covered=categories_covered,
                engagement_metrics=engagement_metrics,
                quality_score=quality_score,
                distribution_channels=distribution_channels,
                user_feedback=user_feedback,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "daily_wins_generated", wins_generated, {"workspace_id": workspace_id}
            )

            await self.monitoring.record_metric(
                "daily_wins_quality_score",
                quality_score,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "daily_wins_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Daily wins generation completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "date": date,
                    "wins_generated": wins_generated,
                    "categories_covered": len(categories_covered),
                    "quality_score": quality_score,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Daily wins generation failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Daily wins generation failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "date": date,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def content_quality_check_job(
        self, workspace_id: str
    ) -> ContentQualityCheckResult:
        """Check content quality for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting content quality check for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "content_quality_check",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get content service
            from content.content_service import get_content_service

            content_service = get_content_service()

            # Get recent content for quality check
            content_items = await content_service.get_recent_content(
                workspace_id, days=7
            )
            content_items_checked = len(content_items)

            # Perform quality checks
            quality_results = await content_service.check_content_quality(content_items)

            # Extract results
            quality_scores = quality_results.get("quality_scores", {})
            issues_found = quality_results.get("issues", [])
            recommendations = quality_results.get("recommendations", [])
            auto_fixes_applied = quality_results.get("auto_fixes_applied", 0)
            manual_review_required = quality_results.get("manual_review_required", 0)
            overall_quality_score = quality_results.get("overall_score", 0.0)

            # Apply auto-fixes
            if auto_fixes_applied > 0:
                await content_service.apply_auto_fixes(
                    workspace_id, quality_results.get("auto_fixes", [])
                )

            # Create quality reports
            await content_service.create_quality_report(workspace_id, quality_results)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = ContentQualityCheckResult(
                workspace_id=workspace_id,
                content_items_checked=content_items_checked,
                quality_scores=quality_scores,
                issues_found=issues_found,
                recommendations=recommendations,
                auto_fixes_applied=auto_fixes_applied,
                manual_review_required=manual_review_required,
                overall_quality_score=overall_quality_score,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "content_quality_items_checked",
                content_items_checked,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "content_quality_overall_score",
                overall_quality_score,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "content_quality_issues_found",
                len(issues_found),
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Content quality check completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "content_items_checked": content_items_checked,
                    "overall_quality_score": overall_quality_score,
                    "issues_found": len(issues_found),
                    "auto_fixes_applied": auto_fixes_applied,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Content quality check failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Content quality check failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def schedule_content_job(self, workspace_id: str) -> ContentScheduleResult:
        """Schedule content for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting content scheduling for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "schedule_content",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get content service
            from content.content_service import get_content_service

            content_service = get_content_service()

            # Get content calendar
            calendar = await content_service.get_content_calendar(workspace_id)

            # Get audience segments
            audience_segments = await content_service.get_audience_segments(
                workspace_id
            )

            # Generate schedule optimizations
            schedule_optimizations = await content_service.optimize_content_schedule(
                workspace_id, calendar, audience_segments
            )

            # Get timing recommendations
            timing_recommendations = await content_service.get_timing_recommendations(
                workspace_id, audience_segments
            )

            # Predict performance
            performance_predictions = await content_service.predict_content_performance(
                workspace_id, schedule_optimizations
            )

            # Create A/B tests
            a_b_tests_created = 0
            if schedule_optimizations:
                a_b_tests = await content_service.create_a_b_tests(
                    workspace_id, schedule_optimizations
                )
                a_b_tests_created = len(a_b_tests)

            # Schedule content
            content_scheduled = await content_service.schedule_content(
                workspace_id, schedule_optimizations
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = ContentScheduleResult(
                workspace_id=workspace_id,
                content_scheduled=content_scheduled,
                schedule_optimizations=schedule_optimizations,
                audience_segments=[
                    segment.get("name") for segment in audience_segments
                ],
                timing_recommendations=timing_recommendations,
                performance_predictions=performance_predictions,
                a_b_tests_created=a_b_tests_created,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "content_scheduled_count",
                content_scheduled,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "content_a_b_tests_created",
                a_b_tests_created,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "content_schedule_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Content scheduling completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "content_scheduled": content_scheduled,
                    "schedule_optimizations": len(schedule_optimizations),
                    "a_b_tests_created": a_b_tests_created,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Content scheduling failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Content scheduling failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def content_analysis_job(
        self, workspace_id: str, period_days: int = 30
    ) -> ContentAnalysisResult:
        """Analyze content performance for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting content analysis for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "period_days": period_days,
                    "job_type": "content_analysis",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get content service
            from content.content_service import get_content_service

            content_service = get_content_service()

            # Get content analytics
            content_analytics = await content_service.get_content_analytics(
                workspace_id, period_days
            )

            # Extract results
            total_content = content_analytics.get("total_content", 0)
            engagement_rates = content_analytics.get("engagement_rates", {})
            top_performing_content = content_analytics.get("top_performing", [])
            content_gaps = content_analytics.get("content_gaps", [])
            audience_insights = content_analytics.get("audience_insights", {})
            trend_analysis = content_analytics.get("trend_analysis", {})

            # Generate optimization opportunities
            optimization_opportunities = (
                await content_service.generate_optimization_opportunities(
                    workspace_id, content_analytics
                )
            )

            # Create content analysis report
            await content_service.create_analysis_report(
                workspace_id, content_analytics
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = ContentAnalysisResult(
                workspace_id=workspace_id,
                total_content=total_content,
                engagement_rates=engagement_rates,
                top_performing_content=top_performing_content,
                content_gaps=content_gaps,
                audience_insights=audience_insights,
                trend_analysis=trend_analysis,
                optimization_opportunities=optimization_opportunities,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "content_analysis_total_content",
                total_content,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "content_analysis_engagement_rate",
                engagement_rates.get("average", 0.0),
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "content_analysis_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Content analysis completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "period_days": period_days,
                    "total_content": total_content,
                    "content_gaps": len(content_gaps),
                    "optimization_opportunities": len(optimization_opportunities),
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Content analysis failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Content analysis failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "period_days": period_days,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def content_optimization_job(self, workspace_id: str) -> Dict[str, Any]:
        """Optimize content for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting content optimization for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "content_optimization",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get content service
            from content.content_service import get_content_service

            content_service = get_content_service()

            # Get underperforming content
            underperforming_content = await content_service.get_underperforming_content(
                workspace_id
            )

            # Generate optimizations
            optimization_results = []

            for content_item in underperforming_content:
                try:
                    optimization = await content_service.optimize_content(content_item)
                    optimization_results.append(optimization)
                except Exception as e:
                    errors.append(
                        f"Failed to optimize content {content_item.id}: {str(e)}"
                    )

            # Apply optimizations
            optimizations_applied = 0
            for optimization in optimization_results:
                if optimization.get("auto_apply", False):
                    await content_service.apply_content_optimization(optimization)
                    optimizations_applied += 1

            # Create optimization report
            await content_service.create_optimization_report(
                workspace_id, optimization_results
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "workspace_id": workspace_id,
                "underperforming_content_found": len(underperforming_content),
                "optimizations_generated": len(optimization_results),
                "optimizations_applied": optimizations_applied,
                "optimization_results": optimization_results,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Record metrics
            await self.monitoring.record_metric(
                "content_optimization_underperforming_found",
                len(underperforming_content),
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "content_optimization_applied",
                optimizations_applied,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Content optimization completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "underperforming_content_found": len(underperforming_content),
                    "optimizations_applied": optimizations_applied,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Content optimization failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Content optimization failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise


# Create global instance
_content_jobs = ContentJobs()


# Job implementations with decorators
@daily_job(
    hour=8,
    minute=0,
    queue="content",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Generate daily wins",
)
async def generate_daily_wins_job(
    workspace_id: str, date: Optional[str] = None
) -> Dict[str, Any]:
    """Generate daily wins job."""
    result = await _content_jobs.generate_daily_wins_job(workspace_id, date)
    return result.__dict__


@daily_job(
    hour=9,
    minute=0,
    queue="content",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Check content quality",
)
async def content_quality_check_job(workspace_id: str) -> Dict[str, Any]:
    """Content quality check job."""
    result = await _content_jobs.content_quality_check_job(workspace_id)
    return result.__dict__


@daily_job(
    hour=10,
    minute=0,
    queue="content",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Schedule content",
)
async def schedule_content_job(workspace_id: str) -> Dict[str, Any]:
    """Schedule content job."""
    result = await _content_jobs.schedule_content_job(workspace_id)
    return result.__dict__


@weekly_job(
    day_of_week=0,  # Sunday
    hour=11,
    minute=0,
    queue="content",
    retries=2,
    timeout=3600,  # 1 hour
    description="Analyze content performance",
)
async def content_analysis_job(
    workspace_id: str, period_days: int = 30
) -> Dict[str, Any]:
    """Content analysis job."""
    result = await _content_jobs.content_analysis_job(workspace_id, period_days)
    return result.__dict__


@daily_job(
    hour=7,
    minute=30,
    queue="content",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Optimize content",
)
async def content_optimization_job(workspace_id: str) -> Dict[str, Any]:
    """Content optimization job."""
    result = await _content_jobs.content_optimization_job(workspace_id)
    return result


# Convenience functions
async def generate_workspace_daily_wins(
    workspace_id: str, date: Optional[str] = None
) -> DailyWinsResult:
    """Generate daily wins for a workspace."""
    return await _content_jobs.generate_daily_wins_job(workspace_id, date)


async def check_workspace_content_quality(
    workspace_id: str,
) -> ContentQualityCheckResult:
    """Check content quality for a workspace."""
    return await _content_jobs.content_quality_check_job(workspace_id)


async def schedule_workspace_content(workspace_id: str) -> ContentScheduleResult:
    """Schedule content for a workspace."""
    return await _content_jobs.schedule_content_job(workspace_id)


async def analyze_workspace_content(
    workspace_id: str, period_days: int = 30
) -> ContentAnalysisResult:
    """Analyze content for a workspace."""
    return await _content_jobs.content_analysis_job(workspace_id, period_days)


async def optimize_workspace_content(workspace_id: str) -> Dict[str, Any]:
    """Optimize content for a workspace."""
    return await _content_jobs.content_optimization_job(workspace_id)


# Export all jobs
__all__ = [
    "ContentJobs",
    "generate_daily_wins_job",
    "content_quality_check_job",
    "schedule_content_job",
    "content_analysis_job",
    "content_optimization_job",
    "generate_workspace_daily_wins",
    "check_workspace_content_quality",
    "schedule_workspace_content",
    "analyze_workspace_content",
    "optimize_workspace_content",
]
