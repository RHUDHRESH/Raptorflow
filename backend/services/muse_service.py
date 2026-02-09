"""
Muse Service: AI content generation orchestration.

Wraps Vertex AI, BCM, and prompt compilation into a unified service.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from backend.services.base_service import BaseService
from backend.services.registry import registry
from backend.services.exceptions import ServiceError, ServiceUnavailableError

logger = logging.getLogger(__name__)

class MuseService(BaseService):
    def __init__(self):
        super().__init__("muse_service")

    async def check_health(self) -> Dict[str, Any]:
        """Check if Muse dependencies are available."""
        try:
            from backend.services.vertex_ai_service import vertex_ai_service
            if not vertex_ai_service:
                return {"status": "disabled", "detail": "Vertex AI not configured"}
            
            vertex_health = await vertex_ai_service.check_health()
            return {"status": vertex_health.get("status", "unknown"), "engine": "vertex_ai"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def generate(
        self,
        workspace_id: str,
        task: str,
        content_type: str = "general",
        tone: str = "professional",
        target_audience: str = "general",
        context: Optional[Dict[str, Any]] = None,
        max_tokens: int = 800,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Generate content using BCM-aware prompts and Vertex AI."""
        
        async def _execute():
            from backend.services.vertex_ai_service import vertex_ai_service
            from backend.services import bcm_service, bcm_memory
            from backend.services.prompt_compiler import (
                get_or_compile_system_prompt,
                build_user_prompt,
            )
            from backend.services import bcm_generation_logger
            from backend.services.bcm_reflector import should_auto_reflect, reflect

            if not vertex_ai_service:
                raise ServiceUnavailableError("Vertex AI unavailable. Configure VERTEX_AI_PROJECT_ID/credentials.")

            # Fetch BCM manifest for this workspace (cache-first, fast path)
            manifest = bcm_service.get_manifest_fast(workspace_id)

            if manifest:
                # Fetch relevant memories so learned preferences influence generation
                memories = None
                try:
                    memories = bcm_memory.get_relevant_memories(workspace_id, limit=5) or None
                except Exception:
                    pass  # memories are best-effort, never block generation

                # Structured prompt path: system instruction + user prompt
                system_prompt = get_or_compile_system_prompt(
                    workspace_id=workspace_id,
                    manifest=manifest,
                    content_type=content_type,
                    target_icp=target_audience if target_audience != "general" else None,
                    memories=memories,
                )
                user_prompt = build_user_prompt(
                    task=task,
                    content_type=content_type,
                    tone=tone,
                    target_audience=target_audience,
                )

                result = await vertex_ai_service.generate_with_system(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    workspace_id=workspace_id,
                    user_id="reconstruction",
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                prompt_for_log = f"[system]{system_prompt[:500]}[/system]\n{user_prompt}"
            else:
                # Legacy fallback: flat prompt (no BCM available)
                prompt = "\n".join(
                    [
                        f"Task: {task}",
                        f"Type: {content_type}",
                        f"Tone: {tone}",
                        f"Target audience: {target_audience}",
                        f"Context: {json.dumps(context or {})}",
                    ]
                )
                result = await vertex_ai_service.generate_text(
                    prompt=prompt,
                    workspace_id=workspace_id,
                    user_id="reconstruction",
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
                prompt_for_log = prompt

            if result.get("status") != "success":
                error = result.get("error") or "Muse generation failed"
                raise ServiceError(error)

            # Log generation for learning
            gen_text = result.get("text") or ""
            bcm_version = manifest.get("version", 0) if manifest else 0

            gen_log = bcm_generation_logger.log_generation(
                workspace_id=workspace_id,
                content_type=content_type,
                prompt_used=prompt_for_log,
                output=gen_text,
                bcm_version=bcm_version,
                tokens_used=int(result.get("total_tokens") or 0),
                cost_usd=float(result.get("cost_usd") or 0.0),
            )

            # Auto-reflection: fire-and-forget if threshold reached
            try:
                if should_auto_reflect(workspace_id):
                    asyncio.create_task(reflect(workspace_id))
            except Exception:
                pass  # never block generation for reflection

            return {
                "success": True,
                "content": gen_text,
                "tokens_used": int(result.get("total_tokens") or 0),
                "cost_usd": float(result.get("cost_usd") or 0.0),
                "metadata": {
                    "model": result.get("model"),
                    "model_type": result.get("model_type"),
                    "generation_time_seconds": result.get("generation_time_seconds"),
                    "structured_prompt": bool(manifest),
                    "generation_id": gen_log.get("id", "") if gen_log else "",
                },
            }

        return await self.execute_with_retry(_execute)

# Global instance
muse_service = MuseService()
registry.register(muse_service)
