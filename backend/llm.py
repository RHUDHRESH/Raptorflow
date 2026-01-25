"""
Raptorflow LLM Integration
==========================

Comprehensive LLM integration layer supporting multiple providers
with unified interface, caching, and performance optimization.

Supported Providers:
- OpenAI (GPT-3.5, GPT-4, GPT-4-turbo)
- Google (Gemini Pro, Gemini Pro Vision)
- Anthropic (Claude-3 Sonnet, Claude-3 Opus)
- HuggingFace (Local models)
- Custom LLM endpoints

Features:
- Unified LLM interface
- Automatic retry and fallback
- Token counting and cost tracking
- Response caching
- Rate limiting
- Streaming support
- Structured output parsing
- Multi-modal support
"""

import asyncio
import hashlib
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

import structlog
import tiktoken

# Robust LangChain imports with fallbacks
try:
    from langchain_core.caches import BaseCache
except ImportError:

    class BaseCache:
        pass


try:
    from langchain.callbacks.base import BaseCallbackHandler
except ImportError:

    class BaseCallbackHandler:
        pass


try:
    from langchain.chat_models.base import BaseChatModel
except ImportError:

    class BaseChatModel:
        pass


try:
    from langchain.globals import set_llm_cache
except ImportError:

    def set_llm_cache(cache):
        pass


try:
    from langchain.llms.base import LLM
except ImportError:

    class LLM:
        pass


try:
    from langchain.memory import ConversationBufferMemory
except ImportError:

    class ConversationBufferMemory:
        pass


try:
    from langchain.schema import AIMessage, HumanMessage, SystemMessage
except ImportError:

    class AIMessage:
        pass

    class HumanMessage:
        pass

    class SystemMessage:
        pass


try:
    from langchain_core.messages import ChatMessage
except ImportError:

    class ChatMessage:
        pass


# Local imports
from .config import LLMProvider, settings

logger = structlog.get_logger(__name__)


class LLMRole(str, Enum):
    """LLM message roles."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class LLMModelType(str, Enum):
    """LLM model types."""

    TEXT = "text"
    VISION = "vision"
    CODE = "code"
    MULTIMODAL = "multimodal"


@dataclass
class LLMMessage:
    """Unified LLM message format."""

    role: LLMRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_langchain(self) -> ChatMessage:
        """Convert to LangChain message format."""
        if self.role == LLMRole.SYSTEM:
            return SystemMessage(content=self.content)
        elif self.role == LLMRole.USER:
            return HumanMessage(content=self.content)
        elif self.role == LLMRole.ASSISTANT:
            return AIMessage(content=self.content)
        else:
            return ChatMessage(role=self.role.value, content=self.content)


@dataclass
class LLMRequest:
    """LLM request configuration."""

    messages: List[LLMMessage]
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    stream: bool = False
    functions: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Union[str, Dict[str, Any]]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    response_format: Optional[Dict[str, Any]] = None
    seed: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """LLM response data."""

    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None
    response_time: float = 0.0
    cost: float = 0.0


@dataclass
class LLMTokenUsage:
    """Token usage information."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float = 0.0
    model: str = ""


class LLMCache(BaseCache):
    """Custom LLM cache implementation."""

    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.memory_cache = {}
        self.ttl = settings.CACHE_TTL

    def _generate_key(self, prompt: str, llm_string: str) -> str:
        """Generate cache key from prompt and LLM string."""
        content = f"{prompt}:{llm_string}"
        return hashlib.sha256(content.encode()).hexdigest()

    def lookup(self, prompt: str, llm_string: str) -> Optional[str]:
        """Look up cached response."""
        key = self._generate_key(prompt, llm_string)

        if self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    return cached.decode("utf-8")
            except Exception as e:
                logger.warning("Redis cache lookup failed", error=str(e))

        return self.memory_cache.get(key)

    def update(self, prompt: str, llm_string: str, return_val: str) -> None:
        """Update cache with new response."""
        key = self._generate_key(prompt, llm_string)

        if self.redis_client:
            try:
                self.redis_client.setex(key, self.ttl, return_val)
            except Exception as e:
                logger.warning("Redis cache update failed", error=str(e))

        self.memory_cache[key] = return_val

    def clear(self, **kwargs: Any) -> None:
        """Clear cache."""
        self.memory_cache.clear()
        if self.redis_client:
            try:
                # This is a bit dangerous on large Redis, but for dev/test it's fine
                # In prod, we'd use namespaces
                pass
            except Exception:
                pass

    async def alookup(self, prompt: str, llm_string: str) -> Optional[Any]:
        """Look up cached response asynchronously."""
        return self.lookup(prompt, llm_string)

    async def aupdate(self, prompt: str, llm_string: str, return_val: Any) -> None:
        """Update cache asynchronously."""
        self.update(prompt, llm_string, return_val)

    async def aclear(self, **kwargs: Any) -> None:
        """Clear cache asynchronously."""
        self.clear(**kwargs)


