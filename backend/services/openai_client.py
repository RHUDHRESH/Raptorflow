"""
OpenAI client wrapper - DEPRECATED

This module is kept for backward compatibility but redirects to Vertex AI Client.
It mimics the OpenAI client interface but uses Vertex AI under the hood.
"""

import asyncio
from typing import Any, Dict, List, Optional
import structlog
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from backend.services.vertex_ai_client import vertex_ai_client
from backend.config.settings import settings

logger = structlog.get_logger(__name__)


class OpenAIClient:
    """
    Wrapper class that mimics OpenAIClient but routes to Vertex AI.
    DEPRECATED: Use vertex_ai_client directly in new code.
    """
    
    def __init__(self):
        self.client = None # No actual OpenAI client
        self.default_model = "gemini-1.5-pro-002" # Map to Vertex equivalent
        
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Redirect chat completion to Vertex AI
        """
        logger.warning("Using deprecated OpenAIClient.chat_completion - redirecting to Vertex AI")
        
        try:
            # Determine model type based on request or default
            model_type = "fast"
            if model and ("gpt-4" in model or "pro" in model):
                model_type = "reasoning"
            
            # Call Vertex AI
            content = await vertex_ai_client.chat_completion(
                messages=messages,
                model_type=model_type,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                **kwargs
            )
            
            # Construct OpenAI-like response structure
            return {
                "choices": [
                    {
                        "message": {
                            "content": content,
                            "role": "assistant"
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "total_tokens": 0, # Placeholder
                    "prompt_tokens": 0,
                    "completion_tokens": 0
                },
                "model": model or self.default_model
            }
            
        except Exception as e:
            logger.error("Redirect to Vertex AI failed", error=str(e))
            raise ValueError(f"Vertex AI redirection failed: {str(e)}")
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """Redirect text generation to Vertex AI"""
        logger.warning("Using deprecated OpenAIClient.generate_text - redirecting to Vertex AI")
        return await vertex_ai_client.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            **kwargs
        )
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Redirect JSON generation to Vertex AI"""
        logger.warning("Using deprecated OpenAIClient.generate_json - redirecting to Vertex AI")
        return await vertex_ai_client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            **kwargs
        )
    
    async def batch_completions(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        concurrency: int = 5,
        **kwargs
    ) -> List[str]:
        """Redirect batch completions to Vertex AI"""
        logger.warning("Using deprecated OpenAIClient.batch_completions - redirecting to Vertex AI")
        return await vertex_ai_client.batch_completions(
            prompts=prompts,
            system_prompt=system_prompt,
            concurrency=concurrency,
            **kwargs
        )
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ):
        """Redirect stream completion to Vertex AI"""
        logger.warning("Using deprecated OpenAIClient.stream_completion - redirecting to Vertex AI")
        async for chunk in vertex_ai_client.stream_completion(messages, **kwargs):
            yield chunk


# Global client instance
openai_client = OpenAIClient()
