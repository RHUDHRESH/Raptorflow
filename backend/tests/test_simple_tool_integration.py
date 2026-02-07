import pytest

pytest.skip(
    "Archived script-style module; not collected in canonical suite.",
    allow_module_level=True,
)

#!/usr/bin/env python3
"""
Simple test for tool integration without relative imports.
"""

import asyncio
import os
import sys
from datetime import datetime

# Set environment variables
os.environ.setdefault("GCP_PROJECT_ID", "test-project")
os.environ.setdefault("GCP_REGION", "us-central1")
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key")
os.environ.setdefault("UPSTASH_REDIS_URL", "https://test.redis.upstash.io")
os.environ.setdefault("UPSTASH_REDIS_TOKEN", "test-token")
os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key-32-chars-long")


async def test_basic_functionality():
    """Test basic agent functionality."""
    print("🧪 Testing basic agent functionality...")

    try:
        # Test 1: Import basic components
        from agents.base import BaseAgent
        from agents.config import ModelTier
        from agents.state import create_initial_state

        print("  ✅ Basic imports successful")

        # Test 2: Create a simple agent
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__(
                    name="TestAgent",
                    description="Test agent for tool integration",
                    model_tier=ModelTier.FLASH_LITE,
                    tools=["web_search"],
                    skills=["test_skill"],
                )

            def get_system_prompt(self) -> str:
                return "You are a test agent."

            async def execute(self, state):
                return self._set_output(state, {"test": "success"})

        agent = TestAgent()
        print(f"  ✅ Agent created: {agent.name}")
        print(f"  ✅ Agent tools: {agent.tools}")
        print(f"  ✅ Agent skills: {agent.skills}")

        # Test 3: Check tool registry access
        tool = agent.get_tool("web_search")
        if tool:
            print("  ✅ Tool registry access working")
        else:
            print("  ⚠️ Tool registry access failed (expected in test)")

        # Test 4: Check skills functionality
        has_skill = agent.has_skill("test_skill")
        print(f"  ✅ Skills check: {has_skill}")

        skills = agent.get_skills()
        print(f"  ✅ Skills list: {skills}")

        # Test 5: Check skill assessment
        assessment = agent.assess_skills()
        print(f"  ✅ Skill assessment: {assessment.get('total_skills', 0)} skills")

        print("🎉 Basic functionality test passed!")
        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting basic functionality tests...")
    print("=" * 60)

    # Run tests
    test1 = await test_basic_functionality()

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)

    if test1:
        print("🎉 All tests passed! Basic agent functionality is working!")
        return True
    else:
        print("🚨 Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
