import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from backend.models.telemetry import TelemetryEventType
from backend.services.telemetry_collector import get_telemetry_collector

logger = logging.getLogger("raptorflow.toolbelt.base")


class RaptorRateLimiter:
    """
    SOTA Resiliency Layer.
    Provides exponential backoff and attempt tracking for external tools.
    """

    _budget_delay_seconds: float = 0.0
    _budget_blocked: bool = False
    _budget_reason: Optional[str] = None

    @staticmethod
    def get_retry_decorator():
        return retry(
            wait=wait_exponential(multiplier=1, min=4, max=10),
            stop=stop_after_attempt(3),
            before_sleep=lambda retry_state: logger.warning(
                f"Retrying tool execution: {retry_state.attempt_number}..."
            ),
        )

    @classmethod
    def apply_budget_throttle(
        cls, delay_seconds: float, reason: str, blocked: bool = False
    ):
        cls._budget_delay_seconds = max(delay_seconds, 0.0)
        cls._budget_blocked = blocked
        cls._budget_reason = reason

    @classmethod
    def clear_budget_throttle(cls):
        cls._budget_delay_seconds = 0.0
        cls._budget_blocked = False
        cls._budget_reason = None

    @classmethod
    async def wait_if_throttled(cls):
        if cls._budget_blocked:
            raise RuntimeError(cls._budget_reason or "Budget gate blocked tool call.")
        if cls._budget_delay_seconds > 0:
            await asyncio.sleep(cls._budget_delay_seconds)


class BaseRaptorTool(ABC):
    """
    SOTA Abstract Base Class for all RaptorFlow tools.
    Ensures standard telemetry, error handling, and caching.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The tool name for the Supervisor/Agents."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description used by the LLM to understand tool utility."""
        pass

    @abstractmethod
    async def _execute(self, **kwargs) -> Any:
        """The actual tool logic implementation."""
        pass

    async def run(self, **kwargs) -> Dict[str, Any]:
        """Wrapper with telemetry and error handling."""
        start_time = datetime.now()
        collector = get_telemetry_collector()
        metadata = {}
        if "workspace_id" in kwargs:
            metadata["workspace_id"] = kwargs.get("workspace_id")
        if "tenant_id" in kwargs:
            metadata["tenant_id"] = kwargs.get("tenant_id")
        if "agent_name" in kwargs:
            metadata["agent_name"] = kwargs.get("agent_name")
        await collector.record_tool_event(
            TelemetryEventType.TOOL_START,
            self.name,
            {
                "parameters": list(kwargs.keys()),
                "started_at": start_time.isoformat(),
            },
            metadata=metadata,
        )
        logger.info(f"Tool {self.name} starting...")
        try:
            await RaptorRateLimiter.wait_if_throttled()
        except RuntimeError as exc:
            logger.warning(f"Tool {self.name} throttled: {exc}")
            return {"success": False, "data": None, "latency_ms": 0, "error": str(exc)}
        try:
            result = await self._execute(**kwargs)
            latency = (datetime.now() - start_time).total_seconds() * 1000
            await collector.record_tool_event(
                TelemetryEventType.TOOL_END,
                self.name,
                {
                    "duration_ms": latency,
                    "success": True,
                },
                metadata=metadata,
            )
            return {
                "success": True,
                "data": result,
                "latency_ms": latency,
                "error": None,
            }
        except Exception as e:
            logger.error(f"Tool {self.name} failed: {e}")
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            await collector.record_tool_event(
                TelemetryEventType.TOOL_END,
                self.name,
                {
                    "duration_ms": duration_ms,
                    "success": False,
                    "error": str(e),
                },
                metadata=metadata,
            )
            return {"success": False, "data": None, "latency_ms": 0, "error": str(e)}
