"""
Infrastructure - Google Gemini AI Provider Adapter.

Implementation of AIProviderPort using Google Gemini API.
"""

import time
from typing import AsyncIterator, Optional
from dataclasses import dataclass

from raptorflow.domain.ai.models import (
    GenerationRequest,
    GenerationResult,
    GenerationConfig,
)
from raptorflow.domain.ai.repositories import (
    AIProviderPort as DomainAIProviderPort,
)


@dataclass
class GeminiConfig:
    """Configuration for Gemini API."""

    api_key: str
    project_id: Optional[str] = None
    location: str = "us-central1"
    model: str = "gemini-2.0-flash"
    timeout_seconds: int = 60


class GeminiAIAdapter(DomainAIProviderPort):
    """
    Google Gemini implementation of AI provider port.

    This adapter handles:
    - Authentication with Google Cloud
    - Request formatting for Gemini API
    - Response parsing
    - Error handling
    - Token counting
    """

    def __init__(self, config: GeminiConfig):
        self._config = config
        self._client = None  # Lazy initialization

    async def _get_client(self):
        """Lazy load the Gemini client."""
        if self._client is None:
            try:
                import google.genai as genai

                genai.configure(api_key=self._config.api_key)
                self._client = genai
            except ImportError:
                raise RuntimeError(
                    "google-genai package not installed. "
                    "Install with: pip install google-genai"
                )
        return self._client

    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """
        Execute generation request using Gemini API.

        Args:
            request: The generation request

        Returns:
            GenerationResult with generated content
        """
        client = await self._get_client()

        start_time = time.perf_counter()

        try:
            # Build the prompt
            contents = []
            if request.system_prompt:
                contents.append(request.system_prompt)
            contents.append(request.prompt)

            # Prepare generation config
            generation_config = {
                "temperature": request.config.temperature,
                "top_p": request.config.top_p,
                "top_k": request.config.top_k,
                "max_output_tokens": request.budget.max_output,
            }

            if request.config.stop_sequences:
                generation_config["stop_sequences"] = request.config.stop_sequences

            # Call Gemini API
            model = client.GenerativeModel(self._config.model)
            response = await model.generate_content_async(
                contents,
                generation_config=generation_config,
            )

            # Calculate latency
            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Parse response
            text = ""
            finish_reason = "stop"
            usage_metadata = None

            if response.parts:
                text = "".join([part.text for part in response.parts])

            if response.usage_metadata:
                usage_metadata = response.usage_metadata

            # Extract token counts
            input_tokens = 0
            output_tokens = 0
            if usage_metadata:
                input_tokens = usage_metadata.prompt_token_count or 0
                output_tokens = usage_metadata.candidates_token_count or 0

            # Calculate cost (simplified - would use actual pricing)
            cost_usd = self._calculate_cost(
                input_tokens,
                output_tokens,
                self._config.model,
            )

            return GenerationResult(
                request_id=request.id,
                text=text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=self._config.model,
                provider="google",
                cost_usd=cost_usd,
                latency_ms=latency_ms,
                finish_reason=finish_reason,
            )

        except Exception as e:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            return GenerationResult(
                request_id=request.id,
                text="",
                input_tokens=0,
                output_tokens=0,
                model=self._config.model,
                provider="google",
                cost_usd=0,
                latency_ms=latency_ms,
                finish_reason="error",
                error_message=str(e),
            )

    async def stream(
        self,
        request: GenerationRequest,
    ) -> AsyncIterator[str]:
        """
        Stream generation tokens from Gemini API.

        Args:
            request: The generation request

        Yields:
            Generated text chunks
        """
        client = await self._get_client()

        try:
            # Build the prompt
            contents = []
            if request.system_prompt:
                contents.append(request.system_prompt)
            contents.append(request.prompt)

            # Prepare generation config
            generation_config = {
                "temperature": request.config.temperature,
                "top_p": request.config.top_p,
                "top_k": request.config.top_k,
                "max_output_tokens": request.budget.max_output,
            }

            # Call Gemini API with streaming
            model = client.GenerativeModel(self._config.model)
            response = await model.generate_content_async(
                contents,
                generation_config=generation_config,
                stream=True,
            )

            # Yield chunks as they arrive
            async for chunk in response:
                if chunk.parts:
                    yield chunk.parts[0].text

        except Exception as e:
            yield f"[Error: {str(e)}]"

    async def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for given model."""
        client = await self._get_client()

        try:
            model_obj = client.GenerativeModel(model)
            result = await model_obj.count_tokens_async(text)
            return result.total_tokens
        except Exception:
            # Fallback estimation
            return len(text) // 4

    async def validate_connection(self) -> bool:
        """Validate provider connection."""
        try:
            client = await self._get_client()
            # Try a simple request to validate
            model = client.GenerativeModel(self._config.model)
            await model.generate_content_async("test")
            return True
        except Exception:
            return False

    def _calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str,
    ) -> float:
        """Calculate cost based on token usage."""
        # Simplified pricing - would use actual pricing tables
        # Gemini 2.0 Flash pricing (example)
        pricing = {
            "gemini-2.0-flash": (0.0, 0.0),  # Free tier
            "gemini-2.0-flash-lite": (0.0, 0.0),
            "gemini-2.0-pro": (0.0, 0.0),
        }

        input_rate, output_rate = pricing.get(model, (0.0, 0.0))

        input_cost = (input_tokens / 1000) * input_rate
        output_cost = (output_tokens / 1000) * output_rate

        return input_cost + output_cost
