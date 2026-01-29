"""
Titan SOTA Intelligence Tool
============================

Unified research engine for the Raptorflow AI system.
Handles LITE, RESEARCH, and DEEP intelligence modes.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..agents.tools.base import RaptorflowTool, ToolResult
from ..services.titan.orchestrator import TitanMode, TitanOrchestrator

logger = logging.getLogger("raptorflow.tools.titan")


class TitanIntelligenceTool(RaptorflowTool):
    """
    Industrial-grade Titan Intelligence Tool.
    Provides tiered research capabilities from fast search to recursive discovery.
    """

    def __init__(self):
        super().__init__(
            name="titan_intelligence_engine",
            description="Execute multi-modal research. Modes: LITE, RESEARCH, DEEP.",
        )
        self._orchestrator = None

    def _get_orchestrator(self) -> TitanOrchestrator:
        """Lazy init for the Titan orchestrator."""
        if self._orchestrator is None:
            self._orchestrator = TitanOrchestrator()
        return self._orchestrator

    async def _arun(
        self, query: str, mode: str = "LITE", focus_areas: List[str] = None, **kwargs
    ) -> ToolResult:
        """Execute tiered research via Titan Orchestrator."""
        max_results = kwargs.get(
            "max_results", 10 if mode == "RESEARCH" else 50 if mode == "DEEP" else 10
        )
        use_stealth = kwargs.get("use_stealth", True)

        try:
            orchestrator = self._get_orchestrator()
            result = await orchestrator.execute(
                query=query,
                mode=mode,
                focus_areas=focus_areas or [],
                max_results=max_results,
                use_stealth=use_stealth,
            )
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def cleanup(self):
        """Cleanup orchestrator resources."""
        if self._orchestrator:
            await self._orchestrator.close()


# Export for dynamic loading
__all__ = ["TitanIntelligenceTool"]
