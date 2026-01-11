"""
Base router class for Raptorflow routing system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseRouter(ABC):
    """Abstract base class for all routers."""

    def __init__(self):
        """Initialize the router."""
        self.name = self.__class__.__name__

    @abstractmethod
    async def route(self, query: str, **kwargs) -> Any:
        """Route a query to the appropriate destination."""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get router information."""
        return {"name": self.name, "type": self.__class__.__name__}
