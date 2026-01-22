"""
Abstract interfaces for cognitive modules
Enables loose coupling and testability
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class IPerceptionModule(ABC):
    """Interface for perception module"""

    @abstractmethod
    async def perceive(
        self,
        request: str,
        user_context: Dict[str, Any],
        recent_messages: Optional[List[Dict[str, str]]] = None,
    ) -> Any:
        """Perceive user request and extract entities/intent"""
        pass


class IPlanningModule(ABC):
    """Interface for planning module"""

    @abstractmethod
    async def create_plan(self, goal: str, context: Any) -> Any:
        """Create execution plan for goal"""
        pass


class IReflectionModule(ABC):
    """Interface for reflection module"""

    @abstractmethod
    async def evaluate(
        self, request: str, output: Any, user_context: Dict[str, Any]
    ) -> Any:
        """Evaluate output quality"""
        pass


class IHumanLoopModule(ABC):
    """Interface for human-in-the-loop module"""

    @abstractmethod
    async def evaluate_approval(
        self,
        content: Any,
        execution_plan: Any,
        quality_score: Any,
        user_context: Dict[str, Any],
    ) -> Any:
        """Evaluate if human approval is needed"""
        pass


class IStorageBackend(ABC):
    """Interface for storage backend"""

    @abstractmethod
    async def save_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Save session data"""
        pass

    @abstractmethod
    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session data"""
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> None:
        """Delete session data"""
        pass


class ICacheBackend(ABC):
    """Interface for cache backend"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set cached value"""
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete cached value"""
        pass


class ILLMClient(ABC):
    """Interface for LLM client"""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from LLM"""
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        pass


class IMetricsCollector(ABC):
    """Interface for metrics collection"""

    @abstractmethod
    async def record_request(
        self,
        request_id: str,
        phase: str,
        tokens_used: int,
        cost_usd: float,
        processing_time_ms: int,
    ) -> None:
        """Record request metrics"""
        pass

    @abstractmethod
    async def record_error(self, request_id: str, error: str, phase: str) -> None:
        """Record error metrics"""
        pass
