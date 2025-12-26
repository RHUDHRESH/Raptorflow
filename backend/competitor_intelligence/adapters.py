"""
Integration adapters for connecting competitor intelligence to swarm system
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..graphs.swarm_orchestrator import SwarmOrchestrator
from ..models.swarm import SwarmState
from .manager import CompetitorIntelligenceManager

logger = logging.getLogger("raptorflow.competitor_intelligence.adapters")


class SwarmCompetitorAdapter:
    """
    Adapter for integrating competitor intelligence into swarm workflows.
    Provides seamless connection between swarm operations and competitor intelligence.
    """

    def __init__(self, orchestrator: SwarmOrchestrator):
        self.orchestrator = orchestrator
        self.managers: Dict[str, CompetitorIntelligenceManager] = {}

    def get_manager(self, thread_id: str) -> CompetitorIntelligenceManager:
        """Get or create competitor intelligence manager for thread."""
        if thread_id not in self.managers:
            self.managers[thread_id] = CompetitorIntelligenceManager(thread_id)
        return self.managers[thread_id]

    async def enhance_swarm_state(self, state: SwarmState) -> SwarmState:
        """Enhance swarm state with competitor intelligence context."""
        thread_id = state.get("thread_id", "default")
        manager = self.get_manager(thread_id)

        # Add competitor context to state
        competitor_profiles = await manager.memory_manager.get_all_competitor_profiles()
        if competitor_profiles:
            state["competitor_profiles"] = {p.id: p for p in competitor_profiles}
            state["competitive_landscape_summary"] = self._generate_landscape_summary(
                competitor_profiles
            )

        # Add recent insights
        recent_insights = await manager.memory_manager.get_all_competitor_insights()
        if recent_insights:
            # Filter insights from last 7 days
            cutoff = datetime.now() - timedelta(days=7)
            recent_insights = [i for i in recent_insights if i.discovered_at > cutoff]
            state["competitor_insights"] = recent_insights

        return state

    def _generate_landscape_summary(self, profiles: List[Any]) -> str:
        """Generate a summary of the competitive landscape."""
        if not profiles:
            return "No competitor data available"

        total_competitors = len(profiles)
        high_threat = len(
            [p for p in profiles if p.threat_level.value in ["high", "critical"]]
        )
        direct_competitors = len(
            [p for p in profiles if p.competitor_type.value == "direct"]
        )

        summary = (
            f"Competitive landscape includes {total_competitors} tracked competitors, "
            f"{high_threat} high-threat competitors, and {direct_competitors} direct competitors. "
        )

        # Add market leaders if any
        market_leaders = [
            p for p in profiles if p.competitor_type.value == "market_leader"
        ]
        if market_leaders:
            summary += (
                f"Market leaders: {', '.join([p.name for p in market_leaders[:3]])}. "
            )

        return summary

    async def route_to_competitor_intelligence(
        self, state: SwarmState
    ) -> Dict[str, Any]:
        """Route swarm operation to competitor intelligence specialist."""
        thread_id = state.get("thread_id", "default")
        manager = self.get_manager(thread_id)

        # Determine operation type
        instructions = state.get("instructions", "").lower()

        if "discover" in instructions or "find" in instructions:
            return await manager.discover_competitors(state)
        elif "analyze" in instructions or "swot" in instructions:
            competitor_ids = self._extract_competitor_ids(state)
            return await manager.analyze_competitors(competitor_ids)
        elif "monitor" in instructions or "track" in instructions:
            competitor_ids = self._extract_competitor_ids(state)
            await manager.start_monitoring(competitor_ids)
            return {"status": "monitoring_started", "competitors": competitor_ids}
        elif "report" in instructions or "summary" in instructions:
            return await manager.generate_report()
        else:
            # Default to general intelligence
            return await manager.node(state)

    def _extract_competitor_ids(self, state: SwarmState) -> List[str]:
        """Extract competitor IDs from state."""
        # Check for explicit target competitors
        if "target_competitors" in state:
            return state["target_competitors"]

        # Extract from instructions
        instructions = state.get("instructions", "")
        import re

        mentions = re.findall(r"@(\w+)", instructions)
        return mentions

    async def cleanup_thread(self, thread_id: str):
        """Cleanup resources for a specific thread."""
        if thread_id in self.managers:
            await self.managers[thread_id].cleanup()
            del self.managers[thread_id]


class SwarmCompetitorNodeFactory:
    """
    Factory for creating competitor intelligence nodes that integrate with swarm.
    """

    @staticmethod
    def create_competitor_intelligence_node(thread_id: str) -> Any:
        """Create a competitor intelligence node for swarm integration."""
        from ..nodes.competitor_intelligence import CompetitorIntelligenceNode

        return CompetitorIntelligenceNode(thread_id)

    @staticmethod
    def create_competitor_monitoring_node(thread_id: str) -> Any:
        """Create a specialized competitor monitoring node."""

        class CompetitorMonitoringNode:
            def __init__(self, thread_id: str):
                self.thread_id = thread_id
                self.manager = CompetitorIntelligenceManager(thread_id)

            async def __call__(self, state: SwarmState) -> Dict[str, Any]:
                competitor_ids = self._extract_competitors(state)
                frequency = state.get("monitoring_frequency", "daily")

                await self.manager.start_monitoring(competitor_ids, frequency)

                return {
                    "analysis_summary": f"Started monitoring {len(competitor_ids)} competitors with {frequency} frequency",
                    "monitored_competitors": competitor_ids,
                    "monitoring_frequency": frequency,
                    "status": "monitoring_active",
                }

            def _extract_competitors(self, state: SwarmState) -> List[str]:
                if "target_competitors" in state:
                    return state["target_competitors"]

                # Get all competitors if none specified
                return list(state.get("competitor_profiles", {}).keys())

        return CompetitorMonitoringNode(thread_id)

    @staticmethod
    def create_competitor_analysis_node(thread_id: str) -> Any:
        """Create a specialized competitor analysis node."""

        class CompetitorAnalysisNode:
            def __init__(self, thread_id: str):
                self.thread_id = thread_id
                self.manager = CompetitorIntelligenceManager(thread_id)

            async def __call__(self, state: SwarmState) -> Dict[str, Any]:
                competitor_ids = self._extract_competitors(state)
                analysis_type = state.get("analysis_type", "swot")

                result = await self.manager.analyze_competitors(competitor_ids)

                return {
                    "analysis_summary": f"Completed {analysis_type} analysis for {len(competitor_ids)} competitors",
                    "analysis_result": result,
                    "analysis_type": analysis_type,
                    "competitors_analyzed": competitor_ids,
                }

            def _extract_competitors(self, state: SwarmState) -> List[str]:
                if "target_competitors" in state:
                    return state["target_competitors"]

                return list(state.get("competitor_profiles", {}).keys())

        return CompetitorAnalysisNode(thread_id)


# Integration helper functions
def register_competitor_nodes_with_orchestrator(orchestrator: SwarmOrchestrator):
    """Register competitor intelligence nodes with swarm orchestrator."""
    thread_id = (
        orchestrator.thread_id if hasattr(orchestrator, "thread_id") else "default"
    )

    # Register nodes
    orchestrator.register_node(
        "competitor_intelligence",
        SwarmCompetitorNodeFactory.create_competitor_intelligence_node(thread_id),
    )
    orchestrator.register_node(
        "competitor_monitoring",
        SwarmCompetitorNodeFactory.create_competitor_monitoring_node(thread_id),
    )
    orchestrator.register_node(
        "competitor_analysis",
        SwarmCompetitorNodeFactory.create_competitor_analysis_node(thread_id),
    )

    logger.info("Competitor intelligence nodes registered with swarm orchestrator")


def enhance_swarm_routing_with_competitors(orchestrator: SwarmOrchestrator):
    """Enhance swarm routing to include competitor intelligence considerations."""
    original_route = orchestrator.route_intent

    async def enhanced_route(query: str) -> Any:
        # Check if query is competitor-related
        competitor_keywords = [
            "competitor",
            "competition",
            "market",
            "rival",
            "opponent",
        ]
        if any(keyword in query.lower() for keyword in competitor_keywords):
            # Route to competitor intelligence
            intent = await original_route(query)
            intent.asset_type = "competitor_analysis"
            return intent

        return await original_route(query)

    orchestrator.route_intent = enhanced_route
    logger.info("Enhanced swarm routing with competitor intelligence detection")
