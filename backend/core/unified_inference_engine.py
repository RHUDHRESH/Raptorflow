"""
Unified Inference Engine
========================

A universal AI inference engine that seamlessly switches between REAL and SIMULATED modes.
This replaces the need for separate REAL_INFERENCE_ENGINE.py and SIMULATED versions
by providing a unified interface with configuration-based mode switching.

Features:
- Seamless real/simulated mode switching via configuration
- Unified interface for all LLM providers
- Automatic fallback to simulation when API keys are missing
- Consistent response format across modes
- Zero-code-change migration from simulated to real inference

Usage:
    # In your code, simply use UnifiedInferenceEngine
    engine = UnifiedInferenceEngine()
    response = await engine.generate(request)

    # Toggle mode via environment variable:
    # INFERENCE_MODE=real    -> Use real LLM providers
    # INFERENCE_MODE=simulate -> Use simulated responses
"""

import asyncio
import hashlib
import json
import os
import re
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional

import structlog

try:
    from config import settings
except ImportError:
    from backend.config import settings
try:
    from llm import (
        CostCalculator,
        LLMManager,
        LLMMessage,
        LLMRequest,
        LLMRole,
        TokenCounter,
    )
except ImportError:
    from backend.llm import (
        CostCalculator,
        LLMManager,
        LLMMessage,
        LLMRequest,
        LLMRole,
        TokenCounter,
    )

try:
    from inference_cache import get_inference_cache
except ImportError:
    from backend.core.inference_cache import get_inference_cache

logger = structlog.get_logger(__name__)


class InferenceMode(str, Enum):
    """Inference mode types."""

    REAL = "real"
    SIMULATE = "simulate"
    AUTO = "auto"  # Auto-detect based on API keys


class ResponseStyle(str, Enum):
    """Response styles for simulated mode."""

    CREATIVE = "creative"  # More varied, imaginative responses
    PROFESSIONAL = "professional"  # Formal, business-like responses
    TECHNICAL = "technical"  # Detailed, technical responses
    CONCISE = "concise"  # Short, direct responses


