"""
OpenAI client with retry logic, rate limiting, and error handling
"""

import asyncio
from typing import Any, Dict, List, Optional
import openai
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from config.settings import settings
import structlog

logger = structlog.get_logger()


class OpenAIClient:
    """Async OpenAI client with automatic retries"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.default_model = settings.OPENAI_MODEL
        self.default_max_tokens = settings.OPENAI_MAX_TOKENS
        self.default_temperature = settings.OPENAI_TEMPERATURE
        
    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError)),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(settings.MAX_RETRIES),
        before_sleep=lambda retry_state: logger.warning(
            "Retrying OpenAI call",
            attempt=retry_state.attempt_number,
            wait=retry_state.next_action.sleep
        )
    )
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
        Create a chat completion with retries
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to settings)
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            response_format: Optional response format (e.g., {"type": "json_object"})
            tools: Optional function calling tools
            **kwargs: Additional parameters for OpenAI API
            
        Returns:
            Response dict with choices, usage, etc.
        """
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature or self.default_temperature,
                max_tokens=max_tokens or self.default_max_tokens,
                response_format=response_format,
                tools=tools,
                **kwargs
            )
            
            logger.debug(
                "OpenAI completion",
                model=response.model,
                tokens_used=response.usage.total_tokens if response.usage else 0
            )
            
            return response.model_dump()
            
        except openai.BadRequestError as e:
            logger.error("Invalid OpenAI request", error=str(e))
            raise ValueError(f"Invalid request to OpenAI: {str(e)}")
        except openai.AuthenticationError:
            logger.error("OpenAI authentication failed")
            raise ValueError("OpenAI API key is invalid")
        except openai.APIConnectionError:
            logger.error("Failed to connect to OpenAI")
            raise ConnectionError("Cannot reach OpenAI API")
        except Exception as e:
            logger.error("Unexpected OpenAI error", error=str(e))
            raise
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple text generation helper
        
        Args:
            prompt: User prompt
            system_prompt: Optional system message
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat_completion(messages, **kwargs)
        return response["choices"][0]["message"]["content"]
    
    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output
        
        Args:
            prompt: User prompt
            system_prompt: Optional system message
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON dict
        """
        import json
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.chat_completion(
            messages,
            response_format={"type": "json_object"},
            **kwargs
        )
        
        content = response["choices"][0]["message"]["content"]
        return json.loads(content)
    
    async def batch_completions(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        concurrency: int = 5,
        **kwargs
    ) -> List[str]:
        """
        Generate multiple completions concurrently
        
        Args:
            prompts: List of user prompts
            system_prompt: Optional system message for all
            concurrency: Max concurrent requests
            **kwargs: Additional parameters
            
        Returns:
            List of generated texts
        """
        semaphore = asyncio.Semaphore(concurrency)
        
        async def limited_generate(prompt: str) -> str:
            async with semaphore:
                return await self.generate_text(prompt, system_prompt, **kwargs)
        
        tasks = [limited_generate(prompt) for prompt in prompts]
        return await asyncio.gather(*tasks)
    
    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        **kwargs
    ):
        """
        Stream a chat completion (for real-time UI)
        
        Args:
            messages: List of message dicts
            model: Model to use
            **kwargs: Additional parameters
            
        Yields:
            Content chunks as they arrive
        """
        try:
            stream = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error("Streaming error", error=str(e))
            raise


# Global client instance
openai_client = OpenAIClient()

