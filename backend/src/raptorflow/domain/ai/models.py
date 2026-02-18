"""
AI Domain Models - Core Entities and Value Objects.

This module defines the core domain entities for the AI system,
following hexagonal architecture principles with immutable value objects.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4


class ModelTier(Enum):
    """AI model capability tiers."""

    FAST = auto()  # Low latency, lower quality
    BALANCED = auto()  # Good balance
    PREMIUM = auto()  # Highest quality


class ExecutionStrategy(Enum):
    """AI execution strategies."""

    SINGLE = "single"  # One model, one pass
    ENSEMBLE = "ensemble"  # Multiple models, vote
    PIPELINE = "pipeline"  # Sequential processing
    COUNCIL = "council"  # Multiple models debating
    SWARM = "swarm"  # Multiple agents collaborating


class FinishReason(Enum):
    """Generation completion reasons."""

    STOP = "stop"
    LENGTH = "length"
    CONTENT_FILTER = "content_filter"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class TokenBudget:
    """Immutable token budget for generation."""

    max_input: int
    max_output: int
    max_total: int = 0

    def __post_init__(self):
        # Auto-calculate max_total if not provided
        if self.max_total == 0:
            object.__setattr__(self, "max_total", self.max_input + self.max_output)

        if self.max_total < self.max_input + self.max_output:
            raise ValueError("max_total must accommodate input + output")

    @classmethod
    def standard(cls) -> "TokenBudget":
        """Create standard token budget (4k input, 1k output)."""
        return cls(max_input=4000, max_output=1000)

    @classmethod
    def large(cls) -> "TokenBudget":
        """Create large token budget (8k input, 4k output)."""
        return cls(max_input=8000, max_output=4000)


@dataclass(frozen=True)
class GenerationConfig:
    """Immutable generation configuration."""

    temperature: float = 0.7
    top_p: float = 1.0
    top_k: int = 50
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    seed: Optional[int] = None
    response_format: Optional[str] = None  # "json", "text", etc.

    def __post_init__(self):
        if not 0 <= self.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")
        if not 0 <= self.top_p <= 1:
            raise ValueError("top_p must be between 0 and 1")
        if self.top_k < 0:
            raise ValueError("top_k must be non-negative")

    @classmethod
    def creative(cls) -> "GenerationConfig":
        """Creative configuration with higher temperature."""
        return cls(temperature=0.9, top_p=0.95)

    @classmethod
    def precise(cls) -> "GenerationConfig":
        """Precise configuration with lower temperature."""
        return cls(temperature=0.3, top_p=0.8)

    @classmethod
    def balanced(cls) -> "GenerationConfig":
        """Balanced default configuration."""
        return cls()


@dataclass
class GenerationRequest:
    """Domain entity for generation requests."""

    id: UUID = field(default_factory=uuid4)
    workspace_id: str = ""
    user_id: str = "system"
    prompt: str = ""
    system_prompt: Optional[str] = None
    config: GenerationConfig = field(default_factory=GenerationConfig)
    budget: TokenBudget = field(default_factory=TokenBudget.standard)
    strategy: ExecutionStrategy = ExecutionStrategy.SINGLE
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.workspace_id:
            raise ValueError("workspace_id is required")
        if not self.prompt:
            raise ValueError("prompt is required")

    @property
    def cache_key(self) -> str:
        """Generate cache key based on prompt and config."""
        import hashlib

        content = f"{self.prompt}:{self.system_prompt}:{self.config.temperature}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class GenerationResult:
    """Domain entity for generation results."""

    request_id: UUID
    text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    provider: str = ""
    cost_usd: float = 0.0
    latency_ms: int = 0
    finish_reason: str = ""
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def success(self) -> bool:
        return bool(self.text) and self.finish_reason != "error"

    @property
    def finish_reason_enum(self) -> FinishReason:
        try:
            return FinishReason(self.finish_reason)
        except ValueError:
            return FinishReason.ERROR


@dataclass
class ModelCapability:
    """Model capability specification."""

    name: str
    tier: ModelTier
    max_tokens: int
    supports_system_prompt: bool = True
    supports_functions: bool = False
    supports_vision: bool = False
    supports_streaming: bool = True
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    provider: str = ""
    description: str = ""

    @property
    def cost_per_1k_total(self) -> float:
        return self.cost_per_1k_input + self.cost_per_1k_output


@dataclass
class ExecutionPlan:
    """Planned execution strategy for a request."""

    request_id: UUID
    executor_type: str
    model: ModelCapability
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_cost_usd: float
    fallback_models: List[str] = field(default_factory=list)
    retry_count: int = 0


@dataclass
class TokenUsage:
    """Token usage tracking."""

    workspace_id: str
    user_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    period_start: datetime
    period_end: datetime


# Common model definitions
class Models:
    """Predefined model capabilities."""

    GEMINI_2_0_FLASH = ModelCapability(
        name="gemini-2.0-flash",
        tier=ModelTier.BALANCED,
        max_tokens=8192,
        supports_system_prompt=True,
        supports_functions=True,
        supports_vision=True,
        cost_per_1k_input=0.0,  # Check current pricing
        cost_per_1k_output=0.0,
        provider="google",
        description="Google Gemini 2.0 Flash - balanced speed and quality",
    )

    GEMINI_2_0_FLASH_LITE = ModelCapability(
        name="gemini-2.0-flash-lite",
        tier=ModelTier.FAST,
        max_tokens=4096,
        supports_system_prompt=True,
        supports_functions=False,
        supports_vision=False,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        provider="google",
        description="Google Gemini 2.0 Flash Lite - fastest, most cost-effective",
    )

    GEMINI_2_0_PRO = ModelCapability(
        name="gemini-2.0-pro",
        tier=ModelTier.PREMIUM,
        max_tokens=32768,
        supports_system_prompt=True,
        supports_functions=True,
        supports_vision=True,
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
        provider="google",
        description="Google Gemini 2.0 Pro - highest quality",
    )
