"""
AI Types - Core type definitions for the AI module.

These types are intentionally decoupled from any specific backend
or orchestration implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionMode(str, Enum):
    SINGLE = "single"
    COUNCIL = "council"
    SWARM = "swarm"


class IntensityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReasoningDepth(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BackendType(str, Enum):
    VERTEX_AI = "vertex_ai"
    GENAI_API_KEY = "genai_api_key"
    DETERMINISTIC_FALLBACK = "deterministic_fallback"
    UNCONFIGURED = "unconfigured"


@dataclass
class GenerationRequest:
    prompt: str
    workspace_id: str
    user_id: str = "system"
    max_tokens: int = 800
    temperature: float = 0.7
    system_prompt: Optional[str] = None
    content_type: str = "general"
    execution_mode: ExecutionMode = ExecutionMode.SINGLE
    intensity: IntensityLevel = IntensityLevel.MEDIUM
    reasoning_depth: ReasoningDepth = ReasoningDepth.MEDIUM
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.execution_mode, str):
            self.execution_mode = ExecutionMode(self.execution_mode)
        if isinstance(self.intensity, str):
            self.intensity = IntensityLevel(self.intensity)
        if isinstance(self.reasoning_depth, str):
            self.reasoning_depth = ReasoningDepth(self.reasoning_depth)


@dataclass
class GenerationResult:
    status: str
    text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    generation_time_seconds: float = 0.0
    model: str = ""
    model_type: str = ""
    backend: BackendType = BackendType.UNCONFIGURED
    error: Optional[str] = None
    fallback_reason: Optional[str] = None
    ensemble: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.status == "success"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "text": self.text,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd,
            "generation_time_seconds": self.generation_time_seconds,
            "model": self.model,
            "model_type": self.model_type,
            "backend": self.backend.value
            if isinstance(self.backend, BackendType)
            else self.backend,
            "error": self.error,
            "fallback_reason": self.fallback_reason,
            "ensemble": self.ensemble,
            "metadata": self.metadata,
        }


@dataclass
class BackendHealth:
    status: str
    backend: BackendType = BackendType.UNCONFIGURED
    model: str = ""
    fallback_ready: bool = False
    detail: Optional[str] = None

    @property
    def healthy(self) -> bool:
        return self.status == "healthy"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "backend": self.backend.value
            if isinstance(self.backend, BackendType)
            else self.backend,
            "model": self.model,
            "fallback_ready": self.fallback_ready,
            "detail": self.detail,
        }


@dataclass
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    timestamp: datetime
    workspace_id: str
    user_id: str
    backend: BackendType

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cost_usd": self.cost_usd,
            "timestamp": self.timestamp.isoformat(),
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "backend": self.backend.value,
        }
