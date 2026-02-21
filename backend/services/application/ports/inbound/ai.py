"""
Application Ports - Inbound (Input Ports/Use Case Interfaces).

These interfaces define the contracts for incoming requests to the application.
They represent the use cases that can be invoked by the outside world (API, CLI, etc.).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncIterator
from uuid import UUID


@dataclass
class GenerateContentCommand:
    """Command for content generation."""

    workspace_id: str
    user_id: str
    prompt: str
    content_type: str = "general"
    tone: str = "professional"
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000


@dataclass
class GenerateContentResult:
    """Result of content generation."""

    success: bool
    content: str = ""
    request_id: Optional[UUID] = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    error_message: str = ""


@dataclass
class StreamContentCommand:
    """Command for streaming content generation."""

    workspace_id: str
    user_id: str
    prompt: str
    model: Optional[str] = None
    temperature: float = 0.7


@dataclass
class GetGenerationHistoryQuery:
    """Query for generation history."""

    workspace_id: str
    limit: int = 100
    offset: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class GetModelsQuery:
    """Query for available models."""

    tier: Optional[str] = None
    provider: Optional[str] = None


# Inbound Port Interfaces


class GenerateContentUseCase(ABC):
    """Inbound port for content generation use case."""

    @abstractmethod
    async def execute(self, command: GenerateContentCommand) -> GenerateContentResult:
        """Execute content generation."""
        pass


class StreamContentUseCase(ABC):
    """Inbound port for streaming content generation use case."""

    @abstractmethod
    async def execute(self, command: StreamContentCommand) -> AsyncIterator[str]:
        """Execute streaming content generation."""
        pass


class GetGenerationHistoryUseCase(ABC):
    """Inbound port for retrieving generation history."""

    @abstractmethod
    async def execute(self, query: GetGenerationHistoryQuery) -> List[Dict[str, Any]]:
        """Execute generation history query."""
        pass


class GetAvailableModelsUseCase(ABC):
    """Inbound port for retrieving available models."""

    @abstractmethod
    async def execute(self, query: GetModelsQuery) -> List[Dict[str, Any]]:
        """Execute get available models query."""
        pass


class GetCostAnalyticsUseCase(ABC):
    """Inbound port for cost analytics."""

    @abstractmethod
    async def execute(
        self, workspace_id: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Execute cost analytics query."""
        pass
