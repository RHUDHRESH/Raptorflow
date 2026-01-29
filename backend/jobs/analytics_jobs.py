"""
Analytics jobs for Raptorflow.

Provides background jobs for daily usage summaries,
weekly reports, and agent performance analysis.
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
class DailyUsageSummary:
    """Daily usage summary data."""

    date: str
    total_users: int
    active_users: int
    total_sessions: int
    total_agent_executions: int
    total_api_requests: int
    total_tokens_used: int
    total_storage_used_mb: float
    average_session_duration: float
    top_agents: List[Dict[str, Any]]
    top_workspaces: List[Dict[str, Any]]
    errors: List[str]


@dataclass
class WeeklyReport:
    """Weekly report data."""

    week_start: str
    week_end: str
    total_users: int
    active_users: int
    new_users: int
    total_sessions: int
    total_agent_executions: int
    total_api_requests: int
    total_tokens_used: int
    total_storage_used_mb: float
    average_session_duration: float
    user_retention_rate: float
    agent_success_rate: float
    api_success_rate: float
    top_agents: List[Dict[str, Any]]
    top_workspaces: List[Dict[str, Any]]
    daily_breakdown: List[Dict[str, Any]]
    errors: List[str]


@dataclass
class AgentPerformanceAnalysis:
    """Agent performance analysis data."""

    agent_name: str
    analysis_period: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_execution_time: float
    average_tokens_per_execution: float
    success_rate: float
    error_rate: float
    top_errors: List[Dict[str, Any]]
    performance_trend: str  # improving, declining, stable
    recommendations: List[str]
    errors: List[str]


class AnalyticsJobs:
    """Analytics job implementations."""

    def __init__(self):
        self.logger = logging.getLogger("analytics_jobs")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

    async def daily_usage_summary_job(
        self, date: Optional[str] = None
    ) -> DailyUsageSummary:
        """Generate daily usage summary."""
        if date is None:
            date = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting daily usage summary for date: {date}",
                {
                    "date": date,
                    "job_type": "daily_usage_summary",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get analytics service
            from analytics.analytics_service import get_analytics_service

            analytics_service = get_analytics_service()

            # Get daily metrics
            daily_metrics = await analytics_service.get_daily_metrics(date)

            # Get user metrics
            user_metrics = await analytics_service.get_daily_user_metrics(date)

            # Get agent metrics
            agent_metrics = await analytics_service.get_daily_agent_metrics(date)

            # Get workspace metrics
            workspace_metrics = await analytics_service.get_daily_workspace_metrics(
                date
            )

            # Get session metrics
            session_metrics = await analytics_service.get_daily_session_metrics(date)

            # Get API metrics
            api_metrics = await analytics_service.get_daily_api_metrics(date)

            # Get storage metrics
            storage_metrics = await analytics_service.get_daily_storage_metrics(date)

            # Get top agents
            top_agents = await analytics_service.get_top_agents(date, limit=10)

            # Get top workspaces
            top_workspaces = await analytics_service.get_top_workspaces(date, limit=10)

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Create summary
            summary = DailyUsageSummary(
                date=date,
                total_users=user_metrics.get("total_users", 0),
                active_users=user_metrics.get("active_users", 0),
                total_sessions=session_metrics.get("total_sessions", 0),
                total_agent_executions=agent_metrics.get("total_executions", 0),
                total_api_requests=api_metrics.get("total_requests", 0),
                total_tokens_used=agent_metrics.get("total_tokens", 0),
                total_storage_used_mb=storage_metrics.get("total_storage_mb", 0.0),
                average_session_duration=session_metrics.get(
                    "average_duration_seconds", 0.0
                ),
                top_agents=top_agents,
                top_workspaces=top_workspaces,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "daily_usage_summary_processing_time", processing_time, {"date": date}
            )

            await self.monitoring.record_metric(
                "daily_active_users", summary.active_users, {"date": date}
            )

            await self.monitoring.record_metric(
                "daily_agent_executions", summary.total_agent_executions, {"date": date}
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Daily usage summary completed for date: {date}",
                {
                    "date": date,
                    "total_users": summary.total_users,
                    "active_users": summary.active_users,
                    "total_sessions": summary.total_sessions,
                    "total_agent_executions": summary.total_agent_executions,
                    "processing_time_seconds": processing_time,
                },
            )

            return summary

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Daily usage summary failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Daily usage summary failed for date: {date}",
                {
                    "date": date,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def weekly_report_job(self, week_start: Optional[str] = None) -> WeeklyReport:
        """Generate weekly report."""
        if week_start is None:
            # Get last week's start date (Monday)
            today = datetime.utcnow().date()
            days_since_monday = today.weekday()
            last_monday = today - timedelta(days=days_since_monday + 7)
            week_start = last_monday.strftime("%Y-%m-%d")

        week_end = (
            datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=6)
        ).strftime("%Y-%m-%d")

        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting weekly report for week: {week_start} to {week_end}",
                {
                    "week_start": week_start,
                    "week_end": week_end,
                    "job_type": "weekly_report",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get analytics service
            from analytics.analytics_service import get_analytics_service

            analytics_service = get_analytics_service()

            # Get weekly metrics
            weekly_metrics = await analytics_service.get_weekly_metrics(
                week_start, week_end
            )

            # Get user metrics
            user_metrics = await analytics_service.get_weekly_user_metrics(
                week_start, week_end
            )

            # Get agent metrics
            agent_metrics = await analytics_service.get_weekly_agent_metrics(
                week_start, week_end
            )

            # Get workspace metrics
            workspace_metrics = await analytics_service.get_weekly_workspace_metrics(
                week_start, week_end
            )

            # Get session metrics
            session_metrics = await analytics_service.get_weekly_session_metrics(
                week_start, week_end
            )

            # Get API metrics
            api_metrics = await analytics_service.get_weekly_api_metrics(
                week_start, week_end
            )

            # Get storage metrics
            storage_metrics = await analytics_service.get_weekly_storage_metrics(
                week_start, week_end
            )

            # Get daily breakdown
            daily_breakdown = []
            current_date = datetime.strptime(week_start, "%Y-%m-%d").date()
            end_date = datetime.strptime(week_end, "%Y-%m-%d").date()

            while current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                daily_metrics = await analytics_service.get_daily_metrics(date_str)

                daily_breakdown.append(
                    {
                        "date": date_str,
                        "active_users": daily_metrics.get("active_users", 0),
                        "agent_executions": daily_metrics.get("agent_executions", 0),
                        "api_requests": daily_metrics.get("api_requests", 0),
                        "tokens_used": daily_metrics.get("tokens_used", 0),
                    }
                )

                current_date += timedelta(days=1)

            # Get top agents
            top_agents = await analytics_service.get_top_agents_for_period(
                week_start, week_end, limit=10
            )

            # Get top workspaces
            top_workspaces = await analytics_service.get_top_workspaces_for_period(
                week_start, week_end, limit=10
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            # Calculate derived metrics
            total_users = user_metrics.get("total_users", 0)
            active_users = user_metrics.get("active_users", 0)
            new_users = user_metrics.get("new_users", 0)
            total_sessions = session_metrics.get("total_sessions", 0)
            total_agent_executions = agent_metrics.get("total_executions", 0)
            total_api_requests = api_metrics.get("total_requests", 0)
            total_tokens_used = agent_metrics.get("total_tokens", 0)
            total_storage_used_mb = storage_metrics.get("total_storage_mb", 0.0)
            average_session_duration = session_metrics.get(
                "average_duration_seconds", 0.0
            )

            # Calculate rates
            user_retention_rate = (
                (active_users / total_users * 100) if total_users > 0 else 0.0
            )
            agent_success_rate = (
                (
                    agent_metrics.get("successful_executions", 0)
                    / total_agent_executions
                    * 100
                )
                if total_agent_executions > 0
                else 0.0
            )
            api_success_rate = (
                (api_metrics.get("successful_requests", 0) / total_api_requests * 100)
                if total_api_requests > 0
                else 0.0
            )

            # Create report
            report = WeeklyReport(
                week_start=week_start,
                week_end=week_end,
                total_users=total_users,
                active_users=active_users,
                new_users=new_users,
                total_sessions=total_sessions,
                total_agent_executions=total_agent_executions,
                total_api_requests=total_api_requests,
                total_tokens_used=total_tokens_used,
                total_storage_used_mb=total_storage_used_mb,
                average_session_duration=average_session_duration,
                user_retention_rate=user_retention_rate,
                agent_success_rate=agent_success_rate,
                api_success_rate=api_success_rate,
                top_agents=top_agents,
                top_workspaces=top_workspaces,
                daily_breakdown=daily_breakdown,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "weekly_report_processing_time",
                processing_time,
                {"week_start": week_start},
            )

            await self.monitoring.record_metric(
                "weekly_active_users", report.active_users, {"week_start": week_start}
            )

            await self.monitoring.record_metric(
                "weekly_agent_executions",
                report.total_agent_executions,
                {"week_start": week_start},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Weekly report completed for week: {week_start} to {week_end}",
                {
                    "week_start": week_start,
                    "week_end": week_end,
                    "total_users": report.total_users,
                    "active_users": report.active_users,
                    "total_agent_executions": report.total_agent_executions,
                    "processing_time_seconds": processing_time,
                },
            )

            return report

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Weekly report failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Weekly report failed for week: {week_start} to {week_end}",
                {
                    "week_start": week_start,
                    "week_end": week_end,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def agent_performance_job(
        self, agent_name: str, period_days: int = 7
    ) -> AgentPerformanceAnalysis:
        """Analyze agent performance."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        analysis_period = (
            f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        )

        job_start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting agent performance analysis for: {agent_name}",
                {
                    "agent_name": agent_name,
                    "period_days": period_days,
                    "analysis_period": analysis_period,
                    "job_type": "agent_performance",
                    "started_at": job_start_time.isoformat(),
                },
            )

            # Get analytics service
            from analytics.analytics_service import get_analytics_service

            analytics_service = get_analytics_service()

            # Get agent metrics for the period
            agent_metrics = await analytics_service.get_agent_performance_metrics(
                agent_name, start_date, end_date
            )

            # Get execution details
            execution_details = await analytics_service.get_agent_execution_details(
                agent_name, start_date, end_date
            )

            # Get error analysis
            error_analysis = await analytics_service.get_agent_error_analysis(
                agent_name, start_date, end_date
            )

            # Get performance trend
            performance_trend = await analytics_service.get_agent_performance_trend(
                agent_name, start_date, end_date
            )

            # Generate recommendations
            recommendations = await analytics_service.generate_agent_recommendations(
                agent_name, agent_metrics, error_analysis
            )

            processing_time = (datetime.utcnow() - job_start_time).total_seconds()

            # Calculate metrics
            total_executions = agent_metrics.get("total_executions", 0)
            successful_executions = agent_metrics.get("successful_executions", 0)
            failed_executions = agent_metrics.get("failed_executions", 0)
            average_execution_time = agent_metrics.get("average_execution_time", 0.0)
            average_tokens_per_execution = agent_metrics.get(
                "average_tokens_per_execution", 0.0
            )
            success_rate = (
                (successful_executions / total_executions * 100)
                if total_executions > 0
                else 0.0
            )
            error_rate = (
                (failed_executions / total_executions * 100)
                if total_executions > 0
                else 0.0
            )

            # Get top errors
            top_errors = error_analysis.get("top_errors", [])

            # Create analysis
            analysis = AgentPerformanceAnalysis(
                agent_name=agent_name,
                analysis_period=analysis_period,
                total_executions=total_executions,
                successful_executions=successful_executions,
                failed_executions=failed_executions,
                average_execution_time=average_execution_time,
                average_tokens_per_execution=average_tokens_per_execution,
                success_rate=success_rate,
                error_rate=error_rate,
                top_errors=top_errors,
                performance_trend=performance_trend,
                recommendations=recommendations,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "agent_performance_analysis_processing_time",
                processing_time,
                {"agent_name": agent_name},
            )

            await self.monitoring.record_metric(
                "agent_success_rate", analysis.success_rate, {"agent_name": agent_name}
            )

            await self.monitoring.record_metric(
                "agent_error_rate", analysis.error_rate, {"agent_name": agent_name}
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Agent performance analysis completed for: {agent_name}",
                {
                    "agent_name": agent_name,
                    "analysis_period": analysis_period,
                    "total_executions": total_executions,
                    "success_rate": success_rate,
                    "error_rate": error_rate,
                    "performance_trend": performance_trend,
                    "processing_time_seconds": processing_time,
                },
            )

            return analysis

        except Exception as e:
            processing_time = (datetime.utcnow() - job_start_time).total_seconds()
            errors.append(f"Agent performance analysis failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Agent performance analysis failed for: {agent_name}",
                {
                    "agent_name": agent_name,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def user_behavior_analysis_job(self, period_days: int = 30) -> Dict[str, Any]:
        """Analyze user behavior patterns."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)

        job_start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting user behavior analysis for period: {period_days} days",
                {
                    "period_days": period_days,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "job_type": "user_behavior_analysis",
                    "started_at": job_start_time.isoformat(),
                },
            )

            # Get analytics service
            from analytics.analytics_service import get_analytics_service

            analytics_service = get_analytics_service()

            # Get user behavior metrics
            behavior_metrics = await analytics_service.get_user_behavior_metrics(
                start_date, end_date
            )

            # Get user segmentation
            user_segments = await analytics_service.get_user_segments(
                start_date, end_date
            )

            # Get usage patterns
            usage_patterns = await analytics_service.get_usage_patterns(
                start_date, end_date
            )

            # Get retention analysis
            retention_analysis = await analytics_service.get_retention_analysis(
                start_date, end_date
            )

            # Get churn prediction
            churn_prediction = await analytics_service.get_churn_prediction(
                start_date, end_date
            )

            processing_time = (datetime.utcnow() - job_start_time).total_seconds()

            result = {
                "period_days": period_days,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "behavior_metrics": behavior_metrics,
                "user_segments": user_segments,
                "usage_patterns": usage_patterns,
                "retention_analysis": retention_analysis,
                "churn_prediction": churn_prediction,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Record metrics
            await self.monitoring.record_metric(
                "user_behavior_analysis_processing_time",
                processing_time,
                {"period_days": period_days},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"User behavior analysis completed for period: {period_days} days",
                {
                    "period_days": period_days,
                    "processing_time_seconds": processing_time,
                    "user_segments_count": len(user_segments),
                    "usage_patterns_count": len(usage_patterns),
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - job_start_time).total_seconds()
            errors.append(f"User behavior analysis failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"User behavior analysis failed for period: {period_days} days",
                {
                    "period_days": period_days,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def system_health_analysis_job(self) -> Dict[str, Any]:
        """Analyze system health and performance."""
        job_start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                "Starting system health analysis",
                {
                    "job_type": "system_health_analysis",
                    "started_at": job_start_time.isoformat(),
                },
            )

            # Get analytics service
            from analytics.analytics_service import get_analytics_service

            analytics_service = get_analytics_service()

            # Get system metrics
            system_metrics = await analytics_service.get_system_metrics()

            # Get performance metrics
            performance_metrics = await analytics_service.get_performance_metrics()

            # Get error metrics
            error_metrics = await analytics_service.get_error_metrics()

            # Get resource utilization
            resource_utilization = await analytics_service.get_resource_utilization()

            # Get service health
            service_health = await analytics_service.get_service_health()

            processing_time = (datetime.utcnow() - job_start_time).total_seconds()

            result = {
                "system_metrics": system_metrics,
                "performance_metrics": performance_metrics,
                "error_metrics": error_metrics,
                "resource_utilization": resource_utilization,
                "service_health": service_health,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Record metrics
            await self.monitoring.record_metric(
                "system_health_analysis_processing_time", processing_time
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                "System health analysis completed",
                {
                    "processing_time_seconds": processing_time,
                    "service_health_status": service_health.get(
                        "overall_status", "unknown"
                    ),
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - job_start_time).total_seconds()
            errors.append(f"System health analysis failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                "System health analysis failed",
                {"error": str(e), "processing_time_seconds": processing_time},
            )

            raise


# Create global instance
_analytics_jobs = AnalyticsJobs()


# Job implementations with decorators
@daily_job(
    hour=1,
    minute=0,
    queue="analytics",
    retries=2,
    timeout=1800,  # 30 minutes
    description="Generate daily usage summary",
)
async def daily_usage_summary_job(date: Optional[str] = None) -> Dict[str, Any]:
    """Daily usage summary job."""
    result = await _analytics_jobs.daily_usage_summary_job(date)
    return result.__dict__


@weekly_job(
    day_of_week=0,  # Sunday
    hour=2,
    minute=0,
    queue="analytics",
    retries=2,
    timeout=3600,  # 1 hour
    description="Generate weekly report",
)
async def weekly_report_job(week_start: Optional[str] = None) -> Dict[str, Any]:
    """Weekly report job."""
    result = await _analytics_jobs.weekly_report_job(week_start)
    return result.__dict__


@hourly_job(
    minute=15,
    queue="analytics",
    retries=1,
    timeout=600,  # 10 minutes
    description="Analyze agent performance",
)
async def agent_performance_job(
    agent_name: str, period_days: int = 7
) -> Dict[str, Any]:
    """Agent performance analysis job."""
    result = await _analytics_jobs.agent_performance_job(agent_name, period_days)
    return result.__dict__


@background_job(
    queue="analytics",
    retries=1,
    timeout=1800,  # 30 minutes
    description="Analyze user behavior patterns",
)
async def user_behavior_analysis_job(period_days: int = 30) -> Dict[str, Any]:
    """User behavior analysis job."""
    result = await _analytics_jobs.user_behavior_analysis_job(period_days)
    return result


@hourly_job(
    minute=45,
    queue="analytics",
    retries=1,
    timeout=300,  # 5 minutes
    description="Analyze system health",
)
async def system_health_analysis_job() -> Dict[str, Any]:
    """System health analysis job."""
    result = await _analytics_jobs.system_health_analysis_job()
    return result


# Convenience functions
async def generate_daily_summary(date: Optional[str] = None) -> DailyUsageSummary:
    """Generate daily usage summary."""
    return await _analytics_jobs.daily_usage_summary_job(date)


async def generate_weekly_report(week_start: Optional[str] = None) -> WeeklyReport:
    """Generate weekly report."""
    return await _analytics_jobs.weekly_report_job(week_start)


async def analyze_agent_performance(
    agent_name: str, period_days: int = 7
) -> AgentPerformanceAnalysis:
    """Analyze agent performance."""
    return await _analytics_jobs.agent_performance_job(agent_name, period_days)


async def analyze_user_behavior(period_days: int = 30) -> Dict[str, Any]:
    """Analyze user behavior patterns."""
    return await _analytics_jobs.user_behavior_analysis_job(period_days)


async def analyze_system_health() -> Dict[str, Any]:
    """Analyze system health."""
    return await _analytics_jobs.system_health_analysis_job()


# Export all jobs
__all__ = [
    "AnalyticsJobs",
    "daily_usage_summary_job",
    "weekly_report_job",
    "agent_performance_job",
    "user_behavior_analysis_job",
    "system_health_analysis_job",
    "generate_daily_summary",
    "generate_weekly_report",
    "analyze_agent_performance",
    "analyze_user_behavior",
    "analyze_system_health",
]
