"""
Deterministic Fallback Backend - Rule-based content generation when AI backends fail.

This backend provides sensible, template-based content generation as a last resort
when all AI backends are unavailable. It uses the BCM manifest to generate
contextually relevant content.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from backend.ai.backends.base import BaseAIBackend
from backend.ai.types import (
    BackendHealth,
    BackendType,
    GenerationRequest,
    GenerationResult,
)

logger = logging.getLogger(__name__)


class DeterministicFallbackBackend(BaseAIBackend):
    """
    Rule-based fallback content generator.

    Generates template-based content using patterns derived from the
    BCM manifest. This ensures the system always returns useful content
    even when AI backends are unavailable.

    Templates are content-type specific and include:
    - Social posts (linkedin, twitter)
    - Email/newsletter content
    - General marketing copy

    Example:
        backend = DeterministicFallbackBackend()
        result = await backend.generate_async(request)
    """

    backend_type = BackendType.DETERMINISTIC_FALLBACK

    def __init__(self):
        super().__init__(model_name="deterministic-fallback")

    async def initialize(self) -> None:
        self._initialized = True
        logger.info("Deterministic fallback backend initialized")

    async def generate_async(self, request: GenerationRequest) -> GenerationResult:
        metadata = request.metadata
        manifest = metadata.get("manifest", {})
        foundation = (
            manifest.get("foundation", {}) if isinstance(manifest, dict) else {}
        )

        company_name = self._extract_company_name(foundation) or "Your company"
        task = request.prompt[:200] if request.prompt else "Create content"
        content_type = metadata.get("content_type", "general")
        tone = metadata.get("tone", "professional")
        target = metadata.get("target_audience", "your audience")

        text = self._generate_content(
            content_type=content_type,
            company_name=company_name,
            task=task,
            tone=tone,
            target=target,
        )

        approx_tokens = max(60, min(220, len(text) // 4))

        return GenerationResult(
            status="success",
            text=text,
            input_tokens=0,
            output_tokens=approx_tokens,
            total_tokens=approx_tokens,
            cost_usd=0.0,
            generation_time_seconds=0.0,
            model="deterministic-fallback",
            model_type="rule-based",
            backend=BackendType.DETERMINISTIC_FALLBACK,
            fallback_reason="ai_unavailable",
        )

    def _extract_company_name(self, foundation: Dict[str, Any]) -> Optional[str]:
        if not isinstance(foundation, dict):
            return None
        return (
            foundation.get("company_name")
            or foundation.get("company")
            or foundation.get("name")
        )

    def _generate_content(
        self,
        content_type: str,
        company_name: str,
        task: str,
        tone: str,
        target: str,
    ) -> str:
        if content_type in {"social", "linkedin", "twitter"}:
            return self._generate_social(company_name, task, target)
        elif content_type in {"email", "newsletter"}:
            return self._generate_email(company_name, task, target)
        else:
            return self._generate_general(company_name, task, tone, target)

    def _generate_social(self, company_name: str, task: str, target: str) -> str:
        return "\n".join(
            [
                f"{company_name} update for {target}:",
                "",
                f"We are shipping a focused move: {task}.",
                "Here is the promise: faster execution with clearer outcomes.",
                "Proof point: our workflow is built around BCM + LangGraph orchestration.",
                'CTA: Reply "interested" and we will share the full rollout checklist.',
            ]
        )

    def _generate_email(self, company_name: str, task: str, target: str) -> str:
        return "\n".join(
            [
                f"Subject: {company_name} | Strategic update",
                "",
                f"Hi {target},",
                "",
                f"We're executing: {task}.",
                "This is designed to improve speed and consistency across campaigns and moves.",
                "If useful, reply to this email and we'll send the execution brief.",
            ]
        )

    def _generate_general(
        self,
        company_name: str,
        task: str,
        tone: str,
        target: str,
    ) -> str:
        return "\n".join(
            [
                f"{company_name} ({tone}):",
                f"- Task: {task}",
                f"- Audience: {target}",
                "- Core message: convert strategy into repeatable execution.",
                "- CTA: request the detailed plan and timeline.",
            ]
        )

    async def health_check(self) -> BackendHealth:
        return BackendHealth(
            status="healthy",
            backend=BackendType.DETERMINISTIC_FALLBACK,
            model="deterministic-fallback",
        )
