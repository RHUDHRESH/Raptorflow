"""
Vertex AI Client Configuration (Upgraded to google-genai)
Handles Gemini API connections via the latest unified SDK.
"""

import hashlib
import json
import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

try:
    from backend.redis.cache import CacheService
except ImportError:
    from redis.cache import CacheService

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class VertexAIConfig(BaseModel):
    """Configuration settings for GenAI"""

    project_id: str
    location: str
    model: str
    api_key: str
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 40


class VertexAIClient:
    """GenAI client wrapper using the latest unified google-genai SDK"""

    def __init__(self, config: Optional[VertexAIConfig] = None):
        self.config = config or self._load_config()
        if self.config.api_key:
            self.client = genai.Client(api_key=self.config.api_key)
            logger.info(f"GenAI Client initialized with model: {self.config.model}")
        else:
            self.client = None
            logger.error("Vertex AI API key missing; GenAI client disabled")

    def _load_config(self) -> VertexAIConfig:
        """Load configuration from environment variables"""
        api_key = os.getenv("VERTEX_AI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("NO API KEY FOUND in environment variables.")

        return VertexAIConfig(
            project_id=os.getenv("VERTEX_AI_PROJECT_ID", "raptorflow-481505"),
            location=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
            model=os.getenv("VERTEX_AI_MODEL", "gemini-2.0-flash-exp"),
            api_key=api_key or "",
            max_tokens=int(os.getenv("VERTEX_AI_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("VERTEX_AI_TEMPERATURE", "0.7")),
            top_p=float(os.getenv("VERTEX_AI_TOP_P", "0.8")),
            top_k=int(os.getenv("VERTEX_AI_TOP_K", "40")),
        )

    def _sanitize_input(self, text: str) -> str:
        """Sanitize input to prevent prompt injection."""
        if not text:
            return ""
        sanitized = text.replace("---", "-").replace("===", "=").replace("###", "#")
        forbidden = [
            "ignore all previous instructions",
            "ignore previous instructions",
            "you are now an admin",
            "system override",
        ]
        for phrase in forbidden:
            if phrase in sanitized.lower():
                sanitized = sanitized.lower().replace(phrase, "[PROTECTED_SEQUENCE]")
        return sanitized

    async def generate_text(
        self, prompt: str, model: Optional[str] = None
    ) -> Optional[str]:
        """Generate text using the unified GenAI SDK."""
        try:
            if not self.client:
                logger.error("GenAI client not initialized (missing API key)")
                return None

            sanitized_prompt = self._sanitize_input(prompt)
            model_to_use = model or self.config.model

            # Check Cache
            cache_service = None
            try:
                cache_service = CacheService()
            except Exception as e:
                logger.warning(f"CacheService unavailable, skipping cache: {e}")

            cache_key = f"ai_res:{hashlib.md5(sanitized_prompt.encode()).hexdigest()}"

            # We use a global/system workspace ID for LLM results if not provided
            # or just bypass workspace isolation for pure prompt-based cache
            if cache_service:
                cached_val = await cache_service.redis.get_json(cache_key)
                if cached_val:
                    logger.info(f"AI Cache Hit: {cache_key}")
                    return cached_val

            # Using the new SDK's generate_content
            response = self.client.models.generate_content(
                model=model_to_use,
                contents=sanitized_prompt,
                config={
                    "max_output_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "top_k": self.config.top_k,
                },
            )

            if response and response.text:
                result = response.text
                # Set Cache (TTL: 24h)
                if cache_service:
                    await cache_service.redis.set_json(cache_key, result, ex=86400)
                return result
            return None
        except Exception as e:
            logger.error(f"Inference failure: {e}")
            return None

    async def generate_text_with_context(
        self, prompt: str, context: str, model: Optional[str] = None
    ) -> Optional[str]:
        """Generate text with context."""
        try:
            full_prompt = f"CONTEXT:\n{context}\n\nUSER REQUEST: {prompt}"
            return await self.generate_text(full_prompt, model)
        except Exception as e:
            logger.error(f"Failed to generate text with context: {e}")
            return None

    async def analyze_text(
        self, text: str, analysis_type: str = "sentiment"
    ) -> Optional[Dict[str, Any]]:
        """Analyze text and return structured JSON."""
        try:
            prompt = f"Analyze for {analysis_type}:\n\n{text}\n\nReturn JSON only."
            response = await self.generate_text(prompt)
            if response:
                cleaned = response.strip()
                if "```json" in cleaned:
                    cleaned = cleaned.split("```json")[1].split("```")[0]
                elif "```" in cleaned:
                    cleaned = cleaned.split("```")[1].split("```")[0]
                return json.loads(cleaned)
            return None
        except Exception as e:
            logger.error(f"Analysis failure: {e}")
            return None

    async def health_check(self) -> Dict[str, Any]:
        """Check connection health."""
        response = await self.generate_text("OK")
        return {"status": "healthy" if response else "unhealthy"}


# Global instance
vertex_ai_client = VertexAIClient()


def get_vertex_ai_client() -> VertexAIClient:
    """Get the upgraded client instance."""
    return vertex_ai_client
