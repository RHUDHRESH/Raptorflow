import asyncio
import logging
from typing import Any, Dict, List, Optional

from agents.specialists.swarm_competitor_intelligence import (
    SwarmCompetitorIntelligenceAgent,
)
from memory.swarm_l1 import SwarmL1MemoryManager
from models.swarm import SwarmState
from services.competitor_monitoring import (
    CompetitorAnalysisService,
    CompetitorMonitoringService,
)

logger = logging.getLogger("raptorflow.nodes.competitor_intelligence")


class CompetitorIntelligenceNode:
    """
    Swarm node for competitor intelligence operations.
    Integrates competitor discovery, analysis, and monitoring into swarm workflows.
    """

    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.memory_manager = SwarmL1MemoryManager(thread_id)
        self.agent = SwarmCompetitorIntelligenceAgent()
        self.monitoring_service = CompetitorMonitoringService(self.memory_manager)
        self.analysis_service = CompetitorAnalysisService(self.memory_manager)

    async def __call__(self, state: SwarmState) -> Dict[str, Any]:
        """Main entry point for competitor intelligence node."""
        logger.info("CompetitorIntelligenceNode called...")

        try:
            # Determine operation type from state or instructions
            operation = self._determine_operation(state)

            if operation == "discover":
                return await self._handle_discovery(state)
            elif operation == "analyze":
                return await self._handle_analysis(state)
            elif operation == "monitor":
                return await self._handle_monitoring(state)
            elif operation == "report":
                return await self._handle_reporting(state)
            elif operation == "benchmark":
                return await self._handle_benchmarking(state)
            else:
                return await self._handle_general_intelligence(state)

        except Exception as e:
            logger.error(f"Error in CompetitorIntelligenceNode: {e}")
            return {
                "analysis_summary": f"Competitor intelligence operation failed: {str(e)}",
                "status": "error",
                "error": str(e),
            }

    def _determine_operation(self, state: SwarmState) -> str:
        """Determine the type of competitor intelligence operation needed."""
        instructions = state.get("instructions", "").lower()

        if "discover" in instructions or "find" in instructions:
            return "discover"
        elif "analyze" in instructions or "swot" in instructions:
            return "analyze"
        elif "monitor" in instructions or "track" in instructions:
            return "monitor"
        elif "report" in instructions or "summary" in instructions:
            return "report"
        elif "benchmark" in instructions or "compare" in instructions:
            return "benchmark"
        else:
            return "general"

    async def _handle_discovery(self, state: SwarmState) -> Dict[str, Any]:
        """Handle competitor discovery operations."""
        logger.info("Handling competitor discovery...")

        # Set operation type for agent
        state["competitor_operation"] = "discover"

        # Call competitor intelligence agent
        result = await self.agent(state)

        if "error" in result:
            return {
                "analysis_summary": f"Competitor discovery failed: {result['error']}",
                "status": "error",
            }

        # Update memory with discovered competitors
        discovered_competitors = result.get("discovered_competitors", [])
        updated_state = result.get("updated_state", state)

        # Store in memory
        for comp_data in discovered_competitors:
            from models.swarm import CompetitorProfile

            competitor = CompetitorProfile.model_validate(comp_data)
            await self.memory_manager.update_competitor_profile(competitor)

        summary = (
            f"Discovered {len(discovered_competitors)} new competitors. "
            f"Key insights: {', '.join(result.get('market_insights', [])[:3])}. "
            f"Competitive gaps identified: {len(result.get('competitive_gaps', []))}."
        )

        return {
            "analysis_summary": summary,
            "discovered_competitors": discovered_competitors,
            "market_insights": result.get("market_insights", []),
            "competitive_gaps": result.get("competitive_gaps", []),
            "recommendations": result.get("recommendations", []),
            "confidence_score": result.get("confidence_score", 0.0),
            "status": "completed",
        }

    async def _handle_analysis(self, state: SwarmState) -> Dict[str, Any]:
        """Handle competitor analysis operations."""
        logger.info("Handling competitor analysis...")

        # Get target competitors from state or instructions
        target_competitors = self._extract_target_competitors(state)

        if not target_competitors:
            # If no specific targets, analyze all known competitors
            all_profiles = await self.memory_manager.get_all_competitor_profiles()
            target_competitors = [p.id for p in all_profiles]

        if not target_competitors:
            return {
                "analysis_summary": "No competitors available for analysis. Run discovery first.",
                "status": "no_competitors",
            }

        # Set operation type for agent
        state["competitor_operation"] = "analyze"
        state["target_competitors"] = target_competitors

        # Call competitor intelligence agent
        result = await self.agent(state)

        if "error" in result:
            return {
                "analysis_summary": f"Competitor analysis failed: {result['error']}",
                "status": "error",
            }

        # Store analysis in memory
        analysis_data = result.get("analysis")
        if analysis_data:
            from models.swarm import CompetitorAnalysis

            analysis = CompetitorAnalysis.model_validate(analysis_data)
            await self.memory_manager.add_competitor_analysis(analysis)

        summary = (
            f"Analyzed {len(target_competitors)} competitors. "
            f"Threat assessment: {result.get('threat_assessment', 'unknown')}. "
            f"Strategic recommendations: {len(result.get('strategic_recommendations', []))}."
        )

        return {
            "analysis_summary": summary,
            "analysis_result": result.get("analysis"),
            "swot_analysis": result.get("swot_analysis", {}),
            "threat_assessment": result.get("threat_assessment"),
            "strategic_recommendations": result.get("strategic_recommendations", []),
            "market_opportunities": result.get("market_opportunities", []),
            "confidence_score": result.get("confidence_score", 0.0),
            "status": "completed",
        }

    async def _handle_monitoring(self, state: SwarmState) -> Dict[str, Any]:
        """Handle competitor monitoring operations."""
        logger.info("Handling competitor monitoring...")

        # Get competitors to monitor
        target_competitors = self._extract_target_competitors(state)

        if not target_competitors:
            all_profiles = await self.memory_manager.get_all_competitor_profiles()
            target_competitors = [p.id for p in all_profiles]

        if not target_competitors:
            return {
                "analysis_summary": "No competitors available for monitoring. Run discovery first.",
                "status": "no_competitors",
            }

        # Determine monitoring frequency
        instructions = state.get("instructions", "").lower()
        frequency = "daily"  # default
        if "hourly" in instructions:
            frequency = "hourly"
        elif "weekly" in instructions:
            frequency = "weekly"
        elif "real" in instructions:
            frequency = "real_time"

        # Start monitoring
        from services.competitor_monitoring import MonitoringFrequency

        freq_enum = MonitoringFrequency(frequency)
        await self.monitoring_service.start_monitoring(target_competitors, freq_enum)

        summary = (
            f"Started monitoring {len(target_competitors)} competitors with {frequency} frequency. "
            f"Automated alerts and insights will be generated."
        )

        return {
            "analysis_summary": summary,
            "monitored_competitors": target_competitors,
            "monitoring_frequency": frequency,
            "monitoring_status": "active",
            "status": "completed",
        }

    async def _handle_reporting(self, state: SwarmState) -> Dict[str, Any]:
        """Handle competitor intelligence reporting."""
        logger.info("Handling competitor intelligence reporting...")

        # Generate comprehensive report
        report = await self.monitoring_service.generate_competitor_intelligence_report()

        # Generate additional analysis
        all_profiles = await self.memory_manager.get_all_competitor_profiles()
        if all_profiles:
            competitor_ids = [p.id for p in all_profiles]

            # SWOT analysis
            swot_analysis = await self.analysis_service.perform_swot_analysis(
                competitor_ids
            )

            # Positioning analysis
            positioning_analysis = (
                await self.analysis_service.perform_positioning_analysis(competitor_ids)
            )

            # Competitive gaps
            competitive_gaps = await self.analysis_service.identify_competitive_gaps(
                competitor_ids
            )

            report["swot_analysis"] = swot_analysis
            report["positioning_analysis"] = positioning_analysis
            report["competitive_gaps"] = competitive_gaps

        summary = (
            f"Generated comprehensive competitor intelligence report covering "
            f"{report.get('competitors_analyzed', 0)} competitors with "
            f"{report.get('total_insights', 0)} insights and "
            f"{report.get('total_analyses', 0)} analyses."
        )

        return {
            "analysis_summary": summary,
            "intelligence_report": report,
            "report_generated_at": report.get("generated_at"),
            "competitors_analyzed": report.get("competitors_analyzed", 0),
            "total_insights": report.get("total_insights", 0),
            "status": "completed",
        }

    async def _handle_benchmarking(self, state: SwarmState) -> Dict[str, Any]:
        """Handle competitor benchmarking operations."""
        logger.info("Handling competitor benchmarking...")

        # Get target competitors
        target_competitors = self._extract_target_competitors(state)

        if not target_competitors:
            all_profiles = await self.memory_manager.get_all_competitor_profiles()
            target_competitors = [p.id for p in all_profiles]

        if not target_competitors:
            return {
                "analysis_summary": "No competitors available for benchmarking. Run discovery first.",
                "status": "no_competitors",
            }

        # Generate benchmarks
        benchmarks = await self.analysis_service.generate_competitive_benchmarks(
            target_competitors
        )

        summary = (
            f"Generated competitive benchmarks for {len(target_competitors)} competitors. "
            f"Analysis includes feature coverage, pricing, market presence, and threat assessment."
        )

        return {
            "analysis_summary": summary,
            "benchmarks": benchmarks,
            "benchmarked_competitors": target_competitors,
            "benchmark_categories": list(benchmarks.keys()),
            "status": "completed",
        }

    async def _handle_general_intelligence(self, state: SwarmState) -> Dict[str, Any]:
        """Handle general competitor intelligence operations."""
        logger.info("Handling general competitor intelligence...")

        # Get current competitive landscape
        all_profiles = await self.memory_manager.get_all_competitor_profiles()
        all_insights = await self.memory_manager.get_all_competitor_insights()

        if not all_profiles:
            return {
                "analysis_summary": "No competitor data available. Run competitor discovery first.",
                "status": "no_data",
            }

        # Generate general intelligence summary
        high_threat = [
            p for p in all_profiles if p.threat_level.value in ["high", "critical"]
        ]
        recent_insights = [
            i
            for i in all_insights
            if i.discovered_at > asyncio.get_event_loop().time() - 86400
        ]  # Last 24 hours

        summary = (
            f"Current competitive landscape: {len(all_profiles)} competitors tracked, "
            f"{len(high_threat)} high-threat competitors, "
            f"{len(recent_insights)} recent insights. "
            f"Competitive intelligence is actively maintained."
        )

        return {
            "analysis_summary": summary,
            "total_competitors": len(all_profiles),
            "high_threat_competitors": len(high_threat),
            "recent_insights": len(recent_insights),
            "competitive_landscape_status": "active",
            "status": "completed",
        }

    def _extract_target_competitors(self, state: SwarmState) -> List[str]:
        """Extract target competitor IDs from state or instructions."""
        target_competitors = []

        # Check for explicit target competitors in state
        if "target_competitors" in state:
            target_competitors = state["target_competitors"]

        # Extract from instructions (look for @mentions or specific names)
        instructions = state.get("instructions", "")
        if "@" in instructions:
            # Extract @mentions
            import re

            mentions = re.findall(r"@(\w+)", instructions)
            target_competitors.extend(mentions)

        return list(set(target_competitors))  # Remove duplicates

    async def cleanup(self):
        """Cleanup resources when node is destroyed."""
        logger.info("Cleaning up CompetitorIntelligenceNode...")

        # Stop monitoring
        await self.monitoring_service.stop_monitoring()

        logger.info("CompetitorIntelligenceNode cleanup completed")


# Factory function for creating competitor intelligence nodes
def create_competitor_intelligence_node(thread_id: str) -> CompetitorIntelligenceNode:
    """Create a competitor intelligence node for the given thread."""
    return CompetitorIntelligenceNode(thread_id)
