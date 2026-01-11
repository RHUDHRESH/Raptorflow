"""
Vertex AI LLM integration for Raptorflow agents.
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

import vertexai
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_vertexai import ChatVertexAI
from pydantic import BaseModel

from .config import ModelTier, estimate_cost, get_config
from .exceptions import ConfigurationError, LLMError, ValidationError

logger = logging.getLogger(__name__)


class LLMUsage(BaseModel):
    """Token usage and cost tracking."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    model_tier: ModelTier
    latency_ms: int = 0


class VertexAILLM:
    """Vertex AI LLM wrapper with usage tracking."""

    def __init__(self, model_tier: ModelTier = ModelTier.FLASH_LITE):
        """Initialize Vertex AI LLM."""
        self.model_tier = model_tier
        self.model_name = model_tier.value

        try:
            # Initialize Vertex AI
            config = get_config()
            vertexai.init(project=config.GCP_PROJECT_ID, location=config.GCP_REGION)
        except Exception as e:
            raise LLMError(
                f"Failed to initialize Vertex AI: {e}",
                error_code=os.getenv("ERROR_CODE"),
                details={"model_tier": model_tier.value},
            )

        try:
            # Create LangChain ChatVertexAI instance
            self.llm = ChatVertexAI(
                model_name=self.model_name,
                temperature=0.7,
                max_output_tokens=config.MAX_TOKENS_PER_REQUEST,
                timeout=config.AGENT_TIMEOUT_SECONDS,
            )
        except Exception as e:
            raise LLMError(
                f"Failed to create ChatVertexAI instance: {e}",
                error_code=os.getenv("ERROR_CODE"),
                details={"model_tier": model_tier.value},
            )

        # Usage tracking
        self.usage_history: List[LLMUsage] = []
        self._current_usage: Optional[LLMUsage] = None

    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        """Generate text response."""
        start_time = time.time()

        # Build messages
        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        try:
            # Generate response
            response = await self.llm.ainvoke(messages)
            content = response.content

            # Track usage
            latency_ms = int((time.time() - start_time) * 1000)
            self._track_usage(response, latency_ms)

            return content

        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    async def generate_structured(
        self, prompt: str, output_schema: BaseModel, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured response following a schema."""
        start_time = time.time()

        # Build messages with schema instruction
        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        # Add schema instruction to prompt
        schema_instruction = f"""
Respond with valid JSON that matches this schema:
{output_schema.model_json_schema()}

Your response must be valid JSON only, no additional text.
"""
        messages.append(HumanMessage(content=prompt + schema_instruction))

        try:
            # Generate response
            response = await self.llm.ainvoke(messages)
            content = response.content.strip()

            # Parse JSON
            import json

            try:
                parsed = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end != 0:
                    parsed = json.loads(content[start:end])
                else:
                    raise ValueError("Could not parse JSON from LLM response")

            # Validate against schema
            validated = output_schema.model_validate(parsed)

            # Track usage
            latency_ms = int((time.time() - start_time) * 1000)
            self._track_usage(response, latency_ms)

            return validated.model_dump()

        except Exception as e:
            logger.error(f"Structured generation failed: {e}")
            raise

    def get_usage(self) -> List[LLMUsage]:
        """Get usage history."""
        return self.usage_history.copy()

    def get_total_cost(self) -> float:
        """Get total cost across all calls."""
        return sum(usage.cost_usd for usage in self.usage_history)

    def reset_usage(self):
        """Reset usage tracking."""
        self.usage_history.clear()

    def _track_usage(self, response: Any, start_time: float):
        """Track token usage and cost with validation."""
        try:
            # Extract usage from response
            usage_metadata = getattr(response, "usage_metadata", {})
            input_tokens = usage_metadata.get("prompt_token_count", 0)
            output_tokens = usage_metadata.get("candidates_token_count", 0)

            # Validate token counts
            if not isinstance(input_tokens, int) or input_tokens < 0:
                raise LLMError(
                    f"Invalid input token count: {input_tokens}",
                    error_code=os.getenv("ERROR_CODE"),
                    details={"type": "input", "value": input_tokens},
                )

            if not isinstance(output_tokens, int) or output_tokens < 0:
                raise LLMError(
                    f"Invalid output token count: {output_tokens}",
                    error_code=os.getenv("ERROR_CODE"),
                    details={"type": "output", "value": output_tokens},
                )

            # Check for reasonable limits
            max_tokens = config.MAX_TOKENS_PER_REQUEST
            total_tokens = input_tokens + output_tokens

            if total_tokens > max_tokens:
                raise LLMError(
                    f"Token count exceeds limit: {total_tokens} > {max_tokens}",
                    error_code=os.getenv("ERROR_CODE"),
                    details={"total": total_tokens, "limit": max_tokens},
                )

            # Calculate cost with validation
            cost = estimate_cost(input_tokens, output_tokens, self.model_tier)

            if cost < 0 or cost > 1.0:  # $1 max per request
                raise LLMError(
                    f"Invalid cost calculation: ${cost}",
                    error_code="INVALID_COST",
                    details={
                        "cost": cost,
                        "input": input_tokens,
                        "output": output_tokens,
                    },
                )

            # Create usage record
            usage = LLMUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost_usd=cost,
                model_tier=self.model_tier,
                latency_ms=int((time.time() - start_time) * 1000),
            )

            # Store usage
            self.usage_history.append(usage)
            self._current_usage = usage

            logger.info(f"LLM usage: {total_tokens} tokens, ${cost:.6f}")

        except LLMError:
            # Re-raise LLM errors
            raise
        except Exception as e:
            logger.error(f"Failed to track usage: {e}")
            # Create minimal usage record
            usage = LLMUsage(
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                model_tier=self.model_tier,
                latency_ms=int((time.time() - start_time) * 1000),
            )
            self.usage_history.append(usage)
            self._current_usage = usage

    def validate_usage_history(self) -> bool:
        """Validate that all usage records are consistent."""
        try:
            for i, usage in enumerate(self.usage_history):
                # Check token counts
                if usage.total_tokens != usage.input_tokens + usage.output_tokens:
                    raise LLMError(
                        f"Token count mismatch in usage record {i}",
                        error_code=os.getenv("ERROR_CODE"),
                        details={
                            "record": i,
                            "total": usage.total_tokens,
                            "input": usage.input_tokens,
                            "output": usage.output_tokens,
                        },
                    )

                # Check cost calculation
                expected_cost = estimate_cost(
                    usage.input_tokens, usage.output_tokens, usage.model_tier
                )
                if (
                    abs(usage.cost_usd - expected_cost) > 0.000001
                ):  # 1 microsecond tolerance
                    raise LLMError(
                        f"Cost calculation mismatch in usage record {i}",
                        error_code="COST_MISMATCH",
                        details={
                            "record": i,
                            "actual": usage.cost_usd,
                            "expected": expected_cost,
                        },
                    )

            return True
        except LLMError:
            raise
        except Exception as e:
            logger.error(f"Usage validation failed: {e}")
            return False


# Global LLM instances cache
_llm_cache: Dict[ModelTier, VertexAILLM] = {}


def get_llm(model_tier: ModelTier = ModelTier.FLASH_LITE) -> VertexAILLM:
    """Get or create cached LLM instance."""
    if model_tier not in _llm_cache:
        _llm_cache[model_tier] = VertexAILLM(model_tier)
    return _llm_cache[model_tier]


async def quick_generate(
    prompt: str,
    model_tier: ModelTier = ModelTier.FLASH_LITE,
    system_prompt: Optional[str] = None,
) -> str:
    """Quick generation helper."""
    llm = get_llm(model_tier)
    return await llm.generate(prompt, system_prompt)


async def quick_generate_structured(
    prompt: str,
    output_schema: BaseModel,
    model_tier: ModelTier = ModelTier.FLASH_LITE,
    system_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    """Quick structured generation helper."""
    llm = get_llm(model_tier)
    return await llm.generate_structured(prompt, output_schema, system_prompt)
