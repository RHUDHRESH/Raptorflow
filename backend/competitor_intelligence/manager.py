"""
Competitor Intelligence Manager - Unified interface for all competitor operations
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .agent import SwarmCompetitorIntelligenceAgent
from .config import CompetitorConfig, CompetitorOperationType
from .memory import SwarmL1MemoryManager
from .monitoring import (
    CompetitorAnalysisService,
    CompetitorMonitoringService,
    MonitoringFrequency,
)
from .node import CompetitorIntelligenceNode
from .utils import (
    format_competitor_summary,
    generate_competitor_id,
    validate_competitor_data,
)

logger = logging.getLogger("raptorflow.competitor_intelligence.manager")


class CompetitorIntelligenceManager:
    """
    Unified manager for all competitor intelligence operations.
    Provides a clean, high-level interface for swarm agents to interact with competitor functionality.
    """

    def __init__(self, thread_id: str, config: Optional[Dict[str, Any]] = None):
        self.thread_id = thread_id
        self.config = CompetitorConfig.validate_config(
            config or CompetitorConfig.get_default_config()
        )

        # Initialize components
        self.memory_manager = SwarmL1MemoryManager(thread_id)
        self.agent = SwarmCompetitorIntelligenceAgent()
        self.monitoring_service = CompetitorMonitoringService(self.memory_manager)
        self.analysis_service = CompetitorAnalysisService(self.memory_manager)
        self.node = CompetitorIntelligenceNode(thread_id)

        # State tracking
        self._monitoring_active = False
        self._last_operation_time = None

        logger.info(f"CompetitorIntelligenceManager initialized for thread {thread_id}")

    # Discovery Operations
    async def discover_competitors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Discover new competitors based on provided context."""
        logger.info("Starting competitor discovery operation")

        try:
            from models.swarm import SwarmState

            state = SwarmState(**context)

            result = await self.agent.discover_competitors(state)
            self._last_operation_time = datetime.now()

            # Log discovery metrics
            discovered_count = len(result.get("discovered_competitors", []))
            logger.info(
                f"Competitor discovery completed: {discovered_count} competitors found"
            )

            return result

        except Exception as e:
            logger.error(f"Competitor discovery failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def add_competitor_manually(
        self, competitor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Manually add a competitor profile."""
        logger.info(
            f"Adding competitor manually: {competitor_data.get('name', 'Unknown')}"
        )

        try:
            # Validate data
            validated_data = validate_competitor_data(competitor_data)

            # Generate ID if not provided
            if "id" not in validated_data:
                validated_data["id"] = generate_competitor_id(
                    validated_data["name"], validated_data.get("website")
                )

            # Create profile
            from models.swarm import CompetitorProfile

            profile = CompetitorProfile(**validated_data)

            # Store in memory
            await self.memory_manager.update_competitor_profile(profile)

            self._last_operation_time = datetime.now()

            return {
                "status": "success",
                "competitor_id": profile.id,
                "profile": profile.model_dump(),
                "message": f"Competitor '{profile.name}' added successfully",
            }

        except Exception as e:
            logger.error(f"Failed to add competitor manually: {e}")
            return {"error": str(e), "status": "failed"}

    # Analysis Operations
    async def analyze_competitors(
        self, competitor_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyze specified competitors or all known competitors."""
        logger.info(
            f"Starting competitor analysis for {len(competitor_ids) if competitor_ids else 'all'} competitors"
        )

        try:
            # Get competitor IDs if not provided
            if not competitor_ids:
                all_profiles = await self.memory_manager.get_all_competitor_profiles()
                competitor_ids = [p.id for p in all_profiles]

            if not competitor_ids:
                return {
                    "error": "No competitors available for analysis",
                    "status": "no_competitors",
                }

            from models.swarm import SwarmState

            state = SwarmState()

            result = await self.agent.analyze_competitors(state, competitor_ids)
            self._last_operation_time = datetime.now()

            logger.info(
                f"Competitor analysis completed for {len(competitor_ids)} competitors"
            )
            return result

        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def perform_swot_analysis(
        self, competitor_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Perform SWOT analysis on competitors."""
        logger.info("Performing SWOT analysis")

        try:
            if not competitor_ids:
                all_profiles = await self.memory_manager.get_all_competitor_profiles()
                competitor_ids = [p.id for p in all_profiles]

            result = await self.analysis_service.perform_swot_analysis(competitor_ids)
            self._last_operation_time = datetime.now()

            return result

        except Exception as e:
            logger.error(f"SWOT analysis failed: {e}")
            return {"error": str(e), "status": "failed"}

    async def identify_competitive_gaps(
        self, competitor_ids: Optional[List[str]] = None
    ) -> List[str]:
        """Identify gaps in the competitive landscape."""
        logger.info("Identifying competitive gaps")

        try:
            if not competitor_ids:
                all_profiles = await self.memory_manager.get_all_competitor_profiles()
                competitor_ids = [p.id for p in all_profiles]

            gaps = await self.analysis_service.identify_competitive_gaps(competitor_ids)
            self._last_operation_time = datetime.now()

            return gaps

        except Exception as e:
            logger.error(f"Competitive gap analysis failed: {e}")
            return []

    # Monitoring Operations
    async def start_monitoring(
        self, competitor_ids: List[str], frequency: str = "daily"
    ) -> Dict[str, Any]:
        """Start monitoring specified competitors."""
        logger.info(
            f"Starting monitoring for {len(competitor_ids)} competitors with {frequency} frequency"
        )

        try:
            # Validate frequency
            valid_frequencies = ["real_time", "hourly", "daily", "weekly", "monthly"]
            if frequency not in valid_frequencies:
                frequency = "daily"

            freq_enum = MonitoringFrequency(frequency)
            await self.monitoring_service.start_monitoring(competitor_ids, freq_enum)

            self._monitoring_active = True
            self._last_operation_time = datetime.now()

            logger.info(f"Monitoring started successfully")
            return {
                "status": "success",
                "monitored_competitors": competitor_ids,
                "monitoring_frequency": frequency,
                "message": f"Started monitoring {len(competitor_ids)} competitors",
            }

        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return {"error": str(e), "status": "failed"}

    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop all competitor monitoring."""
        logger.info("Stopping competitor monitoring")

        try:
            await self.monitoring_service.stop_monitoring()
            self._monitoring_active = False
            self._last_operation_time = datetime.now()

            return {"status": "success", "message": "Competitor monitoring stopped"}

        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return {"error": str(e), "status": "failed"}

    def is_monitoring_active(self) -> bool:
        """Check if monitoring is currently active."""
        return self._monitoring_active

    # Reporting Operations
    async def generate_intelligence_report(
        self, competitor_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive competitor intelligence report."""
        logger.info("Generating competitor intelligence report")

        try:
            report = (
                await self.monitoring_service.generate_competitor_intelligence_report()
            )
            self._last_operation_time = datetime.now()

            logger.info(
                f"Intelligence report generated: {report.get('competitors_analyzed', 0)} competitors"
            )
            return report

        except Exception as e:
            logger.error(f"Failed to generate intelligence report: {e}")
            return {"error": str(e), "status": "failed"}

    async def generate_competitive_benchmarks(
        self, competitor_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate competitive benchmarks."""
        logger.info("Generating competitive benchmarks")

        try:
            if not competitor_ids:
                all_profiles = await self.memory_manager.get_all_competitor_profiles()
                competitor_ids = [p.id for p in all_profiles]

            benchmarks = await self.analysis_service.generate_competitive_benchmarks(
                competitor_ids
            )
            self._last_operation_time = datetime.now()

            return benchmarks

        except Exception as e:
            logger.error(f"Failed to generate benchmarks: {e}")
            return {"error": str(e), "status": "failed"}

    # Data Management Operations
    async def get_competitor_profiles(
        self, competitor_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve competitor profiles."""
        try:
            if competitor_ids:
                profiles = []
                for comp_id in competitor_ids:
                    profile = await self.memory_manager.get_competitor_profile(comp_id)
                    if profile:
                        profiles.append(profile.model_dump())
                return profiles
            else:
                all_profiles = await self.memory_manager.get_all_competitor_profiles()
                return [p.model_dump() for p in all_profiles]

        except Exception as e:
            logger.error(f"Failed to retrieve competitor profiles: {e}")
            return []

    async def get_competitor_insights(
        self, competitor_id: Optional[str] = None, days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Retrieve competitor insights."""
        try:
            all_insights = await self.memory_manager.get_all_competitor_insights()

            # Filter by competitor if specified
            if competitor_id:
                all_insights = [
                    i for i in all_insights if i.competitor_id == competitor_id
                ]

            # Filter by date
            cutoff = datetime.now() - timedelta(days=days_back)
            all_insights = [i for i in all_insights if i.discovered_at > cutoff]

            return [i.model_dump() for i in all_insights]

        except Exception as e:
            logger.error(f"Failed to retrieve competitor insights: {e}")
            return []

    async def add_competitor_insight(
        self, insight_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new competitor insight."""
        logger.info(
            f"Adding competitor insight: {insight_data.get('title', 'Unknown')}"
        )

        try:
            from models.swarm import CompetitorInsight

            insight = CompetitorInsight(**insight_data)

            await self.memory_manager.add_competitor_insight(insight)
            self._last_operation_time = datetime.now()

            return {
                "status": "success",
                "insight_id": insight.id,
                "insight": insight.model_dump(),
                "message": "Competitor insight added successfully",
            }

        except Exception as e:
            logger.error(f"Failed to add competitor insight: {e}")
            return {"error": str(e), "status": "failed"}

    async def update_competitor_watchlist(
        self, competitor_ids: List[str]
    ) -> Dict[str, Any]:
        """Update the competitor watchlist."""
        logger.info(
            f"Updating competitor watchlist with {len(competitor_ids)} competitors"
        )

        try:
            await self.memory_manager.update_competitor_watchlist(competitor_ids)
            self._last_operation_time = datetime.now()

            return {
                "status": "success",
                "watchlist": competitor_ids,
                "message": f"Watchlist updated with {len(competitor_ids)} competitors",
            }

        except Exception as e:
            logger.error(f"Failed to update watchlist: {e}")
            return {"error": str(e), "status": "failed"}

    async def get_competitor_watchlist(self) -> List[str]:
        """Get the current competitor watchlist."""
        try:
            return await self.memory_manager.get_competitor_watchlist()
        except Exception as e:
            logger.error(f"Failed to get watchlist: {e}")
            return []

    # Utility Operations
    async def get_competitor_summary(self, competitor_id: str) -> Dict[str, Any]:
        """Get a comprehensive summary of a specific competitor."""
        try:
            profile = await self.memory_manager.get_competitor_profile(competitor_id)
            if not profile:
                return {
                    "error": f"Competitor {competitor_id} not found",
                    "status": "not_found",
                }

            # Get recent insights
            recent_insights = await self.get_competitor_insights(
                competitor_id, days_back=7
            )

            # Get analyses
            all_analyses = await self.memory_manager.get_all_competitor_analyses()
            competitor_analyses = [
                a for a in all_analyses if competitor_id in a.competitor_ids
            ]

            summary = {
                "profile": profile.model_dump(),
                "summary_text": format_competitor_summary(profile.model_dump()),
                "recent_insights": recent_insights,
                "analyses_count": len(competitor_analyses),
                "last_updated": profile.last_updated.isoformat(),
                "is_monitored": competitor_id in await self.get_competitor_watchlist(),
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to get competitor summary: {e}")
            return {"error": str(e), "status": "failed"}

    async def search_competitors(self, query: str) -> List[Dict[str, Any]]:
        """Search competitors by name, description, or other attributes."""
        try:
            all_profiles = await self.memory_manager.get_all_competitor_profiles()
            query_lower = query.lower()

            matching_profiles = []
            for profile in all_profiles:
                # Search in multiple fields
                searchable_text = " ".join(
                    [
                        profile.name.lower(),
                        (profile.description or "").lower(),
                        (profile.value_proposition or "").lower(),
                        " ".join(profile.target_audience).lower(),
                        " ".join(profile.key_features).lower(),
                        " ".join(profile.strengths).lower(),
                        " ".join(profile.weaknesses).lower(),
                    ]
                )

                if query_lower in searchable_text:
                    matching_profiles.append(profile.model_dump())

            return matching_profiles

        except Exception as e:
            logger.error(f"Failed to search competitors: {e}")
            return []

    def get_operation_status(self) -> Dict[str, Any]:
        """Get the current status of the manager."""
        return {
            "thread_id": self.thread_id,
            "monitoring_active": self._monitoring_active,
            "last_operation_time": (
                self._last_operation_time.isoformat()
                if self._last_operation_time
                else None
            ),
            "config": self.config,
        }

    async def cleanup(self):
        """Cleanup all resources."""
        logger.info(
            f"Cleaning up CompetitorIntelligenceManager for thread {self.thread_id}"
        )

        try:
            # Stop monitoring if active
            if self._monitoring_active:
                await self.stop_monitoring()

            # Cleanup node
            await self.node.cleanup()

            logger.info("CompetitorIntelligenceManager cleanup completed")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    # Context operations for swarm integration
    async def get_swarm_context(self) -> Dict[str, Any]:
        """Get competitor intelligence context for swarm operations."""
        try:
            profiles = await self.memory_manager.get_all_competitor_profiles()
            insights = await self.memory_manager.get_all_competitor_insights()
            watchlist = await self.memory_manager.get_competitor_watchlist()

            # Generate landscape summary
            landscape_summary = ""
            if profiles:
                high_threat = len(
                    [
                        p
                        for p in profiles
                        if p.threat_level.value in ["high", "critical"]
                    ]
                )
                direct_competitors = len(
                    [p for p in profiles if p.competitor_type.value == "direct"]
                )
                landscape_summary = (
                    f"Tracking {len(profiles)} competitors: {high_threat} high-threat, "
                    f"{direct_competitors} direct competitors. "
                )

                # Add top competitors
                top_competitors = sorted(
                    profiles, key=lambda x: x.threat_level.value, reverse=True
                )[:3]
                landscape_summary += (
                    f"Key competitors: {', '.join([p.name for p in top_competitors])}."
                )

            return {
                "competitor_count": len(profiles),
                "insight_count": len(insights),
                "watchlist_count": len(watchlist),
                "monitoring_active": self._monitoring_active,
                "landscape_summary": landscape_summary,
                "high_threat_count": len(
                    [
                        p
                        for p in profiles
                        if p.threat_level.value in ["high", "critical"]
                    ]
                ),
                "direct_competitor_count": len(
                    [p for p in profiles if p.competitor_type.value == "direct"]
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get swarm context: {e}")
            return {
                "competitor_count": 0,
                "insight_count": 0,
                "watchlist_count": 0,
                "monitoring_active": False,
                "landscape_summary": "Competitor intelligence unavailable",
                "error": str(e),
            }
