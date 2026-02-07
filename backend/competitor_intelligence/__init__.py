"""
Competitor Intelligence Integration Module
Provides unified access to all competitor intelligence functionality
"""

from .agent import SwarmCompetitorIntelligenceAgent
from .memory import SwarmL1MemoryManager
from .models import (
    CompetitorAnalysis,
    CompetitorGroup,
    CompetitorInsight,
    CompetitorProfile,
    CompetitorThreatLevel,
    CompetitorType,
)
from .monitoring import CompetitorAnalysisService, CompetitorMonitoringService
from .node import CompetitorIntelligenceNode

__all__ = [
    "CompetitorIntelligenceManager",
    "CompetitorProfile",
    "CompetitorGroup",
    "CompetitorInsight",
    "CompetitorAnalysis",
    "CompetitorType",
    "CompetitorThreatLevel",
    "SwarmCompetitorIntelligenceAgent",
    "CompetitorMonitoringService",
    "CompetitorAnalysisService",
    "CompetitorIntelligenceNode",
]

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("raptorflow.competitor_intelligence")


class CompetitorIntelligenceManager:
    """
    Unified manager for all competitor intelligence operations.
    Provides a clean interface for swarm agents to interact with competitor functionality.
    """

    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.memory_manager = SwarmL1MemoryManager(thread_id)
        self.agent = SwarmCompetitorIntelligenceAgent()
        self.monitoring_service = CompetitorMonitoringService(self.memory_manager)
        self.analysis_service = CompetitorAnalysisService(self.memory_manager)
        self.node = CompetitorIntelligenceNode(thread_id)

    async def discover_competitors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Discover new competitors based on context."""
        from models.swarm import SwarmState

        state = SwarmState(**context)
        return await self.agent.discover_competitors(state)

    async def analyze_competitors(self, competitor_ids: List[str]) -> Dict[str, Any]:
        """Analyze specific competitors."""
        from models.swarm import SwarmState

        state = SwarmState()
        return await self.agent.analyze_competitors(state, competitor_ids)

    async def start_monitoring(
        self, competitor_ids: List[str], frequency: str = "daily"
    ):
        """Start monitoring competitors."""
        from .monitoring import MonitoringFrequency

        freq = MonitoringFrequency(frequency)
        await self.monitoring_service.start_monitoring(competitor_ids, freq)

    async def stop_monitoring(self):
        """Stop all monitoring."""
        await self.monitoring_service.stop_monitoring()

    async def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive intelligence report."""
        return await self.monitoring_service.generate_competitor_intelligence_report()

    async def cleanup(self):
        """Cleanup resources."""
        await self.node.cleanup()
