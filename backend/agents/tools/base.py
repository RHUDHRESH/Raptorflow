"""
Base classes for Raptorflow agent tools.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ToolError(Exception):
    """Custom exception for tool errors."""

    def __init__(
        self, tool_name: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        self.tool_name = tool_name
        self.message = message
        self.details = details or {}
        super().__init__(f"[{tool_name}] {message}")


@dataclass
class ToolResult:
    """Result from tool execution."""

    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    tokens_used: int = 0
    latency_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
        }


class RaptorflowTool(ABC):
    """Base class for all Raptorflow tools."""

    def __init__(self, name: str, description: str):
        """Initialize the tool."""
        self.name = name
        self.description = description
        self.workspace_id: Optional[str] = None

    def set_workspace_id(self, workspace_id: str):
        """Set the workspace context."""
        self.workspace_id = workspace_id

    def _log_call(self, method: str, **kwargs):
        """Log a tool method call."""
        logger.info(
            f"Tool '{self.name}' calling {method} with workspace '{self.workspace_id}'"
        )
        if kwargs:
            logger.debug(f"Parameters: {kwargs}")

    def _log_result(self, method: str, result: ToolResult):
        """Log a tool method result."""
        if result.success:
            logger.info(
                f"Tool '{self.name}' {method} succeeded in {result.latency_ms}ms"
            )
        else:
            logger.error(f"Tool '{self.name}' {method} failed: {result.error}")

    def _handle_error(self, method: str, error: Exception) -> ToolResult:
        """Handle and log errors."""
        error_msg = f"{type(error).__name__}: {str(error)}"
        logger.error(f"Tool '{self.name}' {method} error: {error_msg}")
        return ToolResult(success=False, error=error_msg)

    def _measure_execution(self, func, *args, **kwargs):
        """Measure execution time and return result."""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            latency_ms = int((time.time() - start_time) * 1000)

            if isinstance(result, ToolResult):
                result.latency_ms = latency_ms
            else:
                result = ToolResult(success=True, data=result, latency_ms=latency_ms)

            return result
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return self._handle_error(func.__name__, e)

    @abstractmethod
    async def _arun(self, *args, **kwargs) -> ToolResult:
        """Async implementation of the tool."""
        pass

    async def arun(self, *args, **kwargs) -> ToolResult:
        """Run the tool asynchronously."""
        self._log_call("arun", **kwargs)

        # Ensure workspace_id is set
        if not self.workspace_id:
            raise ToolError(self.name, "Workspace ID not set")

        # Measure execution
        result = self._measure_execution(self._arun, *args, **kwargs)

        self._log_result("arun", result)
        return result

    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "name": self.name,
            "description": self.description,
            "workspace_id": self.workspace_id,
        }

    def validate_workspace_access(self) -> bool:
        """Validate that the tool has proper workspace context."""
        return self.workspace_id is not None
