"""
LLM Infrastructure Layer
Handles Vertex AI / Gemini API connections
"""

import hashlib
import json
import logging
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

load_dotenv()

logger = logging.getLogger(__name__)


class LLMConfig(BaseModel):
    """Configuration settings for GenAI"""
    project_id: str
    location: str
    model: str
    api_key: str
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.8
    top_k: int = 40


class LLMClient:
    """GenAI client wrapper using the unified google-genai SDK"""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or self._load_config()
        self.client = None
        # Lazy init: do not create SDK client at import time

    def _ensure_client(self) -> None:
        if self.client is not None:
            return

        if not self.config.api_key:
            raise ValueError(
                "LLM not configured. Set VERTEX_AI_API_KEY or GOOGLE_API_KEY."
            )
        self.client = genai.Client(api_key=self.config.api_key)
        logger.info(f"LLM Client initialized with model: {self.config.model}")

    def _load_config(self) -> LLMConfig:
        """Load configuration from environment variables"""
        api_key = os.getenv("VERTEX_AI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("NO API KEY FOUND in environment variables.")

        return LLMConfig(
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

    async def generate(self, prompt: str, model: Optional[str] = None) -> Optional[str]:
        """Generate text using the unified GenAI SDK."""
        try:
            self._ensure_client()
            sanitized_prompt = self._sanitize_input(prompt)
            model_to_use = model or self.config.model

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
                return response.text
            return None
        except Exception as e:
            logger.error(f"Inference failure: {e}")
            return None

    async def generate_with_context(self, prompt: str, context: str, model: Optional[str] = None) -> Optional[str]:
        """Generate text with context."""
        try:
            full_prompt = f"CONTEXT:\n{context}\n\nUSER REQUEST: {prompt}"
            return await self.generate(full_prompt, model)
        except Exception as e:
            logger.error(f"Failed to generate text with context: {e}")
            return None

    async def analyze(self, text: str, analysis_type: str = "sentiment") -> Optional[Dict[str, Any]]:
        """Analyze text and return structured JSON."""
        try:
            prompt = f"Analyze for {analysis_type}:\n\n{text}\n\nReturn JSON only."
            response = await self.generate(prompt)
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
        response = await self.generate("OK")
        return {"status": "healthy" if response else "unhealthy"}


_llm_client: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    """Get the LLM client instance."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
