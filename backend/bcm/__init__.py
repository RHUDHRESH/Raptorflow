"""
BCM Module - Business Context Manifest System.

The BCM system manages brand identity, learned preferences, and context
for AI-powered content generation.

Architecture:
├── core/          - BCM manifest CRUD and management
├── memory/        - Learned preferences and insights storage
├── reflection/    - Self-improvement through feedback analysis
└── prompts/       - BCM-specific prompt templates

Usage:
    from backend.bcm import BCMClient

    client = BCMClient()
    manifest = await client.get_manifest(workspace_id="ws_123")
"""

from backend.bcm.core import BCMClient, BCMManifest
from backend.bcm.memory import MemoryClient, MemoryType
from backend.bcm.reflection import ReflectionClient

__all__ = [
    "BCMClient",
    "BCMManifest",
    "MemoryClient",
    "MemoryType",
    "ReflectionClient",
]
