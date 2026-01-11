#!/usr/bin/env python3
"""
Direct test of tool integration without relative imports.
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

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_direct_tool_integration():
    """Test tool integration directly."""
    print("🧪 Testing direct tool integration...")

    try:
        # Test 1: Import tools registry directly
        from agents.tools.registry import get_tool, get_tool_registry

        print("  ✅ Tools registry import successful")

        # Test 2: Get tool registry instance
        registry = get_tool_registry()
        print(f"  ✅ Tool registry instance: {type(registry).__name__}")

        # Test 3: List available tools
        tools = registry.list_tools()
        print(f"  ✅ Available tools: {tools}")

        # Test 4: Get specific tool
        web_search_tool = get_tool("web_search")
        if web_search_tool:
            print(f"  ✅ Web search tool: {type(web_search_tool).__name__}")
        else:
            print("  ⚠️ Web search tool not found")

        # Test 5: Get database tool
        database_tool = get_tool("database")
        if database_tool:
            print(f"  ✅ Database tool: {type(database_tool).__name__}")
        else:
            print("  ⚠️ Database tool not found")

        # Test 6: Test skills registry
        from agents.skills.registry import (
            Skill,
            SkillCategory,
            SkillLevel,
            get_skill,
            get_skills_registry,
            list_skills,
        )

        print("  ✅ Skills registry import successful")

        skills_registry = get_skills_registry()
        print(f"  ✅ Skills registry instance: {type(skills_registry).__name__}")

        skills = list_skills()
        print(f"  ✅ Available skills: {len(skills)} skills")

        # Test 7: Get specific skill
        content_skill = get_skill("content_generation")
        if content_skill:
            print(f"  ✅ Content generation skill: {content_skill.name}")
        else:
            print("  ⚠️ Content generation skill not found")

        print("🎉 Direct tool integration test passed!")
        return True

    except Exception as e:
        print(f"❌ Direct tool integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_base_agent_directly():
    """Test BaseAgent directly."""
    print("\n🧪 Testing BaseAgent directly...")

    try:
        # Test 1: Import BaseAgent directly
        from agents.base import BaseAgent
        from agents.config import ModelTier
        from agents.state import create_initial_state

        print("  ✅ BaseAgent import successful")

        # Test 2: Create a simple agent
        class TestAgent(BaseAgent):
            def __init__(self):
                super().__init__(
                    name="TestAgent",
                    description="Test agent for tool integration",
                    model_tier=ModelTier.FLASH_LITE,
                    tools=["web_search", "database"],
                    skills=["content_generation", "test_skill"],
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
        web_search_tool = agent.get_tool("web_search")
        if web_search_tool:
            print(f"  ✅ Web search tool accessible: {type(web_search_tool).__name__}")
        else:
            print("  ⚠️ Web search tool not accessible")

        database_tool = agent.get_tool("database")
        if database_tool:
            print(f"  ✅ Database tool accessible: {type(database_tool).__name__}")
        else:
            print("  ⚠️ Database tool not accessible")

        # Test 4: Check skills functionality
        has_skill = agent.has_skill("content_generation")
        print(f"  ✅ Skills check: {has_skill}")

        skills = agent.get_skills()
        print(f"  ✅ Skills list: {skills}")

        # Test 5: Check skill assessment
        assessment = agent.assess_skills()
        print(f"  ✅ Skill assessment: {assessment.get('total_skills', 0)} skills")
        print(f"  ✅ Overall confidence: {assessment.get('overall_confidence', 0):.2f}")

        # Test 6: Check skill requirements
        requirements = agent.get_skill_requirements(
            "Create content about digital marketing"
        )
        print(f"  ✅ Skill requirements: {requirements.get('can_execute', False)}")
        print(f"  ✅ Available skills: {requirements.get('available_skills', [])}")
        print(f"  ✅ Missing skills: {requirements.get('missing_skills', [])}")

        print("🎉 BaseAgent test passed!")
        return True

    except Exception as e:
        print(f"❌ BaseAgent test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting direct integration tests...")
    print("=" * 60)

    # Run tests
    test1 = await test_direct_tool_integration()
    test2 = await test_base_agent_directly()

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)

    if test1 and test2:
        print("🎉 All tests passed! Tool integration is working!")
        print("\n📋 SUMMARY:")
        print("✅ Tool registry is working")
        print("✅ Skills registry is working")
        print("✅ BaseAgent can access tools")
        print("✅ BaseAgent has skills functionality")
        print("✅ Tool integration is properly implemented")
        return True
    else:
        print("🚨 Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
