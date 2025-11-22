"""
Abstract base classes for all agents and supervisors.
Provides a lightweight interface and shared logging helpers.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from backend.utils.correlation import get_correlation_id


class BaseAgent(ABC):
    """Base contract for all agents."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task asynchronously."""
        raise NotImplementedError

    def log(self, message: str, **kwargs: Any) -> None:
        """Structured log with correlation id baked in."""
        correlation_id = get_correlation_id()
        self.logger.info(message, extra={"correlation_id": correlation_id, **kwargs})


class BaseSupervisor(BaseAgent):
    """Base class for all supervisor agents."""

    def __init__(self, name: str):
        super().__init__(name)
        self.sub_agents: Dict[str, BaseAgent] = {}

    @abstractmethod
    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate sub-agents to achieve a goal."""
        raise NotImplementedError
