"""
AI Client - High-level interface for AI generation.

Provides a simple, unified interface for content generation with:
- Automatic backend selection and failover
- Profile resolution
- Orchestration strategy selection
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from backend.ai.backends import BackendRegistry, create_default_backends
from backend.ai.orchestration import get_strategy
from backend.ai.profiles import AIProfile
from backend.ai.types import (
    BackendHealth,
    ExecutionMode,
    GenerationRequest,
    GenerationResult,
    IntensityLevel,
    ReasoningDepth,
)

logger = logging.getLogger(__name__)


class AIClient:
    """
    High-level AI client for content generation.

    This is the primary entry point for AI generation in Raptorflow.
    It handles backend selection, failover, profile resolution, and
    orchestration strategy execution.

    Example:
        client = AIClient()
        await client.initialize()

        result = await client.generate(
            prompt="Write a marketing email",
            workspace_id="ws_123",
        )

        print(result.text)

    Attributes:
        registry: Backend registry managing available backends
        initialized: Whether the client has been initialized
    """

    def __init__(
        self,
        registry: Optional[BackendRegistry] = None,
        default_intensity: IntensityLevel = IntensityLevel.MEDIUM,
        default_execution_mode: ExecutionMode = ExecutionMode.SINGLE,
    ):
        self.registry = registry or create_default_backends()
        self.default_intensity = default_intensity
        self.default_execution_mode = default_execution_mode
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all backends."""
        if self._initialized:
            return
        await self.registry.initialize_all()
        self._initialized = True
        logger.info("AI client initialized")

    async def generate(
        self,
        prompt: str,
        workspace_id: str,
        user_id: str = "system",
        *,
        system_prompt: Optional[str] = None,
        max_tokens: int = 800,
        temperature: float = 0.7,
        intensity: Optional[IntensityLevel] = None,
        reasoning_depth: Optional[ReasoningDepth] = None,
        execution_mode: Optional[ExecutionMode] = None,
        content_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GenerationResult:
        """
        Generate content with automatic backend selection and failover.

        Args:
            prompt: The user prompt for generation
            workspace_id: Workspace identifier for tracking
            user_id: User identifier for tracking
            system_prompt: Optional system prompt for persona
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature (0.0-1.0)
            intensity: Resource intensity level
            reasoning_depth: Depth of reasoning
            execution_mode: Single, Council, or Swarm
            content_type: Type of content (email, social, blog, etc.)
            metadata: Additional context (manifest, memories, etc.)

        Returns:
            GenerationResult with generated text and metadata
        """
        if not self._initialized:
            await self.initialize()

        intensity = intensity or self.default_intensity
        execution_mode = execution_mode or self.default_execution_mode

        profile = AIProfile.resolve(
            requested_max_tokens=max_tokens,
            requested_temperature=temperature,
            intensity=intensity,
            reasoning_depth=reasoning_depth,
            execution_mode=execution_mode,
        )

        request = GenerationRequest(
            prompt=prompt,
            workspace_id=workspace_id,
            user_id=user_id,
            max_tokens=profile.max_tokens,
            temperature=profile.temperature,
            system_prompt=system_prompt,
            content_type=content_type,
            execution_mode=profile.execution_mode,
            intensity=profile.intensity,
            reasoning_depth=profile.reasoning_depth,
            metadata={
                **(metadata or {}),
                "profile": profile.to_dict(),
            },
        )

        strategy = get_strategy(profile.execution_mode)

        backend_chain = self.registry.get_backend_chain()
        last_result: Optional[GenerationResult] = None

        for backend in backend_chain:
            if not backend.initialized:
                continue

            try:
                result = await strategy.execute(
                    backend=backend,
                    request=request,
                    ensemble_size=profile.ensemble_size,
                )

                if result.success:
                    result.metadata["profile"] = profile.to_dict()
                    return result

                last_result = result
                logger.warning(
                    "Backend %s failed, trying next: %s",
                    backend.backend_type.value,
                    result.error,
                )
            except Exception as exc:
                logger.warning(
                    "Backend %s raised exception: %s", backend.backend_type.value, exc
                )
                last_result = GenerationResult(
                    status="error",
                    error=str(exc),
                    fallback_reason="backend_exception",
                )

        if last_result:
            return last_result

        return GenerationResult(
            status="error",
            error="No backends available",
            fallback_reason="no_backends",
        )

    async def health_check(self) -> Dict[str, BackendHealth]:
        """Check health of all backends."""
        if not self._initialized:
            await self.initialize()
        return await self.registry.health_check_all()

    async def generate_with_manifest(
        self,
        prompt: str,
        workspace_id: str,
        manifest: Dict[str, Any],
        memories: Optional[list] = None,
        **kwargs,
    ) -> GenerationResult:
        """
        Generate content with BCM manifest context.

        This method compiles system prompts from the BCM manifest
        and includes learned memories for personalization.

        Args:
            prompt: User prompt
            workspace_id: Workspace identifier
            manifest: BCM manifest with identity, prompt_kit, guardrails
            memories: List of learned preferences/insights
            **kwargs: Additional generation parameters

        Returns:
            GenerationResult with contextually enriched output
        """
        from backend.ai.prompts import compile_system_prompt, build_user_prompt

        system_prompt = compile_system_prompt(
            manifest=manifest,
            content_type=kwargs.get("content_type", "general"),
            target_icp=kwargs.get("target_icp"),
            memories=memories,
        )

        metadata = {
            "manifest": manifest,
            "memories": memories,
            "task": prompt,
            "tone": kwargs.get("tone", "professional"),
            "target_audience": kwargs.get("target_audience", "general"),
            "content_type": kwargs.get("content_type", "general"),
        }

        return await self.generate(
            prompt=prompt,
            workspace_id=workspace_id,
            system_prompt=system_prompt,
            metadata=metadata,
            **{k: v for k, v in kwargs.items() if k not in metadata},
        )


_client: Optional[AIClient] = None


def get_client() -> AIClient:
    """Get the global AI client instance."""
    global _client
    if _client is None:
        _client = AIClient()
    return _client


async def initialize_client() -> AIClient:
    """Initialize and return the global AI client."""
    client = get_client()
    await client.initialize()
    return client


__all__ = [
    "AIClient",
    "get_client",
    "initialize_client",
]
