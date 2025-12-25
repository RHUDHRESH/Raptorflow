import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict

from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("raptorflow.toolbelt.base")


class RaptorRateLimiter:
    """
    SOTA Resiliency Layer.
    Provides exponential backoff and attempt tracking for external tools.
    """

    @staticmethod
    def get_retry_decorator():
        return retry(
            wait=wait_exponential(multiplier=1, min=4, max=10),
            stop=stop_after_attempt(3),
            before_sleep=lambda retry_state: logger.warning(
                f"Retrying tool execution: {retry_state.attempt_number}..."
            ),
        )


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
        logger.info(f"Tool {self.name} starting...")
        try:
            result = await self._execute(**kwargs)
            latency = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "success": True,
                "data": result,
                "latency_ms": latency,
                "error": None,
            }
        except Exception as e:
            logger.error(f"Tool {self.name} failed: {e}")
            return {"success": False, "data": None, "latency_ms": 0, "error": str(e)}
