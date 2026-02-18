"""
Vertex AI Service shim for backward compatibility.

This module provides the legacy interface for vertex_ai_service,
bridging to the new modular AI backend system.
"""

from typing import Any, Dict, Optional


class VertexAIService:
    """Legacy Vertex AI service interface for backward compatibility."""

    def __init__(self):
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the service."""
        self._initialized = True

    @property
    def initialized(self) -> bool:
        return self._initialized

    async def generate_with_system(
        self,
        prompt: str,
        workspace_id: str,
        user_id: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate text with system prompt using the AI backend."""
        from backend.ai import AIClient

        client = AIClient()
        result = await client.generate(
            prompt=prompt,
            workspace_id=workspace_id,
            user_id=user_id,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return {
            "status": "success" if result.success else "error",
            "text": result.text,
            "total_tokens": result.total_tokens or 0,
            "cost_usd": result.cost_usd or 0.0,
            "model": result.model or "unknown",
            "model_type": "generative",
            "generation_time_seconds": result.generation_time_seconds or 0.0,
        }

    async def generate_text(
        self,
        prompt: str,
        workspace_id: str,
        user_id: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate text without system prompt."""
        return await self.generate_with_system(
            prompt=prompt,
            workspace_id=workspace_id,
            user_id=user_id,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

    async def check_health(self) -> Dict[str, str]:
        """Check service health."""
        from backend.ai import BackendHealth

        return {"status": "healthy"}


vertex_ai_service = VertexAIService()

__all__ = ["vertex_ai_service", "VertexAIService"]