@dataclass
class InferenceContext:
    """Context for inference requests."""

    request_id: str
    workspace_id: str
    user_id: str
    session_id: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedRequest:
    """Unified request format for inference."""

    prompt: str
    system_prompt: Optional[str] = None
    context: Optional[InferenceContext] = None
    model: str = "gemini-1.5-pro"
    temperature: float = 0.7
    max_tokens: int = 2048
    style: ResponseStyle = ResponseStyle.PROFESSIONAL
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UnifiedResponse:
    """Unified response format for inference."""

    content: str
    model: str
    mode: InferenceMode
    request_id: str
    response_time_ms: float
    tokens_used: int
    cost_usd: float
    cached: bool = False
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseInferenceEngine(ABC):
    """Base class for inference engines."""

    @abstractmethod
    async def generate(
        self, request: UnifiedRequest, context: Optional[InferenceContext] = None
    ) -> UnifiedResponse:
        """Generate a response."""
        pass

    @abstractmethod
    async def generate_stream(
        self, request: UnifiedRequest, context: Optional[InferenceContext] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response."""
        pass

    @abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text."""
        pass


class SimulatedInferenceEngine(BaseInferenceEngine):
    """
    Simulated inference engine for development and testing.

    Generates realistic-looking responses based on prompt content,
    user context, and configured response style.
    """

    # Response templates by style
    TEMPLATES = {
        ResponseStyle.CREATIVE: {
            "greetings": [
                "Here's a creative approach to your question: ",
                "Let me think outside the box for this one... ",
                "Interesting challenge! Here's what I envision: ",
                "I'm excited about this possibility! ",
            ],
            "acknowledgments": [
                "Absolutely! ",
                "Great thinking! ",
                "I love this direction! ",
                "Here's an innovative solution: ",
            ],
            "closings": [
                " Let me know what you think!",
                " Hope this sparks some ideas!",
                " Looking forward to exploring this further!",
                " This could be just the beginning!",
            ],
        },
        ResponseStyle.PROFESSIONAL: {
            "greetings": [
                "Based on your request, here's the analysis: ",
                "Thank you for your inquiry. Here's our response: ",
                "Regarding your question, please find the following: ",
                "I've reviewed your request and prepared the following: ",
            ],
            "acknowledgments": [
                "Understood. ",
                "Acknowledged. ",
                "Noted. ",
                "Understood, proceeding with: ",
            ],
            "closings": [
                " Please let me know if you need clarification.",
                " Feel free to reach out for further details.",
                " We're here to assist with any follow-up questions.",
                " This completes the response to your query.",
            ],
        },
        ResponseStyle.TECHNICAL: {
            "greetings": [
                "Technical analysis: ",
                "Implementation details: ",
                "Technical specification: ",
                "Here's the technical breakdown: ",
            ],
            "acknowledgments": [
                "Processing... ",
                "Analyzing... ",
                "Computing... ",
                "Executing query... ",
            ],
            "closings": [
                " [End of technical response]",
                " Technical implementation complete.",
                " This concludes the technical analysis.",
                " Reference: Implementation complete.",
            ],
        },
        ResponseStyle.CONCISE: [
            "Response: ",
            "Here: ",
            "Answer: ",
            "Summary: ",
        ],
    }

    # Keyword-based response mappings
    KEYWORD_RESPONSES = {
        "plan": "Here's a structured plan for your request:\n\n1. Define objectives\n2. Identify key steps\n3. Allocate resources\n4. Set timeline\n5. Execute and monitor\n6. Review and optimize",
        "strategy": "Strategic approach:\n\n- Analyze current state\n- Define target state\n- Identify gaps\n- Develop roadmap\n- Prioritize initiatives\n- Measure progress",
        "analysis": "Analysis complete:\n\nKey findings:\n• Current performance metrics\n• Opportunity areas\n• Recommended actions\n• Expected outcomes\n• Success criteria",
        "code": "```python\n# Code implementation\ndef solve():\n    # Your solution here\n    pass\n```\n\nThis provides a starting point. Let me know if you need modifications.",
        "summary": "Summary:\n\n• Main point 1\n• Main point 2\n• Main point 3\n\nKey takeaway: Action items defined.",
        "help": "I'm here to help! I can assist with:\n- Planning and strategy\n- Technical implementation\n- Analysis and insights\n- Content creation\n- Problem solving\n\nWhat would you like to work on?",
        "question": "Great question! Here's what you need to know:\n\n[Detailed explanation based on context]",
        "explain": "Let me explain this clearly:\n\n1. Start with the basics\n2. Build up to complexity\n3. Provide examples\n4. Summarize key points",
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize simulated engine."""
        self.config = config or {}
        self.token_counter = TokenCounter()
        self.cost_calculator = CostCalculator()
        self._response_cache = {}

    def _get_style_templates(self, style: ResponseStyle) -> Dict[str, List[str]]:
        """Get response templates for the given style."""
        return self.TEMPLATES.get(style, self.TEMPLATES[ResponseStyle.PROFESSIONAL])

    def _generate_greeting(self, style: ResponseStyle) -> str:
        """Generate a greeting based on style."""
        templates = self._get_style_templates(style)
        greetings = templates.get("greetings", [])
        return greetings[0] if greetings else "Response: "

    def _generate_closing(self, style: ResponseStyle) -> str:
        """Generate a closing based on style."""
        templates = self._get_style_templates(style)
        closings = templates.get("closings", [])
        return closings[0] if closings else ""

    def _generate_acknowledgment(self, style: ResponseStyle) -> str:
        """Generate an acknowledgment based on style."""
        templates = self._get_style_templates(style)
        acknowledgments = templates.get("acknowledgments", [])
        return acknowledgments[0] if acknowledgments else "OK. "

    def _generate_keyword_response(self, prompt: str, style: ResponseStyle) -> str:
        """Generate a response based on detected keywords."""
        prompt_lower = prompt.lower()

        for keyword, response in self.KEYWORD_RESPONSES.items():
            if keyword in prompt_lower:
                return response

        return None

    def _generate_contextual_response(
        self, prompt: str, style: ResponseStyle, context: Optional[InferenceContext]
    ) -> str:
        """Generate a contextual response."""
        # Extract key terms from prompt
        words = re.findall(r"\b\w+\b", prompt.lower())
        key_terms = [w for w in words if len(w) > 3][:5]

        # Build response based on context
        if context:
            workspace_context = context.metadata.get("workspace", "")
            user_context = context.metadata.get("user", "")

            response = f"Based on your workspace context ({workspace_context[:50] if workspace_context else 'general'}) "
            response += f"and query about {', '.join(key_terms)}, "
        else:
            response = f"Regarding your query about {', '.join(key_terms)}, "

        if style == ResponseStyle.CONCISE:
            response = f"Query: {prompt[:100]}...\nResponse: "
        else:
            response += self._generate_acknowledgment(style)

        # Add content based on prompt type
        if "?" in prompt:
            response += (
                "I've analyzed your question and prepared the following insights:\n\n"
            )
            response += "• Understanding of the issue\n"
            response += "• Potential approaches\n"
            response += "• Recommended solution\n\n"
        else:
            response += "Here's what I can help you with:\n\n"
            response += "1. Detailed analysis of your request\n"
            response += "2. Actionable recommendations\n"
            response += "3. Next steps and considerations\n"

        response += self._generate_closing(style)
        return response

    def _generate_default_response(
        self, prompt: str, style: ResponseStyle, context: Optional[InferenceContext]
    ) -> str:
        """Generate a default response when no keyword match."""
        greeting = self._generate_greeting(style)

        if style == ResponseStyle.CONCISE:
            return f"{greeting}\n\nPrompt: {prompt[:200]}...\n\nResponse generated in simulated mode."

        response = f"{greeting}\n\n"
        response += f"I received your message: \"{prompt[:100]}{'...' if len(prompt) > 100 else ''}\"\n\n"

        # Add contextual awareness
        if context:
            response += f"[Context: Workspace {context.workspace_id[:8]}... | User {context.user_id[:8]}...]\n\n"

        response += (
            "In a production environment, this would be processed by a real LLM.\n"
        )
        response += "For simulated mode, I'm providing a placeholder response.\n\n"
        response += "To enable real inference:\n"
        response += "1. Configure your LLM API keys in environment variables\n"
        response += "2. Set INFERENCE_MODE=real in your .env file\n"
        response += "3. Restart the application\n\n"
        response += self._generate_closing(style)

        return response

    async def generate(
        self, request: UnifiedRequest, context: Optional[InferenceContext] = None
    ) -> UnifiedResponse:
        """Generate a simulated response."""
        start_time = time.time()

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Build cache key
        cache_content = {
            "prompt": request.prompt,
            "system_prompt": request.system_prompt,
            "model": request.model,
            "temperature": request.temperature,
            "style": request.style.value,
        }
        cache_key = hashlib.sha256(
            json.dumps(cache_content, sort_keys=True).encode()
        ).hexdigest()

        # Check cache
        if cache_key in self._response_cache:
            cached_response = self._response_cache[cache_key]
            return UnifiedResponse(
                content=cached_response,
                model=request.model,
                mode=InferenceMode.SIMULATE,
                request_id=request_id,
                response_time_ms=(time.time() - start_time) * 1000,
                tokens_used=self.token_counter.count_tokens(
                    cached_response, request.model
                ),
                cost_usd=0.0,
                cached=True,
            )

        # Generate response based on prompt content
        keyword_response = self._generate_keyword_response(
            request.prompt, request.style
        )

        if keyword_response:
            response_content = keyword_response
        else:
            response_content = self._generate_contextual_response(
                request.prompt, request.style, context
            )

        # Cache response
        self._response_cache[cache_key] = response_content

        # Calculate metrics
        response_time_ms = (time.time() - start_time) * 1000
        tokens_used = self.token_counter.count_tokens(response_content, request.model)
        cost_usd = 0.0  # No cost for simulated mode

        return UnifiedResponse(
            content=response_content,
            model=request.model,
            mode=InferenceMode.SIMULATE,
            request_id=request_id,
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            finish_reason="stop",
            metadata={"style": request.style.value, "simulated": True},
        )

    async def generate_stream(
        self, request: UnifiedRequest, context: Optional[InferenceContext] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a simulated streaming response."""
        response = await self.generate(request, context)

        # Simulate streaming by yielding chunks
        chunks = response.content.split(" ")
        for i, chunk in enumerate(chunks):
            yield chunk + (" " if i < len(chunks) - 1 else "")
            await asyncio.sleep(0.01)  # Simulate network delay

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text."""
        return self.token_counter.count_tokens(text, model)


class RealInferenceEngine(BaseInferenceEngine):
    """
    Real inference engine that uses actual LLM providers.

    This wraps the existing LLM providers with a unified interface.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the real inference engine."""
        self.config = config or {}
        self.llm_manager = LLMManager()
        self.token_counter = TokenCounter()
        self.cost_calculator = CostCalculator()
        self._cache = get_inference_cache()

    def _convert_to_llm_request(
        self, request: UnifiedRequest, context: Optional[InferenceContext]
    ) -> LLMRequest:
        """Convert unified request to LLM request."""
        messages = []

        # Add system prompt if provided
        if request.system_prompt:
            messages.append(
                LLMMessage(role=LLMRole.SYSTEM, content=request.system_prompt)
            )

        # Add user prompt
        messages.append(LLMMessage(role=LLMRole.USER, content=request.prompt))

        return LLMRequest(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    async def generate(
        self, request: UnifiedRequest, context: Optional[InferenceContext] = None
    ) -> UnifiedResponse:
        """Generate a real response using LLM providers."""
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Convert to LLM request
        llm_request = self._convert_to_llm_request(request, context)

        # Check cache
        cache_key = self._generate_cache_key(llm_request)
        cached = await self._cache.get(cache_key)
        if cached:
            logger.debug("Real inference cache hit", request_id=request_id)
            return UnifiedResponse(
                content=cached,
                model=request.model,
                mode=InferenceMode.REAL,
                request_id=request_id,
                response_time_ms=0,
                tokens_used=self.token_counter.count_tokens(cached, request.model),
                cost_usd=0.0,
                cached=True,
            )

        # Generate response using LLM manager
        llm_response = await self.llm_manager.generate(llm_request)

        # Cache response
        await self._cache.set(cache_key, llm_response.content)

        # Calculate metrics
        response_time_ms = (time.time() - start_time) * 1000
        tokens_used = llm_response.usage.get("total_tokens", 0)
        cost_usd = llm_response.cost

        return UnifiedResponse(
            content=llm_response.content,
            model=request.model,
            mode=InferenceMode.REAL,
            request_id=request_id,
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            finish_reason=llm_response.finish_reason,
            metadata={
                "provider": llm_response.metadata.get("provider", "unknown"),
                "response_time": llm_response.response_time,
            },
        )

    async def generate_stream(
        self, request: UnifiedRequest, context: Optional[InferenceContext] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a real streaming response."""
        llm_request = self._convert_to_llm_request(request, context)
        async for chunk in self.llm_manager.generate_stream(llm_request):
            yield chunk

    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text."""
        return self.token_counter.count_tokens(text, model)

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


class UnifiedInferenceEngine:
    """
    Unified inference engine that seamlessly switches between real and simulated modes.

    This is the main entry point for all inference operations. It automatically
    selects the appropriate engine based on configuration.

    Configuration (via environment variables):
    - INFERENCE_MODE: "real", "simulate", or "auto" (default: "auto")
    - For auto mode, checks for API keys and falls back to simulation if missing
    """

    _instance: Optional["UnifiedInferenceEngine"] = None
    _initialized: bool = False

    def __new__(cls) -> "UnifiedInferenceEngine":
        """Singleton pattern for consistent engine instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the unified inference engine."""
        if self._initialized:
            return

        self._mode = self._get_inference_mode()
        self._simulated_engine = SimulatedInferenceEngine()
        self._real_engine: Optional[RealInferenceEngine] = None

        # Initialize real engine only if needed
        if self._mode == InferenceMode.REAL:
            try:
                self._real_engine = RealInferenceEngine()
                logger.info("Real inference engine initialized", mode=self._mode.value)
            except Exception as e:
                logger.warning(
                    "Failed to initialize real engine, falling back to simulate",
                    error=str(e),
                )
                self._mode = InferenceMode.SIMULATE

        logger.info(
            "Unified inference engine initialized",
            mode=self._mode.value,
            real_available=self._real_engine is not None,
        )

        self._initialized = True

    def _get_inference_mode(self) -> InferenceMode:
        """Determine inference mode from configuration."""
        mode_env = os.environ.get("INFERENCE_MODE", "auto").lower()

        if mode_env == "real":
            return InferenceMode.REAL
        elif mode_env == "simulate":
            return InferenceMode.SIMULATE
        elif mode_env == "auto":
            return self._auto_detect_mode()
        else:
            logger.warning(f"Unknown inference mode: {mode_env}, using auto")
            return self._auto_detect_mode()

    def _auto_detect_mode(self) -> InferenceMode:
        """Auto-detect mode based on available API keys."""
        # Check for OpenAI key
        openai_key = os.environ.get("OPENAI_API_KEY") or getattr(
            settings, "openai_api_key", None
        )
        if openai_key:
            return InferenceMode.REAL

        # Check for Google key
        google_key = os.environ.get("GOOGLE_API_KEY") or getattr(
            settings, "google_api_key", None
        )
        if google_key:
            return InferenceMode.REAL

        # Check for Anthropic key
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY") or getattr(
            settings, "anthropic_api_key", None
        )
        if anthropic_key:
            return InferenceMode.REAL

        # Default to simulate if no keys found
        logger.info("No API keys found, using simulate mode")
        return InferenceMode.SIMULATE

    def get_current_mode(self) -> InferenceMode:
        """Get the current inference mode."""
        return self._mode

    def set_mode(self, mode: InferenceMode) -> None:
        """Set inference mode at runtime."""
        self._mode = mode
        if mode == InferenceMode.REAL and self._real_engine is None:
            try:
                self._real_engine = RealInferenceEngine()
            except Exception as e:
                logger.error("Failed to initialize real engine", error=str(e))
                self._mode = InferenceMode.SIMULATE

        logger.info("Inference mode changed", mode=mode.value)

    async def generate(
        self, request: UnifiedRequest, context: Optional[InferenceContext] = None
    ) -> UnifiedResponse:
        """
        Generate a response using the appropriate engine.

        Args:
            request: Unified request containing prompt and configuration
            context: Optional inference context with request metadata

        Returns:
            UnifiedResponse with generated content and metadata
        """
        if self._mode == InferenceMode.SIMULATE:
            return await self._simulated_engine.generate(request, context)
        elif self._mode == InferenceMode.REAL and self._real_engine:
            return await self._real_engine.generate(request, context)
        else:
            # Fallback to simulated if real engine not available
            logger.warning("Real engine not available, falling back to simulate")
            return await self._simulated_engine.generate(request, context)

    async def generate_stream(
        self, request: UnifiedRequest, context: Optional[InferenceContext] = None
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming response."""
        if self._mode == InferenceMode.SIMULATE:
            async for chunk in self._simulated_engine.generate_stream(request, context):
                yield chunk
        elif self._mode == InferenceMode.REAL and self._real_engine:
            async for chunk in self._real_engine.generate_stream(request, context):
                yield chunk
        else:
            # Fallback to simulated
            async for chunk in self._simulated_engine.generate_stream(request, context):
                yield chunk

    def count_tokens(self, text: str, model: str = "gemini-1.5-pro") -> int:
        """Count tokens in text."""
        return self._simulated_engine.count_tokens(text, model)

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the inference engine."""
        return {
            "mode": self._mode.value,
            "real_available": self._real_engine is not None,
            "providers_available": (
                self._real_engine.llm_manager.get_available_providers()
                if self._real_engine
                else []
            ),
        }


# Convenience function for quick access
def get_inference_engine() -> UnifiedInferenceEngine:
    """Get the global unified inference engine instance."""
    return UnifiedInferenceEngine()


# Export for easy imports
__all__ = [
    "UnifiedInferenceEngine",
    "UnifiedRequest",
    "UnifiedResponse",
    "InferenceMode",
    "InferenceContext",
    "ResponseStyle",
    "BaseInferenceEngine",
    "SimulatedInferenceEngine",
    "RealInferenceEngine",
    "get_inference_engine",
]
