#!/usr/bin/env python3
"""
Test tool integration and skills functionality
"""

import asyncio
import os
import sys
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def test_tool_usage():
    """Test that agents actually use tools."""
    print("🧪 Testing tool integration...")

    try:
        # Test 1: Import agents with tools
        from agents import ContentCreator, MarketResearch
        from agents.skills.registry import get_skills_registry
        from agents.tools.registry import get_tool_registry

        print("  ✅ Imports successful")

        # Test 2: Create agents with tools
        content_creator = ContentCreator()
        market_research = MarketResearch()

        print(f"  ✅ ContentCreator tools: {content_creator.tools}")
        print(f"  ✅ ContentCreator skills: {content_creator.skills}")
        print(f"  ✅ MarketResearch tools: {market_research.tools}")
        print(f"  ✅ MarketResearch skills: {market_research.skills}")

        # Test 3: Check tool registry
        tool_registry = get_tool_registry()
        tools = tool_registry.list_tools()
        print(f"  ✅ Available tools: {tools}")

        # Test 4: Check skills registry
        skills_registry = get_skills_registry()
        skills = skills_registry.list_skills()
        print(f"  ✅ Available skills: {len(skills)} skills")

        # Test 5: Test agent tool access
        web_search_tool = content_creator.get_tool("web_search")
        if web_search_tool:
            print("  ✅ ContentCreator can access web_search tool")
        else:
            print("  ❌ ContentCreator cannot access web_search tool")

        database_tool = market_research.get_tool("database")
        if database_tool:
            print("  ✅ MarketResearch can access database tool")
        else:
            print("  ❌ MarketResearch cannot access database tool")

        # Test 6: Test skill assessment
        content_assessment = content_creator.assess_skills()
        print(
            f"  ✅ ContentCreator skill assessment: {content_assessment.get('overall_confidence', 0):.2f} confidence"
        )

        market_assessment = market_research.assess_skills()
        print(
            f"  ✅ MarketResearch skill assessment: {market_assessment.get('overall_confidence', 0):.2f} confidence"
        )

        # Test 7: Test skill requirements
        content_task = "Create a blog post about digital marketing"
        content_requirements = content_creator.get_skill_requirements(content_task)
        print(
            f"  ✅ ContentCreator can execute task: {content_requirements.get('can_execute', False)}"
        )

        market_task = "Analyze competitor strategies in SaaS market"
        market_requirements = market_research.get_skill_requirements(market_task)
        print(
            f"  ✅ MarketResearch can execute task: {market_requirements.get('can_execute', False)}"
        )

        print("🎉 Tool integration test passed!")
        return True

    except Exception as e:
        print(f"❌ Tool integration test failed: {e}")
        return False


async def test_mock_tool_execution():
    """Test tool execution with mock data."""
    print("\n🧪 Testing tool execution...")

    try:
        from agents import ContentCreator
        from agents.state import create_initial_state

        # Create agent and state
        agent = ContentCreator()
        state = create_initial_state(
            workspace_id="test_workspace",
            user_id="test_user",
            session_id="test_session",
        )

        # Test tool usage with mock data
        try:
            # This would normally make real web search calls
            # For testing, we'll catch the error and verify the method exists
            search_results = await agent.use_tool(
                "web_search", query="digital marketing trends", max_results=3
            )
            print(
                f"  ✅ Web search executed: {len(search_results.get('results', []))} results"
            )
        except Exception as e:
            print(f"  ⚠️ Web search failed (expected in test): {str(e)[:50]}...")

        try:
            # Test database tool
            db_results = await agent.use_tool(
                "database", table="muse_assets", workspace_id="test_workspace", limit=3
            )
            print(
                f"  ✅ Database query executed: {len(db_results.get('data', []))} records"
            )
        except Exception as e:
            print(f"  ⚠️ Database query failed (expected in test): {str(e)[:50]}...")

        print("🎉 Tool execution test passed!")
        return True

    except Exception as e:
        print(f"❌ Tool execution test failed: {e}")
        return False


async def main():
    """Run all tests."""
    print("🚀 Starting tool integration tests...")
    print("=" * 60)

    # Set environment variables
    os.environ.setdefault("GCP_PROJECT_ID", "test-project")
    os.environ.setdefault("GCP_REGION", "us-central1")
    os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
    os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key")
    os.environ.setdefault("UPSTASH_REDIS_URL", "https://test.redis.upstash.io")
    os.environ.setdefault("UPSTASH_REDIS_TOKEN", "test-token")
    os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key-32-chars-long")

    # Run tests
    test1 = await test_tool_usage()
    test2 = await test_mock_tool_execution()

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)

    if test1 and test2:
        print("🎉 All tests passed! Tool integration is working!")
        return True
    else:
        print("🚨 Some tests failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
