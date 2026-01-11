"""
Raptorflow Base Tool Classes
===========================

Base classes and utilities for creating tools in the Raptorflow system.
Provides a foundation for building consistent, reliable, and performant tools.

Features:
- Abstract base tool class with common functionality
- Tool result and status management
- Error handling and validation
- Performance monitoring and metrics
- Configuration management
- Logging and debugging utilities
- Tool registry and discovery
"""

import asyncio
import json
import time
import traceback
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

import structlog

# External imports
from pydantic import BaseModel, ValidationError

# Local imports
from ..base import BaseComponent, ComponentConfig, ExecutionContext, ExecutionResult
from ..config import settings

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class ToolStatus(str, Enum):
    """Tool execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ToolCategory(str, Enum):
    """Tool categories."""

    DATA_PROCESSING = "data_processing"
    WEB_TOOLS = "web_tools"
    CONTENT_TOOLS = "content_tools"
    COMMUNICATION = "communication"
    FILE_TOOLS = "file_tools"
    INTEGRATION = "integration"
    UTILITIES = "utilities"


@dataclass
class ToolConfig:
    """Tool configuration."""

    name: str
    description: str
    category: ToolCategory
    version: str = "1.0.0"
    author: str = "Raptorflow Team"
    enabled: bool = True
    timeout: int = 300  # 5 minutes
    retry_attempts: int = 3
    retry_delay: float = 1.0
    max_concurrent: int = 1
    required_config: List[str] = field(default_factory=list)
    optional_config: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """Tool execution result."""

    id: str
    tool_name: str
    status: ToolStatus
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_traceback: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "error_traceback": self.error_traceback,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "metadata": self.metadata,
        }

    def is_success(self) -> bool:
        """Check if the result is successful."""
        return self.status == ToolStatus.COMPLETED

    def is_error(self) -> bool:
        """Check if the result is an error."""
        return self.status in [
            ToolStatus.FAILED,
            ToolStatus.TIMEOUT,
            ToolStatus.CANCELLED,
        ]


class ToolError(Exception):
    """Base exception for tool errors."""

    def __init__(
        self,
        message: str,
        tool_name: str = None,
        error_code: str = None,
        context: Dict[str, Any] = None,
    ):
        super().__init__(message)
        self.tool_name = tool_name
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now()


class ToolValidationError(ToolError):
    """Exception for tool validation errors."""

    pass


class ToolExecutionError(ToolError):
    """Exception for tool execution errors."""

    pass


class ToolTimeoutError(ToolError):
    """Exception for tool timeout errors."""

    pass


class ToolConfigError(ToolError):
    """Exception for tool configuration errors."""

    pass


class ToolPerformanceMonitor:
    """Performance monitoring for tools."""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.counters: Dict[str, int] = {}
        self.timers: Dict[str, float] = {}
        self.errors: Dict[str, List[str]] = {}

    def record_metric(self, tool_name: str, metric_name: str, value: float):
        """Record a metric value."""
        key = f"{tool_name}_{metric_name}"
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(value)

        # Keep only last 1000 values
        if len(self.metrics[key]) > 1000:
            self.metrics[key] = self.metrics[key][-1000:]

    def increment_counter(self, tool_name: str, counter_name: str, value: int = 1):
        """Increment a counter."""
        key = f"{tool_name}_{counter_name}"
        self.counters[key] = self.counters.get(key, 0) + value

    def start_timer(self, tool_name: str, timer_name: str):
        """Start a timer."""
        key = f"{tool_name}_{timer_name}"
        self.timers[key] = time.time()

    def end_timer(self, tool_name: str, timer_name: str) -> float:
        """End a timer and return duration."""
        key = f"{tool_name}_{timer_name}"
        if key in self.timers:
            duration = time.time() - self.timers[key]
            self.record_metric(tool_name, f"{timer_name}_duration", duration)
            del self.timers[key]
            return duration
        return 0.0

    def record_error(self, tool_name: str, error: str):
        """Record an error."""
        key = f"{tool_name}_errors"
        if key not in self.errors:
            self.errors[key] = []
        self.errors[key].append(error)

        # Keep only last 100 errors
        if len(self.errors[key]) > 100:
            self.errors[key] = self.errors[key][-100:]

    def get_tool_metrics(self, tool_name: str) -> Dict[str, Any]:
        """Get metrics for a specific tool."""
        tool_metrics = {}

        # Get execution metrics
        for key, values in self.metrics.items():
            if key.startswith(f"{tool_name}_"):
                metric_name = key[len(f"{tool_name}_") :]
                if values:
                    tool_metrics[metric_name] = {
                        "count": len(values),
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values),
                        "sum": sum(values),
                    }

        # Get counters
        for key, value in self.counters.items():
            if key.startswith(f"{tool_name}_"):
                counter_name = key[len(f"{tool_name}_") :]
                tool_metrics[counter_name] = value

        # Get errors
        error_key = f"{tool_name}_errors"
        if error_key in self.errors:
            tool_metrics["errors"] = self.errors[error_key]

        return tool_metrics

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics."""
        all_metrics = {}

        # Group metrics by tool
        tool_names = set()
        for key in self.metrics:
            tool_names.add(key.split("_")[0])
        for key in self.counters:
            tool_names.add(key.split("_")[0])
        for key in self.errors:
            tool_names.add(key.split("_")[0])

        for tool_name in tool_names:
            all_metrics[tool_name] = self.get_tool_metrics(tool_name)

        return all_metrics


