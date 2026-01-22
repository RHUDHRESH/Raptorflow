"""
Enhanced Vertex AI LLM integration for Raptorflow agents with improved initialization.
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

import vertexai
from pydantic import BaseModel

# Initialize logger
logger = logging.getLogger(__name__)

# Updated langchain imports for compatibility
try:
    from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
    from langchain_google_vertexai import ChatVertexAI
except ImportError:
    # Fallback if langchain_google_vertexai is not available
    logger.warning("langchain_google_vertexai not available, using fallback")
    ChatVertexAI = None
    AIMessage = None
    BaseMessage = None
    HumanMessage = None
    SystemMessage = None

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
    """Enhanced Vertex AI LLM wrapper with robust initialization and usage tracking."""

    def __init__(self, model_tier: ModelTier = ModelTier.FLASH_LITE):
        """Initialize Vertex AI LLM with enhanced error handling."""
        self.model_tier = model_tier
        self.model_name = model_tier.value
        self._initialized = False
        self._init_error = None

        try:
            # Get configuration with fallback handling
            config = get_config()
            
            # Enhanced project ID resolution
            project_id = getattr(config, 'GCP_PROJECT_ID', None) or os.getenv("GOOGLE_PROJECT_ID")
            if not project_id:
                raise LLMError(
                    "GOOGLE_PROJECT_ID not found in config or environment variables",
                    error_code="MISSING_PROJECT_ID",
                    details={"model_tier": model_tier.value},
                )
            
            # Enhanced region resolution
            location = getattr(config, 'GCP_REGION', None) or os.getenv("GOOGLE_REGION", "us-central1")
            
            # Initialize Vertex AI with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    vertexai.init(project=project_id, location=location)
                    logger.info(f"Vertex AI initialized successfully (attempt {attempt + 1})")
                    break
                except Exception as e:
                    logger.error(f"Vertex AI init failed (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt == max_retries - 1:
                        raise LLMError(
                            f"Failed to initialize Vertex AI after {max_retries} attempts: {e}",
                            error_code="VERTEX_INIT_FAILED",
                            details={
                                "model_tier": model_tier.value,
                                "project_id": project_id,
                                "location": location,
                                "attempts": max_retries,
                            },
                        )
                    time.sleep(1)  # Wait before retry
            
        except LLMError:
            # Re-raise LLM errors
            raise
        except Exception as e:
            self._init_error = str(e)
            logger.error(f"Vertex AI initialization failed: {e}")
            raise LLMError(
                f"Failed to initialize Vertex AI: {e}",
                error_code="INITIALIZATION_ERROR",
                details={"model_tier": model_tier.value},
            )

        try:
            # Create LangChain ChatVertexAI instance with enhanced configuration
            config = get_config()
            
            # Enhanced timeout and token limits
            timeout = getattr(config, 'AGENT_TIMEOUT_SECONDS', 120)
            max_tokens = getattr(config, 'MAX_TOKENS_PER_REQUEST', 8192)
            
            self.llm = ChatVertexAI(
                model_name=self.model_name,
                temperature=0.7,
                max_output_tokens=max_tokens,
                timeout=timeout,
                # Add additional safety parameters
                max_retries=2,
                request_timeout=timeout - 10,  # Slightly less than overall timeout
            )
            
            self._initialized = True
            logger.info(f"ChatVertexAI instance created for model: {self.model_name}")
            
        except Exception as e:
            self._init_error = str(e)
            logger.error(f"Failed to create ChatVertexAI instance: {e}")
            raise LLMError(
                f"Failed to create ChatVertexAI instance: {e}",
                error_code="CHAT_VERTEX_INIT_FAILED",
                details={"model_tier": model_tier.value},
            )

        # Usage tracking
        self.usage_history: List[LLMUsage] = []
        self._current_usage: Optional[LLMUsage] = None

    @property
    def is_initialized(self) -> bool:
        """Check if LLM is properly initialized."""
        return self._initialized

    @property
    def initialization_error(self) -> Optional[str]:
        """Get initialization error if any."""
        return self._init_error

    async def generate(
        self, prompt: str, system_prompt: Optional[str] = None, **kwargs
    ) -> str:
        """Generate text response with enhanced error handling."""
        if not self._initialized:
            raise LLMError(
                "LLM not properly initialized",
                error_code="NOT_INITIALIZED",
                details={"model_tier": self.model_tier.value},
            )
        
        start_time = time.time()

        try:
            # Build messages
            messages: List[BaseMessage] = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))

            # Enhanced parameter handling
            runtime_config = {}
            
            # Temperature Modulation with validation
            current_temp = getattr(self.llm, "temperature", 0.7)
            if kwargs.get("creative_mode"):
                runtime_config["temperature"] = min(1.0, current_temp + 0.2)  # Cap at 1.0
            elif kwargs.get("analytical_mode"):
                runtime_config["temperature"] = max(0.0, current_temp - 0.5)  # Floor at 0.0
            
            # Token Limit Boost with validation
            current_max_tokens = getattr(self.llm, "max_output_tokens", 8192)
            if kwargs.get("strategy_mode"):
                # Double capacity for deep strategy with safety cap
                runtime_config["max_output_tokens"] = min(32768, current_max_tokens * 2)
            
            # Apply overrides if any
            if runtime_config:
                runnable = self.llm.bind(**runtime_config)
            else:
                runnable = self.llm

            # Generate response with timeout handling
            try:
                response = await asyncio.wait_for(
                    runnable.ainvoke(messages),
                    timeout=getattr(get_config(), 'AGENT_TIMEOUT_SECONDS', 120)
                )
            except asyncio.TimeoutError:
                raise LLMError(
                    "LLM generation timed out",
                    error_code="GENERATION_TIMEOUT",
                    details={"model_tier": self.model_tier.value},
                )
            
            content = response.content
            
            # Track usage
            latency_ms = int((time.time() - start_time) * 1000)
            self._track_usage(response, latency_ms)

            return content

        except LLMError:
            # Re-raise LLM errors
            raise
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise LLMError(
                f"LLM generation failed: {e}",
                error_code="GENERATION_ERROR",
                details={"model_tier": self.model_tier.value},
            )

    def _repair_json(self, json_str: str) -> str:
        """
        [FREEDOM TWEAK] Loose JSON Parsing
        Attempt to repair common LLM JSON errors defined by 'The 20 Tweaks'.
        """
        # 1. Strip markdown code blocks
        if "```" in json_str:
            json_str = json_str.replace("```json", "").replace("```", "").strip()
            
        # 2. Fix trailing commas (common in lists/dicts)
        import re
        json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
        
        # 3. Replace single quotes with double quotes (dangerous but often needed)
        # Only do this if we are desperate and it looks like a dict
        if "'" in json_str and '"' not in json_str:
             json_str = json_str.replace("'", '"')
             
        return json_str

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
                # [FREEDOM TWEAK] Robust Recovery
                # Try to extract and REPAIR JSON
                try:
                    start = content.find("{")
                    end = content.rfind("}") + 1
                    if start != -1 and end != 0:
                        candidate = content[start:end]
                        # Attempt standard load
                        parsed = json.loads(candidate)
                    else:
                        raise ValueError("No JSON object found")
                except (json.JSONDecodeError, ValueError):
                    # Last ditch effort: Repair common syntax errors
                    repaired = self._repair_json(content)
                    start = repaired.find("{")
                    end = repaired.rfind("}") + 1
                    if start != -1 and end != 0:
                        repaired_candidate = repaired[start:end]
                        parsed = json.loads(repaired_candidate)
                    else:
                        raise ValueError("Could not parse JSON even after repair")

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
            config = get_config()
            max_tokens = config.max_tokens_per_request
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


def validate_llm_setup() -> Dict[str, Any]:
    """Validate LLM setup and return status with enhanced error handling."""
    try:
        config = get_config()
        
        # Check configuration with proper attribute names
        project_id = getattr(config, 'GCP_PROJECT_ID', None) or os.getenv("GOOGLE_PROJECT_ID")
        region = getattr(config, 'GCP_REGION', None) or os.getenv("GOOGLE_REGION", "us-central1")
        
        if not project_id:
            return {
                "status": "error",
                "message": "GOOGLE_PROJECT_ID not configured",
                "provider": "vertexai",
                "missing_fields": ["GOOGLE_PROJECT_ID"],
            }
        
        # Test LLM initialization with error handling
        try:
            llm = get_llm(ModelTier.FLASH_LITE)
            return {
                "status": "healthy",
                "message": "LLM initialized successfully",
                "provider": "vertexai",
                "model": llm.model_name,
                "project_id": project_id,
                "region": region,
                "initialized": llm.is_initialized,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"LLM initialization failed: {str(e)}",
                "provider": "vertexai",
                "error_details": str(e),
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Configuration validation failed: {str(e)}",
            "provider": "vertexai",
            "error_details": str(e),
        }


def get_available_models() -> List[str]:
    """Get list of available model tiers."""
    return [tier.value for tier in ModelTier]
