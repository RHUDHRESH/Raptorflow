"""
Research jobs for Raptorflow.

Provides background jobs for competitor intelligence,
trend monitoring, and scheduled research tasks.
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from .decorators import background_job, daily_job, hourly_job, job, weekly_job
from infrastructure.cloud_monitoring import get_cloud_monitoring
from infrastructure.logging import get_cloud_logging

from .models import JobResult, JobStatus

logger = logging.getLogger(__name__)


@dataclass
class CompetitorIntelResult:
    """Result of competitor intelligence gathering."""

    workspace_id: str
    competitors_analyzed: List[str]
    insights_found: int
    market_position_updates: int
    new_features_detected: List[str]
    pricing_changes: List[Dict[str, Any]]
    marketing_campaigns: List[Dict[str, Any]]
    sentiment_analysis: Dict[str, Any]
    recommendations: List[str]
    processing_time_seconds: float
    errors: List[str]


@dataclass
class TrendMonitoringResult:
    """Result of trend monitoring."""

    workspace_id: str
    trends_identified: List[str]
    emerging_trends: List[str]
    declining_trends: List[str]
    market_shifts: List[Dict[str, Any]]
    technology_advances: List[str]
    regulatory_changes: List[str]
    consumer_behavior_changes: List[str]
    impact_assessment: Dict[str, Any]
    opportunities: List[str]
    threats: List[str]
    processing_time_seconds: float
    errors: List[str]


@dataclass
class ScheduledResearchResult:
    """Result of scheduled research task."""

    workspace_id: str
    research_id: str
    research_type: str
    query: str
    sources_analyzed: int
    insights_generated: int
    confidence_score: float
    key_findings: List[str]
    supporting_evidence: List[Dict[str, Any]]
    action_items: List[str]
    next_steps: List[str]
    processing_time_seconds: float
    errors: List[str]


@dataclass
class MarketAnalysisResult:
    """Result of market analysis."""

    workspace_id: str
    market_size: float
    growth_rate: float
    market_segments: List[Dict[str, Any]]
    key_players: List[Dict[str, Any]]
    market_trends: List[str]
    opportunities: List[str]
    threats: List[str]
    swot_analysis: Dict[str, Any]
    recommendations: List[str]
    processing_time_seconds: float
    errors: List[str]


class ResearchJobs:
    """Research job implementations."""

    def __init__(self):
        self.logger = logging.getLogger("research_jobs")
        self.logging = get_cloud_logging()
        self.monitoring = get_cloud_monitoring()

    async def refresh_competitor_intel_job(
        self, workspace_id: str
    ) -> CompetitorIntelResult:
        """Refresh competitor intelligence for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting competitor intelligence refresh for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "refresh_competitor_intel",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get research service
            from research.research_service import get_research_service

            research_service = get_research_service()

            # Get workspace competitors
            competitors = await research_service.get_workspace_competitors(workspace_id)
            competitor_names = [comp.name for comp in competitors]

            insights_found = 0
            market_position_updates = 0
            new_features_detected = []
            pricing_changes = []
            marketing_campaigns = []

            # Analyze each competitor
            for competitor in competitors:
                try:
                    # Get competitor intelligence
                    intel = await research_service.analyze_competitor(competitor.id)

                    insights_found += intel.get("insights_count", 0)
                    market_position_updates += intel.get("position_updates", 0)

                    # Collect new features
                    features = intel.get("new_features", [])
                    new_features_detected.extend(features)

                    # Collect pricing changes
                    pricing = intel.get("pricing_changes", [])
                    pricing_changes.extend(pricing)

                    # Collect marketing campaigns
                    campaigns = intel.get("marketing_campaigns", [])
                    marketing_campaigns.extend(campaigns)

                except Exception as e:
                    errors.append(
                        f"Failed to analyze competitor {competitor.name}: {str(e)}"
                    )

            # Perform sentiment analysis
            sentiment_analysis = await research_service.analyze_competitor_sentiment(
                competitor_names
            )

            # Generate recommendations
            recommendations = (
                await research_service.generate_competitor_recommendations(
                    workspace_id,
                    competitors,
                    insights_found,
                    new_features_detected,
                    pricing_changes,
                )
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = CompetitorIntelResult(
                workspace_id=workspace_id,
                competitors_analyzed=competitor_names,
                insights_found=insights_found,
                market_position_updates=market_position_updates,
                new_features_detected=new_features_detected,
                pricing_changes=pricing_changes,
                marketing_campaigns=marketing_campaigns,
                sentiment_analysis=sentiment_analysis,
                recommendations=recommendations,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "competitor_intel_insights_found",
                insights_found,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "competitor_intel_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Competitor intelligence refresh completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "competitors_analyzed": len(competitor_names),
                    "insights_found": insights_found,
                    "new_features_detected": len(new_features_detected),
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Competitor intelligence refresh failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Competitor intelligence refresh failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def trend_monitoring_job(self, workspace_id: str) -> TrendMonitoringResult:
        """Monitor trends for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting trend monitoring for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "trend_monitoring",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get research service
            from research.research_service import get_research_service

            research_service = get_research_service()

            # Get workspace industry and focus areas
            workspace_info = await research_service.get_workspace_research_focus(
                workspace_id
            )
            industry = workspace_info.get("industry")
            focus_areas = workspace_info.get("focus_areas", [])

            # Monitor trends
            trends_data = await research_service.monitor_trends(industry, focus_areas)

            # Categorize trends
            trends_identified = trends_data.get("trends", [])
            emerging_trends = [
                t for t in trends_identified if t.get("trend_type") == "emerging"
            ]
            declining_trends = [
                t for t in trends_identified if t.get("trend_type") == "declining"
            ]

            # Analyze market shifts
            market_shifts = trends_data.get("market_shifts", [])

            # Identify technology advances
            technology_advances = trends_data.get("technology_advances", [])

            # Monitor regulatory changes
            regulatory_changes = trends_data.get("regulatory_changes", [])

            # Analyze consumer behavior changes
            consumer_behavior_changes = trends_data.get("consumer_behavior_changes", [])

            # Assess impact
            impact_assessment = await research_service.assess_trend_impact(
                workspace_id, trends_identified
            )

            # Generate opportunities and threats
            opportunities = await research_service.identify_opportunities(
                workspace_id, trends_identified, emerging_trends
            )

            threats = await research_service.identify_threats(
                workspace_id, trends_identified, declining_trends
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = TrendMonitoringResult(
                workspace_id=workspace_id,
                trends_identified=[t.get("name") for t in trends_identified],
                emerging_trends=[t.get("name") for t in emerging_trends],
                declining_trends=[t.get("name") for t in declining_trends],
                market_shifts=market_shifts,
                technology_advances=technology_advances,
                regulatory_changes=regulatory_changes,
                consumer_behavior_changes=consumer_behavior_changes,
                impact_assessment=impact_assessment,
                opportunities=opportunities,
                threats=threats,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "trend_monitoring_trends_identified",
                len(trends_identified),
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "trend_monitoring_opportunities",
                len(opportunities),
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "trend_monitoring_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Trend monitoring completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "trends_identified": len(trends_identified),
                    "emerging_trends": len(emerging_trends),
                    "opportunities": len(opportunities),
                    "threats": len(threats),
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Trend monitoring failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Trend monitoring failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def scheduled_research_job(
        self, workspace_id: str, research_id: str
    ) -> ScheduledResearchResult:
        """Execute scheduled research task."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting scheduled research for workspace: {workspace_id}, research: {research_id}",
                {
                    "workspace_id": workspace_id,
                    "research_id": research_id,
                    "job_type": "scheduled_research",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get research service
            from research.research_service import get_research_service

            research_service = get_research_service()

            # Get research task details
            research_task = await research_service.get_research_task(research_id)

            if not research_task:
                raise ValueError(f"Research task not found: {research_id}")

            # Execute research
            research_result = await research_service.execute_research_task(
                workspace_id, research_task
            )

            # Extract results
            sources_analyzed = research_result.get("sources_analyzed", 0)
            insights_generated = research_result.get("insights_generated", 0)
            confidence_score = research_result.get("confidence_score", 0.0)
            key_findings = research_result.get("key_findings", [])
            supporting_evidence = research_result.get("supporting_evidence", [])

            # Generate action items
            action_items = await research_service.generate_action_items(
                workspace_id, research_task, key_findings
            )

            # Generate next steps
            next_steps = await research_service.generate_next_steps(
                workspace_id, research_task, key_findings, action_items
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = ScheduledResearchResult(
                workspace_id=workspace_id,
                research_id=research_id,
                research_type=research_task.get("type", "unknown"),
                query=research_task.get("query", ""),
                sources_analyzed=sources_analyzed,
                insights_generated=insights_generated,
                confidence_score=confidence_score,
                key_findings=key_findings,
                supporting_evidence=supporting_evidence,
                action_items=action_items,
                next_steps=next_steps,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "scheduled_research_insights_generated",
                insights_generated,
                {"workspace_id": workspace_id, "research_type": result.research_type},
            )

            await self.monitoring.record_metric(
                "scheduled_research_confidence_score",
                confidence_score,
                {"workspace_id": workspace_id, "research_type": result.research_type},
            )

            await self.monitoring.record_metric(
                "scheduled_research_processing_time",
                processing_time,
                {"workspace_id": workspace_id, "research_type": result.research_type},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Scheduled research completed for workspace: {workspace_id}, research: {research_id}",
                {
                    "workspace_id": workspace_id,
                    "research_id": research_id,
                    "research_type": result.research_type,
                    "insights_generated": insights_generated,
                    "confidence_score": confidence_score,
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Scheduled research failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Scheduled research failed for workspace: {workspace_id}, research: {research_id}",
                {
                    "workspace_id": workspace_id,
                    "research_id": research_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def market_analysis_job(self, workspace_id: str) -> MarketAnalysisResult:
        """Perform market analysis for a workspace."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting market analysis for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "market_analysis",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get research service
            from research.research_service import get_research_service

            research_service = get_research_service()

            # Get workspace market context
            market_context = await research_service.get_workspace_market_context(
                workspace_id
            )

            # Analyze market size and growth
            market_analysis = await research_service.analyze_market_size_and_growth(
                market_context.get("industry"), market_context.get("geography")
            )

            market_size = market_analysis.get("market_size", 0.0)
            growth_rate = market_analysis.get("growth_rate", 0.0)

            # Analyze market segments
            market_segments = await research_service.analyze_market_segments(
                market_context.get("industry")
            )

            # Identify key players
            key_players = await research_service.identify_key_players(
                market_context.get("industry")
            )

            # Analyze market trends
            market_trends = await research_service.analyze_market_trends(
                market_context.get("industry")
            )

            # Perform SWOT analysis
            swot_analysis = await research_service.perform_swot_analysis(
                workspace_id, market_context
            )

            # Generate opportunities and threats
            opportunities = swot_analysis.get("opportunities", [])
            threats = swot_analysis.get("threats", [])

            # Generate recommendations
            recommendations = await research_service.generate_market_recommendations(
                workspace_id, market_analysis, swot_analysis
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = MarketAnalysisResult(
                workspace_id=workspace_id,
                market_size=market_size,
                growth_rate=growth_rate,
                market_segments=market_segments,
                key_players=key_players,
                market_trends=market_trends,
                opportunities=opportunities,
                threats=threats,
                swot_analysis=swot_analysis,
                recommendations=recommendations,
                processing_time_seconds=processing_time,
                errors=errors,
            )

            # Record metrics
            await self.monitoring.record_metric(
                "market_analysis_market_size",
                market_size,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "market_analysis_growth_rate",
                growth_rate,
                {"workspace_id": workspace_id},
            )

            await self.monitoring.record_metric(
                "market_analysis_processing_time",
                processing_time,
                {"workspace_id": workspace_id},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Market analysis completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "market_size": market_size,
                    "growth_rate": growth_rate,
                    "market_segments": len(market_segments),
                    "key_players": len(key_players),
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Market analysis failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Market analysis failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise

    async def industry_news_monitoring_job(self, workspace_id: str) -> Dict[str, Any]:
        """Monitor industry news and updates."""
        start_time = datetime.utcnow()
        errors = []

        try:
            # Log job start
            await self.logging.log_structured(
                "INFO",
                f"Starting industry news monitoring for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "job_type": "industry_news_monitoring",
                    "started_at": start_time.isoformat(),
                },
            )

            # Get research service
            from research.research_service import get_research_service

            research_service = get_research_service()

            # Get workspace industry
            workspace_info = await research_service.get_workspace_research_focus(
                workspace_id
            )
            industry = workspace_info.get("industry")

            # Monitor industry news
            news_data = await research_service.monitor_industry_news(industry)

            # Categorize news
            breaking_news = news_data.get("breaking_news", [])
            company_news = news_data.get("company_news", [])
            product_news = news_data.get("product_news", [])
            regulatory_news = news_data.get("regulatory_news", [])
            market_news = news_data.get("market_news", [])

            # Analyze sentiment
            sentiment_analysis = await research_service.analyze_news_sentiment(
                breaking_news
            )

            # Identify impact on workspace
            impact_analysis = await research_service.analyze_news_impact(
                workspace_id, breaking_news
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "workspace_id": workspace_id,
                "industry": industry,
                "breaking_news": breaking_news,
                "company_news": company_news,
                "product_news": product_news,
                "regulatory_news": regulatory_news,
                "market_news": market_news,
                "sentiment_analysis": sentiment_analysis,
                "impact_analysis": impact_analysis,
                "processing_time_seconds": processing_time,
                "errors": errors,
            }

            # Record metrics
            await self.monitoring.record_metric(
                "industry_news_breaking_count",
                len(breaking_news),
                {"workspace_id": workspace_id, "industry": industry},
            )

            await self.monitoring.record_metric(
                "industry_news_processing_time",
                processing_time,
                {"workspace_id": workspace_id, "industry": industry},
            )

            # Log completion
            await self.logging.log_structured(
                "INFO",
                f"Industry news monitoring completed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "industry": industry,
                    "breaking_news_count": len(breaking_news),
                    "total_news_count": len(breaking_news)
                    + len(company_news)
                    + len(product_news),
                    "processing_time_seconds": processing_time,
                },
            )

            return result

        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            errors.append(f"Industry news monitoring failed: {str(e)}")

            await self.logging.log_structured(
                "ERROR",
                f"Industry news monitoring failed for workspace: {workspace_id}",
                {
                    "workspace_id": workspace_id,
                    "error": str(e),
                    "processing_time_seconds": processing_time,
                },
            )

            raise


# Create global instance
_research_jobs = ResearchJobs()


# Job implementations with decorators
@daily_job(
    hour=2,
    minute=30,
    queue="research",
    retries=2,
    timeout=3600,  # 1 hour
    description="Refresh competitor intelligence",
)
async def refresh_competitor_intel_job(workspace_id: str) -> Dict[str, Any]:
    """Refresh competitor intelligence job."""
    result = await _research_jobs.refresh_competitor_intel_job(workspace_id)
    return result.__dict__


@daily_job(
    hour=3,
    minute=0,
    queue="research",
    retries=2,
    timeout=3600,  # 1 hour
    description="Monitor trends",
)
async def trend_monitoring_job(workspace_id: str) -> Dict[str, Any]:
    """Trend monitoring job."""
    result = await _research_jobs.trend_monitoring_job(workspace_id)
    return result.__dict__


@background_job(
    queue="research",
    retries=1,
    timeout=1800,  # 30 minutes
    description="Execute scheduled research",
)
async def scheduled_research_job(workspace_id: str, research_id: str) -> Dict[str, Any]:
    """Scheduled research job."""
    result = await _research_jobs.scheduled_research_job(workspace_id, research_id)
    return result.__dict__


@weekly_job(
    day_of_week=1,  # Monday
    hour=1,
    minute=0,
    queue="research",
    retries=2,
    timeout=7200,  # 2 hours
    description="Perform market analysis",
)
async def market_analysis_job(workspace_id: str) -> Dict[str, Any]:
    """Market analysis job."""
    result = await _research_jobs.market_analysis_job(workspace_id)
    return result.__dict__


@hourly_job(
    minute=30,
    queue="research",
    retries=1,
    timeout=1800,  # 30 minutes
    description="Monitor industry news",
)
async def industry_news_monitoring_job(workspace_id: str) -> Dict[str, Any]:
    """Industry news monitoring job."""
    result = await _research_jobs.industry_news_monitoring_job(workspace_id)
    return result


# Convenience functions
async def refresh_workspace_competitor_intel(
    workspace_id: str,
) -> CompetitorIntelResult:
    """Refresh competitor intelligence for a workspace."""
    return await _research_jobs.refresh_competitor_intel_job(workspace_id)


async def monitor_workspace_trends(workspace_id: str) -> TrendMonitoringResult:
    """Monitor trends for a workspace."""
    return await _research_jobs.trend_monitoring_job(workspace_id)


async def execute_workspace_research(
    workspace_id: str, research_id: str
) -> ScheduledResearchResult:
    """Execute scheduled research for a workspace."""
    return await _research_jobs.scheduled_research_job(workspace_id, research_id)


async def analyze_workspace_market(workspace_id: str) -> MarketAnalysisResult:
    """Perform market analysis for a workspace."""
    return await _research_jobs.market_analysis_job(workspace_id)


async def monitor_workspace_industry_news(workspace_id: str) -> Dict[str, Any]:
    """Monitor industry news for a workspace."""
    return await _research_jobs.industry_news_monitoring_job(workspace_id)


# Export all jobs
__all__ = [
    "ResearchJobs",
    "refresh_competitor_intel_job",
    "trend_monitoring_job",
    "scheduled_research_job",
    "market_analysis_job",
    "industry_news_monitoring_job",
    "refresh_workspace_competitor_intel",
    "monitor_workspace_trends",
    "execute_workspace_research",
    "analyze_workspace_market",
    "monitor_workspace_industry_news",
]