def tool_performance_monitor(monitor: ToolPerformanceMonitor):
    """Decorator for tool performance monitoring."""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            tool_name = self.config.name
            monitor.increment_counter(tool_name, "calls")
            monitor.start_timer(tool_name, "execution")

            try:
                result = await func(self, *args, **kwargs)
                monitor.increment_counter(tool_name, "success")
                return result
            except Exception as e:
                monitor.increment_counter(tool_name, "error")
                monitor.record_error(tool_name, str(e))
                raise
            finally:
                monitor.end_timer(tool_name, "execution")

        return wrapper

    return decorator


def tool_timeout(timeout: int):
    """Decorator for tool timeout handling."""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(self, *args, **kwargs), timeout=timeout
                )
            except asyncio.TimeoutError:
                raise ToolTimeoutError(
                    f"Tool execution timed out after {timeout} seconds",
                    tool_name=self.config.name,
                )

        return wrapper

    return decorator


def tool_retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for tool retry logic."""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        sleep_time = delay * (backoff**attempt)
                        logger.warning(
                            f"Tool execution failed, retrying in {sleep_time}s",
                            tool=self.config.name,
                            attempt=attempt + 1,
                            error=str(e),
                        )
                        await asyncio.sleep(sleep_time)
                    else:
                        logger.error(
                            "Tool execution failed after all retries",
                            tool=self.config.name,
                            attempts=max_retries,
                            error=str(e),
                        )

            raise last_exception

        return wrapper

    return decorator


class BaseTool(ABC):
    """Base class for all tools."""

    # Tool metadata (to be overridden by subclasses)
    NAME = "base_tool"
    DESCRIPTION = "Base tool class"
    CATEGORY = ToolCategory.UTILITIES
    VERSION = "1.0.0"
    AUTHOR = "Raptorflow Team"
    REQUIRED_CONFIG = []
    OPTIONAL_CONFIG = []
    CAPABILITIES = []

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.performance_monitor = ToolPerformanceMonitor()
        self._initialized = False
        self._lock = asyncio.Lock()

        # Tool metadata
        self.tool_config = ToolConfig(
            name=self.NAME,
            description=self.DESCRIPTION,
            category=self.CATEGORY,
            version=self.VERSION,
            author=self.AUTHOR,
            required_config=self.REQUIRED_CONFIG,
            optional_config=self.OPTIONAL_CONFIG,
            capabilities=self.CAPABILITIES,
        )

        # Validate configuration
        self._validate_config()

    def _validate_config(self):
        """Validate tool configuration."""
        # Check required config
        for required_key in self.REQUIRED_CONFIG:
            if required_key not in self.config:
                raise ToolConfigError(
                    f"Required configuration missing: {required_key}",
                    tool_name=self.NAME,
                )

        # Validate config values
        self._validate_config_values()

    def _validate_config_values(self):
        """Validate configuration values (to be overridden by subclasses)."""
        pass

    async def initialize(self):
        """Initialize the tool."""
        async with self._lock:
            if self._initialized:
                return

            try:
                await self._on_initialize()
                self._initialized = True

                logger.info(
                    "Tool initialized", tool=self.NAME, category=self.CATEGORY.value
                )

            except Exception as e:
                logger.error("Tool initialization failed", tool=self.NAME, error=str(e))
                raise ToolConfigError(
                    f"Initialization failed: {e}", tool_name=self.NAME
                )

    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        if not self._initialized:
            await self.initialize()

        # Create execution result
        result = ToolResult(
            id=str(uuid.uuid4()),
            tool_name=self.NAME,
            status=ToolStatus.RUNNING,
            start_time=datetime.now(),
        )

        try:
            # Validate input
            self._validate_input(kwargs)

            # Execute with timeout
            timeout = self.config.get("timeout", self.tool_config.timeout)
            if timeout:
                result.data = await asyncio.wait_for(
                    self._execute_with_monitoring(**kwargs), timeout=timeout
                )
            else:
                result.data = await self._execute_with_monitoring(**kwargs)

            # Mark as successful
            result.status = ToolStatus.COMPLETED

            logger.info(
                "Tool execution successful", tool=self.NAME, execution_id=result.id
            )

        except asyncio.TimeoutError:
            result.status = ToolStatus.TIMEOUT
            result.error = f"Tool execution timed out after {timeout} seconds"

            logger.error(
                "Tool execution timed out",
                tool=self.NAME,
                execution_id=result.id,
                timeout=timeout,
            )

        except Exception as e:
            result.status = ToolStatus.FAILED
            result.error = str(e)
            result.error_traceback = traceback.format_exc()

            logger.error(
                "Tool execution failed",
                tool=self.NAME,
                execution_id=result.id,
                error=str(e),
            )

        finally:
            # Finalize result
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()

            return result

    @tool_performance_monitor(performance_monitor)
    async def _execute_with_monitoring(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with performance monitoring."""
        return await self._execute(**kwargs)

    @abstractmethod
    async def _execute(self, **kwargs) -> Dict[str, Any]:
        """Abstract method for tool execution."""
        pass

    @abstractmethod
    async def _on_initialize(self):
        """Abstract method for tool initialization."""
        pass

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data (to be overridden by subclasses)."""
        pass

    async def validate_config(self) -> bool:
        """Validate tool configuration."""
        try:
            self._validate_config()
            return True
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get tool status."""
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "category": self.CATEGORY.value,
            "version": self.VERSION,
            "author": self.AUTHOR,
            "initialized": self._initialized,
            "config": self.config,
            "capabilities": self.CAPABILITIES,
            "performance_metrics": self.performance_monitor.get_tool_metrics(self.NAME),
        }

    def get_info(self) -> Dict[str, Any]:
        """Get tool information."""
        return {
            "name": self.NAME,
            "description": self.DESCRIPTION,
            "category": self.CATEGORY.value,
            "version": self.VERSION,
            "author": self.AUTHOR,
            "required_config": self.REQUIRED_CONFIG,
            "optional_config": self.OPTIONAL_CONFIG,
            "capabilities": self.CAPABILITIES,
            "metadata": self.tool_config.metadata,
        }

    async def cleanup(self):
        """Cleanup tool resources."""
        async with self._lock:
            if hasattr(self, "_on_cleanup"):
                await self._on_cleanup()

            self._initialized = False
            logger.info("Tool cleaned up", tool=self.NAME)


