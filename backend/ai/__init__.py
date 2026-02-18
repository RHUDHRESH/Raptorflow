"""
AI Module - Modular AI Backend System

This module provides a clean, extensible interface for AI generation
with multiple backend support, orchestration strategies, and profiles.

Architecture:
├── backends/       - AI backend implementations (VertexAI, GenAI, etc.)
├── orchestration/  - Generation strategies (single, council, swarm)
├── profiles/       - Intensity and reasoning profiles
└── prompts/       - Prompt building utilities

Usage:
    from backend.ai import AIClient, GenerationRequest, GenerationResult

    client = AIClient()
    result = await client.generate(GenerationRequest(
        prompt="Write a marketing email",
        workspace_id="ws_123",
    ))
"""

from backend.ai.client import AIClient, get_client
from backend.ai.hub import AIHubRuntime
from backend.ai.types import (
    GenerationRequest,
    GenerationResult,
    BackendHealth,
    ExecutionMode,
    IntensityLevel,
    ReasoningDepth,
)
from backend.ai.profiles import AIProfile, ProfileRegistry
from backend.ai.backends import BackendRegistry, BackendType

__all__ = [
    "AIClient",
    "AIHubRuntime",
    "get_client",
    "GenerationRequest",
    "GenerationResult",
    "BackendHealth",
    "ExecutionMode",
    "IntensityLevel",
    "ReasoningDepth",
    "AIProfile",
    "ProfileRegistry",
    "BackendRegistry",
    "BackendType",
]
