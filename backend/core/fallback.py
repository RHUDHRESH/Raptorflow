import logging
from typing import Any, Callable, Awaitable, Optional

logger = logging.getLogger("raptorflow.core.fallback")

class FallbackManager:
    """
    SOTA Deterministic Fallback Manager.
    Ensures agentic spine stability by providing heuristic fallbacks when LLMs fail.
    Implements Osipov's reliability patterns for industrial AI systems.
    """

    async def execute_with_fallback(
        self, 
        func: Callable[[], Awaitable[Any]], 
        fallback_value: Any,
        context: Optional[str] = None
    ) -> Any:
        """Executes an async function with a deterministic fallback on failure."""
        try:
            return await func()
        except Exception as e:
            msg = f"LLM Failure detected{f' in {context}' if context else ''}: {e}. Triggering deterministic fallback."
            logger.warning(msg)
            return fallback_value

    def get_mundane_fallback(self, task_type: str) -> dict:
        """Returns a predefined heuristic response for common task types."""
        fallbacks = {
            "planning": {"thought": "System under high load. Defaulting to standard 4-week growth plan.", "status": "degraded"},
            "research": {"thought": "Research API unavailable. Using cached domain knowledge.", "status": "degraded"},
            "refinement": {"thought": "Refinement failed. Proceeding with raw agent output.", "status": "degraded"}
        }
        return fallbacks.get(task_type, {"thought": "Fallback triggered.", "status": "degraded"})