class DataProcessingTool(BaseTool):
    """Base class for data processing tools."""

    CATEGORY = ToolCategory.DATA_PROCESSING

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.supported_formats = []
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data for data processing."""
        if "data" not in input_data:
            raise ToolValidationError(
                "Missing required 'data' parameter", tool_name=self.NAME
            )

        # Check file size if file data
        if "file_path" in input_data:
            import os

            file_path = input_data["file_path"]
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size > self.max_file_size:
                    raise ToolValidationError(
                        f"File too large: {file_size} bytes", tool_name=self.NAME
                    )


class WebTool(BaseTool):
    """Base class for web-related tools."""

    CATEGORY = ToolCategory.WEB_TOOLS

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.user_agent = "Raptorflow-Agent/1.0"
        self.timeout = 30
        self.max_retries = 3
        self.rate_limit_delay = 1.0

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data for web tools."""
        if "url" not in input_data:
            raise ToolValidationError(
                "Missing required 'url' parameter", tool_name=self.NAME
            )

        # Validate URL format
        url = input_data["url"]
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ToolValidationError("Invalid URL format", tool_name=self.NAME)


class ContentTool(BaseTool):
    """Base class for content-related tools."""

    CATEGORY = ToolCategory.CONTENT_TOOLS

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.supported_languages = ["en"]
        self.max_content_length = 10000  # characters

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data for content tools."""
        if "content" not in input_data:
            raise ToolValidationError(
                "Missing required 'content' parameter", tool_name=self.NAME
            )

        # Check content length
        content = input_data["content"]
        if len(content) > self.max_content_length:
            raise ToolValidationError(
                f"Content too long: {len(content)} characters", tool_name=self.NAME
            )


class CommunicationTool(BaseTool):
    """Base class for communication tools."""

    CATEGORY = ToolCategory.COMMUNICATION

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.required_fields = []
        self.optional_fields = []

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data for communication tools."""
        # Check required fields
        for field in self.required_fields:
            if field not in input_data:
                raise ToolValidationError(
                    f"Missing required field: {field}", tool_name=self.NAME
                )


