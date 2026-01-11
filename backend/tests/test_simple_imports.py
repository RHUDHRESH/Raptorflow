#!/usr/bin/env python3
"""
Simple import test to identify missing dependencies
"""

import os
import sys


def test_imports():
    """Test basic imports."""
    print("🧪 Testing basic imports...")

    try:
        print("  Testing agents.config...")
        from agents.config import ModelTier, get_config

        print("  ✅ agents.config")
    except Exception as e:
        print(f"  ❌ agents.config: {e}")
        return False

    try:
        print("  Testing agents.state...")
        from agents.state import AgentState, create_initial_state

        print("  ✅ agents.state")
    except Exception as e:
        print(f"  ❌ agents.state: {e}")
        return False

    try:
        print("  Testing agents.llm...")
        from agents.llm import VertexAILLM

        print("  ✅ agents.llm")
    except Exception as e:
        print(f"  ❌ agents.llm: {e}")
        return False

    try:
        print("  Testing agents.base...")
        from agents.base import BaseAgent

        print("  ✅ agents.base")
    except Exception as e:
        print(f"  ❌ agents.base: {e}")
        return False

    try:
        print("  Testing agents.tools.registry...")
        from agents.tools.registry import get_tool_registry

        print("  ✅ agents.tools.registry")
    except Exception as e:
        print(f"  ❌ agents.tools.registry: {e}")
        return False

    try:
        print("  Testing agents.routing.pipeline...")
        from agents.routing.pipeline import RoutingPipeline

        print("  ✅ agents.routing.pipeline")
    except Exception as e:
        print(f"  ❌ agents.routing.pipeline: {e}")
        return False

    try:
        print("  Testing agents.dispatcher...")
        from agents.dispatcher import AgentDispatcher

        print("  ✅ agents.dispatcher")
    except Exception as e:
        print(f"  ❌ agents.dispatcher: {e}")
        return False

    try:
        print("  Testing agents.graphs.main...")
        from agents.graphs.main import create_raptorflow_graph

        print("  ✅ agents.graphs.main")
    except Exception as e:
        print(f"  ❌ agents.graphs.main: {e}")
        return False

    print("🎉 All imports successful!")
    return True


if __name__ == "__main__":
    # Set environment variables
    os.environ.setdefault("GCP_PROJECT_ID", "test-project")
    os.environ.setdefault("GCP_REGION", "us-central1")
    os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
    os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key")
    os.environ.setdefault("UPSTASH_REDIS_URL", "https://test.redis.upstash.io")
    os.environ.setdefault("UPSTASH_REDIS_TOKEN", "test-token")
    os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key-32-chars-long")

    success = test_imports()
    sys.exit(0 if success else 1)