class TokenCounter:
    """Token counting utility for different models."""

    def __init__(self):
        self.encoders = {}

    def get_encoder(self, model: str) -> Any:
        """Get tokenizer for model."""
        if model not in self.encoders:
            try:
                if "gpt" in model.lower():
                    self.encoders[model] = tiktoken.encoding_for_model(model)
                else:
                    self.encoders[model] = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.encoders[model] = tiktoken.get_encoding("cl100k_base")
        return self.encoders[model]

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for specific model."""
        try:
            encoder = self.get_encoder(model)
            return len(encoder.encode(text))
        except Exception:
            # Fallback: rough estimation (1 token Γëê 4 characters)
            return len(text) // 4

    def count_messages_tokens(self, messages: List[LLMMessage], model: str) -> int:
        """Count tokens in messages."""
        total = 0
        for message in messages:
            total += self.count_tokens(message.content, model)
            # Add role tokens (rough estimation)
            total += 4
        return total


class CostCalculator:
    """Cost calculation for different models."""

    # Pricing per 1K tokens (USD)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
        "gemini-pro-vision": {"input": 0.00025, "output": 0.0005},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
    }

    def calculate_cost(
        self, input_tokens: int, output_tokens: int, model: str
    ) -> float:
        """Calculate cost for token usage."""
        pricing = self.PRICING.get(model, {"input": 0.001, "output": 0.002})
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        return input_cost + output_cost


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.token_counter = TokenCounter()
        self.cost_calculator = CostCalculator()
        self.cache = LLMCache()

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response from LLM."""
        pass

    @abstractmethod
    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response from LLM."""
        pass

    @abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text."""
        pass

    @abstractmethod
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get model information."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=config.get("api_key"))

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API."""
        start_time = time.time()

        try:
            # Convert messages to OpenAI format
            messages = [
                {"role": msg.role.value, "content": msg.content}
                for msg in request.messages
            ]

            # Make API call
            response = await self.client.chat.completions.create(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                frequency_penalty=request.frequency_penalty,
                presence_penalty=request.presence_penalty,
                stop=request.stop,
                functions=request.functions,
                function_call=request.function_call,
                tools=request.tools,
                tool_choice=request.tool_choice,
                response_format=request.response_format,
                seed=request.seed,
            )

            # Extract response
            choice = response.choices[0]
            content = choice.message.content or ""

            # Calculate metrics
            response_time = time.time() - start_time
            usage = {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": (
                    response.usage.completion_tokens if response.usage else 0
                ),
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            }
            cost = self.cost_calculator.calculate_cost(
                usage["prompt_tokens"], usage["completion_tokens"], request.model
            )

            return LLMResponse(
                content=content,
                model=request.model,
                usage=usage,
                finish_reason=choice.finish_reason,
                function_call=choice.message.function_call,
                tool_calls=choice.message.tool_calls,
                response_time=response_time,
                cost=cost,
                metadata={"provider": "openai"},
            )

        except Exception as e:
            logger.error("OpenAI API error", error=str(e), model=request.model)
            raise

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI API."""
        try:
            messages = [
                {"role": msg.role.value, "content": msg.content}
                for msg in request.messages
            ]

            stream = await self.client.chat.completions.create(
                model=request.model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error("OpenAI streaming error", error=str(e), model=request.model)
            raise

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens using OpenAI tokenizer."""
        return self.token_counter.count_tokens(text, model)

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get OpenAI model information."""
        return {
            "provider": "openai",
            "model": model,
            "max_tokens": 4096 if "gpt-3.5" in model else 8192,
            "supports_streaming": True,
            "supports_functions": True,
            "supports_vision": "vision" in model,
        }


class GoogleProvider(BaseLLMProvider):
    """Google Gemini LLM provider using standard SDK."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        from google import genai

        self.api_key = config.get("api_key")
        self.client = genai.Client(api_key=self.api_key)

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Gemini API."""
        start_time = time.time()

        try:
            model_name = request.model or "gemini-1.5-flash"
            
            # Convert messages
            contents = []
            for msg in request.messages:
                role = "user" if msg.role in [LLMRole.USER, LLMRole.SYSTEM] else "model"
                contents.append({"role": role, "parts": [msg.content]})
            
            response = self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config={
                    "temperature": request.temperature,
                    "max_output_tokens": request.max_tokens,
                    "top_p": request.top_p,
                }
            )

            content = response.text

            prompt_tokens = self.count_tokens(
                "\n".join([msg.content for msg in request.messages]), model_name
            )
            completion_tokens = self.count_tokens(content, model_name)

            return LLMResponse(
                content=content,
                model=model_name,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                },
                finish_reason="stop",
                response_time=time.time() - start_time,
                cost=0.0,
                metadata={"provider": "google_sdk"},
            )

        except Exception as e:
            logger.error("Gemini SDK error", error=str(e), model=request.model)
            raise

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response using Google Gemini API."""
        try:
            model = self.client.GenerativeModel(request.model)

            conversation = []
            for msg in request.messages:
                if msg.role == LLMRole.SYSTEM:
                    conversation.append(
                        {"role": "user", "parts": [{"text": f"System: {msg.content}"}]}
                    )
                else:
                    conversation.append(
                        {"role": msg.role.value, "parts": [{"text": msg.content}]}
                    )

            response = await model.generate_content_async(
                conversation,
                generation_config={
                    "temperature": request.temperature,
                    "max_output_tokens": request.max_tokens,
                    "top_p": request.top_p,
                },
                stream=True,
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error("Google streaming error", error=str(e), model=request.model)
            raise

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens using Google tokenizer."""
        return self.token_counter.count_tokens(text, model)

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get Google model information."""
        return {
            "provider": "google",
            "model": model,
            "max_tokens": 8192,
            "supports_streaming": True,
            "supports_functions": False,
            "supports_vision": "vision" in model,
        }


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude LLM provider."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic(api_key=config.get("api_key"))

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic Claude API."""
        start_time = time.time()

        try:
            # Convert messages to Claude format
            messages = []
            system_message = None

            for msg in request.messages:
                if msg.role == LLMRole.SYSTEM:
                    system_message = msg.content
                else:
                    messages.append({"role": msg.role.value, "content": msg.content})

            # Make API call
            response = await self.client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=messages,
                system=system_message,
            )

            # Extract response
            content = response.content[0].text if response.content else ""

            # Calculate metrics
            prompt_tokens = self.count_tokens(
                "\n".join([msg.content for msg in request.messages]), request.model
            )
            completion_tokens = self.count_tokens(content, request.model)
            total_tokens = prompt_tokens + completion_tokens
            response_time = time.time() - start_time
            cost = self.cost_calculator.calculate_cost(
                prompt_tokens, completion_tokens, request.model
            )

            return LLMResponse(
                content=content,
                model=request.model,
                usage={
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                },
                finish_reason="stop",
                response_time=response_time,
                cost=cost,
                metadata={"provider": "anthropic"},
            )

        except Exception as e:
            logger.error("Anthropic API error", error=str(e), model=request.model)
            raise

    async def generate_stream(self, request: LLMRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response using Anthropic Claude API."""
        try:
            messages = []
            system_message = None

            for msg in request.messages:
                if msg.role == LLMRole.SYSTEM:
                    system_message = msg.content
                else:
                    messages.append({"role": msg.role.value, "content": msg.content})

            response = await self.client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=messages,
                system=system_message,
                stream=True,
            )

            async for chunk in response:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text

        except Exception as e:
            logger.error("Anthropic streaming error", error=str(e), model=request.model)
            raise

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens using Anthropic tokenizer."""
        return self.token_counter.count_tokens(text, model)

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get Anthropic model information."""
        return {
            "provider": "anthropic",
            "model": model,
            "max_tokens": 4096,
            "supports_streaming": True,
            "supports_functions": False,
            "supports_vision": False,
        }


class LLMManager:
    """Main LLM manager with provider abstraction and caching."""

    def __init__(self):
        from .redis_core.client import get_redis

        self.providers = {}
        self.default_provider = None
        self.token_counter = TokenCounter()
        self.cost_calculator = CostCalculator()
        self.cache = LLMCache(redis_client=get_redis())
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize LLM providers based on configuration."""
        config = settings.get_llm_config()
        provider_type = config["provider"]

        if provider_type == "openai":
            self.providers["openai"] = OpenAIProvider(config)
            self.default_provider = "openai"
        elif provider_type == "google":
            self.providers["google"] = GoogleProvider(config)
            self.default_provider = "google"
        else:
            logger.warning(f"Unsupported LLM provider: {provider_type}")

    async def generate(
        self, request: LLMRequest, provider: Optional[str] = None, tier: str = "PRO"
    ) -> LLMResponse:
        """Generate response using specified or default provider."""
        provider_name = provider or self.default_provider

        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider not available: {provider_name}")

        provider = self.providers[provider_name]

        # Apply tier mapping for Google
        if provider_name == "google":
            tier_map = {"LITE": "gemini-1.5-flash", "PRO": "gemini-1.5-pro"}
            request.model = tier_map.get(tier, "gemini-1.5-pro")

        # Check cache first
        cache_key = self._generate_cache_key(request)
        cached_response = self.cache.lookup(cache_key, provider_name)
        if cached_response:
            logger.debug("LLM response cache hit", provider=provider_name)
            return LLMResponse(content=cached_response, model=request.model)

        # Generate response
        response = await provider.generate(request)

        # Cache response
        self.cache.update(cache_key, provider_name, response.content)

        # Log metrics
        logger.info(
            "LLM response generated",
            provider=provider_name,
            model=request.model,
            response_time=response.response_time,
            cost=response.cost,
            tokens=response.usage.get("total_tokens", 0),
        )

        return response

    async def generate_stream(
        self, request: LLMRequest, provider: Optional[str] = None, tier: str = "PRO"
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        provider_name = provider or self.default_provider

        if not provider_name or provider_name not in self.providers:
            raise ValueError(f"Provider not available: {provider_name}")

        provider = self.providers[provider_name]

        # Apply tier mapping for Google
        if provider_name == "google":
            tier_map = {"LITE": "gemini-1.5-flash", "PRO": "gemini-1.5-pro"}
            request.model = tier_map.get(tier, "gemini-1.5-pro")

        async for chunk in provider.generate_stream(request):
            yield chunk

    def _generate_cache_key(self, request: LLMRequest) -> str:
        """Generate cache key for request."""
        content = {
            "messages": [
                {"role": msg.role.value, "content": msg.content}
                for msg in request.messages
            ],
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
        return hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text."""
        return self.token_counter.count_tokens(text, model)

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())

    def get_provider_info(self, provider: str, model: str) -> Dict[str, Any]:
        """Get provider and model information."""
        if provider not in self.providers:
            raise ValueError(f"Provider not available: {provider}")

        return self.providers[provider].get_model_info(model)


# Rate limiting decorator
def rate_limit(calls: int, period: float):
    """Rate limiting decorator for LLM calls."""

    def decorator(func):
        calls_made = []

        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            calls_made[:] = [
                call_time for call_time in calls_made if now - call_time < period
            ]

            if len(calls_made) >= calls:
                sleep_time = period - (now - calls_made[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            calls_made.append(now)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Retry decorator
def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator for LLM calls."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        sleep_time = delay * (backoff**attempt)
                        logger.warning(
                            f"LLM call failed, retrying in {sleep_time}s",
                            attempt=attempt + 1,
                            error=str(e),
                        )
                        await asyncio.sleep(sleep_time)
                    else:
                        logger.error(
                            "LLM call failed after all retries",
                            attempts=max_retries,
                            error=str(e),
                        )

            raise last_exception

        return wrapper

    return decorator


# Global LLM manager instance
llm_manager = LLMManager()

# Set up caching
if settings.CACHE_MAX_SIZE > 0:
    set_llm_cache(llm_manager.cache)

# Export main components
__all__ = [
    "LLMManager",
    "LLMMessage",
    "LLMRequest",
    "LLMResponse",
    "LLMTokenUsage",
    "LLMRole",
    "LLMModelType",
    "BaseLLMProvider",
    "OpenAIProvider",
    "GoogleProvider",
    "AnthropicProvider",
    "TokenCounter",
    "CostCalculator",
    "LLMCache",
    "llm_manager",
    "rate_limit",
    "retry_on_failure",
]