class FileTool(BaseTool):
    """Base class for file-related tools."""

    CATEGORY = ToolCategory.FILE_TOOLS

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.supported_formats = []
        self.max_file_size = 50 * 1024 * 1024  # 50MB

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data for file tools."""
        if "file_path" not in input_data and "file_data" not in input_data:
            raise ToolValidationError(
                "Missing 'file_path' or 'file_data' parameter", tool_name=self.NAME
            )

        # Check file size if file path provided
        if "file_path" in input_data:
            import os

            file_path = input_data["file_path"]
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                if file_size > self.max_file_size:
                    raise ToolValidationError(
                        f"File too large: {file_size} bytes", tool_name=self.NAME
                    )


class IntegrationTool(BaseTool):
    """Base class for integration tools."""

    CATEGORY = ToolCategory.INTEGRATION

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.api_base_url = ""
        self.api_key = ""
        self.api_version = "v1"

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data for integration tools."""
        # Check API configuration
        if not self.api_base_url:
            raise ToolValidationError("Missing API base URL", tool_name=self.NAME)

        if not self.api_key and self.api_key not in input_data:
            raise ToolValidationError("Missing API key", tool_name=self.NAME)


class UtilityTool(BaseTool):
    """Base class for utility tools."""

    CATEGORY = ToolCategory.UTILITIES

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.supported_operations = []

    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate input data for utility tools."""
        if "operation" not in input_data:
            raise ToolValidationError(
                "Missing required 'operation' parameter", tool_name=self.NAME
            )

        operation = input_data["operation"]
        if operation not in self.supported_operations:
            raise ToolValidationError(
                f"Unsupported operation: {operation}", tool_name=self.NAME
            )


# Export main components
__all__ = [
    # Base classes
    "BaseTool",
    "DataProcessingTool",
    "WebTool",
    "ContentTool",
    "CommunicationTool",
    "FileTool",
    "IntegrationTool",
    "UtilityTool",
    # Configuration and results
    "ToolConfig",
    "ToolResult",
    "ToolStatus",
    "ToolCategory",
    # Exceptions
    "ToolError",
    "ToolValidationError",
    "ToolExecutionError",
    "ToolTimeoutError",
    "ToolConfigError",
    # Monitoring and utilities
    "ToolPerformanceMonitor",
    "tool_performance_monitor",
    "tool_timeout",
    "tool_retry",
]
